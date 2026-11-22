

## K1 · Crecimiento interanual de ventas netas (YoY %)

| Campo | Contenido |
|---|---|
| **Responsable** | Maikel Chaves Salas |
| **Objetivo de negocio** | Saber si Invacom vende más que en el mismo mes del año anterior |
| **Fórmula** | (Ventas netas del mes − Ventas netas del mismo mes del año anterior) ÷ Ventas netas del mismo mes del año anterior |
| **Meta** | ≥ 15 % de crecimiento |
| **Semáforo** |  ≥ 15 % ·  entre 0 % y 15 % ·  menor que 0 % |
| **Medidas DAX** | `Ventas Netas`, `Ventas Netas AA`, `Crecimiento YoY %`, `Color YoY` |
| **Visualización** | Tarjeta con color según el semáforo, gráfico de columnas y líneas (año actual frente al anterior) y matriz mensual con formato condicional |

### Atributos SMART

| Atributo | Justificación |
|---|---|
| **S · Específico** | Mide el crecimiento porcentual de las ventas netas (después de descuentos) de cada mes frente al mismo mes del año anterior |
| **M · Medible** | Se calcula con `fact_ventas[monto_neto]` y `dim_tiempo` del Data Warehouse, mediante la medida DAX `Crecimiento YoY %` |
| **A · Alcanzable** | Es una meta conservadora: el crecimiento histórico fue de 61 % (julio a diciembre de 2014 frente al mismo periodo de 2013) y de 121 % (enero a abril de 2015 frente al mismo periodo de 2014) |
| **R · Relevante** | La Junta Directiva lo necesita para evaluar si la estrategia comercial está funcionando |
| **T · Temporal** | Se mide mensualmente, de julio de 2014 a abril de 2015, que son los meses que tienen un año anterior con el cual comparar |

---

## K2 · Variación mensual de ventas netas (MoM %)

| Campo | Contenido |
|---|---|
| **Responsable** | Maikel Chaves Salas |
| **Objetivo de negocio** | Detectar a tiempo las caídas de ventas de un mes al siguiente |
| **Fórmula** | (Ventas netas del mes − Ventas netas del mes anterior) ÷ Ventas netas del mes anterior |
| **Meta** | ≥ 0 % (no caer respecto al mes anterior) |
| **Semáforo** |  ≥ 0 % ·  entre −10 % y 0 % ·  menor que −10 % |
| **Medidas DAX** | `Ventas Netas`, `Ventas Mes Anterior`, `Variación MoM %`, `Color MoM` |
| **Visualización** | Tarjeta con color según el semáforo y matriz mensual con íconos de flecha |

### Atributos SMART

| Atributo | Justificación |
|---|---|
| **S · Específico** | Mide el cambio porcentual de las ventas netas de cada mes frente al mes inmediatamente anterior |
| **M · Medible** | Se calcula con `fact_ventas[monto_neto]` y `dim_tiempo`, mediante la medida DAX `Variación MoM %` |
| **A · Alcanzable** | Históricamente, solo 3 de 21 meses completos cayeron más de 10 % (febrero, junio y noviembre de 2014) |
| **R · Relevante** | El Gerente de Ventas lo usa para reaccionar rápido ante una caída, con promociones o seguimiento a los vendedores |
| **T · Temporal** | Se mide mensualmente, de agosto de 2013 a abril de 2015 |

---

## Consideraciones de los datos

- **Mayo de 2015 está incompleto**: los datos llegan solo hasta el 6 de mayo. Mostraría −85 % mensual y −66 % interanual sin que haya una caída real. Por eso se excluye de la página con un filtro.
- **Antes de julio de 2014 el YoY queda en blanco**, porque los datos empiezan en julio de 2013 y no hay año anterior para comparar.