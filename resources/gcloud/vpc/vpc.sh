# vpc.sh
# Commands for creating a VPC in a host GCP project
# to be used by Dataproc cluster.
# ==================================================
# variables
# ? GCP_PROJECT_ID: GCP host project ID.
# ? GCP_VPC_NAME: VPC network name.
# ? GCP_SUBNET_NAME: subnetwork name.
# ? GCP_SUBNET_IPRANGE: IP range for subnetwork.
# ? GCP_FWALL_RULE_NAME: firewall rule name.
# --------------------------------------------------

# [NOTE] `gcloud` commands. Do not change unless sure.
# --------------------------------------------------
echo "[INFO] Enabling services for VPC Network"
gcloud services enable compute.googleapis.com dataproc.googleapis.com --project=$GCP_PROJECT_ID

echo "[INFO] Deploying VPC: $GCP_VPC_NAME at project: $GCP_PROJECT_ID"
GCP_VPC_FLAGS="
  --project=$GCP_PROJECT_ID
  --subnet-mode=custom
  --mtu=1460
  --bgp-routing-mode=regional
"
gcloud compute networks create $GCP_VPC_NAME $GCP_VPC_FLAGS

echo "[INFO] Deploying subnetwork: $GCP_SUBNET_NAME at VPC: $GCP_VPC_NAME"
GCP_SUBNET_FLAGS="
  --project=$GCP_PROJECT_ID
  --range=$GCP_SUBNET_IPRANGE
  --network=$GCP_VPC_NAME
  --stack-type=IPV4_ONLY
  --region=us-central1
  --enable-private-ip-google-access
"
gcloud compute networks subnets create $GCP_SUBNET_NAME $GCP_SUBNET_FLAGS

echo "[INFO] Deploying firewall: $GCP_FWALL_RULE_NAME at VPC: $GCP_VPC_NAME"
GCP_FWALL_FLAGS="
  --network=$GCP_VPC_NAME
  --source-ranges=$GCP_SUBNET_IPRANGE
  --project=$GCP_PROJECT_ID
  --direction=ingress
  --action=allow
  --rules=all
"
gcloud compute firewall-rules create $GCP_FWALL_RULE_NAME $GCP_FWALL_FLAGS

echo "[INFO] Done"
