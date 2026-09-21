#!/usr/bin/env bash
# Call the Wayfinder Lambda Function URL with a SigV4-signed request.
# The URL uses AWS_IAM auth, so unsigned requests get 403 {"Message":"Forbidden"}.
#
# Usage:
#   scripts/call_api.sh /api/health
#   scripts/call_api.sh /api/chat -X POST -d '{"question":"How do I get AWS access?"}' -H 'content-type: application/json'
#
# Requires: awscli v2, curl >= 7.75 (for --aws-sigv4), and AWS creds in your env/profile.
set -euo pipefail

REGION="${AWS_REGION:-us-east-1}"
FUNCTION_NAME="${APP_NAME:-wayfinder}"
PATH_ARG="${1:-/api/health}"
shift || true

BASE_URL="$(aws lambda get-function-url-config \
  --function-name "$FUNCTION_NAME" --qualifier live \
  --query FunctionUrl --output text --region "$REGION")"
BASE_URL="${BASE_URL%/}"

eval "$(aws configure export-credentials --format env)"

exec curl -sS --aws-sigv4 "aws:amz:${REGION}:lambda" \
  --user "${AWS_ACCESS_KEY_ID}:${AWS_SECRET_ACCESS_KEY}" \
  ${AWS_SESSION_TOKEN:+-H "x-amz-security-token: ${AWS_SESSION_TOKEN}"} \
  "$@" "${BASE_URL}${PATH_ARG}"
