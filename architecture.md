# IndiQR API — Architecture Reference

> Documento de referência da arquitetura. Base para onboarding e planejamento de features.
> Framework herdado do [Recon](https://github.com/lealcristopher/recon-spec) — consulte `recon-spec/architecture.md` para contexto do framework base.

---

## Produto

IndiQR é uma plataforma de marketing por indicação com remuneração por conversão. Permite que empresas (Admins) criem campanhas, convidem influenciadores, e rastreiem conversões validadas por vendedores no ponto de venda via QRCode.

**Cliente inicial:** Personalitte Biomedicina Estética

**Três perfis:**
- **Admin** — cria campanhas, convida membros, visualiza painel completo
- **Influenciador** — aceita campanhas, baixa material (QRCode + PDF), acompanha conversões
- **Vendedor** — valida QRCodes no app mobile, registra conversões

---

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Runtime | Python 3.11, FastAPI, Uvicorn |
| ORM | SQLAlchemy 2.0 |
| Banco relacional | PostgreSQL (Neon serverless) |
| Migrations | Alembic |
| Auth | Auth0 (mesmo tenant do Recon, prefixo `indiqr-`) |
| QRCode | `qrcode[pil]` |
| PDF | `reportlab` |
| Email | Resend |
| Observability | OpenTelemetry → Grafana Cloud (Tempo + Loki) |
| Secrets | Akeyless (GitHub OIDC, path `/indiqr/*`) |
| Container | Docker, docker-compose |
| Deploy | Kubernetes + Helm (GKE, namespace `indiqr`) |
| CI/CD | GitHub Actions + GHCR |

**Sem Elasticsearch** — não há busca full-text no MVP. Todos os dados em PostgreSQL.

---

## Estrutura de diretórios

```
app/
├── main.py
├── core/
│   ├── settings.py          # DB_SCHEMA="indiqr", roles IndiQR
│   ├── telemetry.py         # OpenTelemetry (herdado do Recon)
│   └── logging_config.py
├── api/v1/endpoints/
│   ├── auth.py              # JWT validation (herdado)
│   ├── user.py              # GET /user/me
│   ├── companies.py         # Empresas + membros + convites
│   ├── campaigns.py         # Campanhas + QRCode + PDF
│   └── conversions.py       # Validação + registro
├── database/
│   └── postgres.py          # Engine + SessionLocal
├── models/
│   ├── usuario.py           # Usuario (herdado)
│   ├── company.py           # Company, CompanyMember, Invitation
│   ├── campaign.py          # Campaign, QRCode
│   └── conversion.py        # Conversion (imutável)
├── services/
│   ├── auth0_service.py     # M2M + assign/revoke roles (adaptado)
│   ├── email_service.py     # Resend + templates IndiQR
│   ├── qrcode_service.py    # Geração de QRCode PNG
│   ├── card_pdf_service.py  # Geração de PDF com QRCode
│   └── conversion_calculator.py  # Cálculo de desconto e remuneração
└── policies/
    └── permissions.py       # Matriz RBAC IndiQR
alembic/                     # Migrations (schema: indiqr)
tests/
├── unit/
├── integration/
└── e2e/
```

---

## Domain Model (PostgreSQL — schema `indiqr`)

```
Usuario
  id, email, auth_id (Auth0 sub)

Company
  id, name, slug, created_at
  ├── CompanyMember[]   (usuario_id, role: admin|influenciador|vendedor)
  └── Invitation[]      (email, role, token, status: pending|accepted|revoked)

Campaign
  id, name, company_id, influenciador_id
  status: aguardando_aceite | ativa | encerrada
  remuneracao_modelo: fixo | percentual
  remuneracao_valor (Numeric)
  desconto_pct (Numeric, nullable)
  created_at, updated_at
  └── QRCode (1:1)      (token: UUID, active: bool)
  └── Conversion[]

Conversion   ← imutável após insert, sem updated_at
  id, campaign_id, qrcode_id, influenciador_id, vendedor_id
  valor_bruto, desconto_valor, remuneracao_valor (Numeric)
  created_at
```

**Regras de acesso:**
- Company: só membros da empresa acessam dados dela
- Campaign: admin vê todas da empresa; influenciador vê só as suas
- Conversion: admin vê todas; influenciador vê as suas; vendedor vê as suas

---

## Autenticação

Mesmo mecanismo do Recon — 3 modos via `AUTH_MODE`:

| Modo | Onde | Comportamento |
|------|------|--------------|
| `auth0` | Produção | JWKS do tenant Auth0 compartilhado |
| `local_jwks` | CI / staging | Par RSA local (`/indiqr/LOCAL_JWKS_JSON`) |
| `mock` | Testes | `dependency_overrides` |

`AUTH0_ROLES_CLAIM = "https://indiqr.lealcyber.com/roles"`

---

## RBAC

Ver `behavior/rbac.md` para especificação completa.

**Roles Auth0:** `indiqr-admin`, `indiqr-influenciador`, `indiqr-vendedor`

Implementação em `app/policies/permissions.py` — mesmo padrão do Recon (`require_permission("x:y")`).

---

## Observability

Herdado integralmente do Recon:
- JSON structured logging com `trace_id` e `request_id`
- OTel → Grafana Cloud (Tempo + Loki)
- Middleware ASGI puro para preservar contexto OTel

`OTEL_SERVICE_NAME = "indiqr-api"`

---

## CI/CD

Mesmo pipeline do Recon com ajustes de nomes:

```
push/PR → main, dev
  ├── security-scan (Gitleaks + Trivy)
  ├── static-analysis (Ruff + Bandit)
  ├── build-and-push → ghcr.io/lealcristopher/api-indiqr:{sha}
  ├── test-suite (unit + int + e2e)
  └── staging-validation
       ├── Fetch secrets Akeyless /indiqr/*
       ├── docker-compose staging
       ├── smoke-test
       └── Contract test (Schemathesis → indiqr-spec/api/openapi.yaml)
```

---

## O que NÃO existe no MVP

- Módulo financeiro (pagamentos, saques) — fora do escopo por contrato
- Estorno de conversões — imutável intencionalmente
- Expiração automática de convites de campanha
- Personalização do template PDF (logo/cores da empresa)
- Comissões para vendedor
- Escopo de produtos por campanha
- App mobile nativo — vendedor usa PWA
