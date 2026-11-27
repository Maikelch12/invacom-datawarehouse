# Metodología para el diseño y la construcción de KPI gerenciales

**Proyecto 2:** Dashboard de KPIs en Power BI · Invacom Inc S.A.
**Responsable de la investigación:** Maikel Chaves Salas

---

## 1. ¿Qué es un KPI?

Un **indicador clave de desempeño** (*Key Performance Indicator*, KPI) es una medida cuantificable que muestra qué tan bien una organización avanza hacia sus objetivos estratégicos (Parmenter, 2019). No todo número es un KPI; Parmenter distingue tres tipos de indicadores:

| Tipo | Qué responde | Ejemplo en Invacom |
|---|---|---|
| **Indicador de resultado clave (KRI)** | ¿Cómo nos fue? Visión general para la junta | Ventas netas totales |
| **Indicador de desempeño (PI)** | ¿Qué hay que hacer? Mide una actividad concreta | Pedidos por vendedor |
| **Indicador clave de desempeño (KPI)** | ¿Qué hacer para mejorar drásticamente el desempeño? | % de pedidos entregados a tiempo |

Un buen KPI se mide con frecuencia, tiene un responsable claro, está ligado a un objetivo y permite tomar una acción cuando se sale de la meta (Marr, 2012).

---

## 2. Marcos de referencia investigados

### 2.1 Balanced Scorecard (Cuadro de Mando Integral)

Propuesto por Kaplan y Norton (1992, 1996), traduce la estrategia de la empresa en indicadores organizados en **cuatro perspectivas**, para no medir solo lo financiero:

| Perspectiva | Pregunta que responde |
|---|---|
| **Financiera** | ¿Cómo nos ven los accionistas? |
| **Clientes** | ¿Cómo nos ven los clientes? |
| **Procesos internos** | ¿En qué procesos debemos ser excelentes? |
| **Aprendizaje y crecimiento** | ¿Cómo seguimos mejorando y creando valor? |

**Por qué lo usamos:** obliga a que los KPI cubran varias áreas del negocio y no solo las ventas, y conecta cada indicador con un objetivo estratégico.

### 2.2 Criterios S.M.A.R.T.

Doran (1981) propuso que todo objetivo de gestión debe ser:

| Letra | Criterio | Pregunta de control |
|---|---|---|
| **S** | Específico (*Specific*) | ¿Mide una sola cosa, claramente definida? |
| **M** | Medible (*Measurable*) | ¿Se puede calcular con los datos disponibles? |
| **A** | Alcanzable (*Achievable*) | ¿La meta es realista según el histórico? |
| **R** | Relevante (*Relevant*) | ¿Ayuda a una decisión de un usuario del negocio? |
| **T** | Temporal (*Time-bound*) | ¿Tiene una frecuencia y un periodo de medición? |

**Por qué lo usamos:** es el filtro de calidad de cada KPI. Si un indicador no cumple los cinco criterios, se reformula o se descarta.

### 2.3 Metodología de Parmenter

Parmenter (2019) plantea que los KPI deben salir de los **factores críticos de éxito** de la organización: las pocas cosas que, si se hacen bien, garantizan el éxito. Primero se identifican esos factores y después se diseñan los indicadores que los miden, y no al revés.

**Por qué lo usamos:** evita elegir indicadores solo porque los datos existen. Cada KPI debe responder a una necesidad del negocio.

---

## 3. Metodología aplicada por el equipo

Combinamos los tres marcos en un proceso de 8 pasos:

| Paso | Actividad | Marco de referencia | Resultado en el proyecto |
|---|---|---|---|
| **1** | Identificar los objetivos estratégicos y los usuarios | Balanced Scorecard | 4 usuarios: Junta Directiva, Gerente de Ventas, Jefe de Logística y Gerente de Compras (Proyecto 1) |
| **2** | Definir los factores críticos de éxito | Parmenter | Crecer en ventas, retener clientes, entregar a tiempo y controlar los costos comerciales |
| **3** | Proponer indicadores para cada factor | Parmenter | 8 KPI, 2 por integrante |
| **4** | Ubicar cada KPI en una perspectiva | Balanced Scorecard | Ver la tabla de la sección 4 |
| **5** | Validar los criterios SMART | Doran | Ficha SMART de cada KPI |
| **6** | Definir la meta y el semáforo | SMART (Alcanzable) | Metas basadas en el histórico de 2013 a 2015 |
| **7** | Identificar la fuente en el Data Warehouse | Modelo dimensional (Kimball y Ross, 2013) | Tabla de hechos, dimensiones y medida DAX de cada KPI |
| **8** | Revisión y aprobación | Product Owner (Scrum) | Envío al profesor para su aprobación |

---

## 4. Los 8 KPI del equipo en el Balanced Scorecard

