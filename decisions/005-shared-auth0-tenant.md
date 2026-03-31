# ADR-005: Mesmo Tenant Auth0 que o Recon

**Status:** Aceito
**Data:** 2026-03

## Contexto

O plano Auth0 atual não permite múltiplos tenants. IndiQR precisa de auth isolado do Recon.

## Decisão

Mesmo tenant Auth0, isolamento via prefixo de recursos e claims:

- Roles: `indiqr-admin`, `indiqr-influenciador`, `indiqr-vendedor` (prefixo `indiqr-`)
- Resource Server: `https://indiqr-api.lealcyber.com` (audience separado)
- Roles claim: `https://indiqr.lealcyber.com/roles` (namespace diferente do Recon)
- Apps Auth0: SPA `indiqr-web` e M2M `indiqr-api-backend` (separados dos apps Recon)

O isolamento por audience garante que tokens do IndiQR não funcionam na API do Recon e vice-versa.

## Consequências

- Um usuário pode ter contas nos dois sistemas com o mesmo email (Auth0 sub é o mesmo, roles diferentes)
- IaC: novos arquivos `roles_indiqr.tf`, `apps_indiqr.tf`, `api_indiqr.tf` no mesmo workspace `auth0-recon`
- Quando o plano Auth0 for atualizado: migrar para tenant dedicado ao IndiQR (sem impacto na API, só na config)
