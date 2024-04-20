from airflow import DAG, Dataset
from airflow.decorators import task

from datetime import datetime

file = Dataset("/tmp/file.txt")
file_2 = Dataset("/tmp/file_2.txt")


with DAG(
    dag_id='consumer',
    schedule=[file, file_2],
    start_date=datetime(2024, 1, 1),
    catchup=False
):
    @task
    def read_dataset():
        with open(file.uri, "r") as f:
            print(f.read())

    read_dataset()