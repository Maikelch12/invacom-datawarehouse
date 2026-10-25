# Modelo Dimensional del Data Warehouse


---

## 1. Tipo de esquema

Se eligió un **esquema estrella** :

- Las dimensiones están **desnormalizadas**: la categoría vive dentro de `dim_producto` y el nombre del jefe dentro de `dim_empleado`. Así se evita unir tablas adicionales.
- Las consultas y las tablas dinámicas de Excel son más simples y rápidas: cada hecho se une directamente con cada dimensión.
- El volumen es pequeño (77 productos, 8 categorías), por lo que la redundancia de repetir la categoría no tiene costo relevante.

El modelo tiene **7 dimensiones** y **dos tablas de hechos que comparten las dimensiones comunes** (dimensiones conformadas). Cada tabla de hechos con sus dimensiones forma una estrella. Se usan dos porque hay **dos granularidades distintas** en el negocio (ver sección 3).

---

## 2. Diagrama

![Modelo dimensional del Data Warehouse](img/diagrama_modelo_estrella.png)

Versión en texto (Mermaid), útil para editarla en GitHub:

```mermaid
erDiagram
    dim_tiempo ||--o{ fact_ventas : "fecha_pedido"
    dim_cliente ||--o{ fact_ventas : ""
    dim_producto ||--o{ fact_ventas : ""
    dim_empleado ||--o{ fact_ventas : ""
    dim_transportista ||--o{ fact_ventas : ""
    dim_descuento ||--o{ fact_ventas : ""

    dim_tiempo ||--o{ fact_pedidos : "fecha_pedido / requerida / envio"
    dim_cliente ||--o{ fact_pedidos : ""
    dim_empleado ||--o{ fact_pedidos : ""
    dim_transportista ||--o{ fact_pedidos : ""
    dim_estado_envio ||--o{ fact_pedidos : ""

    fact_ventas {
        int venta_key PK
        int pedido_id "dimension degenerada"
        int fecha_pedido_key FK
        int cliente_key FK
        int producto_key FK
        int empleado_key FK
        int transportista_key FK
        int descuento_key FK
        int cantidad
        decimal precio_unitario
        decimal descuento_pct
        decimal monto_bruto
        decimal monto_descuento
        decimal monto_neto
    }

    fact_pedidos {
        int pedido_id PK "dimension degenerada"
        int fecha_pedido_key FK
        int fecha_requerida_key FK
        int fecha_envio_key FK "NULL si pendiente"
        int cliente_key FK
        int empleado_key FK
        int transportista_key FK
        int estado_envio_key FK
        decimal flete
        int lineas
        decimal monto_neto_pedido
        int dias_despacho
        int entregado_a_tiempo
    }

    dim_tiempo {
        int tiempo_key PK "AAAAMMDD"
        date fecha
        int anio
        int trimestre
        string nombre_trimestre
        int mes
        string nombre_mes
        string anio_mes
        int dia
        int dia_semana
        string nombre_dia
        string es_fin_de_semana
    }

    dim_cliente {
        int cliente_key PK
        string cliente_id "llave de negocio"
        string empresa
        string cargo_contacto
        string ciudad
        string pais
    }

    dim_producto {
        int producto_key PK
        int producto_id "llave de negocio"
        string producto
        string cantidad_por_unidad
        string categoria
        decimal precio_lista
        string descontinuado
    }

    dim_empleado {
        int empleado_key PK
        int empleado_id "llave de negocio"
        string empleado
        string cargo
        string ciudad
        string pais
        string jefe
    }

    dim_transportista {
        int transportista_key PK
        int transportista_id "llave de negocio"
        string transportista
    }

    dim_descuento {
        int descuento_key PK
        decimal descuento_pct "llave de negocio"
        string descuento_texto
        string rango_descuento
        string tiene_descuento
    }

    dim_estado_envio {
        int estado_envio_key PK
        string estado_envio
        string cumplimiento
        string rango_despacho
    }
```

