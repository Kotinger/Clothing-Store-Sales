-- доп. срез | Subscription = reports.kpi_by_subscription
USE clothing_store_sales;

WITH flag AS (
  SELECT customer_id, MIN(subscription_status) AS subscription_status
  FROM clean_orders
  GROUP BY customer_id
),
joined AS (
  SELECT
    f.subscription_status,
    p.customer_id,
    p.orders,
    p.gmv
  FROM people p
  JOIN flag f ON f.customer_id = p.customer_id
)
SELECT
  subscription_status,
  COUNT(*) AS customers,
  ROUND(AVG(orders), 1) AS purchases_avg,
  ROUND(SUM(gmv), 0) AS gmv,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS customers_pct,
  ROUND(100.0 * SUM(gmv) / SUM(SUM(gmv)) OVER (), 1) AS gmv_pct
FROM joined
GROUP BY subscription_status
ORDER BY subscription_status;
