# Implementación del ETL y Guía Técnica

**Herramienta:** Apache Spark 4.2 (PySpark) · **Origen:** PostgreSQL 18 (`invacom_fuente`) · **Destino:** SQL Server 2025 (`InvacomDW`)

Este documento explica **cómo está construido y cómo se ejecuta** el ETL descrito en `04_diseno_etl.md`, el porqué de las decisiones técnicas y las preguntas que se esperan en la sustentación.

---

## 1. Cómo ejecutarlo

### 1.1 Requisitos

| Componente | Versión usada | Nota |
|---|---|---|
| Python | 3 con entorno virtual `.venv` | `pip install -r requirements.txt` (pyspark, python-dotenv) |
| Java | 25 (Temurin) | Spark corre sobre la JVM |
| PostgreSQL | 18 | Base `invacom_fuente` cargada con `psql -f sql/fuente/invacom_fuente.sql` |
| SQL Server | 2025 Developer | Base `InvacomDW`, autenticación mixta, TCP 1433, tablas creadas con `sql/dw/01_crear_modelo_estrella.sql` |
| winutils | `C:\hadoop\bin` | Solo Windows: Spark lo necesita para manejar archivos temporales |

Los drivers JDBC (PostgreSQL y SQL Server) **no se instalan a mano**: Spark los descarga solo la primera vez (`spark.jars.packages` en `config.py`).

### 1.2 Archivo `.env` (raíz del repositorio, no se sube a Git)

```
PG_HOST=localhost
PG_PORT=5432
PG_DB=invacom_fuente
PG_USER=...
PG_PASSWORD=...
MS_HOST=localhost
MS_PORT=1433
MS_DB=InvacomDW
MS_USER=etl_spark
MS_PASSWORD=...
```

### 1.3 Comandos (Git Bash en Windows)

```bash
source .venv/Scripts/activate

winpty python etl/main.py                         # carga completa + validación
winpty python etl/main.py --probar dim_cliente    # transforma una tabla y la muestra, sin escribir en el DW
winpty python etl/validacion.py                   # solo valida lo que ya está cargado
```

`winpty` permite que **Ctrl+C** funcione en Git Bash. En PowerShell o CMD se omite.

Resultado esperado de la carga completa (≈ 95 s):

```
dim_tiempo 1095 · dim_cliente 91 · dim_producto 77 · dim_empleado 9
dim_transportista 3 · dim_descuento 11 · dim_estado_envio 9
fact_ventas 2155 · fact_pedidos 830
Validación: 13 OK · 0 ERROR · 0 PENDIENTE
```

### 1.4 Consultas de análisis

`sql/dw/02_consultas_analisis.sql` se abre en SSMS y se ejecuta con F5. Trae los totales de control y una consulta por cada una de las 9 preguntas de negocio (`03_modelo_dimensional.md` §6). Para correr una sola consulta, se selecciona y se presiona F5.

---

## 2. Estructura del código

```
etl/
├── config.py              Sesión de Spark, conexiones JDBC y utilidades compartidas
├── main.py                Orquestador: extrae, vacía el DW, carga dimensiones, hechos y valida
├── dim_tiempo.py          Dimensiones (una por archivo)
├── dim_cliente.py
├── dim_producto.py
├── dim_empleado.py
├── dim_transportista.py
├── dim_descuento.py
├── dim_estado_envio.py
├── fact_ventas.py         Hechos
├── fact_pedidos.py
└── validacion.py          Conciliación fuente vs. DW
```

**Contrato de cada módulo:** expone `TABLA` (nombre de la tabla destino) y una función `transformar(...)` que **recibe DataFrames y devuelve un DataFrame**. Ningún módulo lee ni escribe por su cuenta: solo `main.py` lo hace. Esto permitió que cada integrante desarrollara y probara su tabla por separado (`--probar`).

### 2.1 `main.py`: orden de ejecución

