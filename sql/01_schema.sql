--  зерно: строка = покупка, нет order_id
CREATE DATABASE IF NOT EXISTS clothing_store_sales
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE clothing_store_sales;

DROP TABLE IF EXISTS people;
DROP TABLE IF EXISTS clean_orders;

CREATE TABLE clean_orders (
  customer_id INT NOT NULL,
  age INT NULL,
  gender VARCHAR(20) NULL,
  item_purchased VARCHAR(100) NULL,
  category VARCHAR(50) NULL,
  purchase_amount DECIMAL(12, 2) NOT NULL,
  location VARCHAR(100) NULL,
  size VARCHAR(10) NULL,
  color VARCHAR(50) NULL,
  season VARCHAR(20) NULL,
  review_rating VARCHAR(20) NULL,
  subscription_status VARCHAR(10) NULL,
  shipping_type VARCHAR(50) NULL,
  promo_code_used TINYINT NULL,
  previous_purchases INT NULL,
  payment_method VARCHAR(50) NULL,
  purchase_date DATETIME NOT NULL,
  weekday_num TINYINT NULL,
  weekday VARCHAR(20) NULL,
  weekend TINYINT NULL,
  churn TINYINT NULL,
  INDEX idx_customer (customer_id),
  INDEX idx_date (purchase_date),
  INDEX idx_location (location)
) ENGINE=InnoDB;

-- 1 клиент = 1 строка (из pipeline people.parquet)
CREATE TABLE people (
  customer_id INT NOT NULL PRIMARY KEY,
  gmv DECIMAL(14, 2) NOT NULL,
  orders INT NOT NULL,
  first_order DATETIME NOT NULL,
  subscription_status VARCHAR(10) NULL
) ENGINE=InnoDB;
