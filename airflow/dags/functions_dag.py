# functions_dag.py
# ==================================================
# standard
import uuid, json
# requirements
import pendulum
# airflow
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.google.cloud.operators.functions import CloudFunctionInvokeFunctionOperator
# --------------------------------------------------

# [NOTE] inner variables
# --------------------------------------------------
UUID_CODE = str(uuid.uuid4())
TODAY = pendulum.today('America/Lima')

# [NOTE] DAG definition
# --------------------------------------------------
DAG_KWARGS = {
    'dag_id': 'm3_a2_gcp',
    'schedule_interval': pendulum.duration(days=2).as_timedelta(),
    'catchup': False,
    'user_defined_macros': {
        'gcp_gcloud_func': 'airflow-function',
        'gcp_gcfunc_location': 'us-central1',
        'exec_date': TODAY
    },
    'default_args': {'owner': 'FName Lname', 'start_date': TODAY.add(days=-1)}
}

with DAG(**DAG_KWARGS) as dag:
    
    operation_uuid = PythonOperator(
        task_id='operation_uuid',
        python_callable=lambda: UUID_CODE
    )
    
    gcp_invoke_gcfunc = CloudFunctionInvokeFunctionOperator(
        task_id='invoke_gcloud_func',
        function_id='{{ gcp_gcloud_func }}',
        project_id=None,
        input_data={
            'data': json.dumps({
                'run': True,
                'external': True,
                'url': 'https://api.worldbank.org/v2/country/per/indicator/DPANUSSPB?date=YTD:2013&format=json'
            })
        },
        location='{{ gcp_gcfunc_location }}',
        gcp_conn_id='google_cloud_default'
    )
    
    print_response = PythonOperator(
        task_id='print_response',
        python_callable=lambda res: res,
        op_kwargs={
            'res': '{{ ti.xcom_pull("invoke_gcloud_func") }}'
        }
    )
    
    bash_task = BashOperator(
        task_id='bash_task',
        bash_command='echo "---> Bash task en Airflow $CODIGO. Fecha de hoy: $TODAY..."',
        env={
            'TODAY': '{{ exec_date }}',
            'CODIGO': '{{ ti.xcom_pull("operation_uuid") }}'
        },
        trigger_rule='all_done'
    )

# [NOTE] dependencies
# --------------------------------------------------
operation_uuid >> gcp_invoke_gcfunc >> print_response >> bash_task
