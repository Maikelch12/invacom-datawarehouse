# Requisitos del Negocio y Objetivos del Data Warehouse


## 1. Propósito del proyecto

Invacom Inc S.A. es una distribuidora de alimentos que vende a empresas clientes en 21 países. Hoy su información de ventas vive en un sistema operacional (base de datos transaccional en PostgreSQL) diseñado para **registrar** pedidos, no para **analizarlos**: responder preguntas como "¿cuánto vendimos por categoría en cada trimestre?" exige consultas complejas que unen siete tablas, son lentas y dependen de personal técnico.

El propósito del proyecto es construir un **Data Warehouse** en SQL Server, alimentado mediante un proceso ETL desarrollado en Apache Spark (PySpark), que integre y limpie los datos de ventas en un **modelo dimensional** orientado al análisis. Así, la junta directiva y las jefaturas podrán consultar indicadores de ventas, clientes, productos, empleados y logística de forma rápida y autónoma mediante tablas dinámicas de Excel, para tomar decisiones basadas en datos.

---

## 2. Usuarios y sus necesidades

| Usuario | Qué necesita saber | Cómo lo usará | Frecuencia |
|---|---|---|---|
| **Junta Directiva / Gerencia General** | Evolución de las ventas netas en el tiempo; países y categorías que más aportan | Definir la estrategia comercial y de expansión por mercado | Trimestral |
| **Gerente de Ventas** | Ventas por empleado, por país y por cliente; ticket promedio; impacto de los descuentos | Asignar metas, evaluar el desempeño de los vendedores y controlar la política de descuentos | Mensual |
| **Jefe de Logística** | Cumplimiento de fechas de entrega, tiempos de despacho y costo de flete por transportista | Negociar con los transportistas y reducir los retrasos | Mensual |
| **Gerente de Compras / Producto** | Productos y categorías más vendidos; peso de los productos descontinuados en las ventas | Planificar el inventario y decidir qué productos impulsar o retirar | Mensual |

---

## 3. Preguntas de negocio y KPI

| # | Pregunta de negocio | KPI | Datos necesarios (tabla.columna) |
|---|---|---|---|
| 1 | ¿Cómo evolucionan nuestras ventas en el tiempo? | Ventas netas por mes, trimestre y año | `order_details.unit_price`, `order_details.quantity`, `order_details.discount`, `orders.order_date` |
| 2 | ¿Qué categorías y productos generan más ingresos? | Ventas netas y unidades vendidas por categoría / producto | `order_details.*`, `products.product_name`, `categories.category_name` |
| 3 | ¿Qué países y clientes son los más importantes? | Ventas netas por país y por cliente; ranking de los 10 mejores clientes | `order_details.*`, `customers.country`, `customers.company_name` |
| 4 | ¿Qué vendedores tienen mejor desempeño? | Ventas netas y número de pedidos por empleado | `order_details.*`, `orders.employee_id`, `employees.employee_name` |
| 5 | ¿Cuánto compra un cliente en cada pedido? | Ticket promedio = ventas netas / número de pedidos | `order_details.*`, `orders.order_id` |
| 6 | ¿Cuánto dinero dejamos de percibir por descuentos? | Monto total descontado y % de líneas con descuento | `order_details.unit_price`, `order_details.quantity`, `order_details.discount` |
| 7 | ¿Estamos cumpliendo los plazos de entrega? | % de pedidos entregados a tiempo (`shipped_date ≤ required_date`) | `orders.shipped_date`, `orders.required_date` |
| 8 | ¿Qué transportista es más rápido y cuál cuesta más? | Días promedio de despacho y flete promedio por transportista | `orders.order_date`, `orders.shipped_date`, `orders.freight`, `shippers.company_name` |
| 9 | ¿Qué parte de las ventas depende de productos descontinuados? | % de ventas netas de productos descontinuados | `order_details.*`, `products.discontinued` |

**Fórmula base:** Ventas netas = `unit_price × quantity × (1 − discount)`. Se usa el precio de `order_details` (precio pactado en la venta) y no el de `products` (precio de lista actual).

### Preguntas descartadas (límites de los datos)

| Pregunta | Motivo |
|---|---|
| ¿Cuál es la ganancia o margen por producto? | La fuente no contiene costos de compra |
| ¿Cómo está el inventario disponible? | No hay datos de existencias ni de proveedores |
| ¿Cuál es la satisfacción de los clientes? | No hay encuestas ni devoluciones registradas |

### Consideraciones para el análisis

- Los pedidos van del **4 de julio de 2013 al 6 de mayo de 2015**. Los años 2013 y 2015 están **incompletos**, por lo que las comparaciones anuales deben hacerse con cuidado (o por mes y trimestre).
- **21 pedidos no tienen fecha de envío** (pendientes de despacho). Se excluyen del KPI de cumplimiento de entregas, pero sí cuentan en las ventas.

---

## 4. Objetivos

### Objetivo general

Desarrollar un Data Warehouse para Invacom Inc S.A., poblado mediante un proceso ETL en Apache Spark desde la base operacional en PostgreSQL hacia un modelo dimensional en SQL Server, que permita a la gerencia analizar ventas, clientes, productos, empleados y logística mediante tablas dinámicas en Excel para apoyar la toma de decisiones.

### Objetivos específicos

1. Analizar la base de datos fuente (7 tablas) para identificar sus estructuras, relaciones y problemas de calidad de datos, documentando cada hallazgo y su estrategia de limpieza.
2. Diseñar un modelo dimensional en esquema estrella, con granularidad a nivel de línea de pedido, que responda las 9 preguntas de negocio definidas.
3. Implementar un proceso ETL en PySpark que extraiga, transforme y cargue el 100 % de los registros válidos de la fuente (830 pedidos y 2155 líneas de detalle) en SQL Server.
4. Validar la carga mediante la conciliación de conteos y de ventas netas totales entre la fuente y el Data Warehouse, con una diferencia de 0 registros.
5. Construir tablas dinámicas en Excel conectadas al Data Warehouse que presenten los 9 KPI definidos para los usuarios de negocio.