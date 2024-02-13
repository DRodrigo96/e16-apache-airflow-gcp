# dataproc_dag.py
# https://cloud.google.com/dataproc-serverless/docs/reference/rest/v1/projects.locations.batches
# https://cloud.google.com/python/docs/reference/dataproc/latest/google.cloud.dataproc_v1.types.Batch
# https://cloud.google.com/dataproc-serverless/docs/concepts/network
# ==================================================
# standard
import uuid
# requirements
import pendulum
# airflow
from airflow import DAG
from airflow.models.variable import Variable
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.google.cloud.operators.dataproc import DataprocCreateBatchOperator
from airflow.providers.google.cloud.operators.dataproc import DataprocDeleteBatchOperator
from airflow.utils.task_group import TaskGroup
# --------------------------------------------------

# [NOTE] airflow variables
# --------------------------------------------------
GCP_PROJECT_ID = Variable.get(key='GCP_PROJECT_ID', default_var=None, deserialize_json=False)
GCP_BUCKET_NAME = Variable.get(key='GCP_DATA_BUCKET', default_var=None, deserialize_json=False)

# [NOTE] inner variables
# --------------------------------------------------
UUID_CODE = str(uuid.uuid4())
TODAY = pendulum.today('America/Lima')
SERVICE_ACCOUNT = 'inner-gcp-sa@{}.iam.gserviceaccount.com'.format(GCP_PROJECT_ID)
PYSPARK_PATHS = [
    {'uri': 'gs://{}/pyspark/src/script_a.py'.format(GCP_BUCKET_NAME), 'args': ['value1', 'value2']},
    {'uri': 'gs://{}/pyspark/src/script_b.py'.format(GCP_BUCKET_NAME), 'args': [GCP_BUCKET_NAME, '{{ ti.xcom_pull("operation_uuid") }}']}
]

# [NOTE] DAG definition
# --------------------------------------------------
DAG_KWARGS = {
    'dag_id': 'm3_a4_gcp',
    'schedule_interval': '@weekly',
    'catchup': False,
    'user_defined_macros': {
        'gcp_project_id': GCP_PROJECT_ID,
        'gcp_dataproc_region': 'us-central1',
        'gcp_jarfile_path': 'gs://spark-lib/bigquery/spark-3.5-bigquery-0.36.1.jar',
        'gcp_dataproc_sacc': SERVICE_ACCOUNT,
        'gcp_dataproc_network': 'airflow-network',
        'gcp_dataproc_subnetwork': 'airflow-subnetwork',
        'exec_date': TODAY
    },
    'default_args': {'owner': 'FName Lname', 'start_date': TODAY.add(days=-1)}
}

with DAG(**DAG_KWARGS) as dag:
    
    operation_uuid = PythonOperator(
        task_id='operation_uuid',
        python_callable=lambda: UUID_CODE
    )
    
    with TaskGroup(group_id='dataproc_batch_jobs') as dataproc_batch_jobs:
        for i, job_dict in enumerate(PYSPARK_PATHS):
            num = i + 1
            dataproc_create_batch = DataprocCreateBatchOperator(
                task_id=f'dataproc_create_batch_{num}',
                batch_id='{{ ti.xcom_pull("operation_uuid") }}-%s'%(num),
                batch={
                    'pyspark_batch': {
                        'main_python_file_uri': job_dict['uri'],
                        'args': job_dict['args'],
                        'jar_file_uris': ['{{ gcp_jarfile_path }}'],
                    },
                    'runtime_config': {
                        'properties': {
                            'spark.executor.instances': '2',
                            'spark.driver.cores': '4',
                            'spark.executor.cores': '4'
                        }
                    },
                    'environment_config': {
                        'execution_config': {
                            'service_account': '{{ gcp_dataproc_sacc }}',
                            'network_uri': '{{ gcp_dataproc_network }}',
                            'subnetwork_uri': '{{ gcp_dataproc_subnetwork }}'
                        }
                    },
                    'labels': {
                        'airflow': 'true',
                        'dev': 'true'
                    }
                },
                retry=None,
                project_id='{{ gcp_project_id }}',
                region='{{ gcp_dataproc_region }}',
                gcp_conn_id='google_cloud_default'
            )
            retrieve_job_id = PythonOperator(
                task_id=f'retrieve_job_id_{num}',
                python_callable=lambda item: item['name'].split('/')[-1],
                op_kwargs={
                    'item': dataproc_create_batch.output
                }
            )
            
            # [NOTE] deletes details from execution batch at GCP. 
            # dataproc_drop_batch = DataprocDeleteBatchOperator(
            #     task_id=f'dataproc_drop_batch_{num}',
            #     batch_id=retrieve_job_id.output,
            #     region='{{ gcp_dataproc_region }}',
            #     project_id='{{ gcp_project_id }}',
            #     gcp_conn_id='google_cloud_default'
            # )
        dataproc_create_batch >> retrieve_job_id # >> dataproc_drop_batch
    
    bash_task = BashOperator(
        task_id='bash_task',
        bash_command='echo "---> Bash task en Airflow $CODIGO. Fecha de hoy: $TODAY..."',
        env={
            'TODAY': '{{ exec_date }}',
            'CODIGO': '{{ ti.xcom_pull("operation_uuid") }}'
        },
        trigger_rule='all_success'
    )

# [NOTE] dependencies
# --------------------------------------------------
operation_uuid >> dataproc_batch_jobs >> bash_task
