import os
import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.environ.get("CRM_DUCKDB_PATH", ROOT / "warehouse" / "crm.duckdb"))

con = duckdb.connect(str(DB_PATH), read_only=True)

checks = {
    "fact rows equal raw pipeline rows": """
        SELECT (SELECT COUNT(*) FROM dw.fact_opportunities)
            = (SELECT COUNT(*) FROM raw.sales_pipeline)""",
    "no duplicate opportunity_id": """
        SELECT COUNT(*) = 0 FROM (
            SELECT opportunity_id FROM dw.fact_opportunities
            GROUP BY 1 HAVING COUNT(*) > 1)""",
    "no NULL foreign keys": """
        SELECT COUNT(*) = 0 FROM dw.fact_opportunities
        WHERE account_key IS NULL OR product_key IS NULL OR sales_agent_key IS NULL
        OR engage_date_key IS NULL OR close_date_key IS NULL""",
    "close_value total equals raw": """
        SELECT COALESCE((SELECT SUM(close_value) FROM dw.fact_opportunities), 0)
            = COALESCE((SELECT SUM(close_value) FROM raw.sales_pipeline), 0)""",
    "unknown account count equals raw NULL accounts": """
        SELECT (SELECT COUNT(*) FROM dw.fact_opportunities WHERE account_key = -1)
            = (SELECT COUNT(*) FROM raw.sales_pipeline WHERE account IS NULL)""",
    "unknown engage date count equals raw NULL engage_date": """
        SELECT (SELECT COUNT(*) FROM dw.fact_opportunities WHERE engage_date_key = -1)
            = (SELECT COUNT(*) FROM raw.sales_pipeline WHERE engage_date IS NULL)""",
    "unknown close date count equals raw NULL close_date": """
        SELECT (SELECT COUNT(*) FROM dw.fact_opportunities WHERE close_date_key = -1)
            = (SELECT COUNT(*) FROM raw.sales_pipeline WHERE close_date IS NULL)""",
}

FOREIGN_KEYS = [
    ("account_key", "dim_account", "account_key"),
    ("product_key", "dim_product", "product_key"),
    ("sales_agent_key", "dim_sales_agent", "sales_agent_key"),
    ("engage_date_key", "dim_date", "date_key"),
    ("close_date_key", "dim_date", "date_key"),
]
for col, dim, dim_col in FOREIGN_KEYS:
    checks[f"every fact.{col} exists in {dim}"] = f"""
        SELECT COUNT(*) = 0 FROM dw.fact_opportunities
        WHERE {col} NOT IN (SELECT {dim_col} FROM dw.{dim})"""

failed = []
for name, sql in checks.items():
    ok = con.execute(sql).fetchone()[0] is True
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok:
        failed.append(name)

con.close()
if failed:
    print(f"\n{len(failed)} validation check(s) failed")
    sys.exit(1)
print(f"\nAll {len(checks)} validation checks passed")