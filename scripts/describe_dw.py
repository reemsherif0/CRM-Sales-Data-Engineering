import os
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.environ.get("CRM_DUCKDB_PATH", ROOT / "warehouse" / "crm.duckdb"))
OUT = ROOT / "docs" / "physical_schema.dbml"

PRIMARY_KEYS = {
    "fact_opportunities": "opportunity_id",
    "dim_account": "account_key",
    "dim_product": "product_key",
    "dim_sales_agent": "sales_agent_key",
    "dim_date": "date_key",
}
FOREIGN_KEYS = {
    "account_key": "dw.dim_account.account_key",
    "product_key": "dw.dim_product.product_key",
    "sales_agent_key": "dw.dim_sales_agent.sales_agent_key",
    "engage_date_key": "dw.dim_date.date_key",
    "close_date_key": "dw.dim_date.date_key",
}

con = duckdb.connect(str(DB_PATH), read_only=True)

print("Database objects")
for schema, table, kind in con.execute("""
    SELECT table_schema, table_name, table_type FROM information_schema.tables
    WHERE table_schema IN ('raw', 'staging', 'dw') ORDER BY 1, 2""").fetchall():
    print(f"  {schema}.{table:<22}{kind}")

tables = [r[0] for r in con.execute("""
    SELECT table_name FROM information_schema.tables WHERE table_schema = 'dw'
    ORDER BY CASE WHEN table_name LIKE 'fact%' THEN 0 ELSE 1 END, table_name""").fetchall()]

dbml = []
for table in tables:
    cols = con.execute("""
        SELECT column_name, data_type FROM information_schema.columns
        WHERE table_schema = 'dw' AND table_name = ? ORDER BY ordinal_position""",
        [table]).fetchall()
    print(f"\ndw.{table}")
    dbml.append(f"Table dw.{table} {{")
    for name, dtype in cols:
        print(f"  {name:<22}{dtype}")
        attrs = []
        if PRIMARY_KEYS.get(table) == name:
            attrs.append("pk")
        if table == "fact_opportunities" and name in FOREIGN_KEYS:
            attrs.append(f"ref: > {FOREIGN_KEYS[name]}")
        suffix = f" [{', '.join(attrs)}]" if attrs else ""
        dbml.append(f"  {name} {dtype.lower()}{suffix}")
    dbml.append("}\n")

OUT.write_text("\n".join(dbml), encoding="utf-8")
print(f"\nWrote {OUT}")
con.close()