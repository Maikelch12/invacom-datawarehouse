# Guía de Defensa del Proyecto

**Proyecto:** Data Warehouse de ventas para Invacom Inc S.A.
**Para:** estudio de todo el equipo antes de la sustentación (role-play con jurado)

> Cómo usar esta guía: lean primero las secciones 1, 5 y 6 (discurso, números y preguntas). Después ensayen el guion de las secciones 2 y 3 en voz alta, cronometrando. **Cada integrante debe poder responder cualquier pregunta**, no solo la de su parte.

---

## Índice

1. El proyecto en 30 segundos
2. Guion de la presentación
3. Guion de la demo en vivo
4. Lo que muestra el Excel: respuestas a las 9 preguntas de negocio
5. Números que hay que saberse de memoria
6. Banco de preguntas y respuestas del jurado
7. Glosario
8. Cómo responder bajo presión
9. Checklist del día de la presentación
10. Preguntas para cuando ustedes sean el jurado

---

## 1. El proyecto en 30 segundos

Memoricen este párrafo. Sirve para abrir la presentación y para responder *"¿de qué trata su proyecto?"*.

> *"Invacom registra sus ventas en un sistema operacional que sirve para capturar pedidos, pero no para analizarlos. Construimos un Data Warehouse en SQL Server con un modelo estrella, alimentado por un proceso ETL en Apache Spark que extrae los datos de PostgreSQL, los limpia y los carga. La gerencia consulta 9 indicadores de negocio desde tablas dinámicas en Excel. Validamos que el DW coincide al centavo con la fuente: 2155 líneas de venta, 830 pedidos y 1 265 793.04 en ventas netas."*

**Las 4 piezas de la solución:**

1. **PostgreSQL:** la fuente (base operacional).
2. **Apache Spark (PySpark):** extrae, transforma y carga.
3. **SQL Server:** el Data Warehouse con el modelo estrella.
4. **Excel:** las tablas dinámicas con los 9 indicadores.

---

## 2. Guion de la presentación

Pregúntenle al profesor cuánto tiempo tienen. Este guion está pensado para unos 20 minutos más las preguntas. El reparto sugerido sigue lo que cada uno programó según el historial de Git, para que hable quien mejor lo conoce:

| Integrante | Lo que construyó |
|---|---|
| Maikel | Infraestructura (PostgreSQL y SQL Server), requisitos, calidad de datos, modelo dimensional, diseño del ETL, `config.py`, `main.py`, dimensiones cliente y producto |
| Xavier | Prueba de conexión, `dim_tiempo`, `dim_transportista` |
| Álvaro | `dim_empleado`, `dim_descuento`, `dim_estado_envio`, `validacion.py`, hechos, consultas de análisis, vistas y Excel |
| Nayely | Informe APA 7, documentación del código, revisión de dimensiones y de `fact_pedidos` |

**Recuerden el formato:** el jurado actúa como la **junta directiva y los usuarios clave de Invacom**. Ustedes son una empresa consultora que les **vende** la solución. Hablen de lo que gana el negocio, no solo de la tecnología.

### Sección 1 · El problema (1 min) — Maikel
**Diapositiva:** el nombre del proyecto y una frase grande con el problema.

> *"Buenos días, miembros de la junta. Hoy Invacom registra cada pedido en su sistema, pero cuando la gerencia pregunta '¿qué vendedor vende más?' o '¿estamos entregando a tiempo?', responderlo exige consultas complejas sobre 7 tablas y depende del personal técnico. Les traemos una solución para que esas respuestas estén a un clic."*

### Sección 2 · Lo que necesita el negocio (2 min) — Nayely
**Diapositiva:** los 4 usuarios y las 9 preguntas (`docs/01`).

- **4 usuarios:** Junta Directiva, Gerente de Ventas, Jefe de Logística y Gerente de Compras.
- **9 preguntas:** ventas en el tiempo, categorías y productos, países y clientes, vendedores, ticket promedio, descuentos, entregas a tiempo, transportistas y productos descontinuados.
- **Lo que no se puede responder:** ganancia (no hay costos), inventario y satisfacción. *"Conocer los límites de los datos también es parte del análisis."*

### Sección 3 · La solución (2 min) — Maikel
**Diapositiva:** `docs/img/diagrama_flujo_etl.png`.

> *"Los datos salen de PostgreSQL, que es la base operacional. Apache Spark los extrae, los limpia y los transforma en memoria. Luego los carga en un Data Warehouse en SQL Server, organizado para análisis. Finalmente, Excel se conecta al DW para mostrar los indicadores. Usamos dos motores de base de datos distintos, como pasa en las empresas reales."*

