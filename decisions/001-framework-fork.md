# ADR-001: Fork do Framework Recon

**Status:** Aceito
**Data:** 2026-03

## Contexto

IndiQR precisa de: multi-tenancy, auth via Auth0, convites por email, RBAC, CI/CD completo, observability. O Recon tem tudo isso implementado e testado.

## Decisão

Fork estrutural do `api-python` (Recon) em vez de greenfield. Reutiliza ~40% do código sem modificação (auth, org/member, email, CI, OTel). Remove Elasticsearch e features de recon de segurança. Adiciona domínio IndiQR (campanhas, QRCodes, conversões).

## O que é copiado sem alteração

- `app/core/telemetry.py`, `logging_config.py` — observability
- `app/database/postgres.py` — engine SQLAlchemy
- `app/api/v1/endpoints/auth.py` — JWT validation + JIT provisioning
- `app/api/v1/endpoints/user.py` — GET /user/me
- CI/CD completo (`.github/workflows/`)
- Dockerfile, Makefile targets, docker-compose structure

## O que é adaptado

- `app/models/organization.py` → Company + MemberRole estendida (admin|influenciador|vendedor)
- `app/core/settings.py` → roles, schema, URLs IndiQR
- `app/services/auth0_service.py` → assign_role parametrizado
- `app/policies/permissions.py` → nova matriz de permissões

## O que é removido

- Elasticsearch stack inteiro (indexes, repositories ES, database/elasticsearch.py)
- HackerOne integration
- Prompts endpoints
- Wildcards e domains endpoints

## Consequências

- Atualizações de segurança do framework base (Recon) precisam ser portadas manualmente
- Divergência aceitável: domínios diferentes não se beneficiam de sincronização automática
