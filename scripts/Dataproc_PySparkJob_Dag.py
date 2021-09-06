


from airflow import DAG

from airflow.utils.dates import days_ago

from airflow.providers.google.cloud.operators.dataproc import DataprocCreateClusterOperator
from airflow.providers.google.cloud.operators.dataproc import DataprocSubmitPySparkJobOperator
from airflow.providers.google.cloud.operators.dataproc import DataprocSubmitJobOperator
from airflow.providers.google.cloud.operators.dataproc import DataprocDeleteClusterOperator

from airflow.operators.python import BranchPythonOperator

from random import uniform

from airflow.utils.task_group import TaskGroup


default_args = {
    'owner': 'David Sanchez',
    'start_date': days_ago(1)
}

dag_args = {
    'dag_id': '10_dataproc_delete',
    'schedule_interval': '@weekly',
    'catchup': False,
    'default_args': default_args
}

# Python Operator
pyspark_files = ('avg_quant', 'avg_tincome', 'avg_uprice')

def number_task(min_num=None, max_num=None):
    #return 'par_task' if round(uniform(min_num, max_num)) % 2 == 0 else 'impar_task'
    #if round(uniform(min_num, max_num)) % 2 == 0:
    if 5 % 2 == 0:
        return 'impar_task'
    else:
        return [f'par_task.{x}' for x in pyspark_files]


with DAG(**dag_args) as dag:

# TASK 1: CREATE CLUSTER --> OPERATOR
    create_cluster = DataprocCreateClusterOperator(
        task_id='create_cluster',
        project_id='regal-oasis-291423',
        cluster_name='spark-cluster-123',
        num_workers=2,
        storage_bucket='spark-bucket-987',
        region='us-east1',
    )


# TASK 2: IDENTIFICAR NÚMERO --> OPERATOR (PYTHON)
    iden_number = BranchPythonOperator(
        task_id='iden_number',
        python_callable=number_task,
        op_kwargs={
            'min_num': 1, 
            'max_num': 100
        },
        do_xcom_push=False
    )


# TASK 3: PYSPARK JOBS

    ## TASK 3.1: EJECUTAR PYSPARK (IMPAR) --> OPERATOR
    pyspark_job = {
        'reference': {
            'project_id': 'regal-oasis-291423',
            'job_id': '10ad560c_mainjob_std'
        },
        'placement': {
            'cluster_name': 'spark-cluster-123'
        },
        'labels': {
            'airflow-version': 'v2-1-0'
        },
        'pyspark_job': {
            'jar_file_uris': ['gs://spark-lib/bigquery/spark-bigquery-latest_2.12.jar'],
            'main_python_file_uri': 'gs://spark-bucket-987/pyspark/impar_task/vars_stdp.py'
        }
    }

    impar_task = DataprocSubmitJobOperator(
        task_id='impar_task',
        project_id='regal-oasis-291423',
        location='us-east1',
        job=pyspark_job,
        gcp_conn_id='google_cloud_default'
    )

    ## TASK 3.2: EJECUTAR PYSPARK (PAR) --> OPERATOR
    with TaskGroup(group_id='par_task') as par_task:

        #pyspark_files = ('avg_quant', 'avg_tincome', 'avg_uprice')

        for subtask in pyspark_files:
            subjob = {
                'reference': {
                    'project_id': 'regal-oasis-291423',
                    'job_id': f'b1b63d0a_subjob_{subtask}'
                },
                'placement': {
                    'cluster_name': 'spark-cluster-123'
                },
                'labels': {
                    'airflow-version': 'v2-1-0'
                },
                'pyspark_job': {
                    'jar_file_uris': ['gs://spark-lib/bigquery/spark-bigquery-latest_2.12.jar'],
                    'main_python_file_uri': f'gs://spark-bucket-987/pyspark/par_task/{subtask}.py'
                }
            }

            DataprocSubmitJobOperator(
                task_id=subtask,
                project_id='regal-oasis-291423',
                location='us-east1',
                job=subjob,
                gcp_conn_id='google_cloud_default'
            )             


# TASK 4: DELETE CLUSTER --> OPERATOR
    delete_cluster = DataprocDeleteClusterOperator(
        task_id='delete_cluster',
        project_id='regal-oasis-291423',
        cluster_name='spark-cluster-123',
        trigger_rule='all_done',
        region='us-east1'
    )



# Dependencies
(
    create_cluster 
    >> iden_number 
    >> [ impar_task , par_task ]
    >> delete_cluster
)