-- =====================================================================
-- Invacom DW - Consultas de análisis
-- Responden las 9 preguntas de negocio (docs/03_modelo_dimensional.md §6)
-- Ejecutar en SSMS sobre InvacomDW (F5 corre todo; o seleccionar una
-- consulta y F5 para correr solo esa). Requiere el ETL ya cargado.
-- =====================================================================

USE InvacomDW;
GO

-- ---------------------------------------------------------------------
-- 0. Totales de control (deben coincidir con docs/02 §2.4)
--    830 pedidos · 2155 líneas · 1 265 793.04 ventas netas · 37 tarde · 21 pendientes
-- ---------------------------------------------------------------------
SELECT
    (SELECT COUNT(*) FROM dbo.fact_pedidos)                               AS pedidos,
    (SELECT COUNT(*) FROM dbo.fact_ventas)                                AS lineas,
    (SELECT CAST(SUM(monto_neto) AS DECIMAL(14,2)) FROM dbo.fact_ventas)  AS ventas_netas,
    (SELECT COUNT(*) FROM dbo.fact_pedidos WHERE entregado_a_tiempo = 0)  AS pedidos_tarde,
    (SELECT COUNT(*) FROM dbo.fact_pedidos WHERE fecha_envio_key IS NULL) AS pedidos_pendientes;


-- ---------------------------------------------------------------------
-- 1. Evolución de las ventas por trimestre
--    (2013 y 2015 son años parciales: H8)
-- ---------------------------------------------------------------------
SELECT t.anio, t.nombre_trimestre,
       CAST(SUM(v.monto_neto) AS DECIMAL(14,2)) AS ventas_netas,
       COUNT(DISTINCT v.pedido_id)              AS pedidos
FROM dbo.fact_ventas v
JOIN dbo.dim_tiempo t ON t.tiempo_key = v.fecha_pedido_key
GROUP BY t.anio, t.trimestre, t.nombre_trimestre
ORDER BY t.anio, t.trimestre;


-- ---------------------------------------------------------------------
-- 2. Categorías que más venden
-- ---------------------------------------------------------------------
SELECT p.categoria,
       CAST(SUM(v.monto_neto) AS DECIMAL(14,2)) AS ventas_netas,
       SUM(v.cantidad)                          AS unidades,
       CAST(100.0 * SUM(v.monto_neto) / SUM(SUM(v.monto_neto)) OVER ()
            AS DECIMAL(5,2))                    AS pct_ventas
FROM dbo.fact_ventas v
JOIN dbo.dim_producto p ON p.producto_key = v.producto_key
GROUP BY p.categoria
ORDER BY ventas_netas DESC;

-- 2b. Top 10 productos
SELECT TOP 10 p.producto, p.categoria,
       CAST(SUM(v.monto_neto) AS DECIMAL(14,2)) AS ventas_netas,
       SUM(v.cantidad)                          AS unidades
FROM dbo.fact_ventas v
JOIN dbo.dim_producto p ON p.producto_key = v.producto_key
GROUP BY p.producto, p.categoria
ORDER BY ventas_netas DESC;


-- ---------------------------------------------------------------------
-- 3. Países y clientes más importantes
-- ---------------------------------------------------------------------
SELECT c.pais,
       CAST(SUM(v.monto_neto) AS DECIMAL(14,2)) AS ventas_netas,
       COUNT(DISTINCT c.cliente_key)            AS clientes
FROM dbo.fact_ventas v
JOIN dbo.dim_cliente c ON c.cliente_key = v.cliente_key
GROUP BY c.pais
ORDER BY ventas_netas DESC;

-- 3b. Top 10 clientes
SELECT TOP 10 c.empresa, c.pais,
       CAST(SUM(v.monto_neto) AS DECIMAL(14,2)) AS ventas_netas
FROM dbo.fact_ventas v
JOIN dbo.dim_cliente c ON c.cliente_key = v.cliente_key
GROUP BY c.empresa, c.pais
ORDER BY ventas_netas DESC;


-- ---------------------------------------------------------------------
-- 4. Desempeño de los vendedores
-- ---------------------------------------------------------------------
SELECT e.empleado, e.cargo, e.jefe,
       CAST(SUM(v.monto_neto) AS DECIMAL(14,2)) AS ventas_netas,
       COUNT(DISTINCT v.pedido_id)              AS pedidos
