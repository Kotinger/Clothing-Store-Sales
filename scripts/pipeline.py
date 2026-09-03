from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUT_DIR = DATA_DIR / "processed"
RAW_PATH = DATA_DIR / "EcommData_CSV.csv"


#нет ORDER_COL=""
#ORDER_KEY=""
MONEY_COL="Purchase Amount (USD)"
DATE_COL="Purchase Date"
DIM_COL="Location"
CLIENT_COL="Customer ID"
CLIENT_KEY=""


def load_data(path: Path)->pd.DataFrame:
    df=pd.read_csv(path, sep=";")

    #print("shape", df.shape)
    #print("columns:", df.columns.to_list())
    #print("dttypes", df.dtypes)
    #print("isna", df.isna().sum())
    return df

#правим дату и денежку
def prepare_types(df: pd.DataFrame)-> pd.DataFrame:
    df= df.copy()
    #print(df[MONEY_COL].head(5))
    df[MONEY_COL] = pd.to_numeric(
        df[MONEY_COL].astype(str).str.replace(",", "", regex=False),
        errors="coerce",
    )
    #print("money dtype", df[MONEY_COL].dtype, "sum", df[MONEY_COL].sum(), "NaN", df[MONEY_COL].isna().sum()) 
    #print("money min/max", df[MONEY_COL].min(), df[MONEY_COL].max(), "<0", int((df[MONEY_COL] < 0).sum()))
    #print(df[DATE_COL].head(5))
    
    df[DATE_COL]= pd.to_datetime(df[DATE_COL], dayfirst=True, errors="coerce") 
    #print("dates", df[DATE_COL].min(), "->", df[DATE_COL].max(), "Nat", df[DATE_COL].isna().sum())
    return df

#ну на прошлом шаге уже все ясно , просто фиксирую build_clean и sanity_check
def build_clean(df: pd.DataFrame) -> pd.DataFrame:
    clean = df.copy()
    #print("старт", len(clean))
    #print("gmv", clean[MONEY_COL].sum())
    return(clean)

def sanity_check (raw: pd.DataFrame, clean: pd.DataFrame)->None:
    print("---sanity---")
    print("rows", len(raw), "->", len(clean))
    print("gmv", clean[MONEY_COL].sum())
    print("dates", clean[DATE_COL].min(), "->", clean[DATE_COL].max())

#тут я застопорился немножко
def add_keys(clean: pd.DataFrame)-> pd.DataFrame:
    clean=clean.copy()
    return clean

def build_people(clean: pd.DataFrame)->pd.DataFrame:

    order_stat = (MONEY_COL, "count")
    people = clean.dropna(subset=[CLIENT_COL]).groupby(CLIENT_COL, as_index=False).agg(
        gmv=(MONEY_COL, "sum"),
        orders= order_stat,
        first_order = (DATE_COL, "min")

    )
    print("клиентов", len(people))
    print("покупок на клиента min/median/max",int(people["orders"].min()), people["orders"].median(), int(people["orders"].max()))
    print("repeat%", round((people["orders"] >= 2).mean() * 100, 1))

    return people

def save_table (clean:  pd.DataFrame, people: pd.DataFrame ) -> None:
    OUT_DIR = ROOT / "data"/ "processed"
    OUT_DIR.mkdir (parents=True, exist_ok=True)
    clean.to_parquet(OUT_DIR / "clean.parquet", index=False)
    people.to_parquet(OUT_DIR / "people.parquet", index=False)
    print ("saved", OUT_DIR)

def main()->None:
    raw = load_data(RAW_PATH)
    typed=prepare_types(raw)
    clean=build_clean(typed)
    sanity_check(raw, clean)
    clean = add_keys(clean)
    people= build_people(clean)
    save_table(clean, people)



if __name__ == "__main__":
    main()
