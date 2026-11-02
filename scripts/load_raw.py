import os
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
DB_PATH = Path(os.environ.get("CRM_DUCKDB_PATH", ROOT / "warehouse" / "crm.duckdb"))
TABLES = ["accounts", "products", "sales_teams", "sales_pipeline"]

DB_PATH.parent.mkdir(parents=True, exist_ok=True)
con = duckdb.connect(str(DB_PATH))

con.execute("CREATE SCHEMA IF NOT EXISTS raw")

for name in TABLES:
    csv_path = (RAW_DIR / f"{name}.csv").as_posix()
    con.execute(
        f"CREATE OR REPLACE TABLE raw.{name} AS "
        f"SELECT * FROM read_csv_auto('{csv_path}', header=true)"
    )
    n = con.execute(f"SELECT COUNT(*) FROM raw.{name}").fetchone()[0]
    print(f"raw.{name}: {n} rows")

con.close()