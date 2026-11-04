# Tablas dinámicas en Excel conectadas al DW

Issue #18 · Requisito del enunciado (tarea 10): *"Visualizar los resultados mediante tablas dinámicas en Excel conectadas al DW"*. Rúbrica, criterio 3 (10 %): conexión exitosa y tablas que respondan los requerimientos del usuario, sin duplicados ni montos mal sumados.

Archivo: `excel/Invacom_DW_Tablas_Dinamicas.xlsx`

---

## 1. Arquitectura

```
SQL Server · InvacomDW
  dbo.fact_ventas  + 6 dimensiones ──► rpt.vw_ventas   (2155 filas, 1 por línea)
  dbo.fact_pedidos + 6 dimensiones ──► rpt.vw_pedidos  (830 filas, 1 por pedido)
                                              │
                         Power Query (conexión SQL Server, solo lectura)
                                              │
                         Modelo de datos de Excel (Data Model)
                                              │
                         9 tablas dinámicas (una hoja por pregunta de negocio)
```

**Decisiones:**

| Decisión | Motivo |
|---|---|
| Vistas en un esquema `rpt` | Capa de presentación: nombres de negocio en español ("Ventas netas", "Categoría") en lugar de llaves. El modelo estrella (`dbo`) no se modifica. |
| Una vista por tabla de hechos | Cada vista respeta la granularidad de su hecho. El **flete** solo existe en `vw_pedidos`: si estuviera en la vista de ventas, un pedido con 5 productos sumaría su flete 5 veces. |
| Rol `rol_lector_excel` con `SELECT` solo sobre `rpt` | Excel no usa el usuario del ETL (`etl_spark`, `db_owner`). Principio de mínimo privilegio. |
| Cargar al **Modelo de datos** | Habilita **Recuento distinto** (pedidos y clientes en la vista de ventas) y hace que el promedio ignore los nulos de los pedidos pendientes. |
| Prefijo `1.`, `2.`… en los rangos | Excel ordena texto alfabéticamente; el prefijo mantiene el orden lógico (Sin descuento → Alto; 0-7 días → Sin enviar). |
| Columna contador (`Líneas` = 1, `Pedidos` = 1) | Sumarla da el número de filas sin depender de qué columna se cuente. |

---

## 2. Preparar el DW (una sola vez)

En **SSMS**, conectado a `localhost` (Autenticación de Windows):

1. Abrir `sql/dw/03_vistas_excel.sql` → **F5**.
2. Revisar la primera grilla de resultados:

   | lineas_vista | ventas_netas_vista | pedidos_vista | flete_vista | pendientes | tarde |
   |---|---|---|---|---|---|
   | 2155 | 1265793.04 | 830 | 64942.69 | 21 | 37 |

   Si coincide, las vistas no duplican ni pierden filas.
3. (Opcional) Usuario SQL `excel_lector`: descomentar el bloque del paso 4 del script, poner una contraseña propia y ejecutar **solo ese bloque**. No subir la contraseña real a Git.

---

## 3. Conectar Excel al DW

Excel de Microsoft 365 para Windows, en el laptop donde corre SQL Server.

1. Excel → libro en blanco → guardar como `excel/Invacom_DW_Tablas_Dinamicas.xlsx` (dentro del clon).
2. **Datos → Obtener datos → De una base de datos → Desde una base de datos de SQL Server** (*Data → Get Data → From Database → From SQL Server Database*).
3. Servidor: `localhost` · Base de datos: `InvacomDW` → **Aceptar**.
4. Credenciales: pestaña **Windows** → *Usar mis credenciales actuales* (o pestaña **Base de datos** con `excel_lector`) → **Conectar**.
   - Si aparece *"No se puede conectar con una conexión cifrada"* → **Aceptar** para conectar sin cifrar (es un servidor local con certificado autofirmado).
5. En el Navegador: marcar **Seleccionar varios elementos** → marcar `rpt.vw_ventas` y `rpt.vw_pedidos`.
6. Abrir la flecha de **Cargar** → **Cargar en…** → *Crear solo conexión* + marcar **Agregar estos datos al Modelo de datos** → **Aceptar**.
7. **Datos → Consultas y conexiones**: deben aparecer las 2 consultas con 2155 y 830 filas cargadas.
8. Clic derecho en cada consulta → **Propiedades** → marcar **Actualizar datos al abrir el archivo**.

Las credenciales quedan en la configuración de orígenes de datos de Windows del usuario, **no dentro del .xlsx**, así que el archivo se puede subir al repo.

---

## 4. Crear cada tabla dinámica

Para todas: **Insertar → Tabla dinámica → Del modelo de datos** (*From Data Model*) → **Hoja de cálculo nueva**. Renombrar la hoja como se indica.

Ajustes que se repiten:

