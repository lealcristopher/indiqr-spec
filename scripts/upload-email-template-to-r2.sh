#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
EMAIL_DIR="$REPO_ROOT/email"

: "${R2_ENDPOINT_URL:?R2_ENDPOINT_URL nao definido}"
: "${R2_ACCESS_KEY_ID:?R2_ACCESS_KEY_ID nao definido}"
: "${R2_SECRET_ACCESS_KEY:?R2_SECRET_ACCESS_KEY nao definido}"
: "${R2_BUCKET:=indiqr-shop}"

TEMPLATES=(
  "template_v1.html"
  "template_lead_qualification.html"
)

for template in "${TEMPLATES[@]}"; do
  SOURCE_FILE="$EMAIL_DIR/$template"
  R2_KEY="email/$template"

  if [ ! -f "$SOURCE_FILE" ]; then
    echo "AVISO: $SOURCE_FILE nao encontrado — pulando"
    continue
  fi

  echo "==> Uploading $SOURCE_FILE para s3://$R2_BUCKET/$R2_KEY"
  echo "    Endpoint: $R2_ENDPOINT_URL"

  AWS_ACCESS_KEY_ID="$R2_ACCESS_KEY_ID" \
  AWS_SECRET_ACCESS_KEY="$R2_SECRET_ACCESS_KEY" \
  aws s3 cp "$SOURCE_FILE" "s3://$R2_BUCKET/$R2_KEY" \
    --endpoint-url "$R2_ENDPOINT_URL" \
    --content-type "text/html; charset=utf-8" \
    --region auto

  echo "    URL: https://private.indiqr.com.br/$R2_KEY"
done

echo "==> Upload de todos os templates concluido com sucesso!"
