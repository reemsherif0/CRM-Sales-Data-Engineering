import duckdb

con = duckdb.connect("warehouse/crm.duckdb", read_only=True)

def show(title, sql):
    print("\n" + title)
    for r in con.execute(sql).fetchall():
        print("  ", r)

show("views in staging", """
    SELECT table_name, table_type FROM information_schema.tables
    WHERE table_schema = 'staging' ORDER BY 1""")

show("row counts", """
    SELECT 'stg_accounts', COUNT(*) FROM staging.stg_accounts
    UNION ALL SELECT 'stg_products', COUNT(*) FROM staging.stg_products
    UNION ALL SELECT 'stg_sales_teams', COUNT(*) FROM staging.stg_sales_teams
    UNION ALL SELECT 'stg_sales_pipeline', COUNT(*) FROM staging.stg_sales_pipeline""")

show("pipeline products not in stg_products (expected 0)", """
    SELECT COUNT(*) FROM staging.stg_sales_pipeline
    WHERE product_name NOT IN (SELECT product_name FROM staging.stg_products)""")

show("typo fixes (expected: technology, Philippines present; old spellings absent)", """
    SELECT 'technology', COUNT(*) FROM staging.stg_accounts WHERE sector = 'technology'
    UNION ALL SELECT 'technolgy', COUNT(*) FROM staging.stg_accounts WHERE sector = 'technolgy'
    UNION ALL SELECT 'Philippines', COUNT(*) FROM staging.stg_accounts WHERE office_location = 'Philippines'
    UNION ALL SELECT 'Philipines', COUNT(*) FROM staging.stg_accounts WHERE office_location = 'Philipines'""")