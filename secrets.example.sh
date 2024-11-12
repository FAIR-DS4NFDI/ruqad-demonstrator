# Insert your secrets here, save as `secrets.sh`, then source the file with
#   . secrets.sh
# Do not add this file to your version control!

# Token to trigger a pipeline run.
export GITLAB_PIPELINE_TOKEN="glptt-123456789"

# Token to get pipeline status and result via the API.
export GITLAB_API_TOKEN="glpat-987654321"

# Key ID and secret to access the S3 bucket defined in `qualitycheck_config.toml`.
export S3_ACCESS_KEY_ID="456S3S3S3654"
export S3_SECRET_ACCESS_KEY="123S3S3S3987"