> GitHub dibuja este diagrama automáticamente. Para el documento APA, después de ejecutar el script se puede generar la imagen en SSMS: **InvacomDW → Database Diagrams → New Database Diagram**, agregando las 7 tablas.

---

## 3. Granularidad (tarea 8)

| Tabla de hechos | Granularidad | Filas esperadas | Preguntas que responde |
|---|---|---|---|
| `fact_ventas` | **Una fila por línea de pedido** (un producto dentro de un pedido) | 2155 | Ventas por producto, categoría, cliente, país, empleado y período; descuentos |
| `fact_pedidos` | **Una fila por pedido** | 830 | Cumplimiento de entregas, días de despacho, flete, ticket promedio |

**¿Por qué el nivel más detallado en ventas?** Es el nivel atómico de la fuente: permite responder cualquier pregunta por producto, y cualquier nivel superior (pedido, cliente, mes) se obtiene sumando. Agregar los datos de antemano (por ejemplo, ventas por mes) impediría analizar por producto.

**¿Por qué una segunda tabla por pedido?** El flete, las fechas de envío y el cumplimiento de entrega pertenecen al **pedido completo**, no a cada producto. Si se guardaran en `fact_ventas`, un pedido con 5 productos repetiría su flete 5 veces, y al sumar en Excel el flete saldría inflado. Lo mismo pasaría con el porcentaje de entregas a tiempo, que quedaría ponderado por la cantidad de productos y no por pedidos.

---

## 4. Dimensiones (tarea 7)

| Dimensión | Filas | Origen | Atributos para analizar | Transformaciones (ver `02_fuentes_y_calidad_datos.md`) |
|---|---|---|---|---|
| `dim_tiempo` | 1095 (2013-01-01 a 2015-12-31) | Generada en el ETL | año, trimestre, mes, día, día de la semana, fin de semana | Se genera con todos los días del rango, aunque no haya ventas (H8) |
| `dim_cliente` | 91 | `customers` | empresa, cargo del contacto, ciudad, país | Espacios dobles (H4), países estandarizados (H5); incluye clientes sin compras (H9) |
| `dim_producto` | 77 | `products` + `categories` | producto, categoría, presentación, descontinuado | Categoría desnormalizada; descontinuado `Sí`/`No` (H10); espacios dobles (H4) |
| `dim_empleado` | 9 | `employees` (+ sí misma) | empleado, cargo, ciudad, país, jefe | Nombre del jefe resuelto desde `reports_to`; `Sin jefe (Dirección)` si es nulo (H3) |
| `dim_transportista` | 3 | `shippers` | transportista | — |
| `dim_descuento` | 11 | Valores distintos de `order_details.discount` | porcentaje, rango de descuento, tiene descuento | Agrupa los porcentajes en rangos: Sin descuento (0 %), Bajo (1–5 %), Medio (6–15 %), Alto (16–25 %); incluye los descuentos atípicos (H7) |
| `dim_estado_envio` | 9 | Generada en el ETL (combinaciones posibles) | estado de envío, cumplimiento, rango de días de despacho | Clasifica los pedidos pendientes (H2) y los entregados a tiempo o tarde |

### Decisiones de diseño