### Sección 4 · Calidad de datos (2 min) — Maikel o Nayely
**Diapositiva:** una tabla con 3 o 4 hallazgos (`docs/02`).

> *"Antes de cargar nada, analizamos la calidad de los datos y encontramos 11 hallazgos. Les cuento los más importantes:"*
1. **Codificación:** dos archivos venían en LATIN1. Los nombres con tildes se veían rotos (`M�nchen`) y lo corregimos en la carga.
2. **21 pedidos sin fecha de envío:** no son errores. Todos son de las últimas semanas registradas, así que están **pendientes**. Los conservamos.
3. **El precio de venta no coincide con el de catálogo en 658 líneas:** tampoco es error. Es el **precio histórico** pactado en cada venta, y las ventas se calculan con ese.
4. **Formatos:** países abreviados (UK, USA) y espacios dobles, que estandarizamos.

> *"No había duplicados ni registros huérfanos."*

### Sección 5 · El modelo dimensional (3 min) — Maikel
**Diapositiva:** `docs/img/diagrama_modelo_estrella.png`.

> *"Diseñamos un esquema estrella con 7 dimensiones y 2 tablas de hechos. Las dimensiones son las perspectivas desde las que se analiza: tiempo, cliente, producto, empleado, transportista, descuento y estado de envío."*

Lo que hay que explicar sí o sí:
- **`fact_ventas`:** una fila por **línea de pedido** (2155). Es el nivel más detallado, y desde ahí se puede sumar a cualquier nivel.
- **`fact_pedidos`:** una fila por **pedido** (830).
- **¿Por qué dos?** *"El flete pertenece al pedido completo. Si estuviera en la tabla de ventas, un pedido con 5 productos repetiría su flete 5 veces y la suma saldría inflada."*

### Sección 6 · Demo en vivo (5-6 min) — Álvaro y Xavier
Ver la sección 3 de esta guía.

### Sección 7 · Cómo trabajamos (1-2 min) — Xavier
**Diapositiva:** captura del Kanban y de GitHub (`Insights → Contributors`).

> *"Trabajamos con Scrum en sprints de una semana. Usamos un tablero Kanban en GitHub Projects y cada tarea se desarrolló en su propia rama. Ningún cambio entró a la rama principal sin un Pull Request revisado por otro compañero. Los 4 integrantes tienen commits en el repositorio."*

### Sección 8 · Cierre (1 min) — Maikel
> *"Con esta solución, Invacom pasa de tener datos guardados a tener información para decidir. Los números están validados al centavo y el proceso se puede repetir cada vez que haya datos nuevos. Como siguientes pasos proponemos la carga incremental, guardar el historial de cambios de clientes y productos, y programar el ETL para que corra solo. Quedamos atentos a sus preguntas."*

---

## 3. Guion de la demo en vivo

### Preparación (antes de entrar al aula)
- [ ] Laptop cargada, con el cargador a mano.
- [ ] Servicios de PostgreSQL y SQL Server encendidos: `Get-Service *postgresql*, MSSQLSERVER` debe decir **Running**.
- [ ] El ETL ya ejecutado una vez ese día, con **13 OK**.
- [ ] VS Code abierto en la carpeta del proyecto, con el `.venv` activado y la letra grande (**Ctrl + +**).
- [ ] SSMS abierto y conectado a `InvacomDW`, con las consultas de verificación listas.
- [ ] Excel abierto y **ya actualizado**.
- [ ] Notificaciones apagadas y otras aplicaciones cerradas.
- [ ] **Plan B:** video de la demo grabado y capturas en las diapositivas.

### Paso a paso

| # | Acción | Qué decir |
|---|---|---|
| 1 | En VS Code: `python etl\main.py` | *"Vamos a ejecutar el proceso completo desde cero. Primero extrae las 7 tablas de PostgreSQL…"* |
| 2 | Mientras corre (unos 90 s) | Narrar las etapas que aparecen: *"…ahora vacía el DW, carga las 7 dimensiones y después los hechos, que necesitan las llaves de las dimensiones."* |
| 3 | Al final, la tabla de validación | *"Estos son 13 controles que comparan la fuente con el DW. Los 13 dan OK: las mismas 2155 líneas, los mismos 830 pedidos y las ventas netas coinciden al centavo, 1 265 793.04."* |
| 4 | En SSMS: `SELECT TOP 10 * FROM dbo.fact_ventas` | *"Así se ve la tabla de hechos: llaves hacia cada dimensión y las medidas de cada venta."* |
| 5 | En Excel: **Datos → Actualizar todo** | *"Excel lee del DW. Cada vez que corre el ETL, basta con actualizar."* |
| 6 | Hoja **P4 Vendedores** | *"¿Qué vendedor vende más? Margaret Peacock, con 232 890.85."* |
| 7 | Hoja **P7 Entregas** | *"El 95.4 % de los pedidos enviados llega a tiempo, y Federal Shipping es el transportista más puntual."* |
| 8 | **Pídanle al jurado que elija** | *"¿Qué les gustaría consultar?"* y respondan filtrando en vivo |

