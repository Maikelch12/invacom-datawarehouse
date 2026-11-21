# Proyecto 2 · Dashboard de KPIs en Power BI
---

## 1. Requisitos del enunciado y quién los cubre

| Requisito | Cómo se cumple | Responsable |
|---|---|---|
| Investigación de la metodología para diseñar KPI | Sección del documento (Balanced Scorecard + criterios SMART) | Nayely (todos revisan) |
| 2 KPI por integrante (8 en total), con atributos SMART y nombre del responsable | Ficha SMART de cada KPI en `docs/proyecto2/kpis/` | Cada uno los suyos |
| Aprobación del profesor en un plazo de 15 días | Enviar el documento de KPI en la semana 1 | Coordinador |
| Dashboard en Power BI conectado al DW | Conexión a `InvacomDW` y modelo estrella | Maikel (base) |
| Pocos gráficos por página, sin sobrecargar | Una página por área, con 3 a 5 gráficos | Todos |
| Gráficos personalizados (nada con el formato por defecto) | Tema común de colores y letras + títulos, etiquetas y sombras en cada gráfico | Maikel (tema) y todos |
| Gráficos secundarios de contexto | Concentración por país, categoría, vendedor y transportista | Todos |
| Comparar periodos mensuales | Mes actual frente al mes anterior y al mismo mes del año anterior | Maikel |
| Al menos 6 funciones DAX distintas | Ver la tabla de la sección 3 | Todos |
| Al menos 2 visuales que no sean nativos (AppSource) | Dial Gauge y Cylindrical Gauge | Álvaro |
| Mapa | Ventas por país | Xavier |
| Árbol de descomposición (Decomposition Tree) | Descuentos por categoría → producto → cliente | Nayely |
| Formato condicional para valores positivos y negativos | Crecimiento en verde o rojo, con flechas | Maikel (y todos en sus tablas) |

---

## 2. División del trabajo: 8 KPI y 4 páginas

| Integrante | KPI | Página del dashboard | Requisitos técnicos que aporta |
|---|---|---|---|
| **Maikel** | **K1** Crecimiento interanual de ventas netas (YoY %) · **K2** Variación mensual de ventas netas (MoM %) | **1. Resumen de ventas** | Conexión, modelo, tabla de medidas y tema visual. `SAMEPERIODLASTYEAR`, `PREVIOUSMONTH`, `VAR`. Comparación mensual y formato condicional |
| **Xavier** | **K3** Ticket promedio por pedido · **K4** Tasa de clientes recurrentes | **2. Clientes y mercados** | **Mapa** de ventas por país. `DISTINCTCOUNT`, `FILTER` |
| **Álvaro** | **K5** % de pedidos entregados a tiempo · **K6** Días promedio de despacho | **3. Logística** | **2 visuales de AppSource** (Dial Gauge y Cylindrical Gauge). `USERELATIONSHIP`, `AVERAGE` |
| **Nayely** | **K7** Tasa de descuento sobre ventas brutas · **K8** Costo de flete sobre ventas netas | **4. Rentabilidad comercial** | **Árbol de descomposición**. `CALCULATE`, `DIVIDE`. Investigación de la metodología y armado del documento |

Cada integrante:
1. Redacta la ficha SMART de sus 2 KPI en `docs/proyecto2/kpis/su-nombre.md`.
2. Escribe y **entiende** las medidas DAX de sus KPI.
3. Construye su página del dashboard.
4. Presenta su página y sus KPI en la sustentación.

---

## 3. Funciones DAX del equipo (mínimo 6 distintas)

| Función | Para qué | KPI |
|---|---|---|
| `SUM` | Sumar montos | Todos |
| `CALCULATE` | Cambiar el contexto de un cálculo | K1, K2, K7 |
| `SAMEPERIODLASTYEAR` | El mismo periodo del año anterior | K1 |
| `PREVIOUSMONTH` | El mes anterior | K2 |
| `VAR` / `RETURN` | Variables para fórmulas legibles | K1, K2, K4 |
| `DIVIDE` | División segura (no falla si el divisor es 0) | Todos los porcentajes |
| `DISTINCTCOUNT` | Contar pedidos y clientes distintos | K3, K4 |
| `FILTER` | Filtrar una tabla dentro de un cálculo | K4 |
| `USERELATIONSHIP` | Activar la relación con la fecha de envío | K6 |
| `AVERAGE` | Promedios | K5, K6 |

---

## 4. Cronograma (sprints de una semana)

| Semana | Entregable |
|---|---|
| **1** | Metodología + fichas SMART de los 8 KPI → **enviar al profesor para su aprobación** |
| **2** | Modelo de Power BI (Maikel) + cada uno empieza su página con sus medidas DAX |
| **3** | Páginas terminadas, personalización, formato condicional y visuales de AppSource |
| **4** | Revisión cruzada, documento final y ensayo de la presentación de 20 minutos |

---

## 5. Reglas para trabajar Power BI con Git

- El dashboard se guarda en la carpeta `powerbi/`.
- **Una página por persona**, cada una en su propia rama.
- **Todas las medidas DAX van en la tabla `_Medidas`.**
- **Avisar en el chat del equipo antes de abrir y modificar el archivo de Power BI.** Si dos personas lo modifican a la vez, uno pierde su trabajo.
- Siempre `git pull` antes de empezar, y commit + push apenas se termina.

---

## 6. Dudas enviadas al profesor (Product Owner)

1. El enunciado dice *"tres (2) KPIs"* por integrante, pero el ejemplo dice 8 KPI para 4 integrantes. ¿Son 2 o 3 por persona? (Este plan supone 2.)
2. ¿Desde qué fecha cuentan los 15 días para la aprobación de los KPI?
3. El contexto menciona a *Grupo Innova S.A.*, pero el DW de la Fase 1 es de Invacom. ¿Se mantiene Invacom?
4. Si el visual **Map** no está disponible en Power BI, ¿se acepta **Azure Maps**?