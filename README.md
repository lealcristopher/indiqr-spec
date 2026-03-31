# indiqr-spec

Repositório de especificação da IndiQR API. Fonte da verdade para o contrato da API e regras de negócio.

## Estrutura

```
architecture.md       ← Referência completa: stack, domínio, padrões, CI/CD
api/
  openapi.yaml        ← Contrato OpenAPI 3.1 — usado pelo CI para contract testing (Schemathesis)
behavior/
  companies.md        ← Regras de negócio: empresas e membros
  campaigns.md        ← Regras de negócio: ciclo de vida das campanhas
  conversions.md      ← Regras de negócio: validação e registro de conversões
  rbac.md             ← Modelo de roles e permissões
decisions/
  001-framework-fork.md         ← Por que forcar o Recon
  002-no-elasticsearch.md       ← Por que não usar Elasticsearch
  003-qrcode-static-token.md    ← Estratégia de QRCode estático
  004-conversion-immutability.md ← Por que conversões são imutáveis
  005-shared-auth0-tenant.md    ← Mesmo tenant Auth0 que o Recon
```

## Ciclo de desenvolvimento (SDD)

1. Atualizar `behavior/*.md` com a nova regra de negócio
2. Atualizar `api/openapi.yaml` com o contrato do endpoint
3. PR no `api-indiqr` implementa o endpoint
4. CI do `api-indiqr` faz checkout deste repo e roda Schemathesis
5. Merge quando contrato e implementação estão alinhados

## Validar spec localmente

```bash
npx @stoplight/spectral-cli lint api/openapi.yaml
```

## Repositórios relacionados

| Repo | Papel |
|------|-------|
| `api-indiqr` | Implementação do backend (FastAPI + PostgreSQL) |
| `recon-spec` | Spec do Recon (framework base) |
| `akeyless-iac` | Secrets centralizados (Akeyless) |
| `auth0-iac` | Auth0 IaC (roles, apps, resource servers) |
