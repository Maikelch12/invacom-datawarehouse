# Fuentes de Datos y Evaluación de Calidad

---

## 1. Identificación de las fuentes de datos 

La fuente es la base operacional **`invacom_fuente`** en PostgreSQL, cargada a partir de 7 archivos CSV entregados por el profesor. Su modelo es relacional y normalizado: `orders` (encabezado del pedido) y `order_details` (líneas del pedido) registran las transacciones, mientras que las otras 5 tablas son catálogos.

### 1.1 Tablas y su uso en el DW

| Tabla | Filas | Llave primaria | Tipo | Uso en el Data Warehouse |
|---|---|---|---|---|
| `order_details` | 2155 | (`order_id`, `product_id`) | Transaccional | **Hechos**: precio, cantidad y descuento de cada línea de venta |
| `orders` | 830 | `order_id` | Transaccional | **Hechos** (fechas, flete) y llaves hacia cliente, empleado y transportista |
| `customers` | 91 | `customer_id` | Catálogo | Dimensión **Cliente** (empresa, ciudad, país) |
| `products` | 77 | `product_id` | Catálogo | Dimensión **Producto** |
| `categories` | 8 | `category_id` | Catálogo | Atributos de la dimensión Producto (categoría) |
| `employees` | 9 | `employee_id` | Catálogo | Dimensión **Empleado** (incluye la jerarquía con `reports_to`) |
| `shippers` | 3 | `shipper_id` | Catálogo | Dimensión **Transportista** |

### 1.2 Relaciones

| Tabla hija | Columna | Tabla padre |
|---|---|---|
| `order_details` | `order_id` | `orders` |
| `order_details` | `product_id` | `products` |
| `orders` | `customer_id` | `customers` |
| `orders` | `employee_id` | `employees` |
| `orders` | `shipper_id` | `shippers` |
| `products` | `category_id` | `categories` |
| `employees` | `reports_to` | `employees` (relación recursiva: jefe directo) |

Las 7 llaves foráneas se crearon **después** de cargar los datos (`sql/fuente/03_llaves_foraneas.sql`) y todas se validaron sin errores: **no existen registros huérfanos**.

### 1.3 Campos que alimentarán el DW

| Origen | Campos | Destino previsto |
|---|---|---|
| `order_details` | `unit_price`, `quantity`, `discount` | Medidas de la tabla de hechos |
| `orders` | `order_date`, `required_date`, `shipped_date` | Dimensión Tiempo y medidas de logística |
| `orders` | `freight` | Medida de logística (a nivel de pedido) |
| `customers` | `company_name`, `contact_title`, `city`, `country` | Dimensión Cliente |
| `products` + `categories` | `product_name`, `quantity_per_unit`, `discontinued`, `category_name` | Dimensión Producto |
| `employees` | `employee_name`, `title`, `city`, `country`, `reports_to` | Dimensión Empleado |
| `shippers` | `company_name` | Dimensión Transportista |

**Campos descartados:** `categories.description` y `customers.contact_name` no responden ninguna pregunta de negocio; se pueden omitir sin afectar los KPI.

---

## 2. Evaluación de la calidad de los datos (tarea 5)

### 2.1 Resumen

| Dimensión de calidad | Resultado |
|---|---|
| Completitud (nulos) | 2 columnas con nulos: `orders.shipped_date` (21) y `employees.reports_to` (1) |
| Unicidad (duplicados) | 0 duplicados en llaves, nombres de clientes y nombres de productos |
| Integridad referencial | 0 registros huérfanos (7 llaves foráneas validadas) |
| Consistencia de formato | Codificación LATIN1, espacios dobles y nombres de país abreviados |
| Validez (reglas de negocio) | 0 fechas incoherentes, 0 valores negativos; descuentos atípicos en 1 pedido |

### 2.2 Hallazgos y estrategia de tratamiento

