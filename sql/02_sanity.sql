-- orders = COUNT(*) — нет order_id, строка = покупка
USE clothing_store_sales;

SELECT COUNT(*) AS rows_n FROM clean_orders;

SELECT
  COUNT(*) AS orders_n,
  SUM(purchase_amount) AS gmv,
  MIN(purchase_date) AS date_min,
  MAX(purchase_date) AS date_max,
  COUNT(DISTINCT customer_id) AS customers_n
FROM clean_orders;

SELECT COUNT(*) AS people_n, SUM(gmv) AS gmv_people FROM people;
