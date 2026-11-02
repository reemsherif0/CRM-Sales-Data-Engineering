import duckdb

con = duckdb.connect("warehouse/crm.duckdb", read_only=True)

def show(title, sql):
    print("\n" + title)
    for r in con.execute(sql).fetchall():
        print("  ", r)

show("1) fact rows (expected 8800)", "SELECT COUNT(*) FROM dw.fact_opportunities")

show("2) duplicate opportunity_id (expected 0)", """
    SELECT COUNT(*) FROM (
        SELECT opportunity_id FROM dw.fact_opportunities
        GROUP BY 1 HAVING COUNT(*) > 1)""")

show("3) NULL keys (expected all 0)", """
    SELECT COUNT(*) FILTER (WHERE account_key IS NULL),
        COUNT(*) FILTER (WHERE product_key IS NULL),
        COUNT(*) FILTER (WHERE sales_agent_key IS NULL),
        COUNT(*) FILTER (WHERE engage_date_key IS NULL),
        COUNT(*) FILTER (WHERE close_date_key IS NULL)
    FROM dw.fact_opportunities""")

show("4) Unknown member usage (expected 1425 / 500 / 2089)", """
    SELECT COUNT(*) FILTER (WHERE account_key = -1),
        COUNT(*) FILTER (WHERE engage_date_key = -1),
        COUNT(*) FILTER (WHERE close_date_key = -1)
    FROM dw.fact_opportunities""")

show("5) orphan keys (expected all 0)", """
    SELECT
        (SELECT COUNT(*) FROM dw.fact_opportunities WHERE account_key NOT IN (SELECT account_key FROM dw.dim_account)),
        (SELECT COUNT(*) FROM dw.fact_opportunities WHERE product_key NOT IN (SELECT product_key FROM dw.dim_product)),
        (SELECT COUNT(*) FROM dw.fact_opportunities WHERE sales_agent_key NOT IN (SELECT sales_agent_key FROM dw.dim_sales_agent)),
        (SELECT COUNT(*) FROM dw.fact_opportunities WHERE engage_date_key NOT IN (SELECT date_key FROM dw.dim_date)),
        (SELECT COUNT(*) FROM dw.fact_opportunities WHERE close_date_key NOT IN (SELECT date_key FROM dw.dim_date))""")

show("6) close_value total: fact vs staging (must be equal)", """
    SELECT (SELECT SUM(close_value) FROM dw.fact_opportunities),
        (SELECT SUM(close_value) FROM staging.stg_sales_pipeline)""")

show("7) deals and revenue per stage", """
    SELECT deal_stage, COUNT(*), SUM(close_value)
    FROM dw.fact_opportunities GROUP BY 1 ORDER BY 2 DESC""")

show("8) sample star-join: Won revenue per regional office", """
    SELECT s.regional_office, COUNT(*) AS deals, SUM(f.close_value) AS revenue
    FROM dw.fact_opportunities f
    JOIN dw.dim_sales_agent s USING (sales_agent_key)
    WHERE f.deal_stage = 'Won'
    GROUP BY 1 ORDER BY 3 DESC""")