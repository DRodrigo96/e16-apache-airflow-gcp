# destroy.sh
# This scripts cleans deployments from GCP at
# apply.sh stage.
# ==================================================
# variables
# --------------------------------------------------
source "./vars.sh"
# --------------------------------------------------

# Destroy BigQuery Datasets
bq rm -r -f $GCP_PROJECT_ID:input_dataset
bq rm -r -f $GCP_PROJECT_ID:output_dataset

# Destroy Storage Bucket
gcloud storage rm --recursive gs://$GCP_BUCKET_NAME --project=$GCP_PROJECT_ID -q

# Destroy Cloud Function
gcloud functions delete $GCP_FUNCTION_NAME --project=$GCP_PROJECT_ID --region=us-central1 -q

# Destroy VPC
gcloud compute firewall-rules delete projects/$GCP_PROJECT_ID/global/firewalls/$GCP_FWALL_RULE_NAME --project=$GCP_PROJECT_ID -q
gcloud compute networks subnets delete projects/$GCP_PROJECT_ID/regions/us-central1/subnetworks/$GCP_SUBNET_NAME --project=$GCP_PROJECT_ID -q
gcloud compute networks delete projects/$GCP_PROJECT_ID/global/networks/$GCP_VPC_NAME --project=$GCP_PROJECT_ID -q

# Remove from IAM and destroy Service Accounts
gcloud projects remove-iam-policy-binding $GCP_PROJECT_ID --member=$GCP_OUTTER_IAM_MEMBER --role="roles/bigquery.jobUser" --all > /dev/null
gcloud projects remove-iam-policy-binding $GCP_PROJECT_ID --member=$GCP_OUTTER_IAM_MEMBER --role="projects/$GCP_PROJECT_ID/roles/$GCP_IAM_CUSTOM_ROLE" --all > /dev/null
gcloud projects remove-iam-policy-binding $GCP_PROJECT_ID --member=$GCP_INNER_IAM_MEMBER --role="roles/dataproc.worker" --all > /dev/null
gcloud iam service-accounts delete $GCP_INNER_ACCOUNT@$GCP_PROJECT_ID.iam.gserviceaccount.com --project=$GCP_PROJECT_ID -q
gcloud iam service-accounts delete $GCP_OUTTER_ACCOUNT@$GCP_PROJECT_ID.iam.gserviceaccount.com --project=$GCP_PROJECT_ID -q

# Destroy Custom Role
gcloud iam roles delete $GCP_IAM_CUSTOM_ROLE --project=$GCP_PROJECT_ID
