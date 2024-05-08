from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from datetime import datetime, timedelta
import os

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2022, 8, 9),
    'end_date': datetime(2022, 8, 10),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
    'catchup': True
}

dag = DAG(
    'upload_sales_csv_to_gcs',
    default_args=default_args,
    description='Upload all CSV files from a directory to GCS',
    schedule_interval='@daily',  # Щоденний запуск о 01:00
    catchup=True
)


def upload_files(**kwargs):
    ds = kwargs['ds']  # Отримуємо дату запуску з контексту
    execution_date = datetime.strptime(ds, '%Y-%m-%d')

    # Перевірка, що дата виконання не пізніша за 'end_date'
    if execution_date > default_args['end_date']:
        print(f"Skipping execution for {ds}, as it is beyond the end_date.")
        return

    local_directory = f'/file_storage/csv/{ds}/'
    bucket_name = 'robot-dreams-hw-bucket07052024'
    year, month, day = ds.split('-')
    destination_blob_path = f'src1/sales/v1/{year}/{month}/{day}/'

    if os.path.exists(local_directory):
        files = [f for f in os.listdir(local_directory) if f.endswith('.csv')]
        for file in files:
            task_id = f'upload_{file.replace(".", "_").replace("-", "_")}_to_gcs'
            upload_task = LocalFilesystemToGCSOperator(
                task_id=task_id,
                src=os.path.join(local_directory, file),
                dst=destination_blob_path + file,
                bucket=bucket_name,
                dag=dag
            )
            upload_task.execute(kwargs)


upload_files_task = PythonOperator(
    task_id='upload_files',
    python_callable=upload_files,
    provide_context=True,
    dag=dag,
)