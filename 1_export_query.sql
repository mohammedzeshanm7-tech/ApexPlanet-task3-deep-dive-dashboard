-- Run this in MySQL Workbench on the classicmodels database.
-- Then use "Export recordset to an external file" (CSV) and save as sales_data.csv
USE classicmodels;

SELECT
    o.orderNumber,
    o.orderDate,
    o.status,
    c.customerNumber,
    c.customerName,
    c.country,
    p.productLine,
    p.productName,
    od.quantityOrdered,
    od.priceEach,
    od.quantityOrdered * od.priceEach AS sales
FROM orders o
JOIN customers c     ON o.customerNumber = c.customerNumber
JOIN orderdetails od ON o.orderNumber = od.orderNumber
JOIN products p      ON od.productCode = p.productCode
WHERE o.status <> 'Cancelled';
