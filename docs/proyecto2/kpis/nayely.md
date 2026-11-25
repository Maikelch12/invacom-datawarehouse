# KPIs de Nayely Vega

## K7 · Tasa de descuento sobre ventas brutas

| Campo | Contenido |
|---|---|
| **Responsable** | Nayely Vega |
| **Objetivo de negocio** | Controlar el porcentaje de los ingresos por ventas que se deja de percibir debido a los descuentos aplicados. |
| **Fórmula** | (Monto de descuentos ÷ Ventas brutas) × 100 |
| **Meta** | ≤ 6 % |
| **Semáforo** | Verde: ≤ 6 % · Amarillo: > 6 % y ≤ 8 % · Rojo: > 8 % |
| **Medidas DAX** | `Ventas Brutas`, `Monto Descuento`, `Tasa de Descuento %`, `Color Descuento` |
| **Visualización** | Tarjeta con semáforo, árbol de descomposición por categoría, producto y cliente, y gráfico de columnas mensuales con formato condicional. |

### Atributos SMART

| Atributo | Justificación |
|---|---|
| **S · Específico** | Mide el porcentaje de las ventas brutas que se deja de percibir por los descuentos aplicados. |
| **M · Medible** | Se calcula utilizando `fact_ventas[monto_descuento]` y `fact_ventas[monto_bruto]`. |
| **A · Alcanzable** | La tasa histórica general es de 6,55 %. La meta se cumplió en 10 de los 22 meses analizados, equivalente al 45,45 %, con un mejor resultado mensual de 3,58 %. Esto demuestra que alcanzar la meta es posible. |
| **R · Relevante** | Permite al Gerente de Ventas controlar la política de descuentos e identificar las categorías, productos y clientes con mayor impacto sobre los ingresos. |
| **T · Temporal** | Se mide mensualmente, de julio de 2013 a abril de 2015. Se excluye mayo de 2015 de la evaluación mensual porque contiene información de un periodo incompleto. |

---

## K8 · Costo de flete sobre ventas netas

| Campo | Contenido |
|---|---|
| **Responsable** | Nayely Vega |
| **Objetivo de negocio** | Controlar el impacto del costo de transporte sobre los ingresos generados por las ventas netas. |
| **Fórmula** | (Flete total ÷ Ventas netas de los pedidos) × 100 |
| **Meta** | ≤ 5 % |
| **Semáforo** | Verde: ≤ 5 % · Amarillo: > 5 % y ≤ 6 % · Rojo: > 6 % |
| **Medidas DAX** | `Flete Total`, `Ventas Netas Pedidos`, `Flete sobre Ventas %`, `Color Flete` |
| **Visualización** | Tarjeta con semáforo y gráfico de barras por transportista. |

### Atributos SMART

| Atributo | Justificación |
|---|---|
| **S · Específico** | Mide el porcentaje de las ventas netas destinado a cubrir los costos de flete. |
| **M · Medible** | Se calcula utilizando `fact_pedidos[flete]` y `fact_pedidos[monto_neto_pedido]`, considerando una fila por pedido para evitar la duplicación del flete. |
| **A · Alcanzable** | El valor histórico general es de 5,13 %. La meta se cumplió en 10 de los 22 meses analizados, equivalente al 45,45 %, con un mejor resultado mensual de 3,65 %. Esto demuestra que alcanzar la meta es posible. |
| **R · Relevante** | Permite al Jefe de Logística y a la Junta evaluar los costos de transporte, negociar tarifas y tomar decisiones sobre la selección de transportistas. |
| **T · Temporal** | Se mide mensualmente, de julio de 2013 a abril de 2015. Se excluye mayo de 2015 de la evaluación mensual porque contiene información de un periodo incompleto. |