| # | Hallazgo | Evidencia | Impacto | Estrategia en el ETL |
|---|---|---|---|---|
| H1 | **Codificación LATIN1** en `customers.csv` y `products.csv` | La carga en UTF-8 falla con `invalid byte sequence`; los nombres se ven como `M�nchen` | Nombres ilegibles en los reportes | Leer los archivos con `ENCODING 'LATIN1'`; en PostgreSQL y en el DW quedan en UTF-8 (`München`, `Luleå`) |
| H2 | **21 pedidos sin `shipped_date`** | Todos son de abril y mayo de 2015, los últimos días registrados | No son errores: son pedidos **pendientes de envío** | Conservarlos. Crear un atributo `estado_envio` (`Enviado` / `Pendiente`); excluirlos del KPI de entregas a tiempo y de días de despacho, pero incluirlos en las ventas |
| H3 | **1 empleado sin `reports_to`** | Andrew Fuller, *Vice President Sales* | Es el máximo jerarca; no tiene jefe | Conservar. En la dimensión Empleado, mostrar el jefe como `Sin jefe (Dirección)` |
| H4 | **Espacios dobles** en textos | `Wolski  Zajazd`, `24 - 250 g  jars` | Agrupaciones y búsquedas inconsistentes | Aplicar `trim` y reemplazar espacios múltiples por uno solo en todos los campos de texto |
| H5 | **Países con formato mixto** | `UK` y `USA` abreviados; los otros 19 con nombre completo | Reportes poco uniformes | Estandarizar a nombre completo: `UK` → `United Kingdom`, `USA` → `United States` |
| H6 | **Precio de venta ≠ precio de lista** | 658 líneas con `order_details.unit_price` distinto de `products.unit_price` | No es un error: es el **precio histórico** pactado en cada venta | Calcular las ventas siempre con `order_details.unit_price`; el precio de lista no se usa como medida |
| H7 | **Descuentos fuera de la política** | 8 líneas con descuentos de 1 % a 6 %; todas en el pedido 11077 | Valores válidos (entre 0 y 25 %), pero atípicos | Conservarlos y documentarlos; consultar al Product Owner si fue una excepción comercial |
| H8 | **Períodos incompletos** | Pedidos del 04/07/2013 al 06/05/2015 | Comparar años completos sesga el análisis | La dimensión Tiempo cubrirá todo el rango; los reportes compararán por mes y trimestre, indicando que 2013 y 2015 son parciales |
| H9 | **Clientes sin compras** | `PARIS` y `FISSA` no tienen pedidos | Ninguno en las ventas | Conservarlos en la dimensión Cliente (permiten medir clientes inactivos) |
| H10 | **`discontinued` como 0/1** | Valores numéricos sin significado para el usuario | Poco legible en Excel | Transformar a `Sí` / `No` |
| H11 | **Posible error de digitación** | Cliente `Blondesddsl père et fils` | El nombre parece mal escrito | No se modifica sin confirmación del negocio; se reporta al Product Owner |

### 2.3 Validaciones que **no** encontraron problemas

- Ninguna fecha requerida ni de envío es anterior a la fecha del pedido.
- No hay precios, cantidades ni fletes negativos o en cero. Rangos: precio de 2.00 a 263.50, cantidad de 1 a 130, flete de 0.02 a 1007.64.
- Todos los pedidos tienen al menos una línea de detalle, y todos los productos se vendieron al menos una vez.
- No hay nulos en ciudades, países, categorías ni en las llaves de los pedidos.

### 2.4 Totales de control para validar el ETL

Después de la carga, el Data Warehouse debe coincidir **exactamente** con estos valores de la fuente:

| Control | Valor esperado |
|---|---|
| Pedidos | 830 |
| Líneas de pedido (filas de la tabla de hechos) | 2155 |
| Ventas netas totales `SUM(unit_price × quantity × (1 − discount))` | **1 265 793.04** |
| Pedidos entregados tarde | 37 |
| Pedidos pendientes de envío | 21 |
