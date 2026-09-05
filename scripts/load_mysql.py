from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "data" / "processed"

CLEAN_RENAME = {
    "Customer ID": "customer_id",
    "Age": "age",
    "Gender": "gender",
    "Item Purchased": "item_purchased",
    "Category": "category",
    "Purchase Amount (USD)": "purchase_amount",
    "Location": "location",
    "Size": "size",
    "Color": "color",
    "Season": "season",
    "Review Rating": "review_rating",
    "Subscription Status": "subscription_status",
    "Shipping Type": "shipping_type",
    "Promo Code Used": "promo_code_used",
    "Previous Purchases": "previous_purchases",
    "Payment Method": "payment_method",
    "Purchase Date": "purchase_date",
    "WeekdayNum": "weekday_num",
    "Weekday": "weekday",
    "Weekend": "weekend",
    "Churn": "churn",
}

PEOPLE_RENAME = {
    "Customer ID": "customer_id",
    "gmv": "gmv",
    "orders": "orders",
    "first_order": "first_order",
}

SUB_COL = "subscription_status"


def read_password() -> str:
    env = os.environ.get("MYSQL_PASSWORD")
    if env:
        return env.strip()
    pass_file = ROOT / "pass.txt"
    if pass_file.exists():
        for line in pass_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                return line
    raise SystemExit("Нет пароля: MYSQL_PASSWORD или pass.txt")


DB_USER = os.getenv("MYSQL_USER", "root")
DB_HOST = os.getenv("MYSQL_HOST", "localhost")
DB_NAME = os.getenv("MYSQL_DATABASE", "clothing_store_sales")


def main() -> None:
    db_pass = read_password()
    url = f"mysql+pymysql://{DB_USER}:{db_pass}@{DB_HOST}/{DB_NAME}"
    engine = create_engine(url)

    clean = pd.read_parquet(OUT_DIR / "clean.parquet").rename(columns=CLEAN_RENAME)
    people = pd.read_parquet(OUT_DIR / "people.parquet").rename(columns=PEOPLE_RENAME)

    # флаг на people — для страницы Customers в PBI (у клиента один статус)
    if SUB_COL in clean.columns and "customer_id" in people.columns:
        sub = clean.groupby("customer_id", as_index=False)[SUB_COL].first()
        people = people.merge(sub, on="customer_id", how="left")

    with engine.begin() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`"))
        conn.execute(text(f"USE `{DB_NAME}`"))

    clean.to_sql("clean_orders", engine, if_exists="replace", index=False, chunksize=5000)
    people.to_sql("people", engine, if_exists="replace", index=False, chunksize=5000)

    print("clean_orders", len(clean), "gmv", float(clean["purchase_amount"].sum()))
    print("people", len(people), "gmv", float(people["gmv"].sum()), "cols", people.columns.tolist())


if __name__ == "__main__":
    main()
