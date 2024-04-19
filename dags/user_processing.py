from datetime import datetime

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator

with DAG(
    "user_processing",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
) as dag:
    
    create_table = PostgresOperator(
        task_id="create_table",
        postgres_conn_id="postgres",
        sql="""
            CREATE TABLE IF NOT EXISTS users (
                firstname text NOT NULL,
                lastname text NOT NULL,
                country text NOT NULL,
                username text NOT NULL,
                password text NOT NULL,
                email text NOT NULL
            );
        """,
    )
