-- срез Location = reports.kpi_by_dim
USE clothing_store_sales;

SELECT
  location,
  SUM(purchase_amount) AS gmv,
  COUNT(*) AS orders,
  SUM(purchase_amount) / COUNT(*) AS aov
FROM clean_orders
GROUP BY location
ORDER BY gmv DESC
LIMIT 10;
