# KPIs de Xavier Fernández

## K3 · Ticket promedio por pedido

| Campo | Contenido |
|---|---|
| **Responsable** | Xavier Fernández |
| **Objetivo de negocio** | Saber cuánto compra en promedio un cliente en cada pedido |
| **Fórmula** | Ventas netas ÷ Cantidad de pedidos distintos |
| **Meta** | ≥ 1 500 por pedido |
| **Semáforo** |  ≥ 1 500 ·  entre 1 300 y 1 500 ·  menor que 1 300 |
| **Medidas DAX** | `Pedidos`, `Ticket Promedio`, `Color Ticket` |
| **Visualización** | Tarjeta con semáforo y gráfico de línea mensual |

### Atributos SMART

| Atributo | Justificación |
|---|---|
| **S · Específico** | Mide el valor promedio de las ventas netas por pedido |
| **M · Medible** | Se calcula con `fact_ventas[monto_neto]` y el conteo distinto de `fact_ventas[pedido_id]` |
| **A · Alcanzable** | El ticket histórico es de 1 525,05. Por año subió de 1 368,97 (2013) a 1 512,46 (2014) y a 1 631,94 (2015). La meta se cumplió en 10 de 22 meses |
| **R · Relevante** | El Gerente de Ventas lo usa para evaluar estrategias de venta cruzada y combos |
| **T · Temporal** | Se mide mensualmente, de julio de 2013 a abril de 2015 |

---

## K4 · Tasa de clientes recurrentes

| Campo | Contenido |
|---|---|
| **Responsable** | Xavier Fernández |
| **Objetivo de negocio** | Medir la fidelidad: qué parte de los clientes que compran en un mes ya habían comprado antes |
| **Fórmula** | Clientes del periodo que ya habían comprado antes ÷ Clientes activos del periodo |
| **Meta** | ≥ 90 % |
| **Semáforo** |  ≥ 90 % ·  entre 80 % y 90 % ·  menor que 80 % |
| **Medidas DAX** | `Clientes Activos`, `Clientes Recurrentes`, `Tasa Clientes Recurrentes`, `Color Recurrentes` |
| **Visualización** | Tarjeta con semáforo y mapa de ventas por país |

### Atributos SMART

| Atributo | Justificación |
|---|---|
| **S · Específico** | Mide el porcentaje de clientes activos en el periodo que ya tenían compras anteriores |
| **M · Medible** | Se calcula con `fact_ventas[cliente_key]` y `dim_tiempo[fecha]` mediante la medida `Tasa Clientes Recurrentes` |
| **A · Alcanzable** | Desde enero de 2014, el promedio mensual fue de 94,8 % |
| **R · Relevante** | La Junta Directiva lo usa para medir la retención: retener clientes cuesta menos que conseguir nuevos |
| **T · Temporal** | Se mide mensualmente desde enero de 2014. Antes de esa fecha la tasa sale baja porque no hay suficiente historial de compras |