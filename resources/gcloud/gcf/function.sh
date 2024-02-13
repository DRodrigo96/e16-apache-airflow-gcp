# function.sh
# This script if for deployment purposes and to be
# executed in GCP shell.
# ==================================================
# variables
# ? GCP_PROJECT_ID: GCP project ID.
# ? GCP_FUNCTION_NAME: cloud function instance name.
# ? GCP_INNER_ACCOUNT: service account for function.
# --------------------------------------------------

# [NOTE] `gcloud` commands, do not change unless sure.
# --------------------------------------------------
echo "[INFO] Enabling services for Cloud Functions"
GCP_SERVICES="
  iam.googleapis.com
  cloudfunctions.googleapis.com
  cloudbuild.googleapis.com
  artifactregistry.googleapis.com
"
gcloud services enable $GCP_SERVICES --project=$GCP_PROJECT_ID

echo "[INFO] Deploying function: $GCP_FUNCTION_NAME at project: $GCP_PROJECT_ID"
GCP_CFUN_FLAGS="
  --runtime=python310
  --no-allow-unauthenticated
  --source=./gcf/src/
  --clear-labels
  --update-labels=airflow=true,dev=true
  --docker-registry=artifact-registry
  --timeout=540s
  --max-instances=5
  --memory=256MB
  --trigger-http
  --project=$GCP_PROJECT_ID
  --region=us-central1
  --entry-point=main
  --service-account=$GCP_INNER_ACCOUNT@$GCP_PROJECT_ID.iam.gserviceaccount.com
  --set-env-vars=airflow=true
  --set-env-vars=dev=true
"
gcloud functions deploy $GCP_FUNCTION_NAME $GCP_CFUN_FLAGS
echo "[INFO] Done"
