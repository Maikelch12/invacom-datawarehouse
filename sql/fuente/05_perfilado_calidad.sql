
-- ---------------------------------------------------------------------
-- 1. Volumen: filas por tabla
-- ---------------------------------------------------------------------
SELECT 'categories' AS tabla, COUNT(*) AS filas FROM categories
UNION ALL SELECT 'customers',     COUNT(*) FROM customers
UNION ALL SELECT 'employees',     COUNT(*) FROM employees
UNION ALL SELECT 'products',      COUNT(*) FROM products
UNION ALL SELECT 'shippers',      COUNT(*) FROM shippers
UNION ALL SELECT 'orders',        COUNT(*) FROM orders
UNION ALL SELECT 'order_details', COUNT(*) FROM order_details;


-- ---------------------------------------------------------------------
-- 2. Valores nulos en columnas relevantes
-- ---------------------------------------------------------------------
SELECT 'orders.shipped_date'   AS columna, COUNT(*) AS nulos FROM orders    WHERE shipped_date IS NULL
UNION ALL SELECT 'employees.reports_to',   COUNT(*) FROM employees WHERE reports_to   IS NULL
UNION ALL SELECT 'customers.city',         COUNT(*) FROM customers WHERE city         IS NULL
UNION ALL SELECT 'customers.country',      COUNT(*) FROM customers WHERE country      IS NULL
UNION ALL SELECT 'products.category_id',   COUNT(*) FROM products  WHERE category_id  IS NULL
UNION ALL SELECT 'orders.customer_id',     COUNT(*) FROM orders    WHERE customer_id  IS NULL
UNION ALL SELECT 'orders.employee_id',     COUNT(*) FROM orders    WHERE employee_id  IS NULL;

-- Detalle: pedidos sin fecha de envío (¿pendientes?)
SELECT order_id, order_date, required_date, shipped_date
FROM orders
WHERE shipped_date IS NULL
ORDER BY order_date;

-- Detalle: empleado sin jefe (¿error o es el máximo jerarca?)
SELECT employee_id, employee_name, title, reports_to
FROM employees
WHERE reports_to IS NULL;


-- ---------------------------------------------------------------------
-- 3. Duplicados
-- ---------------------------------------------------------------------
-- Clientes con el mismo nombre de empresa
SELECT company_name, COUNT(*) AS veces
FROM customers
GROUP BY company_name
HAVING COUNT(*) > 1;

-- Productos con el mismo nombre
SELECT product_name, COUNT(*) AS veces
FROM products
GROUP BY product_name
HAVING COUNT(*) > 1;


-- ---------------------------------------------------------------------
-- 4. Formatos inconsistentes en textos
-- ---------------------------------------------------------------------
-- Espacios dobles o espacios al inicio/fin
SELECT 'customers.company_name' AS columna, company_name AS valor
FROM customers
WHERE company_name LIKE '%  %' OR company_name <> TRIM(company_name)
UNION ALL
SELECT 'products.quantity_per_unit', quantity_per_unit
FROM products
WHERE quantity_per_unit LIKE '%  %' OR quantity_per_unit <> TRIM(quantity_per_unit);

-- Países: algunos abreviados (UK, USA) y otros con nombre completo
SELECT country, COUNT(*) AS clientes
FROM customers
GROUP BY country
ORDER BY country;

-- Verificación de la codificación (debe verse München, Luleå, Genève)
SELECT customer_id, company_name, city
FROM customers
WHERE city IN ('München', 'Luleå', 'Genève', 'Århus');


-- ---------------------------------------------------------------------
-- 5. Reglas de negocio en fechas
-- ---------------------------------------------------------------------
-- Rango de fechas de los pedidos (¿años completos?)
SELECT MIN(order_date) AS primer_pedido, MAX(order_date) AS ultimo_pedido
FROM orders;

-- Pedidos por año
SELECT EXTRACT(YEAR FROM order_date) AS anio, COUNT(*) AS pedidos
FROM orders
GROUP BY 1
ORDER BY 1;

-- Fechas incoherentes: requerida o enviada antes del pedido (debe dar 0)
SELECT COUNT(*) AS fechas_incoherentes
FROM orders
WHERE required_date < order_date
   OR shipped_date  < order_date;

-- Pedidos entregados tarde (enviados después de la fecha requerida)
SELECT COUNT(*) AS pedidos_tarde
FROM orders
WHERE shipped_date > required_date;


-- ---------------------------------------------------------------------
-- 6. Reglas de negocio en valores numéricos
-- ---------------------------------------------------------------------
-- Rangos de precio, cantidad, descuento y flete (no deben ser negativos)
SELECT MIN(unit_price) AS precio_min, MAX(unit_price) AS precio_max,
       MIN(quantity)   AS cant_min,   MAX(quantity)   AS cant_max,
       MIN(discount)   AS desc_min,   MAX(discount)   AS desc_max
FROM order_details;

SELECT MIN(freight) AS flete_min, MAX(freight) AS flete_max
FROM orders;

-- Distribución de descuentos (¿valores fuera de la política 0, 5, 10, 15, 20, 25 %?)
SELECT discount, COUNT(*) AS lineas
FROM order_details
GROUP BY discount
ORDER BY discount;

-- Detalle de los descuentos atípicos
SELECT order_id, product_id, unit_price, quantity, discount
FROM order_details
WHERE discount NOT IN (0, 0.05, 0.10, 0.15, 0.20, 0.25);

-- Precio de venta distinto al precio de lista actual del producto
SELECT COUNT(*) AS lineas_con_precio_distinto
FROM order_details od
JOIN products p ON p.product_id = od.product_id
WHERE od.unit_price <> p.unit_price;


-- ---------------------------------------------------------------------
-- 7. Integridad y completitud entre tablas
-- ---------------------------------------------------------------------
-- Clientes que nunca han comprado
SELECT c.customer_id, c.company_name
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id
WHERE o.order_id IS NULL;

-- Pedidos sin líneas de detalle (debe dar 0)
SELECT COUNT(*) AS pedidos_sin_detalle
FROM orders o
LEFT JOIN order_details od ON od.order_id = o.order_id
WHERE od.order_id IS NULL;

-- Productos que nunca se han vendido (debe dar 0)
SELECT COUNT(*) AS productos_sin_ventas
FROM products p
LEFT JOIN order_details od ON od.product_id = p.product_id
WHERE od.product_id IS NULL;


-- ---------------------------------------------------------------------
-- 8. Total de control para validar el ETL después
-- ---------------------------------------------------------------------
-- Ventas netas totales: el DW debe dar exactamente este mismo valor
SELECT ROUND(SUM(unit_price * quantity * (1 - discount)), 2) AS ventas_netas_totales
FROM order_details;