| KPI | Responsable | Perspectiva | Factor crítico de éxito |
|---|---|---|---|
| K1 · Crecimiento interanual de ventas netas | Maikel Chaves | Financiera | Crecer en ventas |
| K2 · Variación mensual de ventas netas | Maikel Chaves | Financiera | Crecer en ventas |
| K3 · Ticket promedio por pedido | Xavier Fernández | Financiera | Crecer en ventas |
| K4 · Tasa de clientes recurrentes | Xavier Fernández | Clientes | Retener clientes |
| K5 · % de pedidos entregados a tiempo | Álvaro Víctor | Procesos internos | Entregar a tiempo |
| K6 · Días promedio de despacho | Álvaro Víctor | Procesos internos | Entregar a tiempo |
| K7 · Tasa de descuento sobre ventas brutas | Nayely Vega | Financiera | Controlar los costos comerciales |
| K8 · Costo de flete sobre ventas netas | Nayely Vega | Procesos internos | Controlar los costos comerciales |

**Limitación:** la perspectiva de **aprendizaje y crecimiento** no tiene KPI, porque el Data Warehouse no contiene datos de capacitación, personal ni innovación. Se documenta como una mejora futura: incorporar datos de recursos humanos.

---

## 5. Del KPI al dashboard

Cada KPI aprobado sigue el mismo camino hasta Power BI:

1. **Dato** en el Data Warehouse .
2. **Medida DAX** que lo calcula .
3. **Meta y semáforo**: verde, amarillo o rojo con formato condicional.
4. **Visualización** principal y gráficos de contexto.
5. **Comparación en el tiempo**: mes contra mes anterior y contra el mismo mes del año anterior.

---

## 6. Aplicación de la metodología a la rentabilidad comercial

**Responsable del aporte:** Nayely Vega Murillo.

### 6.1 Aplicación del Balanced Scorecard

El indicador K7 pertenece a la perspectiva financiera, debido a que permite controlar el impacto de los descuentos sobre los ingresos comerciales.

El indicador K8 pertenece a la perspectiva de procesos internos, ya que permite evaluar la eficiencia de los costos asociados al transporte de los pedidos.

Ambos indicadores contribuyen al control de los costos comerciales y apoyan la toma de decisiones gerenciales.

### 6.2 Justificación de las metas SMART

Las metas se establecieron considerando el comportamiento histórico de los datos y la posibilidad de alcanzar mejores resultados.

| Indicador | Resultado histórico | Meta | Mejor resultado mensual |
|---|---:|---:|---:|
| K7 - Tasa de descuento | 6,55 % | <= 6 % | 3,58 % |
| K8 - Flete sobre ventas netas | 5,13 % | <= 5 % | 3,65 % |

Para evaluar la viabilidad de las metas se analizaron 22 meses completos, desde julio de 2013 hasta abril de 2015. Ambos indicadores alcanzaron su respectiva meta en 10 de los 22 meses analizados.

Mayo de 2015 se excluyó de esta evaluación mensual porque contiene información parcial.

### 6.3 Criterios de interpretación

| Indicador | Verde | Amarillo | Rojo |
|---|---|---|---|
| K7 | Hasta 6 % | Mayor a 6 % y hasta 8 % | Mayor a 8 % |
| K8 | Hasta 5 % | Mayor a 5 % y hasta 6 % | Mayor a 6 % |

Los colores permiten identificar rápidamente las desviaciones respecto a las metas establecidas.

### 6.4 Validación de los indicadores

Las medidas DAX se contrastaron con consultas SQL sobre las tablas de hechos del Data Warehouse.

Los resultados obtenidos en Power BI coincidieron con los cálculos realizados en SQL Server.

Se incorporó el archivo `sql/dw/validacion_k7_k8.sql` para facilitar la reproducción de estas comprobaciones.

### 6.5 Apoyo a la toma de decisiones

- Identificar categorías, productos y clientes con mayores montos de descuento.
- Analizar el comportamiento mensual de los descuentos.
- Comparar el costo relativo del flete entre transportistas.
- Detectar desviaciones respecto a las metas comerciales.

Estos indicadores permiten evaluar los descuentos y costos de transporte, aunque no representan por sí solos la rentabilidad total de la empresa, debido a que no se dispone de todos los costos operativos.

---

## Referencias

Doran, G. T. (1981). There's a S.M.A.R.T. way to write management's goals and objectives. *Management Review, 70*(11), 35–36.

Kaplan, R. S., & Norton, D. P. (1992). The balanced scorecard: Measures that drive performance. *Harvard Business Review, 70*(1), 71–79.

Kaplan, R. S., & Norton, D. P. (1996). *The balanced scorecard: Translating strategy into action*. Harvard Business School Press.

Kimball, R., & Ross, M. (2013). *The data warehouse toolkit: The definitive guide to dimensional modeling* (3rd ed.). Wiley.

Marr, B. (2012). *Key performance indicators (KPI): The 75 measures every manager needs to know*. Pearson Education.

Parmenter, D. (2019). *Key performance indicators: Developing, implementing, and using winning KPIs* (4th ed.). Wiley.