from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2022, 8, 8),
    'end_date': datetime(2022, 8, 13),
    'email': ['your-email@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
    'max_active_runs': 1
}

dag = DAG(
    dag_id='process_sales',
    default_args=default_args,
    description='DAG for processing sales data',
    schedule_interval='0 1 * * *',  # Запускається о 1 ночі UTC щодня
    catchup=True, #при True запускається й за попередні періоди
)

# Таска для отримання даних з API
t1 = BashOperator(
    task_id='extract_data_from_api',
    bash_command="""
    response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "http://host.docker.internal:8081/sales" -H "Content-Type: application/json" -d '{"raw_dir":"file_storage/raw/sales/{{ ds }}","date":"{{ ds }}"}')
    if [ $response -ne 201 ]; then
        echo "Request failed with status code $response"
        exit 1
    fi
    """,
    dag=dag,
)

# Таска для конвертації в Avro
t2 = BashOperator(
    task_id='convert_to_avro',
    bash_command="""
    response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "http://host.docker.internal:8082/convert_to_avro" -H "Content-Type: application/json" -d '{"raw_dir":"file_storage/raw/sales/{{ ds }}","stg_dir":"file_storage/stg/sales/{{ ds }}"}')
    if [ $response -ne 201 ]; then
        echo "Request failed with status code $response"
        exit 1
    fi
    """,
    dag=dag,
)


t1 >> t2