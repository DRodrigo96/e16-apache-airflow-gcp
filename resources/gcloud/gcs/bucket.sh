# bucket.sh
# Commands for creating a bucket in a host GCP project
# and moving objects into it.
# ==================================================
# variables
# ? GCP_PROJECT_ID: GCP project ID.
# ? GCP_BUCKET_NAME: cloud storage bucket name/id (unique).
# --------------------------------------------------

# [NOTE] `gcloud` commands. Do not change unless sure.
# --------------------------------------------------
echo "[INFO] Enabling services for Cloud Storage"
gcloud services enable storage.googleapis.com --project=$GCP_PROJECT_ID

echo "[INFO] Creating bucket: $GCP_BUCKET_NAME at project: $GCP_PROJECT_ID"
gsutil mb -p $GCP_PROJECT_ID gs://$GCP_BUCKET_NAME
echo "[INFO] Done"

echo "[INFO] Moving objects from local repository to bucket..."
gsutil -m cp -r ./gcs/data/* gs://$GCP_BUCKET_NAME
echo "[INFO] Done"
