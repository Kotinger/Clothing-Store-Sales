-- маршрут продажи | totals = reports.kpi_totals
USE clothing_store_sales;

SELECT
  SUM(purchase_amount) AS gmv,
  COUNT(*) AS orders,
  SUM(purchase_amount) / COUNT(*) AS aov
FROM clean_orders;
