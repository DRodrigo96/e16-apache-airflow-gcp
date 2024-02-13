# inner.sh
# Script para creación de cuenta de servicio de
# interna de GCP y asignación de roles.
# ==================================================
# variables
# ? GCP_PROJECT_ID: GCP project ID.
# ? GCP_INNER_ACCOUNT: Service Account para uso interno de servicios.
# ? GCP_INNER_IAM_MEMBER: Inner Service Account as member.
# --------------------------------------------------

echo "[INFO] Creating service account for internal resources"
gcloud iam service-accounts create $GCP_INNER_ACCOUNT --display-name="Inner GCP SA" --project=$GCP_PROJECT_ID
echo "[INFO] Done"

echo "[INFO] Assigning role for Dataproc"
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID --member=$GCP_INNER_IAM_MEMBER --role="roles/dataproc.worker" --condition=None > /dev/null
echo "[INFO] Done"