- **Cambiar la operación:** clic en el campo de Valores → *Configuración de campo de valor* → Suma / Promedio / Recuento distinto.
- **Formato:** misma ventana → *Formato de número* → Número con 2 decimales y separador de miles, o Porcentaje.
- **Mostrar como %:** misma ventana → pestaña *Mostrar valores como* → **% del total general**.
- **Top 10:** flecha de *Etiquetas de fila* → *Filtros de valor* → *Diez mejores…* → 10, por *Suma de Ventas netas*.
- **Renombrar el encabezado** del valor (ej. "Suma de Ventas netas" → "Ventas netas " con un espacio al final, porque Excel no deja repetir el nombre exacto del campo) para que se lea como reporte.

### P1 · Evolución de las ventas — hoja `P1 Tiempo`
Fuente: `vw_ventas`
| Área | Campo | Operación |
|---|---|---|
| Filas | Año → Trimestre | |
| Valores | Ventas netas | Suma |
| Valores | Pedido | **Recuento distinto** |

Agregar un **gráfico dinámico** de líneas (*Analizar tabla dinámica → Gráfico dinámico*). Nota visible en la hoja: *2013 (desde julio) y 2015 (hasta mayo) son años parciales*.

### P2 · Categorías y productos — hoja `P2 Productos`
Fuente: `vw_ventas`
| Área | Campo | Operación |
|---|---|---|
| Filas | Categoría | |
| Valores | Ventas netas | Suma |
| Valores | Ventas netas (otra vez) | Suma, *Mostrar como* % del total general |
| Valores | Cantidad | Suma |

Ordenar de mayor a menor por ventas. Segunda tabla dinámica en la misma hoja: Filas = **Producto**, Valores = Ventas netas (Suma), filtro **Top 10**.

### P3 · Países y clientes — hoja `P3 Clientes`
Fuente: `vw_ventas`
| Área | Campo | Operación |
|---|---|---|
| Filas | País | |
| Valores | Ventas netas | Suma |
| Valores | Código cliente | **Recuento distinto** |

Segunda tabla: Filas = **Cliente**, Valores = Ventas netas, filtro **Top 10**. Agregar una **segmentación** (*slicer*) de **Año**.

### P4 · Desempeño de los vendedores — hoja `P4 Vendedores`
Fuente: `vw_ventas`
| Área | Campo | Operación |
|---|---|---|
| Filas | Vendedor | |
| Columnas | Año | |
| Valores | Ventas netas | Suma |
| Valores | Pedido | **Recuento distinto** |

### P5 · Ticket promedio — hoja `P5 Ticket`
Fuente: **`vw_pedidos`**
| Área | Campo | Operación |
|---|---|---|
| Filas | Año | |
| Valores | Pedidos | Suma |
| Valores | Monto pedido | **Promedio** |

Ticket = ventas netas / pedidos. Se calcula sobre `vw_pedidos` porque ahí hay una fila por pedido; promediar en `vw_ventas` daría el promedio por **línea**, que es otra cosa.

### P6 · Dinero no percibido por descuentos — hoja `P6 Descuentos`
Fuente: `vw_ventas`
| Área | Campo | Operación |
|---|---|---|
| Filas | Rango descuento | |
| Valores | Líneas | Suma |
| Valores | Líneas (otra vez) | Suma, *Mostrar como* % del total general |
| Valores | Monto bruto | Suma |
| Valores | Monto descuento | Suma |

Filtro opcional: **Categoría**.

### P7 · Cumplimiento de entregas — hoja `P7 Entregas`
Fuente: **`vw_pedidos`**
| Área | Campo | Operación |
|---|---|---|
| Filas | Año | |
| Columnas | Cumplimiento | |
| Valores | Pedidos | Suma |

Segunda tabla: Filas = **Año**, Valores = **A tiempo** con **Promedio**, formato Porcentaje. El promedio ignora los 21 pendientes (A tiempo = NULL), así que da el % solo de los pedidos enviados.

### P8 · Transportistas — hoja `P8 Transportistas`
Fuente: **`vw_pedidos`**
| Área | Campo | Operación |
|---|---|---|
| Filtros | Estado envío = **Enviado** | |
| Filas | Transportista | |
| Valores | Pedidos | Suma |
| Valores | Días despacho | **Promedio** |
| Valores | Flete | **Promedio** |
| Valores | Flete (otra vez) | Suma |
| Valores | A tiempo | **Promedio**, Porcentaje |

Segunda tabla opcional: Filas = Transportista, Columnas = **Rango despacho**, Valores = Pedidos.

### P9 · Productos descontinuados — hoja `P9 Descontinuados`
Fuente: `vw_ventas`
| Área | Campo | Operación |
|---|---|---|
| Filas | Descontinuado | |
| Valores | Producto | **Recuento distinto** |
| Valores | Ventas netas | Suma |
| Valores | Ventas netas (otra vez) | Suma, % del total general |

