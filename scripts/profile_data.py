import duckdb
from pathlib import Path

RAW = Path("data/raw")
con = duckdb.connect() 

for f in sorted(RAW.glob("*.csv")):
    print("=" * 80)
    print(f.name)
    con.execute(
        f"CREATE OR REPLACE TEMP VIEW t AS "
        f"SELECT * FROM read_csv_auto('{f.as_posix()}', header=true)"
    )

    rows = con.execute("SELECT COUNT(*) FROM t").fetchone()[0]
    distinct_rows = con.execute(
        "SELECT COUNT(*) FROM (SELECT DISTINCT * FROM t)"
    ).fetchone()[0]
    print(f"rows={rows}  fully_duplicated_rows={rows - distinct_rows}")

    print(f"{'column':<22}{'type':<12}{'nulls':>7}{'distinct':>10}   min .. max")
    for col in con.execute("DESCRIBE t").fetchall():
        name, dtype = col[0], col[1]
        q = f'"{name}"'
        nulls, distinct, mn, mx = con.execute(
            f"SELECT COUNT(*) FILTER (WHERE {q} IS NULL), "
            f"COUNT(DISTINCT {q}), MIN({q}), MAX({q}) FROM t"
        ).fetchone()
        print(f"{name:<22}{dtype:<12}{nulls:>7}{distinct:>10}   {mn} .. {mx}")

    if f.name == "data_dictionary.csv":
        print("\n--- full content ---")
        for r in con.execute("SELECT * FROM t").fetchall():
            print(r)