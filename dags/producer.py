from airflow import DAG, Dataset
from airflow.decorators import task

from datetime import datetime

file = Dataset('/tmp/file.txt')
file_2 = Dataset('/tmp/file_2.txt')

with DAG(
    dag_id='producer',
    schedule="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False
):
    
    @task(outlets=[file]) 
    def update_dataset():
        with open(file.uri, "a+") as f:
            f.write('producer update')
    
    @task(outlets=[file_2]) 
    def update_dataset_2():
        with open(file_2.uri, "a+") as f:
            f.write('producer update')
    
    update_dataset() >> update_dataset_2()