| Etapa | Qué hace | Por qué en ese orden |
|---|---|---|
| 1. Extracción | Lee las 7 tablas de PostgreSQL por JDBC y las deja en caché | Se leen una sola vez y las reutilizan todas las transformaciones |
| 2. Vaciado | `DELETE` de hechos → dimensiones y reinicio de `IDENTITY` con `DBCC CHECKIDENT` | Los hechos tienen llaves foráneas hacia las dimensiones: se borran primero |
| 3. Dimensiones | `transformar` + escritura de las 7 dimensiones | Los hechos necesitan sus llaves sustitutas |
| 4. Hechos | Relee las dimensiones **desde SQL Server** y carga `fact_ventas` y `fact_pedidos` | Las llaves `IDENTITY` las genera SQL Server al insertar; Spark no las conoce hasta releerlas |
| 5. Validación | Ejecuta `validacion.ejecutar` | Confirma que el DW cuadra con la fuente antes de usar los reportes |

Si falta el archivo de alguna tabla, `main.py` la marca como **PENDIENTE** y sigue: así se pudo integrar el trabajo por partes.

### 2.2 `config.py`: utilidades compartidas

| Función | Uso |
|---|---|
| `crear_spark()` | Sesión local (`local[*]`), drivers JDBC, zona horaria UTC, logs reducidos |
| `leer_fuente` / `leer_dw` / `escribir_dw` | Lectura y escritura JDBC. Se escribe con `mode="append"` |
| `ejecutar_sql_dw` | Ejecuta `DELETE` y `DBCC` en SQL Server (Spark no ejecuta sentencias por JDBC) |
| `limpiar_texto` | `trim` + espacios múltiples → uno (H4) |
| `estandarizar_pais` | `UK` → `United Kingdom`, `USA` → `United States` (H5) |
| `fecha_key` | Fecha → entero `AAAAMMDD` (llave de `dim_tiempo`); NULL si la fecha es nula |
| `buscar_llave` | Lookup de llave sustituta con LEFT JOIN; **detiene el ETL** si alguna fila no encuentra su llave |

---

## 3. Transformaciones implementadas

### 3.1 Dimensiones

| Tabla | Origen | Lo más importante |
|---|---|---|
| `dim_tiempo` | Generada | 1095 días (2013–2015) con `sequence` + `explode`. Llave `AAAAMMDD`. Nombres de mes y día en español fijos, sin depender del idioma de la máquina. `dia_semana` 1 = lunes |
| `dim_cliente` | `customers` | 91 clientes, incluidos los 2 sin compras (H9). Limpieza de textos y países |
| `dim_producto` | `products` + `categories` | Join para desnormalizar la categoría (estrella, no copo de nieve). `discontinued` → Sí/No (H10). `precio_lista` es solo descriptivo (H6) |
| `dim_empleado` | `employees` × `employees` | **Self-join** para el nombre del jefe; Andrew Fuller queda como `Sin jefe (Dirección)` (H3) |
| `dim_transportista` | `shippers` | 3 transportistas |
| `dim_descuento` | `distinct order_details.discount` | Dimensión de **bandas**: 11 porcentajes agrupados en Sin descuento / Bajo / Medio / Alto. Conserva los atípicos del pedido 11077 (H7) |
| `dim_estado_envio` | Generada | **Junk dimension**: 9 combinaciones de estado × cumplimiento × rango de días. Se insertan en un solo bloque (`coalesce(1)`) para que las llaves sean siempre las mismas (1 = Enviado/A tiempo/0-7 días … 9 = Pendiente) |

`dim_estado_envio.columnas_estado()` contiene **las reglas de clasificación** de un pedido (Pendiente si no tiene `shipped_date`; A tiempo si `shipped_date ≤ required_date`; rango según días de despacho). La usa `fact_pedidos`, así la dimensión y los hechos nunca pueden tener reglas distintas.

### 3.2 `fact_ventas` (una fila por línea de pedido, 2155)

1. `calcular_lineas(fuente)`: join `order_details` + `orders` por `order_id` y cálculo de medidas:
   - `monto_bruto = precio_unitario × cantidad`
   - `monto_descuento = monto_bruto × descuento_pct`
   - `monto_neto = monto_bruto − monto_descuento`
2. Lookup de llaves sustitutas con `buscar_llave`: cliente, producto, empleado, transportista y descuento (este último por su porcentaje).
3. Se usa el **precio histórico** de `order_details`, nunca el de catálogo (H6).

