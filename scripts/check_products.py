import duckdb

con = duckdb.connect()
con.execute("CREATE VIEW products AS SELECT * FROM read_csv_auto('data/raw/products.csv', header=true)")
con.execute("CREATE VIEW sales_pipeline AS SELECT * FROM read_csv_auto('data/raw/sales_pipeline.csv', header=true)")

print("products.csv:")
for r in con.execute("SELECT product, series, sales_price FROM products ORDER BY product").fetchall():
    print("  ", r)

print("\nsales_pipeline.product (count per value):")
for r in con.execute("""
    SELECT product, COUNT(*) AS n,
        product IN (SELECT product FROM products) AS exists_in_products
    FROM sales_pipeline GROUP BY product ORDER BY product
""").fetchall():
    print("  ", r)