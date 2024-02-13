# GCP con Apache Airflow

## Description
4 ejercicios básicos que demuestran cómo podemos orquestar servicios de Google Cloud a través de [Apache Airflow](https://airflow.apache.org/).

En el repositorio se encuentran 4 [DAGs](./airflow/dags/):
1. `storage_dag.py`: ejercicio para realizar operaciones entre directorios en el servicio Goocle Cloud Storage.
2. `functions_dag.py`: ejercicio para realizar invocaciones de instancias de Cloud Functions desde Airflow.
3. `bigquery_dag.py`: ejercicio sobre extracción, carga de datos, y ejecución de jobs en BigQuery.
4. `dataproc_dag.py`: ejercicio para ejecutar jobs de PySpark en el servicio Dataproc Batch.

## Airflow
* La versión de Airflow corresponde a `Airflow 2.8.1`.
* Las dependencias y variables utilizadas se encuentran en la carpeta `./airflow/`, `requirements.txt` y `airflow-variables.json`, respectivamente.

## Google Cloud
* El folder `./resources/gcloud/` contiene los comandos para desplegar todos los recursos que los DAGs utilizan.
* En `vars.sh` especificar las variables según correponda y haciendo referencia `airflow-variables.json`.
* Ejecutar en shell de GCP `bash apply.sh` para crear los recursos cloud.
* Ejecutar en shell de GCP `bash destroy.sh` para limpiar los recursos desplegados en el paso anterior.

La ejecución de los DAGs se validó a la fecha: February 13th, 2024.
