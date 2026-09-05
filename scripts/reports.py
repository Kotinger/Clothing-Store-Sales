from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "data" / "processed"

MONEY_COL = "Purchase Amount (USD)"
DATE_COL = "Purchase Date"
DIM_COL = "Location"
CLIENT_COL = "Customer ID"
SUB_COL = "Subscription Status"


def load_table():
    clean = pd.read_parquet(OUT_DIR / "clean.parquet")
    people = pd.read_parquet(OUT_DIR / "people.parquet")
    return clean, people


def kpi_totals(clean: pd.DataFrame) -> None:
    gmv = clean[MONEY_COL].sum()
    orders = len(clean)
    aov = gmv / orders
    print("gmv", gmv, "orders", orders, "aov", aov)


def kpi_by_dim(clean: pd.DataFrame) -> pd.DataFrame:
    by_dim = clean.groupby(DIM_COL, as_index=False).agg(
        gmv=(MONEY_COL, "sum"),
        orders=(MONEY_COL, "count"),
    )
    by_dim["aov"] = by_dim["gmv"] / by_dim["orders"]
    by_dim = by_dim.sort_values("gmv", ascending=False)
    print(by_dim.head(10))
    return by_dim


def kpi_year_month(clean: pd.DataFrame) -> pd.DataFrame:
    y_m = clean.copy()
    y_m["year"] = y_m[DATE_COL].dt.year
    y_m["month"] = y_m[DATE_COL].dt.month
    y_m = y_m.groupby(["year", "month"], as_index=False).agg(
        gmv=(MONEY_COL, "sum"),
        orders=(MONEY_COL, "count"),
    )
    y_m["aov"] = y_m["gmv"] / y_m["orders"]
    y_m = y_m.sort_values(["year", "month"])
    print(y_m.head(10))
    return y_m



def kpi_repeat(people: pd.DataFrame) -> None:
    # из pipeline: все клиенты покупали минимум 2 раза — смотрю медиану, не один repeat%
    print("people", len(people))
    print(
        "покупок min/median/max",
        int(people["orders"].min()),
        people["orders"].median(),
        int(people["orders"].max()),
    )
    print("repeat%", round((people["orders"] >= 2).mean() * 100, 1))
    print(
        "ltv min/median/max",
        people["gmv"].min(),
        people["gmv"].median(),
        people["gmv"].max(),
    )
    print("gmv people", people["gmv"].sum())


def kpi_retention(clean: pd.DataFrame) -> None:
    # нет чека: строка = покупка
    orders = clean[[CLIENT_COL, DATE_COL]].copy()
    orders = orders.rename(columns={DATE_COL: "order_date"})
    orders["order_month"] = orders["order_date"].dt.to_period("M")
    first = orders.groupby(CLIENT_COL)["order_month"].min().rename("cohort")
    orders = orders.join(first, on=CLIENT_COL)
    orders["period_n"] = orders["order_month"].astype(int) - orders["cohort"].astype(int)
    size = orders.groupby("cohort")[CLIENT_COL].nunique()
    active = orders.groupby(["cohort", "period_n"])[CLIENT_COL].nunique()
    ret = active.div(size, level=0).unstack(fill_value=0)
    print(
        "когорт",
        len(size),
        "размер min/median/max",
        int(size.min()),
        float(size.median()),
        int(size.max()),
    )
    if 1 in ret.columns:
        print("retention period_n=1 median", round(float(ret[1].median()), 3))
    print(ret.iloc[:6, :8].round(3))


def kpi_rfm(clean: pd.DataFrame, people: pd.DataFrame) -> pd.DataFrame:
    # R = дни с ПОСЛЕДНЕЙ покупки (не first_order). Опора = max даты в файле, не now().
    ref = clean[DATE_COL].max()
    last = clean.groupby(CLIENT_COL)[DATE_COL].max().rename("last_order")
    rfm = people.merge(last, left_on=CLIENT_COL, right_index=True, how="left")
    rfm["recency"] = (ref - rfm["last_order"]).dt.days
    rfm["frequency"] = rfm["orders"]
    rfm["monetary"] = rfm["gmv"]
    # R: меньше дней → выше балл. F/M: больше → выше.
    rfm["R"] = pd.qcut(rfm["recency"], 3, labels=[3, 2, 1], duplicates="drop")
    rfm["F"] = pd.qcut(
        rfm["frequency"].rank(method="first"), 3, labels=[1, 2, 3], duplicates="drop"
    )
    rfm["M"] = pd.qcut(
        rfm["monetary"].rank(method="first"), 3, labels=[1, 2, 3], duplicates="drop"
    )
    rfm["segment"] = rfm["R"].astype(str) + rfm["F"].astype(str) + rfm["M"].astype(str)
    print("--- rfm ---")
    print(
        "recency дней min/median/max",
        int(rfm["recency"].min()),
        float(rfm["recency"].median()),
        int(rfm["recency"].max()),
    )
    print(rfm["segment"].value_counts().head(10))
    top = rfm[rfm["segment"] == "333"]
    if len(top):
        print(
            "333 клиентов",
            len(top),
            "доля gmv%",
            round(top["gmv"].sum() / rfm["gmv"].sum() * 100, 1),
        )
    cold = rfm[rfm["R"].astype(int) == 1]
    print(
        "остывшие R=1",
        len(cold),
        "доля клиентов%",
        round(len(cold) / len(rfm) * 100, 1),
        "доля gmv%",
        round(cold["gmv"].sum() / rfm["gmv"].sum() * 100, 1),
    )
    return rfm


def kpi_by_subscription(clean: pd.DataFrame, people: pd.DataFrame) -> pd.DataFrame:
    # в этом файле у клиента один статус на все строки — можно взять first
    sub = clean.groupby(CLIENT_COL, as_index=False)[SUB_COL].first()
    p = people.merge(sub, on=CLIENT_COL, how="left")
    gmv_all = p["gmv"].sum()
    out = p.groupby(SUB_COL, as_index=False).agg(
        customers=(CLIENT_COL, "count"),
        purchases_median=("orders", "median"),
        ltv_median=("gmv", "median"),
        gmv=("gmv", "sum"),
    )
    out["customers_pct"] = (out["customers"] / out["customers"].sum() * 100).round(1)
    out["gmv_pct"] = (out["gmv"] / gmv_all * 100).round(1)
    print("--- subscription ---")
    print(out)
    return out


def main() -> None:
    clean, people = load_table()
    kpi_totals(clean)
    kpi_by_dim(clean)
    kpi_year_month(clean)
    kpi_repeat(people)
    kpi_retention(clean)
    kpi_rfm(clean, people)
    kpi_by_subscription(clean, people)


if __name__ == "__main__":
    main()