**Si algo falla:** mantengan la calma y digan *"Les mostramos la ejecución que grabamos esta mañana"*. Pongan el video o las capturas y sigan.

**Si el ETL no termina el proceso en la terminal** (pasa en Windows): los resultados ya están cargados. Sigan con SSMS y Excel.

---

## 4. Lo que muestra el Excel: respuestas a las 9 preguntas de negocio

Calculadas con los datos de la fuente. **Comprueben que su Excel muestre estos mismos números.** En el DW, los países aparecen estandarizados (`United States` en vez de `USA`).

| # | Pregunta | Respuesta |
|---|---|---|
| **P1** | ¿Cómo evolucionan las ventas? | 2013: **208 083.97** (desde julio) · 2014: **617 085.20** · 2015: **440 623.87** (hasta el 6 de mayo). Mejor mes: **abril de 2015** (123 798.68) |
| **P2** | ¿Qué categorías y productos venden más? | Categorías: **Beverages** (267 868.18), Dairy Products (234 507.28), Confections (167 357.22). La más baja es Grains & Cereals (95 744.59). Producto top: **Côte de Blaye** (141 396.73). Más unidades: Camembert Pierrot (1577) |
| **P3** | ¿Qué países y clientes son los más importantes? | Países: **United States** (245 584.61), Germany (230 284.63), Austria (128 003.84). Clientes: **QUICK-Stop** (110 277.30), Ernst Handel (104 874.98), Save-a-lot Markets (104 361.95) |
| **P4** | ¿Qué vendedores tienen mejor desempeño? | **Margaret Peacock** (232 890.85, 156 pedidos), Janet Leverling (202 812.84), Nancy Davolio (192 107.60). El último es Steven Buchanan (68 792.28), que es gerente |
| **P5** | ¿Cuál es el ticket promedio? | **1 525.05** por pedido. Sube cada año: 1 368.97 (2013) → 1 512.46 (2014) → 1 631.94 (2015) |
| **P6** | ¿Cuánto se deja de percibir por descuentos? | **88 665.55** (6.5 % de las ventas brutas, que son 1 354 458.59). El 38.9 % de las líneas tiene descuento |
| **P7** | ¿Estamos entregando a tiempo? | **95.43 %** de los 809 pedidos enviados llegó a tiempo. 37 llegaron tarde y 21 están pendientes |
| **P8** | ¿Qué transportista es más rápido y cuál cuesta más? | Más puntual y más rápido: **Federal Shipping** (96.4 % a tiempo, 7.5 días promedio). Más caro por pedido: **United Package** (86.64 de flete promedio). Más barato: Speedy Express (65.00) |
| **P9** | ¿Cuánto depende de productos descontinuados? | **184 990.93**, el **14.6 %** de las ventas netas |

**Ideas para la junta** (lenguaje de negocio):
- *"Beverages y Dairy Products concentran casi el 40 % de las ventas."*
- *"Casi el 15 % de las ventas viene de productos descontinuados: es un riesgo si no se reemplazan."*
- *"United Package es el transportista que más usamos y el más caro por pedido. Además, es el menos puntual."*

---

## 5. Números que hay que saberse de memoria

| Dato | Valor |
|---|---|
| Tablas fuente | 7 |
| Pedidos (`orders`) | **830** |
| Líneas de pedido (`order_details`) | **2155** |
| Clientes / productos / empleados / transportistas / categorías | 91 / 77 / 9 / 3 / 8 |
| Clientes que nunca compraron | 2 (PARIS y FISSA) |
| **Ventas netas totales** | **1 265 793.04** |
| Ventas brutas | 1 354 458.59 |
| Descuentos | 88 665.55 |
| Flete total | 64 942.69 |
| Pedidos pendientes (sin fecha de envío) | **21** |
| Pedidos entregados tarde | **37** |
| Pedidos enviados | 809 |
| % a tiempo | 95.43 % |
| Rango de fechas | 4 de julio de 2013 al 6 de mayo de 2015 |
| Días en `dim_tiempo` | 1095 (de 2013-01-01 a 2015-12-31) |
| Dimensiones / tablas de hechos | 7 / 2 |
| Filas de `dim_descuento` / `dim_estado_envio` | 11 / 9 |
| Hallazgos de calidad | 11 (H1 a H11) |
| Controles de validación | **13 de 13 OK** |
| Líneas con precio distinto al de catálogo | 658 |
| Tiempo de ejecución del ETL | unos 90 segundos |

