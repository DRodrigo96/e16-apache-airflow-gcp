# apply.sh
# Script for deploying resources in Google Cloud.
# ==================================================
# variables
source "./vars.sh"
# --------------------------------------------------

source "./gcs/bucket.sh"
source "./bq/dataset.sh"
source "./iam/inner.sh"
source "./gcf/function.sh"
source "./vpc/vpc.sh"
source "./iam/role.sh"
source "./iam/outter.sh"
