import duckdb

con = duckdb.connect("warehouse/crm.duckdb", read_only=True)

checks = [
    ("accounts", "sector"),
    ("accounts", "office_location"),
    ("products", "series"),
    ("sales_teams", "manager"),
    ("sales_teams", "regional_office"),
    ("sales_pipeline", "deal_stage"),
]

for table, col in checks:
    rows = con.execute(
        f"SELECT {col}, COUNT(*) FROM raw.{table} GROUP BY 1 ORDER BY 1"
    ).fetchall()
    print(f"\n{table}.{col}")
    for r in rows:
        print("  ", r)