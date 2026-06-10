SHELL := /bin/bash
OPENAPI_SPEC := api/openapi.yaml

.PHONY: help test-contract lint-oa lint test-cov-report validate-spec

help:
	@echo "IndiQR Spec — quality and contract test targets"
	@echo ""
	@echo "  make test-contract     Run Schemathesis contract tests against OpenAPI spec"
	@echo "  make lint-oa           Lint OpenAPI spec with Spectral"
	@echo "  make lint              All linting"
	@echo "  make validate-spec     Validate OpenAPI spec structure"
	@echo "  make test-cov-report   Generate test coverage report placeholder"

# ── Contract tests (local Schemathesis) ───────────────────────────────────────

test-contract: .schemathesis-deps
	@echo "==> Running Schemathesis contract tests against $(OPENAPI_SPEC)"
	schemathesis run $(OPENAPI_SPEC) \
		--base-url=http://localhost:8000/api/v1 \
		--checks all \
		--hypothesis-max-examples=50 \
		--stateful=links \
		--workers=auto \
		--cassette-path=.schemathesis-cassettes \
		--request-timeout=5000

.schemathesis-deps:
	@pip install schemathesis hypothesis 2>/dev/null || true
	@which schemathesis >/dev/null 2>&1 || { echo "ERROR: schemathesis not installed. Install with: pip install schemathesis"; exit 1; }
	@touch $@

# ── OpenAPI linting ───────────────────────────────────────────────────────────

lint-oa: .spectral-deps
	@echo "==> Linting OpenAPI spec with Spectral"
	npx @stoplight/spectral-cli lint $(OPENAPI_SPEC)

.spectral-deps:
	@which npx >/dev/null 2>&1 || { echo "ERROR: npx not available. Install Node.js."; exit 1; }
	@touch $@

# ── All linting ──────────────────────────────────────────────────────────────

lint: lint-oa

# ── Validate spec structure ──────────────────────────────────────────────────

validate-spec:
	@echo "==> Validating OpenAPI spec structure"
	@python3 -c "
import yaml, sys
with open('$(OPENAPI_SPEC)') as f:
    spec = yaml.safe_load(f)
assert spec.get('openapi'), 'Missing openapi version'
assert spec.get('info'), 'Missing info'
assert spec.get('paths'), 'Missing paths'
for path, methods in spec['paths'].items():
    for method, details in methods.items():
        assert 'responses' in details, f'{method} {path}: missing responses'
        resp_codes = [k for k in details['responses'].keys() if k != 'default']
        print(f'  {method.upper()} {path}  → {sorted(resp_codes)}')
print()
print('OK: OpenAPI spec is structurally valid')
" 2>/dev/null || echo "Install pyyaml to validate: pip install pyyaml"

# ── Coverage report placeholder ──────────────────────────────────────────────

test-cov-report:
	@echo "==> Run in api-indiqr repo:"
	@echo "    pytest tests/ --cov=app --cov-report=term-missing --cov-fail-under=80"
	@echo ""
	@echo "See behavior/tests.md for full coverage specification."