### 3.3 `fact_pedidos` (una fila por pedido, 830)

1. Reutiliza `calcular_lineas` y agrupa por pedido: `lineas = count(*)`, `monto_neto_pedido = sum(monto_neto)`.
2. Medidas de logística:
   - `fecha_envio_key`, `dias_despacho`, `entregado_a_tiempo` → **NULL en los 21 pedidos pendientes** (H2)
   - `entregado_a_tiempo` = 1 / 0, para que en Excel el **promedio sea directamente el % de entregas a tiempo**
3. Clasificación con `columnas_estado()` y lookup de `estado_envio_key` por las 3 columnas.
4. Lookup de cliente, empleado y transportista.

### 3.4 Validación (`validacion.py`)

Compara **fuente, DW y valor esperado** en 13 controles (conteos de las 9 tablas, ventas netas, flete total, pedidos pendientes y pedidos tarde) y muestra OK / ERROR / PENDIENTE. Los totales se calculan en DECIMAL en ambos lados. También se puede correr sola, sin recargar.

---

## 4. Decisiones técnicas y su justificación

| Decisión | Alternativa descartada | Por qué |
|---|---|---|
| **ETL** (transformar en Spark) | ELT (transformar dentro de SQL Server) | El DW solo recibe datos limpios y la lógica queda versionada en Python |
| **Carga completa** en cada ejecución | Carga incremental | ≈ 3 000 filas y fuente estática: más simple y el DW queda idéntico a la fuente. En producción se usaría incremental + SCD tipo 2 |
| `DELETE` + `DBCC CHECKIDENT` | `TRUNCATE` | SQL Server no permite `TRUNCATE` en tablas referenciadas por llaves foráneas |
| `mode="append"` sobre tablas ya creadas | `mode="overwrite"` | `overwrite` borra y recrea la tabla, y se pierden PK, FK y tipos del script SQL |
| Llaves sustitutas `IDENTITY` + relectura | Generarlas en Spark | La base es la dueña de las llaves; los hechos las obtienen releyendo las dimensiones |
| `dim_tiempo` con llave `AAAAMMDD` | `IDENTITY` | Es legible, ordena bien y los hechos la calculan directo desde la fecha, sin lookup |
| Medidas en **DECIMAL** | `float` / `double` | El float acumula errores de redondeo; con DECIMAL la suma da exacto **1 265 793.04** |
| Montos con 4 decimales | 2 decimales | `monto_bruto × descuento` produce 4 decimales; redondear por línea haría que la suma no cuadre |
| Dos tablas de hechos | Una sola | Flete, fechas y cumplimiento son del **pedido**: en `fact_ventas` se repetirían por cada producto y el flete saldría inflado al sumar |
| `buscar_llave` con LEFT JOIN + error | INNER JOIN | Un INNER JOIN descarta en silencio las filas sin llave; así el ETL avisa cuáles faltan |
| Pendientes con NULL | 0 o fecha ficticia | Un 0 bajaría el % de entregas a tiempo y el promedio de días; `AVG` ignora los NULL |
| Junk dimension `dim_estado_envio` | 3 columnas de texto en el hecho | Menos texto repetido en 830 filas y un solo filtro en Excel |

---

## 5. Problemas conocidos (Windows)

| Síntoma | Causa | Qué hacer |
|---|---|---|
| `Failed to delete ... Temp\spark-...` al terminar | Windows bloquea archivos temporales de Spark | Inofensivo, se ignora |
| El proceso no termina después de imprimir el resultado | Cierre de la JVM de Spark en Windows | Con `winpty`, Ctrl+C. Sin `winpty`, finalizar `java.exe` en el Administrador de tareas |
| `dim_estado_envio` tarda ≈ 20 s | Crear un DataFrame desde una lista de Python arranca un proceso de Python aparte | No afecta el resultado |
| `stdout is not a tty` | Se combinó `winpty` con `>` o `| tee` | Usar `winpty` sin redirección |

---

## 6. Preguntas probables del jurado

### Arquitectura y herramienta

