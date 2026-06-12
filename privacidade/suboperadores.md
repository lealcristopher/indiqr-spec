# Inventário de Suboperadores — IndiQR

**Data:** 11 de junho de 2026
**Responsável técnico:** CTO
**Referência LGPD:** Arts. 26 (operador), 33 (transferência internacional), 35 (cláusulas-padrão)
**Issue:** [IND-62](/IND/issues/IND-62)
**Issue pai:** [IND-51](/IND/issues/IND-51)

---

## 1. Lista de Suboperadores Ativos

### 1.1 Auth0 (Okta, Inc.)

| Campo | Valor |
|-------|-------|
| **Serviço** | Autenticação como serviço (Identity-as-a-Service) |
| **Tipo** | Suboperador — processa credenciais de login e emite tokens JWT |
| **Dados processados** | `email`, `auth_id` (identificador Auth0/sub), roles (`indiqr-admin`, `indiqr-influenciador`, `indiqr-vendedor`), metadados de login (IP, user-agent, timestamp) |
| **Localização do fornecedor** | Okta, Inc. — San Francisco, CA, EUA |
| **Localização dos dados** | EUA / Global (infraestrutura Auth0) |
| **Mecanismo de transferência aplicável** | **EU SCCs (Standard Contractual Clauses)** — Okta está listada no Data Privacy Framework (DPF) e oferece SCCs como salvaguarda adicional; **Data Privacy Framework (EU-US DPF)** — Okta, Inc. é participante ativo do DPF |
| **Base contratual** | DPA do Auth0/Okta (https://www.okta.com/agreements/data-processing-addendum/) |
| **Certificações do fornecedor** | SOC 2 Type II, ISO 27001, ISO 27017, ISO 27018, GDPR compliant, EU-US DPF, UK Extension to EU-US DPF, Swiss-US DPF |

### 1.2 Resend (Resend, Inc.)

| Campo | Valor |
|-------|-------|
| **Serviço** | Envio de emails transacionais (API de email) |
| **Tipo** | Suboperador — processa remetente, destinatário e conteúdo de email |
| **Dados processados** | `email` do destinatário, `email` do remetente (configurado), conteúdo HTML do email (nome da empresa, campanha, valores de remuneração, links de aceite/recusa, código OTP) |
| **Localização do fornecedor** | Resend, Inc. — San Francisco, CA, EUA |
| **Localização dos dados** | EUA (AWS us-east-1) |
| **Mecanismo de transferência aplicável** | **EU SCCs** — Resend oferece DPA com SCCs incorporadas; **Data Privacy Framework** — verificar status de certificação DPF do Resend |
| **Base contratual** | DPA do Resend (https://resend.com/legal/dpa) |
| **Certificações do fornecedor** | SOC 2 Type II, GDPR compliant |

### 1.3 Neon (Neon, Inc.)

| Campo | Valor |
|-------|-------|
| **Serviço** | Banco de dados PostgreSQL serverless |
| **Tipo** | Suboperador — armazena todos os dados operacionais da plataforma |
| **Dados processados** | **Todos os dados da plataforma:** `usuarios` (email, auth_id), `companies` (name, slug), `company_members` (role), `invitations` (email, role), `campaigns` (nome, parâmetros financeiros), `conversions` (valores financeiros, IDs de influenciador/vendedor), `carteiras` (saldo), `resgate_tokens` (código OTP), `resgates` (valores), `shops` (dados públicos), `membership_requests` |
| **Localização do fornecedor** | Neon, Inc. — San Francisco, CA, EUA |
| **Localização dos dados** | **`sa-east-1` (São Paulo, Brasil)** — configurado para residência de dados em território nacional. Ver [IND-73](/IND/issues/IND-73). |
| **Mecanismo de transferência aplicável** | **Residência de dados**: região `sa-east-1` (São Paulo, Brasil) — dados permanecem em território nacional, eliminando a necessidade de mecanismo de transferência internacional. EU SCCs como salvaguarda secundária. |
| **Base contratual** | DPA do Neon (https://neon.tech/legal/dpa) |
| **Certificações do fornecedor** | SOC 2 Type II, ISO 27001, GDPR compliant |

### 1.4 Cloudflare R2 (Cloudflare, Inc.)

| Campo | Valor |
|-------|-------|
| **Serviço** | Armazenamento de objetos (object storage) para mídia da vitrine e deploy de site estático |
| **Tipo** | Suboperador — armazena imagens e arquivos estáticos públicos |
| **Dados processados** | Imagens da vitrine (logo, hero, produtos, galeria), site estático deployado (HTML público com nome da empresa, tagline, URLs de Instagram/WhatsApp, email de contato, nomes e preços de produtos) |
| **Localização do fornecedor** | Cloudflare, Inc. — San Francisco, CA, EUA |
| **Localização dos dados** | Global (CDN). Cloudflare R2 permite configuração de jurisdição de dados. |
| **Mecanismo de transferência aplicável** | **EU SCCs** — Cloudflare oferece DPA com SCCs; **Data Privacy Framework (EU-US DPF)** — Cloudflare, Inc. é participante ativo do DPF |
| **Base contratual** | DPA do Cloudflare (https://www.cloudflare.com/cloudflare-customer-dpa/) |
| **Certificações do fornecedor** | SOC 2 Type II, ISO 27001, ISO 27701, GDPR compliant, EU-US DPF, UK Extension to EU-US DPF, Swiss-US DPF |

### 1.5 Grafana Cloud (Grafana Labs)

| Campo | Valor |
|-------|-------|
| **Serviço** | Observabilidade — coleta de logs, métricas e traces (OpenTelemetry) |
| **Tipo** | Suboperador — processa logs de aplicação e telemetria |
| **Dados processados** | Logs de acesso (`client_ip`, `method`, `path`, `status_code`, `request_id`), telemetria (`trace_id`, `span_id`), logs de aplicação estruturados em JSON. **Dados sensíveis são mascarados antes do envio:** códigos OTP nunca em texto plano nos logs, tokens mascarados. |
| **Localização do fornecedor** | Grafana Labs — Nova York, NY, EUA |
| **Localização dos dados** | EUA / Global (Grafana Cloud) |
| **Mecanismo de transferência aplicável** | **EU SCCs** — Grafana Labs oferece DPA com SCCs; verificar status DPF |
| **Base contratual** | DPA do Grafana Labs (https://grafana.com/legal/dpa/) |
| **Certificações do fornecedor** | SOC 2 Type II, GDPR compliant |

### 1.6 Akeyless (Akeyless Security)

| Campo | Valor |
|-------|-------|
| **Serviço** | Gerenciamento de segredos (secrets management) |
| **Tipo** | Suboperador de infraestrutura — NÃO processa dados pessoais de usuários |
| **Dados processados** | **Nenhum dado pessoal de usuário.** Apenas credenciais de infraestrutura: chaves de API, strings de conexão de banco, tokens M2M, chaves JWT, segredos de deploy. |
| **Localização do fornecedor** | Akeyless Security — Tel Aviv, Israel / Nova York, EUA |
| **Localização dos dados** | Definido pelo cliente (SaaS ou self-hosted) |
| **Mecanismo de transferência aplicável** | Como não processa dados pessoais, a transferência internacional de dados pessoais **não se aplica**. Para segredos de infraestrutura, o modo SaaS usa infraestrutura global do Akeyless. |
| **Base contratual** | DPA do Akeyless (se aplicável — não processa PII) |
| **Certificações do fornecedor** | SOC 2 Type II, ISO 27001, FIPS 140-2 |

---

## 2. Fluxo Técnico de Dados por Suboperador

### 2.1 Auth0 — Autenticação

**Direção do fluxo:** Usuário (browser) ↔ Auth0 ↔ IndiQR API

```
[Browser/SPA]
  │
  ├─ POST /authorize ──────────────────────────────► [Auth0 Universal Login]
  │    query: client_id, redirect_uri, scope, audience
  │    body:  email + senha (processados SOMENTE pelo Auth0)
  │
  ├─◄── JWT (RS256) + refresh token ─────────────── [Auth0]
  │
  ├─ GET/POST/PATCH/DELETE /api/v1/* ──────────────► [IndiQR API (GKE)]
  │    header: Authorization: Bearer <JWT>
  │    JWT claims processadas pela API:
  │      sub (auth_id), email, iss, aud, exp,
  │      https://indiqr.lealcyber.com/roles
  │
  └─◄── Resposta JSON ──────────────────────────── [IndiQR API]

[IndiQR API]
  │
  ├─ POST /api/v2/users/{auth_id}/roles ──────────► [Auth0 Management API]
  │    header: Authorization: Bearer <M2M token>
  │    body: { roles: ["role-id"] }
  │    (atribuição/revogação de roles)
  │
  └─ DELETE /api/v2/users/{auth_id}/roles ────────► [Auth0 Management API]
```

**Campos trafegados:**
| Campo | Direção | Persistido na API? |
|-------|---------|-------------------|
| `email` | Auth0 → API (via JWT claim) | Sim — `usuarios.email` |
| `sub` (auth_id) | Auth0 → API (via JWT claim) | Sim — `usuarios.auth_id` |
| `roles` (indiqr-*) | Auth0 → API (via JWT claim) | Não — validado a cada request |
| `aud` | Auth0 → API (via JWT claim) | Não — validado a cada request |
| `exp` | Auth0 → API (via JWT claim) | Não — validado a cada request |

**O que o IndiQR NÃO processa:** Senhas (nunca chegam à API), credenciais de login, tokens de refresh (gerenciados pelo Auth0 SDK no browser).

**Endpoint da API IndiQR:** `GET /api/v1/auth/me` — retorna `id`, `email`, `roles`, `company_id` do token JWT validado.

---

### 2.2 Resend — Email Transacional

**Direção do fluxo:** IndiQR API → Resend API

```
[IndiQR API]
  │
  ├─ POST https://api.resend.com/emails ───────────► [Resend API]
  │    header: Authorization: Bearer <RESEND_API_KEY>
  │    body: {
  │      "from": "IndiQR <naoresponder@indiqr.lealcyber.com>",
  │      "to": "<destinatario@exemplo.com>",
  │      "subject": "<assunto do email>",
  │      "html": "<HTML do template>"
  │    }
  │
  └─◄── { "id": "res-123" } ───────────────────── [Resend API]
```

**Tipos de email e dados trafegados:**

| Tipo de email | Função | Campos trafegados no HTML |
|---------------|--------|--------------------------|
| Convite de empresa | `send_company_invite()` | `email` do convidado, nome da empresa, role, URL de aceite |
| Convite de campanha | `send_campaign_invite()` | `email` do influenciador, nome da campanha, nome da empresa, URL de aceite, URL de recusa, descrição da remuneração, descrição do desconto |
| Campanha aceita | `send_campaign_accepted()` | `email` do admin, `email` do influenciador, nome da campanha |
| Campanha recusada | `send_campaign_declined()` | `email` do admin, `email` do influenciador, nome da campanha |
| Campanha encerrada | `send_campaign_ended()` | `email` do influenciador, nome da campanha, nome da empresa |
| Influenciador saiu | `send_influencer_left_campaign()` | `email` do admin, `email` do influenciador, nome da campanha |
| Solicitação de adesão | `send_membership_request_notification()` | `email` do admin, `email` do solicitante, nome da empresa, role |
| Adesão aceita | `send_membership_accepted()` | `email` do solicitante, nome da empresa, role |
| Adesão recusada | `send_membership_declined()` | `email` do solicitante, nome da empresa, mensagem |
| Notificação de conversão | `send_conversion_notification()` | `email` do influenciador, nome da campanha, `valor_bruto`, `remuneracao_valor` |
| Código OTP de resgate | `send_redemption_otp()` | `email` do influenciador, `otp_code` (6 dígitos) |
| Vitrine publicada | `send_shop_deployed()` | `email` do admin, nome da vitrine, URL pública |

**Endpoints envolvidos (IndiQR API):**
- `POST /api/v1/companies/{company_id}/invitations` → dispara `send_company_invite()`
- `POST /api/v1/campaigns` → pode disparar `send_campaign_invite()`
- `POST /api/v1/campaigns/invitations/{token}/accept` → dispara `send_campaign_accepted()`
- `POST /api/v1/campaigns/invitations/{token}/decline` → dispara `send_campaign_declined()`
- `POST /api/v1/campaigns/{id}/close` → dispara `send_campaign_ended()`
- `POST /api/v1/campaigns/{id}/leave` → dispara `send_influencer_left_campaign()`
- `POST /api/v1/conversions/validate` → dispara `send_conversion_notification()`
- `POST /api/v1/redemptions/tokens` → dispara `send_redemption_otp()`
- `POST /api/v1/shop/{handle}/deploy` → dispara `send_shop_deployed()`

---

### 2.3 Neon — Banco de Dados PostgreSQL

**Direção do fluxo:** IndiQR API ↔ Neon PostgreSQL (bidirecional, conexão persistente)

```
[IndiQR API (GKE)]
  │
  ├─ TCP/TLS :5432 ─────────────────────────────────► [Neon PostgreSQL]
  │    Connection string via Akeyless (/indiqr/DATABASE_URL)
  │    Schema: indiqr
  │
  └─◄── Result sets ─────────────────────────────── [Neon PostgreSQL]
```

**Tabelas e campos com dados pessoais processados:**

| Tabela | Campos com dado pessoal | Operações | Volume estimado |
|--------|------------------------|-----------|-----------------|
| `usuarios` | `email`, `auth_id` | INSERT (JIT), SELECT, UPDATE (anonimização), DELETE (exclusão) | ~1 por usuário |
| `company_members` | `usuario_id`, `role` | INSERT, SELECT, DELETE | ~5-50 por empresa |
| `invitations` | `email`, `role` | INSERT, SELECT, DELETE, UPDATE (status) | ~10-100 por empresa |
| `membership_requests` | `requester_id` | INSERT, SELECT, DELETE | ~5-20 por empresa |
| `campaigns` | `influenciador_id` | INSERT, SELECT, UPDATE (status) | ~10-100 por empresa |
| `conversions` | `influenciador_id`, `vendedor_id`, `valor_bruto` | INSERT (imutável), SELECT | ~100-10.000 por campanha |
| `carteiras` | `influenciador_id` | INSERT, SELECT, UPDATE (saldo) | 1 por influenciador |
| `resgate_tokens` | `influenciador_id`, `code` (OTP) | INSERT, SELECT, UPDATE (status) | ~10-100 por influenciador |
| `resgates` | `influenciador_id`, `vendedor_id`, `valor` | INSERT (imutável), SELECT | ~10-100 por influenciador |
| `shops` | `email`, `instagram_url`, `whatsapp_url` | INSERT, SELECT, UPDATE | 1 por empresa |

**Dados que NÃO são processados pelo Neon:** Senhas (Auth0), segredos de infraestrutura (Akeyless), arquivos de mídia (R2), logs (Grafana Cloud).

---

### 2.4 Cloudflare R2 — Armazenamento de Mídia

**Direção do fluxo:** IndiQR API → Cloudflare R2 (upload), Browser ← Cloudflare R2 (download/CDN)

```
[Upload]
[IndiQR API]
  │
  ├─ PUT s3://{bucket}/media/{company_id}/{uuid}.{ext} ──► [Cloudflare R2]
  │    header: Authorization (S3-compatible)
  │    body:  imagem binária (PNG/JPEG/WebP)
  │    (via POST /api/v1/shop/{handle}/media)
  │
  └─◄── 200 OK ─────────────────────────────────────── [Cloudflare R2]

[Deploy de site estático]
[IndiQR API]
  │
  ├─ PUT s3://{bucket}/sites/{handle}/index.html ──────► [Cloudflare R2]
  │    body: HTML do site estático
  │    (via POST /api/v1/shop/{handle}/deploy)
  │
  └─◄── 200 OK ─────────────────────────────────────── [Cloudflare R2]

[Download público (CDN)]
[Browser visitante]
  │
  ├─ GET https://{SHOP_BASE_URL}/{handle}/ ────────────► [Cloudflare R2 / CDN]
  └─◄── site estático + imagens ───────────────────── [Cloudflare R2 / CDN]
```

**Dados armazenados no R2:**

| Categoria | Conteúdo | Natureza | Público? |
|-----------|----------|----------|----------|
| Imagens de vitrine | Logo, hero, produtos, galeria | Dados de negócio | Sim (via CDN) |
| Site estático | HTML com nome da empresa, tagline, Instagram, WhatsApp, email, produtos e preços | Dados públicos da vitrine | Sim (indexável) |
| Nomes de arquivo | UUID (não revela nome original) | Metadado | Sim |

**Dados que NÃO vão para o R2:** Dados de usuários, dados financeiros, tokens, logs — esses permanecem no Neon e Grafana Cloud.

---

### 2.5 Grafana Cloud — Observabilidade

**Direção do fluxo:** IndiQR API → Grafana Cloud OTLP (push)

```
[IndiQR API (GKE)]
  │
  ├─ OTLP/gRPC ─────────────────────────────────► [Grafana Cloud Tempo (traces)]
  │    span data: trace_id, span_id, operation name,
  │               attributes (http.method, http.url, http.status_code)
  │
  ├─ OTLP/HTTP ─────────────────────────────────► [Grafana Cloud Loki (logs)]
  │    log data: timestamp, level, message, trace_id,
  │              request_id, client_ip, method, path,
  │              status_code
  │    OTP codes: MASCARADOS (***921 ou [REDACTED])
  │    Tokens: MASCARADOS
  │
  └─◄── ACK ──────────────────────────────────── [Grafana Cloud]
```

**Campos trafegados para Grafana Cloud:**

| Campo | Fonte | Contém dado pessoal? | Mascarado? |
|-------|-------|----------------------|------------|
| `trace_id` | OTel middleware | Não (UUID) | N/A |
| `span_id` | OTel middleware | Não (hex) | N/A |
| `request_id` | ASGI middleware | Não (UUID) | N/A |
| `client_ip` | Header `X-Forwarded-For` | **Sim (IP do cliente)** | Não |
| `method` | Request | Não (GET/POST/etc.) | N/A |
| `path` | Request | Potencialmente (URLs contêm IDs) | Parcial (tokens em paths são mascarados) |
| `status_code` | Response | Não (número) | N/A |
| `user_id` (trace attribute) | JWT `sub` | **Sim (auth_id)** | Não — necessário para rastreabilidade |

**Medidas de proteção:**
- Códigos OTP mascarados nos logs: `***921` ou `[REDACTED]`
- Tokens sensíveis (convite, QRCode) mascarados nos logs de path
- Stack traces nunca enviados (tratados como `Internal server error`)
- `OTEL_SERVICE_NAME = "indiqr-api"` para segregação no tenant Grafana Cloud

**O que NÃO é enviado para Grafana Cloud:** Corpos de requisição/resposta, conteúdo de emails, dados financeiros, senhas.

---

### 2.6 Akeyless — Gerenciamento de Segredos

**Direção do fluxo:** GitHub Actions CI/CD → Akeyless (OIDC), IndiQR API → Akeyless (runtime)

```
[CI/CD — GitHub Actions]
  │
  ├─ Auth: GitHub OIDC ───────────────────────► [Akeyless]
  │
  ├─ GET /indiqr/DATABASE_URL ────────────────► [Akeyless]
  ├─ GET /indiqr/RESEND_API_KEY ──────────────► [Akeyless]
  ├─ GET /indiqr/AUTH0_M2M_* ─────────────────► [Akeyless]
  ├─ GET /indiqr/R2_* ────────────────────────► [Akeyless]
  ├─ GET /indiqr/GRAFANA_CLOUD_* ─────────────► [Akeyless]
  ├─ GET /indiqr/LOCAL_JWKS_JSON ─────────────► [Akeyless]
  │
  └─◄── Secrets injetados como env vars ───── [Akeyless]

[Runtime — Kubernetes]
  │
  └─ Segredos injetados via env vars no container
     (NUNCA em código-fonte, .gitignore inclui .env)
```

**Dados pessoais processados pelo Akeyless:** **NENHUM.** O Akeyless armazena exclusivamente credenciais de infraestrutura. Não há `email`, `auth_id`, nomes de empresas, ou quaisquer dados de usuários no Akeyless.

---

## 3. Resumo de Mecanismos de Transferência Internacional

| Suboperador | País de origem | Mecanismo primário | Mecanismo secundário | Status |
|-------------|---------------|-------------------|---------------------|--------|
| **Auth0 (Okta)** | EUA | EU-US DPF | EU SCCs (DPA Okta) | Ambos disponíveis |
| **Resend** | EUA | EU SCCs (DPA Resend) | DPF (verificar) | SCCs disponíveis |
| **Neon** | EUA (região configurável) | Residência de dados (`sa-east-1`) | EU SCCs (DPA Neon) | sa-east-1 em configuração ([IND-73](/IND/issues/IND-73)) |
| **Cloudflare R2** | EUA (global) | EU-US DPF | EU SCCs (DPA Cloudflare) | Ambos disponíveis |
| **Grafana Cloud** | EUA | EU SCCs (DPA Grafana Labs) | — | SCCs disponíveis |
| **Akeyless** | Israel / EUA | N/A (não processa PII) | N/A | Não aplicável |

### Situação atual (jun/2026)

A política de privacidade em `privacidade/politica-de-privacidade.md` §4.2 menciona que o IndiQR "adotará SCCs da ANPD quando publicadas" mas **não referencia os mecanismos já existentes** (EU SCCs, DPF).

**Recomendação técnica:** Atualizar a política de privacidade para:
1. Referenciar explicitamente as EU SCCs como salvaguarda vigente para Auth0, Resend, Cloudflare R2 e Grafana Cloud
2. Referenciar o EU-US Data Privacy Framework para Auth0 e Cloudflare R2 (participantes ativos)
3. Para Neon, a região `sa-east-1` (São Paulo) está sendo configurada para residência de dados em território nacional, eliminando a necessidade de mecanismo de transferência internacional. Ver [IND-73](/IND/issues/IND-73).
4. Documentar que Akeyless não processa dados pessoais e portanto não requer mecanismo de transferência

---

## 4. Ação Necessária (DPO + CEO)

A preparação técnica está concluída. As seguintes ações contratuais/jurídicas são necessárias:

1. **Firmar DPAs** com Auth0, Resend, Neon, Cloudflare R2 e Grafana Labs (links para DPAs de cada fornecedor na seção 1)
2. **Atualizar `privacidade/politica-de-privacidade.md`** §4.2 para referenciar EU SCCs e DPF como mecanismos vigentes
3. **Configurar região Neon para `sa-east-1`** (São Paulo) para residência de dados no Brasil — em andamento: [IND-73](/IND/issues/IND-73)
4. **Armazenar cópias dos DPAs** em repositório seguro para auditoria (ex: diretório `privacidade/dpas/` com acesso restrito)
5. **Elaborar template de DPA** para empresas-clientes (relação controlador-operador no uso da vitrine)
6. **Incluir na política links para DPAs** dos suboperadores

---

## 5. Template de DPA (Controlador-Operador) para Clientes

A ser elaborado pelo DPO + CEO. O template deve cobrir:

- Partes: Cliente (controlador) e IndiQR/LealCyber (operador)
- Dados processados: conforme categoria do cliente (admin, influenciador, vendedor)
- Finalidade: operação da plataforma de marketing por indicação
- Suboperadores: lista conforme este documento
- Transferência internacional: mecanismos conforme seção 3
- Obrigações do operador (IndiQR): Art. 37 da LGPD
- Obrigações do controlador (cliente): Art. 38 da LGPD
- Vigência: enquanto durar a prestação de serviço
- Lei aplicável: LGPD (Lei 13.709/2018)

---

**Versão do documento:** `privacidade/suboperadores.md`
**Repositório:** [indiqr-spec](https://github.com/lealcristopher/indiqr-spec)
**Próximo passo:** DPO + CEO — itens 3-7 dos critérios de aceite de [IND-62](/IND/issues/IND-62)
