# role.sh
# Script para creación de rol personalizado GCP.
# ==================================================
# variables
# ? GCP_PROJECT_ID: GCP project ID.
# ? GCP_IAM_CUSTOM_ROLE: Custom Role ID for outter SA.
# --------------------------------------------------

# [NOTE] `gcloud` commands, do not change unless sure.
# --------------------------------------------------
echo "[INFO] Creating custom role for Dataproc Airflow"
gcloud iam roles create $GCP_IAM_CUSTOM_ROLE --project=$GCP_PROJECT_ID --file=./iam/custom.json
echo "[INFO] Done"