FROM dbo.fact_ventas v
JOIN dbo.dim_empleado e ON e.empleado_key = v.empleado_key
GROUP BY e.empleado, e.cargo, e.jefe
ORDER BY ventas_netas DESC;


-- ---------------------------------------------------------------------
-- 5. Ticket promedio por año
-- ---------------------------------------------------------------------
SELECT t.anio,
       COUNT(*)                                          AS pedidos,
       CAST(AVG(f.monto_neto_pedido) AS DECIMAL(14,2))   AS ticket_promedio
FROM dbo.fact_pedidos f
JOIN dbo.dim_tiempo t ON t.tiempo_key = f.fecha_pedido_key
GROUP BY t.anio
ORDER BY t.anio;


-- ---------------------------------------------------------------------
-- 6. Dinero no percibido por descuentos
-- ---------------------------------------------------------------------
SELECT d.rango_descuento,
       COUNT(*)                                       AS lineas,
       CAST(SUM(v.monto_bruto)     AS DECIMAL(14,2))  AS monto_bruto,
       CAST(SUM(v.monto_descuento) AS DECIMAL(14,2))  AS monto_descuento
FROM dbo.fact_ventas v
JOIN dbo.dim_descuento d ON d.descuento_key = v.descuento_key
GROUP BY d.rango_descuento
ORDER BY monto_descuento DESC;


-- ---------------------------------------------------------------------
-- 7. Cumplimiento de entregas (los pendientes no cuentan en el %: H2)
-- ---------------------------------------------------------------------
SELECT e.estado_envio, e.cumplimiento, e.rango_despacho,
       COUNT(*) AS pedidos
FROM dbo.fact_pedidos f
JOIN dbo.dim_estado_envio e ON e.estado_envio_key = f.estado_envio_key
GROUP BY e.estado_envio_key, e.estado_envio, e.cumplimiento, e.rango_despacho
ORDER BY e.estado_envio_key;

-- 7b. % de entregas a tiempo por año (AVG ignora los NULL de los pendientes)
SELECT t.anio,
       CAST(100.0 * AVG(CAST(f.entregado_a_tiempo AS DECIMAL(5,2))) AS DECIMAL(5,2))
           AS pct_a_tiempo
FROM dbo.fact_pedidos f
JOIN dbo.dim_tiempo t ON t.tiempo_key = f.fecha_pedido_key
GROUP BY t.anio
ORDER BY t.anio;


-- ---------------------------------------------------------------------
-- 8. Transportista más rápido y más caro (solo pedidos enviados)
-- ---------------------------------------------------------------------
SELECT tr.transportista,
       COUNT(*)                                                    AS pedidos_enviados,
       CAST(AVG(CAST(f.dias_despacho AS DECIMAL(6,2))) AS DECIMAL(6,2)) AS dias_promedio,
       CAST(AVG(f.flete) AS DECIMAL(10,2))                         AS flete_promedio,
       CAST(100.0 * AVG(CAST(f.entregado_a_tiempo AS DECIMAL(5,2))) AS DECIMAL(5,2))
                                                                   AS pct_a_tiempo
FROM dbo.fact_pedidos f
JOIN dbo.dim_transportista tr ON tr.transportista_key = f.transportista_key
WHERE f.fecha_envio_key IS NOT NULL
GROUP BY tr.transportista
ORDER BY dias_promedio;


-- ---------------------------------------------------------------------
-- 9. Peso de los productos descontinuados en las ventas
-- ---------------------------------------------------------------------
SELECT p.descontinuado,
       COUNT(DISTINCT p.producto_key)           AS productos,
       CAST(SUM(v.monto_neto) AS DECIMAL(14,2)) AS ventas_netas,
       CAST(100.0 * SUM(v.monto_neto) / SUM(SUM(v.monto_neto)) OVER ()
            AS DECIMAL(5,2))                    AS pct_ventas
FROM dbo.fact_ventas v
JOIN dbo.dim_producto p ON p.producto_key = v.producto_key
GROUP BY p.descontinuado;
