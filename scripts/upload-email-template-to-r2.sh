#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SOURCE_FILE="$REPO_ROOT/email/template_v1.html"
R2_KEY="email/template_v1.html"

: "${R2_ENDPOINT_URL:?R2_ENDPOINT_URL nao definido}"
: "${R2_ACCESS_KEY_ID:?R2_ACCESS_KEY_ID nao definido}"
: "${R2_SECRET_ACCESS_KEY:?R2_SECRET_ACCESS_KEY nao definido}"
: "${R2_BUCKET:=indiqr-shop}"

if [ ! -f "$SOURCE_FILE" ]; then
  echo "ERRO: $SOURCE_FILE nao encontrado"
  exit 1
fi

echo "==> Uploading $SOURCE_FILE para s3://$R2_BUCKET/$R2_KEY"
echo "    Endpoint: $R2_ENDPOINT_URL"

AWS_ACCESS_KEY_ID="$R2_ACCESS_KEY_ID" \
AWS_SECRET_ACCESS_KEY="$R2_SECRET_ACCESS_KEY" \
aws s3 cp "$SOURCE_FILE" "s3://$R2_BUCKET/$R2_KEY" \
  --endpoint-url "$R2_ENDPOINT_URL" \
  --content-type "text/html; charset=utf-8" \
  --region auto

echo "==> Upload concluido com sucesso!"
echo "    URL: https://private.indiqr.com.br/$R2_KEY"
