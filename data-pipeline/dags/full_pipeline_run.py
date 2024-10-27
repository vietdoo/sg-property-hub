import airflow
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

dag = DAG(
    dag_id = "full_pipeline_run",
    default_args = {
        "owner": "etsu",
        "start_date": airflow.utils.dates.days_ago(1)
    },
    schedule_interval = "@daily"
)

start = PythonOperator(
    task_id="start",
    python_callable = lambda: print("Jobs started"),
    dag=dag
)

extract_to_bronze = SparkSubmitOperator(
    task_id="extract1",
    conn_id="spark-conn",
    application="spark/jobs/load_to_bronze.py",
    dag=dag
)

transform_to_silver = SparkSubmitOperator(
    task_id="transform1",
    conn_id="spark-conn",
    application="spark/jobs/transform_to_silver.py",
    packages="org.apache.hadoop:hadoop-aws:3.2.2",
    dag=dag
)

load_to_gold = SparkSubmitOperator(
    task_id="load1",
    conn_id="spark-conn",
    application="spark/jobs/load_to_gold.py",
    packages="org.apache.hadoop:hadoop-aws:3.2.2",
    dag=dag
)

load_to_postgre=SparkSubmitOperator(
    task_id="load2",
    conn_id="spark-conn",
    application="spark/jobs/load_to_postgre.py",
    packages="org.apache.hadoop:hadoop-aws:3.2.2,org.postgresql:postgresql:42.2.6",
    dag=dag
)

load_to_postgre_db=SparkSubmitOperator(
    task_id="load3",
    conn_id="spark-conn",
    application="spark/jobs/load_to_postgre_db.py",
    packages="org.apache.hadoop:hadoop-aws:3.2.2,org.postgresql:postgresql:42.2.6",
    dag=dag
)


end = PythonOperator(
    task_id="end",
    python_callable = lambda: print("Jobs completed successfully"),
    dag=dag
)

start >> extract_to_bronze >> transform_to_silver >> load_to_gold >>[load_to_postgre,load_to_postgre_db] >> end
