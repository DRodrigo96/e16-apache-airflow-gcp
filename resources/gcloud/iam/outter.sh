# outter.sh
# Script para creación de cuenta de servicio de Airflow
# y asignación de roles recursos previamente creados.
# ==================================================
# variables
# ? GCP_PROJECT_ID: GCP project ID.
# ? GCP_BUCKET_NAME: GCS bucket name.
# ? GCP_OUTTER_ACCOUNT: Service Account name for Airflow (outter).
# ? GCP_INNER_ACCOUNT: Service Account name for internal services (inner).
# ? GCP_STORAGE_ROLES: IAM Roles for resource level access to bucket.
# ? GCP_CFUN_ROLES: IAM roles for resource level access to function.
# ? GCP_FUNCTION_NAME: Cloud Function instance name/ID.
# ? GCP_IAM_CUSTOM_ROLE: Custom Role ID for outter SA.
# ? GCP_OUTTER_IAM_MEMBER: Outter Service Account as member.
# --------------------------------------------------

# [NOTE] `gcloud` commands, do not change unless sure.
# --------------------------------------------------
echo "[INFO] Creating service account for Airflow (outter)"
gcloud iam service-accounts create $GCP_OUTTER_ACCOUNT --display-name="Outter GCP SA" --project=$GCP_PROJECT_ID
echo "[INFO] Done"

echo "[INFO] Assigning role to GCS bucket"
for R in $GCP_STORAGE_ROLES; do
  gcloud storage buckets add-iam-policy-binding gs://$GCP_BUCKET_NAME --member=$GCP_OUTTER_IAM_MEMBER --role=$R
done
echo "[INFO] Done"

echo "[INFO] Assigning role to Cloud Function"
for R in $GCP_CFUN_ROLES; do
  gcloud functions add-iam-policy-binding $GCP_FUNCTION_NAME --project=$GCP_PROJECT_ID --region=us-central1 --member=$GCP_OUTTER_IAM_MEMBER --role=$R
done
echo "[INFO] Done"

echo "[INFO] Assigning role for BigQuery"
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID --member=$GCP_OUTTER_IAM_MEMBER --role="roles/bigquery.jobUser" --condition=None > /dev/null
bq query --project_id=$GCP_PROJECT_ID --use_legacy_sql=false "GRANT \`roles/bigquery.dataOwner\` ON SCHEMA \`$GCP_PROJECT_ID.input_dataset\` TO \"$GCP_OUTTER_IAM_MEMBER\";" > /dev/null
bq query --project_id=$GCP_PROJECT_ID --use_legacy_sql=false "GRANT \`roles/bigquery.dataOwner\` ON SCHEMA \`$GCP_PROJECT_ID.output_dataset\` TO \"$GCP_OUTTER_IAM_MEMBER\";" > /dev/null
echo "[INFO] Done"

echo "[INFO] Assigning custom role for Dataproc Airflow"
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID --member=$GCP_OUTTER_IAM_MEMBER --role="projects/$GCP_PROJECT_ID/roles/$GCP_IAM_CUSTOM_ROLE" --condition=None > /dev/null
echo "[INFO] Done"

echo "[INFO] Assign SA User role to outter account at inner account"
gcloud iam service-accounts add-iam-policy-binding $GCP_INNER_ACCOUNT@$GCP_PROJECT_ID.iam.gserviceaccount.com --member=$GCP_OUTTER_IAM_MEMBER --project=$GCP_PROJECT_ID --role='roles/iam.serviceAccountUser'
echo "[INFO] Done"
