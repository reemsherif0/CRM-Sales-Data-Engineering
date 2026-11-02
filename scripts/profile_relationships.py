import duckdb
from pathlib import Path

RAW = Path("data/raw")
con = duckdb.connect()
for name in ["accounts", "products", "sales_teams", "sales_pipeline"]:
    con.execute(
        f"CREATE VIEW {name} AS "
        f"SELECT * FROM read_csv_auto('{(RAW / (name + '.csv')).as_posix()}', header=true)"
    )

def show(title, sql):
    print("\n" + "=" * 80)
    print(title)
    cur = con.execute(sql)
    cols = [d[0] for d in cur.description]
    print(" | ".join(cols))
    for r in cur.fetchall():
        print(" | ".join(str(x) for x in r))

show("1) deal_stage values + null patterns per stage", """
SELECT deal_stage,
    COUNT(*) AS n,
    COUNT(*) FILTER (WHERE account IS NULL)     AS null_account,
    COUNT(*) FILTER (WHERE engage_date IS NULL) AS null_engage,
    COUNT(*) FILTER (WHERE close_date IS NULL)  AS null_close_date,
    COUNT(*) FILTER (WHERE close_value IS NULL) AS null_close_value,
    COUNT(*) FILTER (WHERE close_value = 0)     AS zero_close_value
FROM sales_pipeline GROUP BY deal_stage ORDER BY n DESC
""")

show("2) Orphan keys (expected 0 for a clean join)", """
SELECT 'pipeline.product not in products' AS check_name, COUNT(*) AS n
FROM sales_pipeline WHERE product NOT IN (SELECT product FROM products)
UNION ALL
SELECT 'pipeline.account not in accounts (non-null only)', COUNT(*)
FROM sales_pipeline WHERE account IS NOT NULL
    AND account NOT IN (SELECT account FROM accounts)
UNION ALL
SELECT 'pipeline.sales_agent not in sales_teams', COUNT(*)
FROM sales_pipeline WHERE sales_agent NOT IN (SELECT sales_agent FROM sales_teams)
UNION ALL
SELECT 'accounts.subsidiary_of not in accounts', COUNT(*)
FROM accounts WHERE subsidiary_of IS NOT NULL
    AND subsidiary_of NOT IN (SELECT account FROM accounts)
""")

show("3) Dimension members with no opportunities", """
SELECT 'accounts' AS dim, COUNT(*) AS n FROM accounts
    WHERE account NOT IN (SELECT account FROM sales_pipeline WHERE account IS NOT NULL)
UNION ALL
SELECT 'products', COUNT(*) FROM products
    WHERE product NOT IN (SELECT product FROM sales_pipeline)
UNION ALL
SELECT 'sales_teams', COUNT(*) FROM sales_teams
    WHERE sales_agent NOT IN (SELECT sales_agent FROM sales_pipeline)
""")

show("4) Date sanity", """
SELECT COUNT(*) FILTER (WHERE close_date < engage_date) AS close_before_engage,
    COUNT(*) FILTER (WHERE close_date IS NOT NULL AND engage_date IS NULL) AS close_without_engage,
    COUNT(*) FILTER (WHERE (close_date IS NULL) <> (close_value IS NULL)) AS close_date_vs_value_mismatch
FROM sales_pipeline
""")

show("5) Hidden whitespace in key columns", """
SELECT 'pipeline.account' AS col, COUNT(*) AS n FROM sales_pipeline WHERE account <> TRIM(account)
UNION ALL SELECT 'pipeline.product', COUNT(*) FROM sales_pipeline WHERE product <> TRIM(product)
UNION ALL SELECT 'pipeline.sales_agent', COUNT(*) FROM sales_pipeline WHERE sales_agent <> TRIM(sales_agent)
""")