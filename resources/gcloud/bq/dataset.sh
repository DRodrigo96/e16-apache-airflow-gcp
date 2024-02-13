# dataset.sh
# This script if for deployment purposes and to be
# executed in GCP shell.
# ==================================================
# variables
# ? GCP_PROJECT_ID: GCP project ID.
# --------------------------------------------------

# [NOTE] `gcloud` commands, do not change unless sure.
# --------------------------------------------------
echo "[INFO] Creating datasets at project: $GCP_PROJECT_ID"
bq --location=US mk -d --description "Airflow input dataset." $GCP_PROJECT_ID:input_dataset
bq --location=US mk -d --description "Airflow output dataset." $GCP_PROJECT_ID:output_dataset
echo "[INFO] Done"