---

## 6. Banco de preguntas y respuestas del jurado

### 6.1 Negocio y requisitos

**¿Qué problema resuelve el proyecto?**
El sistema operacional de Invacom está hecho para registrar pedidos, no para analizarlos. El DW reorganiza los datos para que la gerencia responda sus preguntas sola, rápido y con números confiables.

**¿Quiénes son los usuarios y qué gana cada uno?**
La Junta Directiva ve la evolución de las ventas por país y categoría. El Gerente de Ventas evalúa a los vendedores y controla los descuentos. El Jefe de Logística mide la puntualidad y el costo de los transportistas. El Gerente de Compras decide qué productos impulsar o retirar.

**¿Qué es un KPI y cuáles definieron?**
Un indicador clave de desempeño: un número medible que dice si el negocio va bien respecto a una meta. Definimos 9; por ejemplo, ventas netas, ticket promedio, % de entregas a tiempo y monto perdido por descuentos.

**¿Por qué no pueden mostrar la ganancia?**
La fuente no tiene costos de compra, solo precios de venta. Sin costos no hay margen. Lo documentamos como un límite de los datos.

**¿Por qué no comparan 2013 contra 2015?**
Porque ninguno es un año completo: 2013 empieza en julio y 2015 termina en mayo. Compararlos sesgaría el análisis. Lo correcto es comparar por mes o por trimestre.

**¿Cuál es el hallazgo de negocio más importante?**
Escojan uno y defiéndanlo. Por ejemplo: *"El 14.6 % de las ventas depende de productos descontinuados. Si no se reemplazan, Invacom perdería esos ingresos."* Otra opción: *"United Package lleva la mayor parte de los envíos, pero es el más caro y el menos puntual."*

### 6.2 Fuentes y calidad de datos

**¿De dónde vienen los datos?**
De 7 archivos CSV que cargamos en PostgreSQL. Esa base simula el sistema operacional de Invacom.

**¿Qué problemas de calidad encontraron?**
11 hallazgos. Los principales: codificación LATIN1, 21 pedidos sin fecha de envío, un empleado sin jefe, espacios dobles, países abreviados, precios históricos distintos al de catálogo y descuentos atípicos en un pedido.

**¿Cómo trataron los nulos?**
Depende de lo que significan. Los 21 `shipped_date` nulos son pedidos pendientes: se conservan en las ventas y se excluyen del % de entregas. El `reports_to` nulo es del vicepresidente, que no tiene jefe: se muestra como *"Sin jefe (Dirección)"*. **No borramos ni inventamos datos.**

**¿Por qué no eliminaron los pedidos sin fecha de envío?**
Porque son ventas reales. Eliminarlos haría que las ventas no cuadren con la fuente. Solo no tienen sentido para medir entregas, y por eso ahí quedan fuera.

**¿Por qué el precio de la venta es distinto al del producto?**
`order_details.unit_price` es el precio que se cobró en cada venta, es decir, el histórico. `products.unit_price` es el precio actual de catálogo. Las ventas siempre se calculan con el histórico. Pasa en 658 líneas.

**¿Corrigieron el cliente "Blondesddsl père et fils"?**
No. Parece un error de digitación, pero un DW no debe cambiar datos sin la confirmación del negocio. Lo reportamos al Product Owner.

**¿Qué pasó con los descuentos raros?**
El pedido 11077 tiene descuentos de 1 % a 6 %, cuando la política es de 5 % en 5 %. Están dentro del rango válido (0 a 25 %), así que se conservaron, quedaron en los rangos Bajo y Medio, y se consultaron con el Product Owner.

**¿Había duplicados o registros huérfanos?**
No. Lo comprobamos con consultas SQL y al crear las 7 llaves foráneas, que PostgreSQL valida contra los datos existentes.

### 6.3 Modelo dimensional

**¿Qué es un Data Warehouse y en qué se diferencia de la base fuente?**
La base fuente (OLTP) está normalizada y optimizada para registrar transacciones una por una. El DW (OLAP) está organizado para leer y resumir grandes cantidades de datos: menos tablas que unir, nombres de negocio y datos limpios e integrados.

