from datetime import datetime
import json
from pandas import json_normalize

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import SimpleHttpOperator, HttpOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

def _process_user(ti):
    user = ti.xcom_pull(task_ids="extract_user")
    user = user['results'][0]
    process_user = json_normalize({
        'firstname': user['name']['first'],
        'lastname': user['name']['last'],
        'country': user['location']['country'],
        'username': user['login']['username'],
        'password': user['login']['password'],
        'email': user['email']
    })
    process_user.to_csv('/tmp/processed_user.csv', index=None, header=False)


def _store_user():
    hook = PostgresHook(postgres_conn_id="postgres")
    hook.copy_expert(
        sql="COPY users FROM STDIN WITH DELIMITER as ','",
        filename='/tmp/processed_user.csv'
    )


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

    is_api_available = HttpSensor(
        task_id="is_api_available",
        http_conn_id="user_api",
        endpoint="api/",
    )

    extract_user = HttpOperator(
        task_id="extract_user",
        http_conn_id="user_api",
        endpoint="api/",
        method="GET",
        response_filter=lambda response: json.loads(response.text),
        log_response=True,
    )

    process_user = PythonOperator(
        task_id="process_user",
        python_callable=_process_user
    )

    store_user = PythonOperator(
        task_id="store_user",
        python_callable=_store_user
    )

    create_table >> is_api_available >> extract_user >> process_user >> store_user