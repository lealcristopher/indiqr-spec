#!/usr/bin/env bash
set -euo pipefail

# ──────────────────────────────────────────────────────────────────────────────
# upload-landing-to-r2.sh
#
# Faz upload do landing-page-v1.html para Cloudflare R2.
#
# Pré-requisitos:
#   - aws-cli instalado (pip install awscli ou apt install awscli)
#   - Variáveis de ambiente configuradas (via .env ou export):
#       R2_ENDPOINT_URL
#       R2_ACCESS_KEY_ID
#       R2_SECRET_ACCESS_KEY
#       R2_BUCKET          (default: indiqr-shop)
#
# Uso:
#   export R2_ENDPOINT_URL=https://<account>.r2.cloudflarestorage.com
#   export R2_ACCESS_KEY_ID=<seu-access-key>
#   export R2_SECRET_ACCESS_KEY=<seu-secret-key>
#   ./scripts/upload-landing-to-r2.sh
#
# Ou com .env:
#   cp .env.example .env
#   # edite .env com as credenciais R2
#   set -a; source .env; set +a
#   ./scripts/upload-landing-to-r2.sh
# ──────────────────────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SOURCE_FILE="$REPO_ROOT/landing-page-v1.html"
R2_KEY="paginas/landing-page-v1.html"

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
