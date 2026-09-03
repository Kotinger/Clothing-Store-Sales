from pathlib import Path
import pandas as pd

ROOT= Path(__file__).resolve().parent.parent
OUT_DIR = ROOT /"data" / "processed"

MONEY_COL="Purchase Amount (USD)"
DATE_COL="Purchase Date"
DIM_COL="Location"
CLIENT_COL="Customer ID"

def load_table() -> pd.DataFrame:
    return pd.read_parquet(OUT_DIR/"clean.parquet")

def kpi_totals(clean: pd.DataFrame)->None:
    gmv= clean[MONEY_COL].sum()
    orders = len(clean)
    aov = gmv / orders
    print("gmv",gmv, "orders",orders, "aov",aov)
    

def kpi_by_dim(clean: pd.DataFrame)-> pd.DataFrame:
    by_dim = clean.groupby(DIM_COL, as_index=False).agg(
        gmv =(MONEY_COL , "sum"),
        orders=(MONEY_COL, "count")
    )
    by_dim["aov"] = by_dim["gmv"]/by_dim["orders"] 
    by_dim = by_dim.sort_values("gmv", ascending=False )

    print (by_dim.head(10))
    return by_dim

def kpi_year_month(clean: pd.DataFrame)->pd.DataFrame:
    y_m=clean.copy()
    y_m["year"]= y_m[DATE_COL].dt.year
    y_m["month"]=y_m[DATE_COL].dt.month
    y_m = y_m.groupby(["year", "month"], as_index=False).agg(
        gmv = (MONEY_COL, "sum"),
        orders= (MONEY_COL, "count")
    )
    y_m["aov"]=y_m["gmv"]/ y_m["orders"]
    y_m=y_m.sort_values(["year", "month"])
    print(y_m.head(10))
    return y_m


def main()-> None:
    clean = load_table()
    kpi_totals(clean)
    kpi_by_dim(clean)
    kpi_year_month(clean)

if __name__ == "__main__":
    main()