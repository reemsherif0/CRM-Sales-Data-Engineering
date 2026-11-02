from datetime import datetime
from pathlib import Path

from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import dag
from cosmos import DbtTaskGroup, ExecutionConfig, ProfileConfig, ProjectConfig, RenderConfig

AIRFLOW_HOME = Path("/usr/local/airflow")
DBT_PROJECT_PATH = AIRFLOW_HOME / "dbt_project"
DBT_EXECUTABLE = str(AIRFLOW_HOME / "dbt_venv" / "bin" / "dbt")
PYTHON = str(AIRFLOW_HOME / "dbt_venv" / "bin" / "python")
SCRIPTS = AIRFLOW_HOME / "scripts"

profile_config = ProfileConfig(
    profile_name="crm_dbt",
    target_name="dev",
    profiles_yml_filepath=DBT_PROJECT_PATH / "profiles.yml",
)


@dag(
    dag_id="crm_sales_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    # DuckDB allows a single writer, so only one task may touch crm.duckdb at a time
    max_active_tasks=1,
)
def crm_sales_pipeline():
    load_raw_data = BashOperator(
        task_id="load_raw_data",
        bash_command=f"{PYTHON} {SCRIPTS / 'load_raw.py'}",
    )

    dbt_transformations = DbtTaskGroup(
        group_id="dbt_transformations",
        project_config=ProjectConfig(dbt_project_path=DBT_PROJECT_PATH),
        profile_config=profile_config,
        execution_config=ExecutionConfig(dbt_executable_path=DBT_EXECUTABLE),
        # relationships tests span two models (child and parent). Without this they run
        # inside the first parent's test task, before the child model exists on a clean database.
        render_config=RenderConfig(should_detach_multiple_parents_tests=True),
    )

    validate_dw = BashOperator(
        task_id="validate_dw",
        bash_command=f"{PYTHON} {SCRIPTS / 'validate_dw.py'}",
    )

    load_raw_data >> dbt_transformations >> validate_dw


crm_sales_pipeline()