### Hoja `Portada` (primera hoja)
Título, fecha de la última actualización, las 9 preguntas con un hipervínculo a su hoja (*Insertar → Vínculo → Lugar de este documento*) y la nota: **Datos → Actualizar todo** recarga desde el DW.

---

## 5. Validación (antes de hacer commit)

Comparar con `sql/dw/02_consultas_analisis.sql` en SSMS:

| Hoja | Debe dar |
|---|---|
| P1 | Total general de ventas netas = **1 265 793.04**; recuento distinto de pedidos = **830** |
| P2 | Beverages ≈ **21 %** de las ventas; Top 1 producto = **Côte de Blaye** |
| P3 | Total = 1 265 793.04; mismos países y Top 10 que la consulta 3/3b |
| P4 | Suma de los pedidos de los 9 vendedores = 830 |
| P5 | Ticket 2013 ≈ **1 369**; 2015 ≈ **1 632**; pedidos totales = 830 |
| P6 | Total de monto descuento ≈ **88 600** |
| P7 | Tarde = **37**; Pendiente = **21** |
| P8 | Federal Shipping: ≈ **7.5 días**, ≈ **96 %** a tiempo; United Package: el más caro y lento. Flete total (sin filtro) = **64 942.69** |
| P9 | Descontinuados (Sí) ≈ **14.6 %** de las ventas |

**Prueba de "conexión viva" para la presentación:** en SSMS cambiar temporalmente un dato (o correr el ETL de nuevo) → en Excel **Datos → Actualizar todo** → la tabla cambia. Demuestra que Excel lee del DW y no de una copia pegada.

---

## 6. Problemas comunes

| Síntoma | Causa / solución |
|---|---|
| No aparece *Del modelo de datos* al insertar la tabla | En el paso 3.6 no se marcó *Agregar al Modelo de datos*. Clic derecho en la consulta → Cargar en… → marcarlo. |
| No existe *Recuento distinto* en la configuración de campo | La tabla dinámica se creó desde un rango y no desde el Modelo de datos. Volver a crearla. |
| Error de certificado / cifrado | Aceptar la conexión sin cifrar (paso 3.4). |
| *Login failed* con `excel_lector` | SQL Server no tiene habilitada la autenticación mixta, o el usuario no se creó. Usar la pestaña Windows. |
| El servidor no responde en `localhost` | Si SQL Server es una instancia con nombre, usar `localhost\NOMBRE_INSTANCIA`. |
| Los meses salen desordenados | Usar el campo **Mes** (`01 Enero`, `02 Febrero`…) o **Año-Mes**, no el nombre solo. |
| Archivo `~$Invacom_DW….xlsx` en `git status` | Es el archivo de bloqueo de Excel abierto; está ignorado en `.gitignore`. Cerrar Excel antes del commit. |

---

## 7. Preguntas probables del jurado

**¿Por qué no conectan Excel directo a las tablas `fact_` y `dim_`?**
Se podría (el Modelo de datos admite relaciones), pero `fact_pedidos` tiene tres fechas contra la misma `dim_tiempo` y Excel solo permite una relación activa. Las vistas resuelven esos joins en SQL Server una sola vez, entregan nombres de negocio y aíslan a Excel del esquema físico: si mañana cambia una tabla, se ajusta la vista y el libro sigue funcionando.

**¿Cómo garantizan que no hay montos duplicados?**
Cada vista tiene exactamente la granularidad de su hecho (2155 y 830 filas; el script lo verifica). El flete solo vive en la vista de pedidos. Los pedidos en la vista de ventas se cuentan con recuento distinto, no con suma.

**¿Por qué el ticket promedio sale de otra vista que las ventas?**
Porque el ticket es por pedido. Promediar las líneas daría el valor promedio de un producto dentro de un pedido, no de la compra completa.

**¿Cómo se calcula el % de entregas a tiempo y qué pasa con los pendientes?**
`A tiempo` vale 1 o 0 por pedido enviado y NULL si está pendiente. El promedio ignora los NULL, por lo que el % se calcula solo sobre pedidos enviados (809), como define el requisito.

**¿Con qué usuario se conecta Excel?**
Con Windows o con `excel_lector`, que pertenece a `rol_lector_excel`: solo `SELECT` sobre el esquema `rpt`. No puede leer `dbo` ni modificar nada.

**¿Si llegan datos nuevos, hay que rehacer las tablas?**
No. Se corre el ETL y en Excel **Actualizar todo** (o se abre el archivo, que actualiza solo).

**¿Por qué los rangos tienen "1.", "2." adelante?**
Excel ordena el texto alfabéticamente ("15-28 días" antes que "8-14 días"). El prefijo se agrega solo en la vista de presentación; el DW conserva la etiqueta original.
