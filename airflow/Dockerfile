FROM astrocrpublic.azurecr.io/runtime:3.3-8


# dbt gets its own virtual environment so its dependencies never clash with Airflow's
RUN python -m venv /usr/local/airflow/dbt_venv && \
    /usr/local/airflow/dbt_venv/bin/pip install --no-cache-dir \
    dbt-core==1.12.5 dbt-duckdb==1.11.0 duckdb==1.5.6