-- =====================================================================
-- Invacom DW - Capa de presentación para Excel (issue #18)
-- Motor: SQL Server  |  Base: InvacomDW  |  Esquema: rpt
--
-- Crea 2 vistas planas (una por tabla de hechos) que Excel consume con
-- Power Query + Modelo de datos para las tablas dinámicas:
--   rpt.vw_ventas   -> 1 fila por línea de pedido (2155) = fact_ventas
--   rpt.vw_pedidos  -> 1 fila por pedido (830)           = fact_pedidos
--
-- Por qué vistas y no las tablas directo:
--   * Excel ve nombres de negocio ("Ventas netas", "Categoría"), no llaves.
--   * Cada vista respeta la granularidad de su hecho: el flete solo existe
--     en vw_pedidos, así nunca se suma repetido por cada producto.
--   * Excel lee con un rol de solo lectura sobre el esquema rpt; no toca
--     las tablas dbo ni necesita el usuario del ETL (etl_spark).
--
-- Ejecutar en SSMS (F5). Se puede volver a ejecutar (CREATE OR ALTER).
-- Requiere el ETL ya cargado.
-- =====================================================================

USE InvacomDW;
GO

-- ---------------------------------------------------------------------
-- 1. Esquema rpt (reporting)
-- ---------------------------------------------------------------------
IF SCHEMA_ID('rpt') IS NULL
    EXEC ('CREATE SCHEMA rpt AUTHORIZATION dbo');
GO


-- ---------------------------------------------------------------------
-- 2. Vista de ventas (granularidad: línea de pedido)
--    Preguntas 1, 2, 3, 4, 6 y 9
-- ---------------------------------------------------------------------
CREATE OR ALTER VIEW rpt.vw_ventas
AS
SELECT
    -- Pedido (dimensión degenerada)
    v.pedido_id                                         AS [Pedido],

    -- Tiempo (fecha del pedido)
    t.fecha                                             AS [Fecha pedido],
    t.anio                                              AS [Año],
    t.nombre_trimestre                                  AS [Trimestre],
    -- '03 Marzo': el número adelante hace que Excel ordene los meses bien
    RIGHT('0' + CAST(t.mes AS VARCHAR(2)), 2) + ' ' + t.nombre_mes
                                                        AS [Mes],
    t.anio_mes                                          AS [Año-Mes],

    -- Cliente
    c.cliente_id                                        AS [Código cliente],
    c.empresa                                           AS [Cliente],
    c.ciudad                                            AS [Ciudad cliente],
    c.pais                                              AS [País],

    -- Producto
    p.producto                                          AS [Producto],
    p.categoria                                         AS [Categoría],
    p.descontinuado                                     AS [Descontinuado],

    -- Empleado
    e.empleado                                          AS [Vendedor],
    e.cargo                                             AS [Cargo vendedor],
    e.jefe                                              AS [Jefe],

    -- Transportista
    tr.transportista                                    AS [Transportista],

    -- Descuento (prefijo numérico solo para ordenar los rangos en Excel)
    d.descuento_texto                                   AS [Descuento],
    CASE WHEN d.descuento_pct = 0    THEN '1. '
         WHEN d.descuento_pct <= 0.05 THEN '2. '
         WHEN d.descuento_pct <= 0.15 THEN '3. '
         ELSE '4. '
    END + d.rango_descuento                             AS [Rango descuento],
    d.tiene_descuento                                   AS [Con descuento],

    -- Medidas
    v.cantidad                                          AS [Cantidad],
    v.precio_unitario                                   AS [Precio unitario],   -- promediar, no sumar
    v.descuento_pct                                     AS [Descuento %],       -- promediar, no sumar
    v.monto_bruto                                       AS [Monto bruto],
    v.monto_descuento                                   AS [Monto descuento],
    v.monto_neto                                        AS [Ventas netas],
    1                                                   AS [Líneas]             -- contador: Suma = n.º de líneas
FROM dbo.fact_ventas v
JOIN dbo.dim_tiempo        t  ON t.tiempo_key         = v.fecha_pedido_key
JOIN dbo.dim_cliente       c  ON c.cliente_key        = v.cliente_key
JOIN dbo.dim_producto      p  ON p.producto_key       = v.producto_key
JOIN dbo.dim_empleado      e  ON e.empleado_key       = v.empleado_key
JOIN dbo.dim_transportista tr ON tr.transportista_key = v.transportista_key
JOIN dbo.dim_descuento     d  ON d.descuento_key      = v.descuento_key;
GO


-- ---------------------------------------------------------------------
-- 3. Vista de pedidos (granularidad: pedido)
--    Preguntas 5, 7 y 8
--    dim_tiempo se usa 3 veces (rol): pedido, requerida y envío.
--    Pendientes: [Fecha envío], [Días despacho] y [A tiempo] quedan NULL;
--    el Promedio de Excel los ignora (H2).
-- ---------------------------------------------------------------------
CREATE OR ALTER VIEW rpt.vw_pedidos
AS
SELECT
    f.pedido_id                                         AS [Pedido],

    -- Tiempo (rol: fecha del pedido)
    tp.fecha                                            AS [Fecha pedido],
    tp.anio                                             AS [Año],
    tp.nombre_trimestre                                 AS [Trimestre],
    RIGHT('0' + CAST(tp.mes AS VARCHAR(2)), 2) + ' ' + tp.nombre_mes
                                                        AS [Mes],
    tp.anio_mes                                         AS [Año-Mes],

    -- Tiempo (roles: fecha requerida y fecha de envío)
    tq.fecha                                            AS [Fecha requerida],
    te.fecha                                            AS [Fecha envío],       -- NULL = pendiente

    -- Cliente / empleado / transportista
    c.cliente_id                                        AS [Código cliente],
    c.empresa                                           AS [Cliente],
    c.pais                                              AS [País],
    e.empleado                                          AS [Vendedor],
    tr.transportista                                    AS [Transportista],

    -- Estado de envío (junk dimension); prefijo solo para ordenar
    s.estado_envio                                      AS [Estado envío],
    s.cumplimiento                                      AS [Cumplimiento],
    CASE WHEN s.rango_despacho LIKE '0-7%'   THEN '1. '
         WHEN s.rango_despacho LIKE '8-14%'  THEN '2. '
         WHEN s.rango_despacho LIKE '15-28%' THEN '3. '
         WHEN s.estado_envio = 'Enviado'     THEN '4. '   -- Más de 28 días
         ELSE '5. '                                       -- Sin enviar
    END + s.rango_despacho                              AS [Rango despacho],

    -- Medidas
    f.flete                                             AS [Flete],
    f.lineas                                            AS [Líneas],
    f.monto_neto_pedido                                 AS [Monto pedido],      -- Promedio = ticket promedio
    f.dias_despacho                                     AS [Días despacho],     -- promediar
    CAST(f.entregado_a_tiempo AS DECIMAL(3,0))          AS [A tiempo],          -- Promedio = % a tiempo
    1                                                   AS [Pedidos]            -- contador: Suma = n.º de pedidos
FROM dbo.fact_pedidos f
JOIN      dbo.dim_tiempo        tp ON tp.tiempo_key        = f.fecha_pedido_key
JOIN      dbo.dim_tiempo        tq ON tq.tiempo_key        = f.fecha_requerida_key
LEFT JOIN dbo.dim_tiempo        te ON te.tiempo_key        = f.fecha_envio_key   -- LEFT: pendientes
JOIN      dbo.dim_cliente       c  ON c.cliente_key        = f.cliente_key
JOIN      dbo.dim_empleado      e  ON e.empleado_key       = f.empleado_key
JOIN      dbo.dim_transportista tr ON tr.transportista_key = f.transportista_key
JOIN      dbo.dim_estado_envio  s  ON s.estado_envio_key   = f.estado_envio_key;
GO


-- ---------------------------------------------------------------------
-- 4. Rol de solo lectura para Excel
--    Solo puede hacer SELECT sobre el esquema rpt (no ve dbo).
-- ---------------------------------------------------------------------
IF DATABASE_PRINCIPAL_ID('rol_lector_excel') IS NULL
    CREATE ROLE rol_lector_excel;
GO
GRANT SELECT ON SCHEMA::rpt TO rol_lector_excel;
GO

-- (Opcional) Usuario SQL para Excel. Requiere permisos de sysadmin
-- (correr conectado con Autenticación de Windows en SSMS).
-- ⚠ Cambiar la contraseña ANTES de ejecutar y NO subir la real a Git.
--
-- CREATE LOGIN excel_lector WITH PASSWORD = 'CAMBIAR_ESTA_CLAVE', CHECK_POLICY = ON;
-- CREATE USER  excel_lector FOR LOGIN excel_lector;
-- ALTER ROLE   rol_lector_excel ADD MEMBER excel_lector;
-- GO


-- ---------------------------------------------------------------------
-- 5. Totales de control: las vistas NO duplican ni pierden filas
--    Esperado: 2155 · 1 265 793.04 · 830 · 64 942.69 · 21 · 37
-- ---------------------------------------------------------------------
SELECT
    (SELECT COUNT(*)                                     FROM rpt.vw_ventas)  AS lineas_vista,
    (SELECT CAST(SUM([Ventas netas]) AS DECIMAL(14,2))   FROM rpt.vw_ventas)  AS ventas_netas_vista,
    (SELECT COUNT(*)                                     FROM rpt.vw_pedidos) AS pedidos_vista,
    (SELECT CAST(SUM([Flete]) AS DECIMAL(14,2))          FROM rpt.vw_pedidos) AS flete_vista,
    (SELECT COUNT(*) FROM rpt.vw_pedidos WHERE [Estado envío] = 'Pendiente')  AS pendientes,
    (SELECT COUNT(*) FROM rpt.vw_pedidos WHERE [Cumplimiento] = 'Tarde')      AS tarde;

-- Orden de los rangos (debe salir 1..4 y 1..5 sin huecos)
SELECT DISTINCT [Rango descuento] FROM rpt.vw_ventas  ORDER BY 1;
SELECT DISTINCT [Rango despacho]  FROM rpt.vw_pedidos ORDER BY 1;