**¿Por qué estrella y no copo de nieve?**
En la estrella, las dimensiones están desnormalizadas: la categoría vive dentro de `dim_producto`. Hay menos uniones, las consultas son más simples y Excel lo navega mejor. Con solo 8 categorías, la redundancia no cuesta nada.

**¿Qué es la granularidad y cuál eligieron?**
Es el nivel de detalle de cada fila. En `fact_ventas`, una fila es una línea de pedido (un producto dentro de un pedido). Es el nivel más fino que existe, y desde ahí se puede sumar a cualquier nivel superior.

**¿Por qué dos tablas de hechos?**
Porque hay dos granularidades. El flete, las fechas de envío y el cumplimiento son del pedido completo, no de cada producto. Si estuvieran en `fact_ventas`, un pedido con 5 productos repetiría su flete 5 veces y al sumar saldría inflado.

**¿Qué es una tabla de hechos y qué es una dimensión?**
Los hechos guardan las **medidas** numéricas de cada evento de negocio (cantidad, monto). Las dimensiones guardan el **contexto** para analizarlas: quién, qué, cuándo y dónde.

**¿Qué medidas tienen?**
En `fact_ventas`: cantidad, precio unitario, % de descuento, monto bruto, monto de descuento y monto neto. En `fact_pedidos`: flete, cantidad de líneas, monto neto del pedido, días de despacho y entregado a tiempo.

**¿Qué es una medida aditiva?**
Una que se puede sumar en cualquier dimensión, como el monto neto o la cantidad. El precio unitario y el % de descuento **no** son aditivos: se promedian, no se suman.

**¿Qué es una llave sustituta y para qué sirve?**
Es un entero propio del DW (`cliente_key`) que reemplaza al código de la fuente (`customer_id = 'ALFKI'`). Independiza al DW de los códigos del sistema origen, hace las uniones más rápidas y permitiría guardar el historial de cambios en el futuro (SCD tipo 2).

**¿Por qué la llave de `dim_tiempo` es AAAAMMDD y no un IDENTITY?**
Es legible (20140315 es el 15 de marzo de 2014), se ordena bien, y los hechos la calculan directo desde la fecha sin tener que buscarla.

**¿Por qué `dim_tiempo` tiene días sin ventas?**
Porque es un calendario completo. Así se pueden ver los días sin ventas y el DW acepta fechas futuras. Además, las fechas requeridas llegan hasta junio de 2015.

**¿Qué es una dimensión degenerada?**
`pedido_id`: identifica el pedido pero no tiene atributos propios, así que vive en la tabla de hechos sin tabla aparte. Sirve para contar o agrupar pedidos.

**¿Qué es una dimensión de rol?**
Una dimensión que se usa varias veces con distintos significados. `dim_tiempo` aparece 3 veces en `fact_pedidos`: fecha de pedido, fecha requerida y fecha de envío.

**¿Qué es `dim_descuento`?**
Una **dimensión de bandas**: convierte el porcentaje, que es un número, en rangos que el negocio entiende (Sin descuento, Bajo, Medio, Alto). Tiene 11 filas, una por cada porcentaje que existe.

**¿Qué es `dim_estado_envio`?**
Una ***junk dimension*** (dimensión basura): junta en una tabla pequeña de 9 filas tres indicadores de pocos valores (estado, cumplimiento y rango de días). Generamos todas las combinaciones, aunque 2 no tengan pedidos hoy, para que el DW acepte datos futuros.

**¿Por qué la categoría no es una dimensión aparte?**
Sería un copo de nieve. En la estrella, la categoría es un atributo de `dim_producto`, y así se evita una unión más.

### 6.4 ETL y Apache Spark

**¿Qué es ETL?**
Extract, Transform, Load: extraer datos de la fuente, transformarlos (limpiar, unir, calcular) y cargarlos en el DW.

**¿Por qué ETL y no ELT?**
La transformación ocurre en Spark, antes de llegar a SQL Server. El DW solo recibe datos limpios, y toda la lógica de negocio queda en código Python versionado en Git.

**¿Por qué Apache Spark con tan pocos datos?**
Fue la herramienta que elegimos de la lista del enunciado. Su ventaja es que el mismo código escala: si Invacom pasara a millones de filas, solo cambia una línea (`master("local[*]")` por un clúster). Para este volumen procesa todo en memoria en segundos.

**¿Qué es un DataFrame?**
Una tabla en memoria dentro de Spark, con columnas y tipos, sobre la que se aplican las transformaciones.