- **Llaves sustitutas** (`cliente_key`, `producto_key`, etc.): enteros autoincrementales propios del DW. Se conserva además la **llave de negocio** de la fuente (`cliente_id`, `producto_id`...) para rastrear cada registro hasta su origen. Así el DW no depende de cómo la fuente numere sus registros.
- **Dimensión de rol (role-playing):** `dim_tiempo` se usa tres veces en `fact_pedidos` (fecha de pedido, requerida y de envío) sin duplicar la tabla.
- **Dimensión degenerada:** `pedido_id` vive en los hechos sin tabla propia, porque el pedido no tiene atributos descriptivos adicionales; sirve para agrupar o contar pedidos.
- **Dimensión de bandas (`dim_descuento`):** convierte un número continuo (el porcentaje) en rangos que el negocio entiende, para analizar, por ejemplo, cuánto se vende con descuento alto frente a sin descuento.
- **Dimensión basura o *junk dimension* (`dim_estado_envio`):** agrupa en una sola tabla pequeña varios indicadores de baja cardinalidad (estado, cumplimiento, rango de días) que de otro modo serían columnas de texto repetidas en los hechos. Tiene solo 9 combinaciones posibles.
- **Llave de tiempo `AAAAMMDD`** (ej. `20140315`): es legible y permite filtrar por rangos de fechas directamente en los hechos.
- **Pedidos pendientes:** apuntan a la fila `Pendiente / Pendiente / Sin enviar` de `dim_estado_envio`; `fecha_envio_key`, `dias_despacho` y `entregado_a_tiempo` quedan en `NULL` (H2). En Excel, el promedio de `entregado_a_tiempo` ignora los nulos y da directamente el **% de entregas a tiempo** solo de los pedidos enviados.

---

## 5. Medidas (tarea 7)

### `fact_ventas`

| Medida | Cálculo | Tipo | Uso |
|---|---|---|---|
| `cantidad` | `order_details.quantity` | Aditiva | Unidades vendidas |
| `precio_unitario` | `order_details.unit_price` (precio histórico, H6) | No aditiva | Se promedia, no se suma |
| `descuento_pct` | `order_details.discount` | No aditiva | Se promedia, no se suma |
| `monto_bruto` | `precio_unitario × cantidad` | Aditiva | Ventas antes de descuento |
| `monto_descuento` | `monto_bruto × descuento_pct` | Aditiva | Dinero no percibido por descuentos |
| `monto_neto` | `monto_bruto − monto_descuento` | Aditiva | **Ventas netas** (medida principal) |

### `fact_pedidos`

| Medida | Cálculo | Tipo | Uso |
|---|---|---|---|
| `flete` | `orders.freight` | Aditiva | Costo de transporte |
| `lineas` | Cantidad de líneas del pedido | Aditiva | Tamaño del pedido |
| `monto_neto_pedido` | Suma de `monto_neto` de sus líneas | Aditiva | Ticket promedio (promedio de esta medida) |
| `dias_despacho` | `shipped_date − order_date` | Semiaditiva (se promedia) | Velocidad de despacho |
| `entregado_a_tiempo` | 1 si `shipped_date ≤ required_date`, 0 si no | Indicador (se promedia) | % de entregas a tiempo |

Los montos se guardan con 4 decimales para que la suma de las líneas coincida exactamente con el total de control de la fuente (**1 265 793.04**).

---

## 6. Cobertura de las preguntas de negocio

| # | Pregunta (de `01_requisitos_negocio.md`) | Hecho | Medida | Dimensiones |
|---|---|---|---|---|
| 1 | Evolución de las ventas | `fact_ventas` | Suma de `monto_neto` | Tiempo |
| 2 | Categorías y productos que más venden | `fact_ventas` | `monto_neto`, `cantidad` | Producto |
| 3 | Países y clientes más importantes | `fact_ventas` | `monto_neto` | Cliente |
| 4 | Desempeño de los vendedores | `fact_ventas` | `monto_neto`, conteo de `pedido_id` | Empleado |
| 5 | Ticket promedio | `fact_pedidos` | Promedio de `monto_neto_pedido` | Tiempo, Cliente |
| 6 | Dinero no percibido por descuentos | `fact_ventas` | Suma de `monto_descuento` | Descuento, Producto, Cliente, Tiempo |
| 7 | Cumplimiento de entregas | `fact_pedidos` | Promedio de `entregado_a_tiempo`, conteo de pedidos | Estado de envío, Transportista, Tiempo |
| 8 | Transportista más rápido y más caro | `fact_pedidos` | Promedio de `dias_despacho`, `flete` | Transportista, Estado de envío (rango de días) |
| 9 | Peso de los productos descontinuados | `fact_ventas` | `monto_neto` | Producto (`descontinuado`) |

Las 9 preguntas quedan cubiertas por el modelo.
