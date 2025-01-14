# Save this file as `secrets.sh`, insert your secrets here, then source the file with
#   set -a && . secrets.sh
#
# !!! Do not add this file to your version control !!!
#
#
# Note: Do not quote the value if you plan to use the file as a Docker env-file

## Kadi
# Host and token to retrieve data
KADIHOST=http://localhost/kadi
KADITOKEN=pat_KADI123456789

## S3
# Key ID and secret to access the S3 bucket defined in `qualitycheck_config.toml`.
#S3_ACCESS_KEY_ID=456S3S3S3654
#S3_SECRET_ACCESS_KEY=123S3S3S3987

## Gitlab
# Tokens to trigger a pipeline run and to get pipeline status and result via the API.
#GITLAB_PIPELINE_TOKEN=glptt-123456789
#GITLAB_API_TOKEN=glpat-987654321

SKIP_QUALITY_CHECK=True