**¿Cómo se conecta Spark a las bases?**
Por JDBC, con los drivers oficiales de PostgreSQL y SQL Server. Spark los descarga solo la primera vez.

**¿En qué orden se carga?**
Primero las 7 dimensiones y después los 2 hechos, porque los hechos necesitan las llaves sustitutas de las dimensiones. Al vaciar es al revés: primero los hechos.

**¿Cómo obtiene `fact_ventas` las llaves de las dimensiones?**
Después de cargar las dimensiones, Spark las vuelve a leer desde SQL Server, que es quien generó las llaves, y une los hechos por la llave de negocio (por ejemplo, `cliente_id`) para traer la sustituta (`cliente_key`).

**¿Qué pasa si una venta no encuentra su cliente en la dimensión?**
La función `buscar_llave` detiene el ETL y muestra cuáles faltan. Con un INNER JOIN esas filas se perderían sin avisar.

**¿Carga completa o incremental? ¿Por qué?**
Completa: en cada ejecución se vacía el DW y se recarga todo. Son unas 3000 filas de una fuente que no cambia, así que es lo más simple y garantiza que el DW quede idéntico a la fuente. En producción usaríamos carga incremental.

**¿Qué pasa si ejecuto el ETL dos veces?**
Nada malo. Se vacía y se recarga, y los contadores de las llaves se reinician. El resultado es siempre el mismo: es un proceso **idempotente**.

**¿Por qué `append` y no `overwrite` al escribir?**
`overwrite` borra y recrea la tabla, y se pierden las llaves primarias, las foráneas y los tipos de dato del script SQL. Con `append` se respetan las tablas que diseñamos.

**¿Por qué `DELETE` y no `TRUNCATE`?**
SQL Server no permite `TRUNCATE` en tablas referenciadas por llaves foráneas. Por eso usamos `DELETE` y reiniciamos los contadores con `DBCC CHECKIDENT`.

**¿Cómo está organizado el código?**
Un archivo por tabla, cada uno con una función `transformar()`. `config.py` tiene las conexiones y las utilidades compartidas, y `main.py` orquesta el orden. Así cada integrante desarrolló y probó su parte por separado.

**¿Cómo prueban una sola tabla sin tocar el DW?**
Con `python etl\main.py --probar dim_cliente`: transforma y muestra el resultado sin escribir en SQL Server.