**¿Por qué Spark para tan pocos datos?**
Fue la herramienta asignada. Su ventaja es que el mismo código escala: si Invacom pasara a millones de filas, solo cambia `master("local[*]")` por un clúster. Para este volumen procesa todo en memoria en segundos.

**¿Dónde ocurre la transformación?**
En memoria, dentro de Spark, antes de llegar a SQL Server. Por eso es ETL y no ELT.

**¿Cómo se conecta Spark a las bases?**
Por JDBC, con los drivers oficiales de PostgreSQL y SQL Server. Las credenciales se leen del `.env`, que no se sube al repositorio.

**¿Qué pasa si se ejecuta dos veces?**
Nada malo: cada ejecución vacía el DW y lo recarga completo, y los contadores `IDENTITY` se reinician. El resultado es siempre el mismo (idempotente).

### Modelo y llaves

**¿Por qué estrella y no copo de nieve?**
La categoría se desnormalizó dentro de `dim_producto`. Hay menos joins, las consultas son más simples y Excel lo navega mejor.

**¿Qué es una llave sustituta y por qué no usar el ID de la fuente?**
Es un entero propio del DW (`cliente_key`). Desacopla el DW de los códigos del sistema origen (por ejemplo, `customer_id` es texto) y permitiría guardar historia de cambios (SCD tipo 2) en el futuro.

**¿Cómo obtiene `fact_ventas` la llave del cliente?**
Relee `dim_cliente` desde SQL Server y hace un join por `cliente_id` (llave de negocio) para traer `cliente_key`. Si un cliente no existe en la dimensión, el ETL se detiene y dice cuál es.

**¿Qué es `pedido_id` en los hechos?**
Una **dimensión degenerada**: identifica el pedido pero no tiene atributos propios, así que no necesita su propia tabla.

**¿Qué es una junk dimension?**
`dim_estado_envio` agrupa indicadores de baja cardinalidad (estado, cumplimiento, rango de días) en una tabla pequeña de 9 filas. Se generan todas las combinaciones, aunque 2 no tengan pedidos hoy (Tarde con 0-7 y 8-14 días), para que el DW acepte datos futuros sin cambios.

### Calidad de datos

**¿Cómo trataron los nulos?**
- `shipped_date` (21 pedidos): no son errores, son **pendientes**. Se conservan en las ventas y quedan fuera del % de entregas y de los días de despacho (H2).
- `reports_to` (1 empleado): es el máximo jerarca, se muestra como `Sin jefe (Dirección)` (H3).

**¿Por qué el precio de la venta no coincide con el de catálogo?**
Son 658 líneas. `order_details.unit_price` es el precio pactado en cada venta (histórico); el de `products` es el actual. Las ventas siempre usan el histórico (H6).

**¿Corrigieron el cliente `Blondesddsl père et fils`?**
No. Parece un error de digitación, pero no se modifica sin confirmación del negocio; se reportó al Product Owner (H11).

**¿Qué hicieron con los descuentos raros del pedido 11077?**
Son válidos (entre 0 y 25 %), pero fuera de la política habitual. Se conservaron y quedan en los rangos Bajo y Medio (H7).

### Validación y resultados

**¿Cómo saben que la carga es correcta?**
`validacion.py` compara 13 controles entre la fuente y el DW: los conteos de todas las tablas, las ventas netas (1 265 793.04 exacto), el flete total (64 942.69), los 21 pendientes y los 37 pedidos tarde. La última carga dio 13 de 13 OK.

**¿Por qué no usaron float para los montos?**
El float acumula errores de redondeo en las sumas. Con DECIMAL el total coincide al centavo con la fuente.

**Si sumo el flete en `fact_ventas`, ¿sale inflado?**
El flete no está en `fact_ventas`: está en `fact_pedidos`, una fila por pedido. Por eso existen dos tablas de hechos.

### Mejoras futuras

- **Carga incremental** (solo pedidos nuevos o modificados) en lugar de carga completa.
- **SCD tipo 2** en cliente y producto para guardar el historial de cambios (por ejemplo, un cliente que cambia de país).
- **Orquestación** programada (Airflow, o el Programador de tareas de Windows) con alertas si la validación da ERROR.
