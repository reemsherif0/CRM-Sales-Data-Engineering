import duckdb

con = duckdb.connect("warehouse/crm.duckdb", read_only=True)

def show(title, sql):
    print("\n" + title)
    for r in con.execute(sql).fetchall():
        print("  ", r)

show("tables in dw", """
    SELECT table_name, table_type FROM information_schema.tables
    WHERE table_schema = 'dw' ORDER BY 1""")

show("row counts (expected 86 / 7 / 35 / 732)", """
    SELECT 'dim_account', COUNT(*) FROM dw.dim_account
    UNION ALL SELECT 'dim_product', COUNT(*) FROM dw.dim_product
    UNION ALL SELECT 'dim_sales_agent', COUNT(*) FROM dw.dim_sales_agent
    UNION ALL SELECT 'dim_date', COUNT(*) FROM dw.dim_date""")

show("unknown members", """
    SELECT 'dim_account', account_key, account_name FROM dw.dim_account WHERE account_key = -1
    UNION ALL SELECT 'dim_date', date_key, month_name FROM dw.dim_date WHERE date_key = -1""")

show("date range (expected 2016-01-01 .. 2017-12-31)", """
    SELECT MIN(full_date), MAX(full_date) FROM dw.dim_date""")

show("sample dim_date row", """
    SELECT * FROM dw.dim_date WHERE date_key = 20170315""")

show("sample dim_sales_agent rows", """
    SELECT * FROM dw.dim_sales_agent ORDER BY sales_agent_key LIMIT 3""")