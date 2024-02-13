# vars.sh
# ==================================================
# --------------------------------------------------

# [NOTE] variables
# --------------------------------------------------
GCP_PROJECT_ID="{project-id}"
GCP_BUCKET_NAME="airflow-bucket-{random}"

# [NOTE] parameters
# --------------------------------------------------
GCP_INNER_ACCOUNT="inner-gcp-sa"
GCP_OUTTER_ACCOUNT="outter-gcp-sa"
GCP_FUNCTION_NAME="airflow-function"
GCP_VPC_NAME="airflow-network"
GCP_SUBNET_NAME="airflow-subnetwork"
GCP_SUBNET_IPRANGE="10.128.0.0/20"
GCP_FWALL_RULE_NAME="allow-internal-ingress"
GCP_IAM_CUSTOM_ROLE="dataprocBatchUser"
GCP_STORAGE_ROLES="roles/storage.legacyBucketWriter roles/storage.legacyObjectReader"
GCP_CFUN_ROLES="roles/cloudfunctions.developer roles/cloudfunctions.invoker"
GCP_INNER_IAM_MEMBER="serviceAccount:$GCP_INNER_ACCOUNT@$GCP_PROJECT_ID.iam.gserviceaccount.com"
GCP_OUTTER_IAM_MEMBER="serviceAccount:$GCP_OUTTER_ACCOUNT@$GCP_PROJECT_ID.iam.gserviceaccount.com"