**¿Qué problemas técnicos tuvieron?**
La codificación LATIN1, la descarga interrumpida de PySpark (450 MB), `winutils.exe` y `HADOOP_HOME` en Windows, Java interpretando mal las rutas con `\`, y los avisos de archivos temporales al cerrar Spark. Todos están documentados.

### 6.5 Validación y exactitud

**¿Cómo saben que los números son correctos?**
`validacion.py` compara 13 controles entre la fuente y el DW: los conteos de todas las tablas, las ventas netas, el flete total, los pedidos pendientes y los entregados tarde. La última carga dio **13 de 13 OK**.

**¿Por qué usaron DECIMAL y no float?**
El float guarda aproximaciones binarias: 0.1 + 0.2 no da exactamente 0.3. En miles de sumas aparecen centavos de diferencia. Con DECIMAL el total coincide al centavo: 1 265 793.04.

**¿Por qué los montos tienen 4 decimales?**
`monto_bruto × descuento` produce hasta 4 decimales. Si se redondeara cada línea a 2, la suma de las 2155 líneas no coincidiría con la fuente.

**¿Cómo se calcula el % de entregas a tiempo?**
`entregado_a_tiempo` vale 1 si `shipped_date ≤ required_date`, 0 si llegó tarde y NULL si está pendiente. El promedio ignora los NULL, así que el % se calcula solo sobre los 809 pedidos enviados: 95.43 %.

**¿Por qué pusieron NULL y no 0 a los pendientes?**
Un 0 los contaría como entregados tarde y bajaría el % de puntualidad injustamente. NULL significa "todavía no aplica".

### 6.6 Excel

**¿Cómo se conecta Excel al DW?**
Con Power Query, a SQL Server. Los datos se cargan al Modelo de datos de Excel y las tablas dinámicas leen de ahí.

**¿Por qué Excel lee vistas y no las tablas directamente?**
Las vistas del esquema `rpt` ya resuelven las uniones con las dimensiones y usan nombres de negocio ("Ventas netas", "Categoría"). Además, `fact_pedidos` usa `dim_tiempo` 3 veces y Excel solo permite una relación activa entre dos tablas. Si mañana cambia una tabla, se ajusta la vista y el Excel sigue funcionando.

**¿Cómo evitan montos duplicados en Excel?**
Cada vista respeta la granularidad de su hecho: `vw_ventas` tiene 2155 filas y `vw_pedidos` 830. El flete solo vive en la de pedidos. Los pedidos en la vista de ventas se cuentan con recuento distinto, no sumando.

**¿Por qué el ticket promedio sale de la vista de pedidos?**
Porque el ticket es por pedido. Promediar las líneas daría el valor promedio de un producto, no el de una compra completa.

**¿Qué pasa cuando llegan datos nuevos?**
Se ejecuta el ETL y en Excel se presiona **Actualizar todo**. No hay que rehacer las tablas dinámicas.

**¿Por qué los rangos tienen "1.", "2." al inicio?**
Excel ordena el texto alfabéticamente, y "15-28 días" quedaría antes que "8-14 días". El número fuerza el orden lógico.

### 6.7 Seguridad

**¿Dónde están las contraseñas?**
En un archivo `.env` que **no se sube a GitHub** (está en `.gitignore`). En el repo solo hay una plantilla sin contraseñas.

**¿Con qué usuario se conecta el ETL?**
Con `etl_spark`, que solo tiene permisos sobre la base `InvacomDW`. No usamos `sa`, el administrador de todo el servidor. Es el **principio de mínimo privilegio**.

**¿Y Excel?**
Con un usuario de solo lectura (`excel_lector`), que únicamente puede consultar las vistas del esquema `rpt`. No puede modificar nada.

### 6.8 Metodología y trabajo en equipo

**¿Cómo aplicaron Scrum?**
Sprints de una semana, un Scrum Master, un tablero Kanban con Product Backlog y Sprint Backlog en GitHub Projects, dailies por chat y revisión semanal con los commits.

**¿Cómo usaron Git?**
Un repositorio en GitHub, una rama por tarea y Pull Requests revisados por otro integrante antes de unirlos a `main`. Los 4 integrantes tienen commits.

**¿Qué hizo cada uno?**
Cada integrante debe poder explicar con detalle **su** parte (ver la tabla de la sección 2) y de forma general las demás.

**¿Qué fue lo más difícil?**
Respondan con honestidad. Por ejemplo: configurar Spark en Windows, o decidir la granularidad y descubrir que hacían falta dos tablas de hechos.

### 6.9 Limitaciones y mejoras

**¿Qué limitaciones tiene la solución?**
Es una carga completa, no incremental. No guarda el historial de cambios de los clientes. Se ejecuta a mano. Y los datos no permiten calcular ganancias.

**¿Qué mejorarían?**
1. **Carga incremental:** solo los pedidos nuevos o modificados.
2. **SCD tipo 2:** guardar el historial cuando un cliente cambia de país, o un producto de precio.
3. **Orquestación:** programar el ETL (por ejemplo con Airflow) y avisar si la validación falla.
4. **Power BI:** tableros interactivos además de Excel.

**¿Qué es SCD?**
*Slowly Changing Dimension*, o dimensión de cambio lento. Es la técnica para manejar los cambios en los atributos de una dimensión. El tipo 1 sobrescribe el valor; el tipo 2 crea una fila nueva y conserva la historia.

### 6.10 Preguntas trampa

**"Si sumo el flete en la tabla de ventas, ¿sale inflado?"**
El flete no está en `fact_ventas`: está en `fact_pedidos`, una fila por pedido. Precisamente por eso hay dos tablas de hechos.

**"Su DW tiene los mismos datos que la fuente. ¿Para qué sirve?"**
Los datos son los mismos, pero están limpios, integrados, con nombres de negocio y organizados para analizar. La pregunta "ventas por categoría y trimestre" en la fuente une 4 tablas; en el DW es un filtro en Excel.

**"¿Por qué no usaron simplemente Excel con los CSV?"**
No se valida la calidad, no se repite automáticamente, no escala y no hay una sola versión de la verdad compartida. El DW es la fuente oficial y validada.

**"¿Y si la fuente tiene un error?"**
Se reporta al negocio y no se corrige a ciegas, como hicimos con "Blondesddsl". El DW refleja la fuente y la validación garantiza que no la alteramos.

**"Si eliminan un cliente de la fuente, ¿qué pasa en el DW?"**
Con la carga completa desaparecería en la siguiente ejecución. Por eso en producción se usaría carga incremental con SCD, que conserva el historial.

---

## 7. Glosario

| Término | Definición corta |
|---|---|
| **Data Warehouse (DW)** | Base de datos organizada para el análisis, que integra datos limpios de una o varias fuentes |
| **OLTP / OLAP** | Sistemas para registrar transacciones / sistemas para analizar datos |
| **ETL** | Extraer, transformar y cargar |
| **Modelo estrella** | Una tabla de hechos al centro, rodeada de dimensiones desnormalizadas |
| **Copo de nieve** | Una estrella cuyas dimensiones están normalizadas en varias tablas |
| **Tabla de hechos** | Guarda las medidas numéricas de los eventos de negocio |
| **Dimensión** | Guarda el contexto descriptivo: quién, qué, cuándo, dónde |
| **Granularidad** | Nivel de detalle de una fila de la tabla de hechos |
| **Medida aditiva** | Se puede sumar por cualquier dimensión (monto, cantidad) |
| **Llave sustituta** | Llave numérica propia del DW, independiente de la fuente |
| **Llave de negocio** | El código original de la fuente (`customer_id`) |
| **Dimensión degenerada** | Atributo en los hechos sin tabla propia (`pedido_id`) |
| **Dimensión de rol** | Una dimensión usada varias veces con distinto significado (las fechas) |
| **Junk dimension** | Agrupa indicadores de pocos valores en una tabla pequeña |
| **Dimensión de bandas** | Convierte un valor continuo en rangos |
| **SCD** | Dimensión de cambio lento: manejo del historial de atributos |
| **Desnormalizar** | Juntar en una tabla datos que antes estaban separados |
| **JDBC** | Estándar de Java para conectarse a bases de datos |
| **DataFrame** | Tabla en memoria dentro de Spark |
| **Idempotente** | Ejecutarlo varias veces da siempre el mismo resultado |
| **KPI** | Indicador clave de desempeño |
| **Mínimo privilegio** | Dar a cada usuario solo los permisos que necesita |

---

## 8. Cómo responder bajo presión

1. **Escuchen la pregunta completa.** Si no la entienden, pidan que la repitan: *"¿Se refiere a…?"*.
2. **Respondan primero en una frase** y después den el detalle.
3. **Si no saben:** *"Es una buena pregunta. No lo evaluamos en este alcance, pero lo abordaríamos así…"*. Nunca inventen.
4. **Pasen la pregunta a quien la domina:** *"Esa parte la desarrolló Álvaro, él les explica."* Está bien, pero cada uno debe poder responder lo básico de todo.
5. **Usen la evidencia:** muestren el diagrama, la validación o el Excel. Un número vale más que una explicación.
6. **Hablen al nivel del jurado:** si hace de junta directiva, lenguaje de negocio; si hace de usuario técnico, detalle técnico.
7. **No se contradigan entre ustedes.** Si un compañero dijo algo incompleto, complementen: *"Agrego a lo que dijo mi compañero…"*.

---

## 9. Checklist del día de la presentación

**El día anterior**
- [ ] Ensayo completo cronometrado con los 4 integrantes.
- [ ] Simulacro de preguntas: uno hace de jurado difícil.
- [ ] Video de la demo grabado y capturas en las diapositivas.
- [ ] El repo con todo subido a `main`, y el README completo.
- [ ] El informe APA en su versión final.

**Antes de entrar**
- [ ] Laptop cargada y cargador a mano.
- [ ] Servicios encendidos y el ETL ejecutado con 13 OK.
- [ ] VS Code, SSMS y Excel abiertos y actualizados.
- [ ] Diapositivas listas y el video a mano.
- [ ] Probar el proyector y la resolución de pantalla, si es posible.

**Durante**
- [ ] Hablan los 4.
- [ ] Respetar el tiempo de cada sección.
- [ ] Mirar al jurado, no a la pantalla.

---

## 10. Preguntas para cuando ustedes sean el jurado

Ustedes también van a evaluar a otro grupo. Lleven estas preguntas preparadas:

**De negocio**
1. ¿Qué decisión concreta puede tomar la gerencia con su solución que hoy no puede tomar?
2. ¿Cuál fue el hallazgo de negocio más importante que encontraron en los datos?
3. ¿Qué preguntas del negocio no pudieron responder, y por qué?

**Técnicas**
4. ¿Cómo garantizan que los totales del DW son iguales a los de la fuente?
5. ¿Cuál es la granularidad de su tabla de hechos y por qué la eligieron?
6. ¿Cómo trataron los pedidos sin fecha de envío?
7. ¿Qué pasa si ejecutan su ETL dos veces seguidas?
8. ¿Dónde guardan las contraseñas de las bases de datos?
9. ¿Cómo evitan que el flete se sume repetido?
10. ¿Por qué eligieron esa herramienta de ETL frente a las demás?
