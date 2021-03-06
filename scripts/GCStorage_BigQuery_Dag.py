
# AIRFLOW MODULES
from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.models import Variable
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryExecuteQueryOperator
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.operators.python import PythonOperator

# VARIABLES
PROJECT = Variable.get('project')
BUCKET = Variable.get('bucket')
BACKUP_BUCKET = Variable.get('backup_bucket')
DATASET = Variable.get('dataset')
ORIG_TABLE = Variable.get('orig_table')

# ARGUMENTS
default_args = {
    'owner': 'David Sanchez',
    'start_date': days_ago(1)
}

dag_args = {
    'dag_id': 'gcs_bigquery',
    'schedule_interval': '@daily', 
    'catchup': False, 
    'max_active_runs': 1,
    'user_defined_macros': {
        'project': PROJECT,
        'dataset': DATASET,
        'orig_table': ORIG_TABLE,
        'dest_table': '{}_resume'.format(ORIG_TABLE),
        'bucket': BUCKET,
        'backup_bucket': BACKUP_BUCKET
    },
    'default_args': default_args
}

# HOOKS
def list_objects(bucket=None):
    return GCSHook().list(bucket)

def move_objects(source_bucket=None, destination_bucket=None, prefix=None, **kwargs):
    storage_objects = kwargs['ti'].xcom_pull(task_ids='list_files')

    for ob in storage_objects:
        dest_ob = ob

        if prefix:
            dest_ob = f'{prefix}/{ob}'

        GCSHook().copy(source_bucket, ob, destination_bucket, dest_ob)
        GCSHook().delete(source_bucket, ob)

# DAG DEFINITION
with DAG(**dag_args) as dag:

    # TASK
    list_files = PythonOperator(
        task_id='list_files',
        python_callable=list_objects,
        op_kwargs={'bucket': '{{ bucket }}'}
    )

    # TASK
    cargar_datos = GCSToBigQueryOperator(
        task_id='cargar_datos',
        bucket='{{ bucket }}',
        source_objects=['*'],
        source_format='CSV',
        skip_leading_rows=1,
        field_delimiter=';',
        destination_project_dataset_table='{{ project }}.{{ dataset }}.{{ orig_table }}',
        create_disposition='CREATE_IF_NEEDED',
        write_disposition='WRITE_APPEND',
        bigquery_conn_id='google_cloud_default',
        google_cloud_storage_conn_id='google_cloud_default'
    )

    # TASK
    query = (
        '''
        SELECT
            `year`,
            `area`,
            ROUND(AVG(`total_inc`), 4) AS avg_income
        FROM
            `{{ project }}.{{ dataset }}.{{ orig_table }}`
        GROUP BY
            `year`,
            `area`
        ORDER BY
            `area` ASC
        '''
    )

    tabla_resumen = BigQueryExecuteQueryOperator(
        task_id='tabla_resumen',
        sql=query,
        destination_dataset_table='{{ project }}.{{ dataset }}.{{ dest_table }}',
        write_disposition='WRITE_TRUNCATE',
        create_disposition='CREATE_IF_NEEDED',
        use_legacy_sql=False,
        location='us-east1',
        bigquery_conn_id='google_cloud_default'
    )

    # TASK
    move_files = PythonOperator(
        task_id='move_files',
        python_callable=move_objects,
        op_kwargs={
            'source_bucket': '{{ bucket }}', 
            'destination_bucket': '{{ backup_bucket }}',
            'prefix': '{{ ts_nodash }}'
        },
        provide_context=True
    )

# DEPENDENCIES
list_files >> cargar_datos >> tabla_resumen >> move_files
