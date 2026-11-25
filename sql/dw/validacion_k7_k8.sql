-- Validacion de indicadores K7 y K8
-- Base de datos: InvacomDW

USE InvacomDW;
GO

-- K7: Tasa de descuento
SELECT
    SUM(monto_bruto) AS ventas_brutas,
    SUM(monto_descuento) AS monto_descuento,
    ROUND(
        100.0 * SUM(monto_descuento) /
        NULLIF(SUM(monto_bruto), 0), 2
    ) AS tasa_descuento_pct
FROM fact_ventas;

-- K8: Flete sobre ventas netas
SELECT
    SUM(flete) AS flete_total,
    SUM(monto_neto_pedido) AS ventas_netas,
    ROUND(
        100.0 * SUM(flete) /
        NULLIF(SUM(monto_neto_pedido), 0), 2
    ) AS flete_sobre_ventas_pct
FROM fact_pedidos;
