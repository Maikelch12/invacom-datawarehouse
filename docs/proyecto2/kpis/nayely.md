# KPIs de Nayely Vega

## K7 · Tasa de descuento sobre ventas brutas

| Campo | Contenido |
|---|---|
| **Responsable** | Nayely Vega |
| **Objetivo de negocio** | Controlar cuánto de las ventas se deja de percibir por descuentos |
| **Fórmula** | Monto de descuentos ÷ Ventas brutas |
| **Meta** | ≤ 6 % |
| **Semáforo** |  ≤ 6 % ·  entre 6 % y 8 % ·  más de 8 % |
| **Medidas DAX** | `Ventas Brutas`, `Monto Descuento`, `Tasa de Descuento %`, `Color Descuento` |
| **Visualización** | Árbol de descomposición y columnas mensuales con semáforo |

### Atributos SMART

| Atributo | Justificación |
|---|---|
| **S · Específico** | Mide el porcentaje de las ventas brutas que se pierde por descuentos |
| **M · Medible** | Se calcula con `fact_ventas[monto_descuento]` y `fact_ventas[monto_bruto]` |
| **A · Alcanzable** | La tasa histórica es de 6,55 %, y la meta se cumplió en 10 de 22 meses (el mejor mes, 3,6 %) |
| **R · Relevante** | El Gerente de Ventas lo usa para controlar la política de descuentos de los vendedores |
| **T · Temporal** | Se mide mensualmente, de julio de 2013 a abril de 2015 |

---

## K8 · Costo de flete sobre ventas netas

| Campo | Contenido |
|---|---|
| **Responsable** | Nayely Vega |
| **Objetivo de negocio** | Controlar el peso del costo de transporte frente a lo que se vende |
| **Fórmula** | Flete total ÷ Ventas netas de los pedidos |
| **Meta** | ≤ 5 % |
| **Semáforo** |  ≤ 5 % ·  entre 5 % y 6 % ·  más de 6 % |
| **Medidas DAX** | `Flete Total`, `Flete sobre Ventas %`, `Color Flete` |
| **Visualización** | Tarjeta con semáforo y barras por transportista |

### Atributos SMART

| Atributo | Justificación |
|---|---|
| **S · Específico** | Mide qué porcentaje de las ventas netas se gasta en flete |
| **M · Medible** | Se calcula con `fact_pedidos[flete]` y `fact_pedidos[monto_neto_pedido]` (una fila por pedido, sin duplicar el flete) |
| **A · Alcanzable** | El valor histórico es de 5,13 %, y la meta se cumplió en 10 de 22 meses (el mejor mes, 3,7 %) |
| **R · Relevante** | El Jefe de Logística y la Junta lo usan para negociar tarifas y decidir qué transportista usar |
| **T · Temporal** | Se mide mensualmente, de julio de 2013 a abril de 2015 |