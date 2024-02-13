# bigquery_dag.py
# https://cloud.google.com/bigquery/docs/reference/rest/v2/jobs
# https://cloud.google.com/bigquery/docs/reference/rest/v2/jobs/insert
# https://cloud.google.com/bigquery/docs/reference/rest/v2/Job
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
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
# --------------------------------------------------

# [NOTE] airflow variables
# --------------------------------------------------
GCP_PROJECT_ID = Variable.get(key='GCP_PROJECT_ID', default_var=None, deserialize_json=False)
GCP_DATA_BUCKET = Variable.get(key='GCP_DATA_BUCKET', default_var=None, deserialize_json=False)

# [NOTE] inner variables
# --------------------------------------------------
UUID_CODE = str(uuid.uuid4())
TODAY = pendulum.today('America/Lima')
GCP_BIGQUERY_SQL = 'gs://{}/queries/scripts/bigquery-query.txt'.format(GCP_DATA_BUCKET)
GCP_INPUT_DATASET = '{}.input_dataset'.format(GCP_PROJECT_ID)
GCP_OUTPUT_DATASET = '{}.output_dataset'.format(GCP_PROJECT_ID)

# [NOTE] inner functions
# --------------------------------------------------
def read_gcs_txtquery(gcp_conn_id: str, gcp_gcs_querypath: str, created_table: str) -> str:
    gcspath_splits = gcp_gcs_querypath.replace('gs://', '').split('/')
    bucket_name, object_key = gcspath_splits[0], '/'.join(gcspath_splits[1:])
    content = GCSHook(gcp_conn_id=gcp_conn_id).download(
        bucket_name=bucket_name, object_name=object_key, filename=None
    )
    print(completed_query := content.decode('utf-8').replace('%CREATED_TABLE%', created_table))
    return completed_query

# [NOTE] DAG definition
# --------------------------------------------------
DAG_KWARGS = {
    'dag_id': 'm3_a3_gcp',
    'schedule_interval': '@weekly',
    'catchup': False,
    'user_defined_macros': {
        'gcp_project_id': GCP_PROJECT_ID,
        'gcp_input_dataset': GCP_INPUT_DATASET,
        'gcp_data_bucket': GCP_DATA_BUCKET,
        'gcp_bigquery_sql': GCP_BIGQUERY_SQL,
        'gcp_output_dataset': GCP_OUTPUT_DATASET,
        'exec_date': TODAY
    },
    'render_template_as_native_obj': True,
    'default_args': {'owner': 'FName Lname', 'start_date': TODAY.add(days=-1)}
}

with DAG(**DAG_KWARGS) as dag:
    
    operation_uuid = PythonOperator(
        task_id='operation_uuid',
        python_callable=lambda: UUID_CODE
    )
    
    imported_paths = '{{ ti.xcom_pull(task_ids="gcs_export_objects.export_objects", dag_id="m3_a1_gcp", include_prior_dates=True) }}'
    gcp_make_bigquery_table = GCSToBigQueryOperator(
        task_id='gcp_make_bigquery_table',
        bucket='{{ gcp_data_bucket }}',
        source_objects=imported_paths,
        destination_project_dataset_table='{{ gcp_input_dataset }}.{{ ti.xcom_pull("operation_uuid") }}',
        source_format='CSV',
        schema_fields=[
            {'name': 'id'          , 'type': 'INTEGER' , 'mode': 'NULLABLE'},
            {'name': 'year'        , 'type': 'INTEGER' , 'mode': 'NULLABLE'},
            {'name': 'area'        , 'type': 'STRING'  , 'mode': 'NULLABLE'},
            {'name': 'cod_product' , 'type': 'INTEGER' , 'mode': 'NULLABLE'},
            {'name': 'quant'       , 'type': 'INTEGER' , 'mode': 'NULLABLE'},
            {'name': 'uprice_usd'  , 'type': 'INTEGER' , 'mode': 'NULLABLE'},
            {'name': 'total_inc'   , 'type': 'INTEGER' , 'mode': 'NULLABLE'}
        ],
        create_disposition='CREATE_NEVER',
        skip_leading_rows=0,
        write_disposition='WRITE_EMPTY',
        field_delimiter=';',
        max_bad_records=0,
        quote_character='"',
        ignore_unknown_values=True,
        allow_quoted_newlines=True,
        allow_jagged_rows=False,
        encoding='UTF-8',
        external_table=True,
        location='US',
        labels={'airflow': 'true', 'dev': 'true'},
        description='temp-table'
    )
    
    retrieve_bigquery_query = PythonOperator(
        task_id='retrieve_bigquery_query',
        python_callable=read_gcs_txtquery,
        op_kwargs={
            'gcp_conn_id': 'google_cloud_default',
            'gcp_gcs_querypath': '{{ gcp_bigquery_sql }}',
            'created_table': '{{ gcp_input_dataset }}.{{ ti.xcom_pull("operation_uuid") }}'
        }
    )
    
    gcp_bigquery_job = BigQueryInsertJobOperator(
        task_id='gcp_bigquery_job',
        configuration={
            'query': {
                'query': '{{ ti.xcom_pull("retrieve_bigquery_query") }}',
                'destinationTable': {
                    'projectId': '{{ gcp_output_dataset.split(".")[0] }}',
                    'datasetId': '{{ gcp_output_dataset.split(".")[1] }}',
                    'tableId': '{{ ti.xcom_pull("operation_uuid") }}'
                },
                'createDisposition': 'CREATE_IF_NEEDED',
                'writeDisposition': 'WRITE_TRUNCATE',
                'useQueryCache': True,
                'maximumBytesBilled': int(1e9),
                'useLegacySql': False
            },
            'dryRun': False,
            'labels': {'airflow': 'true', 'dev': 'true'}
        },
        project_id=GCP_PROJECT_ID,
        gcp_conn_id='google_cloud_default'
    )
    
    bash_task = BashOperator(
        task_id='bash_task',
        bash_command='echo "---> Bash task en Airflow $CODIGO. Fecha de hoy: $TODAY..."',
        env={
            'TODAY': '{{ exec_date.to_datetime_string() }}',
            'CODIGO': '{{ ti.xcom_pull("operation_uuid") }}'
        },
        trigger_rule='all_success'
    )

# [NOTE] dependencies
# --------------------------------------------------
operation_uuid >> gcp_make_bigquery_table >> retrieve_bigquery_query >> gcp_bigquery_job >> bash_task
