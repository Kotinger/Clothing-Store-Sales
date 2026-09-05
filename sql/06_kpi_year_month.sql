-- год × месяц = reports.kpi_year_month
USE clothing_store_sales;

SELECT
  YEAR(purchase_date) AS year,
  MONTH(purchase_date) AS month,
  SUM(purchase_amount) AS gmv,
  COUNT(*) AS orders,
  SUM(purchase_amount) / COUNT(*) AS aov
FROM clean_orders
GROUP BY YEAR(purchase_date), MONTH(purchase_date)
ORDER BY year, month;
