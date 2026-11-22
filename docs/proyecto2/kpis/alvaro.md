# KPIs de Álvaro Víctor

## K5 · Porcentaje de pedidos entregados a tiempo

| Campo | Contenido |
|---|---|
| **Responsable** | Álvaro Víctor |
| **Objetivo de negocio** | Medir la puntualidad de las entregas a los clientes |
| **Fórmula** | Pedidos enviados con fecha de envío ≤ fecha requerida ÷ Pedidos enviados |
| **Meta** | ≥ 95 % |
| **Semáforo** |  ≥ 95 % ·  entre 90 % y 95 % ·  menor que 90 % |
| **Medidas DAX** | `% Entregas a Tiempo`, `Pedidos Tarde`, `Meta Entregas`, `Color Entregas` |
| **Visualización** | Dial Gauge (AppSource) con la meta, y barras por transportista |

### Atributos SMART

| Atributo | Justificación |
|---|---|
| **S · Específico** | Mide qué porcentaje de los pedidos enviados llegó en la fecha requerida o antes |
| **M · Medible** | Se calcula con `fact_pedidos[entregado_a_tiempo]` (1 = a tiempo, 0 = tarde). Los 21 pedidos pendientes no se cuentan porque no tienen fecha de envío |
| **A · Alcanzable** | El cumplimiento histórico es de 95,43 % (772 de 809 pedidos enviados). El mes más bajo tuvo 91,2 % |
| **R · Relevante** | El Jefe de Logística lo usa para evaluar a los transportistas y negociar con ellos |
| **T · Temporal** | Se mide mensualmente, según la fecha del pedido, de julio de 2013 a abril de 2015 |

---

## K6 · Días promedio de despacho

| Campo | Contenido |
|---|---|
| **Responsable** | Álvaro Víctor |
| **Objetivo de negocio** | Medir la rapidez con que se despachan los pedidos |
| **Fórmula** | Promedio de (fecha de envío − fecha del pedido), en días |
| **Meta** | ≤ 8 días |
| **Semáforo** |  ≤ 8 ·  entre 8 y 10 ·  más de 10 días |
| **Medidas DAX** | `Días Promedio Despacho`, `Meta Días`, `Color Días` |
| **Visualización** | Cylindrical Gauge (AppSource) con la meta, y línea mensual |

### Atributos SMART

| Atributo | Justificación |
|---|---|
| **S · Específico** | Mide el tiempo promedio, en días, entre que se hace el pedido y se envía |
| **M · Medible** | Se calcula con `fact_pedidos[dias_despacho]`, usando la fecha de envío mediante `USERELATIONSHIP` |
| **A · Alcanzable** | El promedio histórico es de 8,49 días. Siete meses ya estuvieron en 8 días o menos (el mejor, 6,1) |
| **R · Relevante** | Un despacho rápido mejora la satisfacción del cliente y reduce el riesgo de entregar tarde |
| **T · Temporal** | Se mide mensualmente, según la fecha de envío, de julio de 2013 a mayo de 2015 |