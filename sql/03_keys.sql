-- ключи: order_id нет — проверяем таблицы и людей
USE clothing_store_sales;

SHOW TABLES;
DESCRIBE clean_orders;
DESCRIBE people;

SELECT customer_id, purchase_amount, purchase_date, location
FROM clean_orders
LIMIT 5;

SELECT customer_id, gmv, orders, first_order
FROM people
LIMIT 5;

-- у клиента один subscription_status?
SELECT COUNT(*) AS mixed_subscription
FROM (
  SELECT customer_id
  FROM clean_orders
  GROUP BY customer_id
  HAVING COUNT(DISTINCT subscription_status) > 1
) t;
