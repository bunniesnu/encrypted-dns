#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.." || exit 1

if ! command -v aws &> /dev/null; then
  echo "Error: AWS CLI is not installed." >&2
  exit 1
fi

# Load .env
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

mkdir -p certbot
if aws s3 cp --endpoint-url "$AWS_ENDPOINT_URL" s3://$AWS_BUCKET_NAME/certbot.tar.gz.enc certbot.tar.gz.enc; then
  age -d -i <(printf '%s\n' "$AGE_SECRET_KEY") certbot.tar.gz.enc | tar -xz -C ./certbot
  rm certbot.tar.gz.enc
fi

uv run scripts/build.py

aws s3 sync out/ "s3://$AWS_BUCKET_NAME/profiles/" \
  --endpoint-url "$AWS_ENDPOINT_URL" \
  --exclude "*" \
  --include "*.mobileconfig" \
  --include "providers.json" \
  --delete \
  --dryrun
