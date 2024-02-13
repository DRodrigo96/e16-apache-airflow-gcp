# storage_dag.py
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
from airflow.providers.google.cloud.operators.gcs import GCSListObjectsOperator
from airflow.providers.google.cloud.operators.gcs import GCSDeleteObjectsOperator
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.utils.task_group import TaskGroup
# --------------------------------------------------

# [NOTE] airflow variables
# --------------------------------------------------
GCP_GCS_BUCKET = Variable.get(key='GCP_DATA_BUCKET', default_var=None, deserialize_json=False)

# [NOTE] inner variables
# --------------------------------------------------
UUID_CODE = str(uuid.uuid1())
TODAY = pendulum.today('America/Lima')

# [NOTE] inner functions
# --------------------------------------------------
def copy_gcs_items(gcp_conn_id: str, gcp_gcs_bucket: str, prefix: str, **kwargs) -> None:
    ti_operation_uuid = kwargs['ti'].xcom_pull('operation_uuid')
    ti_list_bucket_items = kwargs['ti'].xcom_pull('gcs_bucket_objects')
    
    for item in ti_list_bucket_items:
        origin = f'gs://{gcp_gcs_bucket}/{item}'
        print('origin:', origin)
        
        destination = f'gs://{gcp_gcs_bucket}/historic/{ti_operation_uuid}/{item.replace(prefix, "")}'
        print('destination:', destination)
        
        GCSHook(gcp_conn_id=gcp_conn_id).copy(
            source_bucket=gcp_gcs_bucket,
            source_object=item,
            destination_object=destination.replace(f'gs://{gcp_gcs_bucket}/', '')
        )
    return ti_list_bucket_items

# [NOTE] DAG definition
# --------------------------------------------------
DAG_KWARGS = {
    'dag_id': 'm3_a1_gcp',
    'schedule_interval': pendulum.duration(days=2).as_timedelta(),
    'catchup': False,
    'user_defined_macros': {
        'gcp_gcs_bucket': GCP_GCS_BUCKET,
        'gcp_gcs_src_prefix': 'current/process/',
        'gcp_gcs_export_prefix': 'queries/data/',
        'gcp_gcs_filtered': '.csv',
        'exec_date': TODAY
    },
    'default_args': {'owner': 'FName Lname', 'start_date': TODAY.add(days=-1)}
}

with DAG(**DAG_KWARGS) as dag:
    
    operation_uuid = PythonOperator(
        task_id='operation_uuid',
        python_callable=lambda: UUID_CODE
    )
    
    gcs_bucket_objects = GCSListObjectsOperator(
        task_id='gcs_bucket_objects',
        bucket='{{ gcp_gcs_bucket }}',
        prefix='{{ gcp_gcs_src_prefix }}',
        delimiter='{{ gcp_gcs_filtered }}',
        gcp_conn_id='google_cloud_default',
        do_xcom_push=True
    )
    
    with TaskGroup(group_id='gcs_move_objects') as gcs_move_objects:
        copy_items = PythonOperator(
            task_id=f'copy_items',
            python_callable=copy_gcs_items,
            op_kwargs={
                'gcp_conn_id': '{{ conn.google_cloud_default }}',
                'gcp_gcs_bucket': '{{ gcp_gcs_bucket }}',
                'prefix': '{{ gcp_gcs_src_prefix }}'
            }
        )
        
        # [NOTE] keep section commented for multiple executions (do not deleted bucket objects)
        # drop_items = GCSDeleteObjectsOperator(
        #     task_id='drop_items',
        #     bucket_name='{{ gcp_gcs_bucket }}',
        #     objects=copy_items.output,
        #     gcp_conn_id='google_cloud_default',
        # )
        # copy_items >> drop_items
    
    with TaskGroup(group_id='gcs_export_objects') as gcs_export_objects:
        export_objects = GCSListObjectsOperator(
            task_id='export_objects',
            bucket='{{ gcp_gcs_bucket }}',
            prefix='{{ gcp_gcs_export_prefix }}',
            delimiter='{{ gcp_gcs_filtered }}',
            gcp_conn_id='google_cloud_default',
            do_xcom_push=True
        )
    
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
operation_uuid >> gcs_bucket_objects >> gcs_move_objects >> gcs_export_objects >> bash_task
