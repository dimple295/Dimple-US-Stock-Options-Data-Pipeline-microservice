from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.http.operators.http import HttpOperator
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
import logging
import pendulum

# Set timezone to US Eastern Time (ET)
local_tz = pendulum.timezone("America/New_York")

# Centralized configuration
HTTP_CONN_ID = "file_writer_service"

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

def log_response(**context):
    """Log the API response for a given task."""
    task_id = context["task"].task_id.replace("log_", "write_")
    response = context["task_instance"].xcom_pull(task_ids=task_id)
    try:
        logging.info(f"API Response for {task_id}: {response}")
    except Exception as e:
        logging.error(f"Failed to log response for {task_id}: {str(e)}")
        raise

def create_http_task(task_id, endpoint, dag):
    """Factory function to create HttpOperator tasks."""
    return HttpOperator(
        task_id=task_id,
        http_conn_id=HTTP_CONN_ID,
        endpoint=f"api/{endpoint}/",
        method="POST",
        headers={"Content-Type": "application/json"},
        data="{}",
        response_check=lambda response: (logging.info(f"Status: {response.status_code}, Body: {response.text}"), response.status_code in [200, 202])[1],
        dag=dag,
    )

def create_log_task(task_id, dag):
    """Factory function to create PythonOperator log tasks."""
    return PythonOperator(
        task_id=task_id,
        python_callable=log_response,
        dag=dag,
    )

with DAG(
    "store_last_15min_data",
    default_args=default_args,
    description="DAG to write stock data every 15 minutes during market hours",
    schedule_interval="30 17 * * 1-5",
    start_date=datetime(2025, 6, 20, tzinfo=local_tz),
    catchup=False,
) as dag_15min:
    store_last_15min_data = create_http_task("store_last_15min_data", "store_last_15min_data", dag_15min)
    log_last_15min_data = create_log_task("log_last_15min_data", dag_15min)
    store_last_15min_data >> log_last_15min_data

with DAG(
    "store_historical_data",
    default_args=default_args,
    description="DAG to write historical stock data once",
    schedule="@once",
    start_date=datetime(2025, 7, 19, tzinfo=local_tz),
    catchup=False,
) as dag_historical:
    store_historical_data = create_http_task("store_historical_data", "store_historical_data", dag_historical)
    log_historical_data = create_log_task("log_historical_data", dag_historical)
    store_historical_data >> log_historical_data

with DAG(
    "store_stock_daily",
    default_args=default_args,
    description="DAG for daily stock and options data write after market close",
    schedule_interval="30 17 * * 1-5",
    start_date=datetime(2025, 7, 19, tzinfo=local_tz),
    catchup=False,
) as dag_daily:
    start = DummyOperator(task_id="start")
    store_each_day_data = create_http_task("store_each_day_data", "store_each_day_data", dag_daily)
    store_option_data = create_http_task("store_option_data", "store_option_data", dag_daily)
    log_each_day_data = create_log_task("log_each_day_data", dag_daily)
    log_option_data = create_log_task("log_option_data", dag_daily)

    start >> [store_each_day_data, store_option_data]
    store_each_day_data >> log_each_day_data
    store_option_data >> log_option_data