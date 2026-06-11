# IndiQR Security Requirements Specification

> **Referência:** OWASP ASVS 4.0.3 Nível 2
> **Alcance:** `api-indiqr` (FastAPI) e `indiqr-web` (React SPA)
> **Versão:** 1.0 — 11/06/2026
> **Objetivo:** Especificar todos os requisitos de segurança do IndiQR, documentar como cada um é atendido (com evidência de implementação) e alertar sobre gaps que devem alimentar o backlog.

---

## Estrutura de Requisitos

Cada requisito segue o formato:

```
REQ-{DOMÍNIO}-{NNN}  [STATUS]  Prioridade-Gap  ASVS-Ref
```

**Status:**
- `[OK]` — Implementado com evidência documentada
- `[~]` — Parcialmente implementado
- `[X]` — Não implementado (gap)

**Prioridade de Gap:** `P0` (crítico) > `P1` (alto) > `P2` (médio) > `P3` (baixo)

---

## SEC-ARCH — Arquitetura de Segurança

### REQ-ARCH-001 [OK] — SDLC com etapas de segurança no CI/CD

**O que:** O ciclo de desenvolvimento inclui verificações de segurança automatizadas em todas as etapas.

**Como é atendido:**
- Pipeline GitHub Actions com 5 estágios documentados em `architecture.md` §CI/CD:
  1. `security-scan` — Gitleaks (detecção de secrets) + Trivy (vulnerabilidades de container)
  2. `static-analysis` — Ruff (linting Python) + Bandit (SAST Python)
  3. `build-and-push` — Build Docker e push para GHCR com SHA tag
  4. `test-suite` — unit + integration + e2e + smoke tests
  5. `staging-validation` — Schemathesis (contract fuzzing contra `api/openapi.yaml`)
- Docker/docker-compose para staging validation
- Kubernetes namespace isolado `indiqr` em GKE

**ASVS:** 1.1.1, 1.14.3, 1.14.4

---

### REQ-ARCH-002 [X] P1 — Threat Modeling formal

**O que:** Realizar modelagem de ameaças a cada sprint ou mudança significativa de design.

**Gap:** Não há evidência de processo formal de threat modeling. ADRs (decisions/001-007) cobrem decisões de arquitetura mas não modelagem de ameaças.

**Ação recomendada:** Adotar metodologia (STRIDE ou similar) e documentar no diretório `security/threats/`. Integrar ao planning de sprint.

**ASVS:** 1.1.2

---

### REQ-ARCH-003 [OK] — Documentação de trust boundaries e componentes

**O que:** Documentar limites de confiança, componentes e fluxos de dados significativos.

**Como é atendido:**
- `architecture.md` — stack completa, domain model, estrutura de diretórios, CI/CD
- `frontend/architecture.md` — stack frontend, Auth0 config, estrutura de pastas
- ADRs em `decisions/001-007-*.md` — decisões arquiteturais com justificativas
- Trust boundaries implícitas: frontend (Cloudflare Pages) ↔ API (GKE) ↔ Auth0 ↔ Neon (PostgreSQL) ↔ Resend (email)

**ASVS:** 1.1.4, 1.1.5

---

### REQ-ARCH-004 [OK] — Controles de segurança centralizados e reutilizáveis

**O que:** Mecanismos de segurança implementados em pontos únicos, evitando duplicação.

**Como é atendido:**
- **RBAC centralizado:** `app/policies/permissions.py` — função `require_permission("x:y")` usada por todos os endpoints
- **Auth centralizada:** `app/api/v1/endpoints/auth.py` — validação JWT com 3 modos (auth0 / local_jwks / mock)
- **ORM centralizado:** `app/database/postgres.py` — SQLAlchemy SessionLocal para todas as queries
- **Serviços reutilizáveis:** `app/services/` — `auth0_service.py`, `email_service.py`, `qrcode_service.py`, `card_pdf_service.py`, `conversion_calculator.py`

**ASVS:** 1.1.6

---

### REQ-ARCH-005 [~] P2 — Guia de codificação segura para desenvolvedores

**O que:** Disponibilizar checklist/guia de codificação segura para todos os desenvolvedores e testers.

**Como é parcialmente atendido:**
- `behavior/security.md` — especificação de 48 cenários de teste de segurança
- `privacidade/analise-conformidade.md` — checklist de conformidade LGPD

**Gap:** Falta um documento formal de "secure coding guidelines" para onboarding de novos desenvolvedores. Não cobre práticas como: nunca usar `eval()`, sempre usar queries parametrizadas, validar input no backend, etc.

**Ação recomendada:** Criar `security/coding-guidelines.md` com regras práticas e exemplos de código.

**ASVS:** 1.1.7

---

### REQ-ARCH-006 [OK] — Segredos gerenciados via cofre (key vault)

**O que:** Todos os segredos (API keys, senhas de banco, tokens) são gerenciados fora do código-fonte.

**Como é atendido:**
- **Akeyless** com GitHub OIDC — path `/indiqr/*`
- Segredos nunca em código-fonte (`.gitignore` inclui `.env`)
- Variáveis de ambiente injetadas no runtime (Docker/Kubernetes)
- CI/CD busca secrets dinamicamente via Akeyless no estágio `staging-validation`

**ASVS:** 1.6.2, 2.10.4

---

### REQ-ARCH-007 [X] P1 — Política de ciclo de vida de chaves criptográficas

**O que:** Documentar e implementar política explícita de gerenciamento de chaves (geração, rotação, revogação, destruição).

**Gap:** Akeyless gerencia secrets de infraestrutura mas não há política documentada de ciclo de vida conforme NIST SP 800-57. Sem processo de rotação periódica de chaves JWT (local_jwks), sem processo de re-criptografia.

**Ação recomendada:** Documentar política em `security/key-management.md`. Implementar rotação automática de chaves `LOCAL_JWKS_JSON`.

**ASVS:** 1.6.1, 1.6.3

---

### REQ-ARCH-008 [OK] — Segregação de componentes com diferentes níveis de confiança

**O que:** Componentes com diferentes níveis de confiança são isolados.

**Como é atendido:**
- **Kubernetes (GKE):** namespace `indiqr` isolado
- **Cloudflare Pages:** frontend servido separadamente da API
- **Neon:** PostgreSQL serverless isolado
- **Docker:** containers isolados, staging separado de produção
- **3 modos de auth:** ambientes dev/staging/prod com configurações distintas

**ASVS:** 1.14.1, 1.14.5

---

### REQ-ARCH-009 [OK] — Classificação de dados sensíveis

**O que:** Dados sensíveis são identificados e classificados por nível de proteção.

**Como é atendido:**
- **`privacidade/politica-de-privacidade.md`** — categorias de dados coletados:
  - Dados de cadastro: email, nome
  - Dados de uso: campanhas, conversões, resgates
  - Dados financeiros: valores de remuneração, descontos, saldo de carteira

**Gap (documentado em `privacidade/analise-conformidade.md`):** Falta classificação técnica formal (PII, financeiro, auth) com níveis de proteção explícitos no código.

**Ação recomendada:** Ver [IND-46](/IND/issues/IND-46) — Análise de Conformidade LGPD.

**ASVS:** 1.8.1, 8.1.1

---

## SEC-AUTH — Autenticação

### REQ-AUTH-001 [OK] — Autenticação delegada a IdP único (Auth0)

**O que:** Toda autenticação é delegada ao Auth0 como único provedor de identidade.

**Como é atendido:**
- **Auth0 tenant compartilhado** (prefixo `indiqr-`)
- **3 modos de auth** via variável `AUTH_MODE`:
  - `auth0` — Produção, JWKS do tenant Auth0 (`app/api/v1/endpoints/auth.py`)
  - `local_jwks` — CI/staging, par RSA local (`/indiqr/LOCAL_JWKS_JSON`)
  - `mock` — Testes, `dependency_overrides`
- **Frontend:** `@auth0/auth0-react` SDK com Universal Login
- **Frontend:** Axios interceptor injeta Bearer token automaticamente (`frontend/architecture.md` §Interceptor Axios)
- **JWT RS256** com validação rigorosa de `aud`, `iss`, `exp` e assinatura

**ASVS:** 1.2.3, 1.2.4

---

### REQ-AUTH-002 [OK] — Validação rigorosa de JWT

**O que:** Todo token JWT é validado quanto a expiração, audience, issuer, assinatura e claims obrigatórias.

**Como é atendido:**
- **Arquivo:** `app/api/v1/endpoints/auth.py` — middleware de validação JWT
- **Testes:** `tests/security/test_jwt_validation.py` — 10 cenários:
  - Token expirado → 401
  - Audience errado → 401
  - Audience ausente → 401
  - Issuer errado → 401
  - Roles claim ausente → 403
  - Token malformado → 401
  - Token vazio → 401
  - Sem header Authorization → 401
  - Assinatura adulterada → 401
- **Config:** `AUTH0_ROLES_CLAIM = "https://indiqr.lealcyber.com/roles"`, `AUTH0_AUDIENCE = "https://indiqr-api.lealcyber.com"`

**ASVS:** 3.5.3, 13.2.1

---

### REQ-AUTH-003 [OK] — Provisionamento JIT de usuários

**O que:** Usuários são criados automaticamente no primeiro login autenticado.

**Como é atendido:**
- **Model:** `app/models/usuario.py` — `Usuario(id, email, auth_id)`
- **Fluxo:** Primeira requisição autenticada → verifica se `auth_id` existe → se não, cria `Usuario` com email do token
- **Sem contas default ou compartilhadas**

**ASVS:** 2.5.4

---

### REQ-AUTH-004 [X] P0 — Rate limiting para proteção contra brute force

**O que:** Limitar tentativas de autenticação e operações sensíveis para prevenir ataques de força bruta.

**Gap:**
- `behavior/security.md` §8 marca rate limiting como "condicional — implementar apenas se o rate-limiter estiver ativo no middleware"
- Sem implementação confirmada de rate limiting
- OTP de 6 dígitos sem rate limit é vulnerável a enumeração (espaço de apenas 1 milhão de combinações)
- Sem lockout após múltiplas falhas

**Ação recomendada:** Implementar rate limiting com slow down progressivo (exponencial) no middleware FastAPI. Máximo 100 tentativas/hora por conta. Header `Retry-After`. Prioritário para endpoints: `/redemptions/validate` (OTP), `/conversions/validate` (QRCode).

**ASVS:** 2.2.1, 13.1.4

---

### REQ-AUTH-005 [X] P1 — MFA (Multi-Factor Authentication)

**O que:** Exigir múltiplos fatores de autenticação, especialmente para ações administrativas.

**Gap:**
- Auth0 suporta MFA mas não está configurado como obrigatório para o tenant IndiQR
- Ações administrativas (criar campanha, gerenciar membros) não exigem step-up authentication
- Sem resistência a phishing via FIDO2/WebAuthn

**Ação recomendada:**
1. Habilitar MFA no tenant Auth0 para todos os usuários
2. Implementar step-up authentication para ações críticas (criar/remover membros, criar campanha, validar resgate de alto valor)
3. Avaliar suporte a FIDO2/WebAuthn para o futuro

**ASVS:** 2.2.4, 4.3.1, 4.3.3

---

### REQ-AUTH-006 [OK] — Tokens de convite e OTP com entropia e expiração

**O que:** Segredos gerados pelo sistema são aleatórios, com entropia suficiente e expiração curta.

**Como é atendido:**
- **Invitation tokens:** 32 caracteres URL-safe, não sequenciais (`app/models/company.py` — `Invitation.token`)
- **OTP de resgate:** 6 dígitos numéricos, gerado por `secrets` module (Python), expira em 15 minutos (`app/models/conversion.py` — `ResgateToken.code`, `ResgateToken.expires_at = created_at + 15 min`)
- **Short token de campanha:** 6 caracteres alfanuméricos (`[a-zA-Z0-9]`), espaço de 56 bilhões de combinações

**ASVS:** 2.3.1

---

### REQ-AUTH-007 [X] P0 — OTP armazenado com hash (não em texto plano)

**O que:** Códigos OTP devem ser armazenados com hash resistente a ataque offline, nunca em texto plano.

**Gap:** `ResgateToken.code` armazena o código OTP de 6 dígitos em texto plano no banco de dados. Se o banco for comprometido, todos os OTPs ativos são expostos.

**Ação recomendada:** Armazenar apenas `hash(code + salt)` no banco. Na validação, computar hash do código recebido e comparar. Incluir salt por token.

**ASVS:** 2.7.5

---

### REQ-AUTH-008 [OK] — OTP de uso único com proteção contra replay

**O que:** Códigos OTP são usáveis apenas uma vez dentro do período de validade.

**Como é atendido:**
- **Model:** `ResgateToken.status` — `pendente|usado|expirado`
- **Testes:** `tests/security/test_race_conditions.py` — `test_concurrent_validate_same_otp_one_succeeds` (3 validações simultâneas, apenas 1 sucede)
- **Imutabilidade:** ADR-007 — resgates são imutáveis após confirmação

**ASVS:** 2.7.3, 2.8.4

---

### REQ-AUTH-009 [OK] — Segredos de serviço nunca em código-fonte

**O que:** Credenciais de serviço (banco, email, Auth0 M2M) nunca armazenadas no repositório.

**Como é atendido:**
- **Akeyless** com GitHub OIDC para todos os secrets de infraestrutura (`/indiqr/*`)
- **Auth0 M2M:** `app/services/auth0_service.py` — tokens Machine-to-Machine, não credenciais fixas
- `.gitignore` inclui `.env`
- CI/CD com Gitleaks para detectar secrets expostos acidentalmente

**ASVS:** 2.10.1, 2.10.2, 2.10.3, 2.10.4

---

### REQ-AUTH-010 [X] P3 — Suporte a FIDO2/WebAuthn

**O que:** Suporte a autenticadores criptográficos (U2F, FIDO2) como segundo fator.

**Gap:** Sem suporte a hardware tokens ou WebAuthn. Fora do escopo do MVP.

**ASVS:** 2.3.2, 2.9.*

---

## SEC-SESSION — Gerenciamento de Sessão

### REQ-SESSION-001 [OK] — JWT em memória, nunca em storage persistente

**O que:** Tokens de sessão não são armazenados em localStorage, sessionStorage ou cookies.

**Como é atendido:**
- **Auth0 React SDK** (`@auth0/auth0-react`) gerencia o token em memória
- **Axios interceptor** (`frontend/architecture.md` §Interceptor Axios) injeta token via `getAccessTokenSilently()`
- Token nunca em URL parameters

**ASVS:** 3.1.1, 3.2.3

---

### REQ-SESSION-002 [OK] — Novo token gerado a cada autenticação

**O que:** Um novo token de sessão é gerado no login.

**Como é atendido:**
- Auth0 gera novo JWT a cada fluxo de autenticação (Universal Login)
- `getAccessTokenSilently()` para refresh silencioso
- Sem reutilização de tokens entre sessões

**ASVS:** 3.2.1

---

### REQ-SESSION-003 [OK] — Tokens com assinatura digital e proteção contra tampering

**O que:** Tokens stateless usam assinatura digital para prevenir adulteração.

**Como é atendido:**
- JWT RS256 com chave RSA 2048+ bits — entropia >> 64 bits
- Validação de assinatura em toda requisição (`app/api/v1/endpoints/auth.py`)
- `tests/security/test_jwt_validation.py` — `test_tampered_signature_returns_401`

**ASVS:** 3.2.2, 3.2.4, 3.5.3

---

### REQ-SESSION-004 [~] P1 — Invalidação de token no logout

**O que:** Logout deve invalidar o token, impedindo reutilização via back button.

**Como é parcialmente atendido:**
- Auth0 SDK redireciona para Universal Login no logout
- Token é removido da memória do browser

**Gap:** JWT permanece válido até expirar (`exp` claim). Não há endpoint de revogação server-side. Um token roubado pode ser reutilizado até expirar.

**Ação recomendada:** Implementar token revocation list (Redis) ou reduzir drasticamente o tempo de vida do token (15 min) com refresh token.

**ASVS:** 3.3.1

---

### REQ-SESSION-005 [X] P1 — Re-autenticação periódica

**O que:** Exigir re-autenticação após 12 horas ou 30 minutos de inatividade (ASVS L2).

**Gap:** Sem mecanismo de re-autenticação periódica. Validade do JWT depende da configuração do Auth0 (não documentada na spec).

**Ação recomendada:** Configurar `exp` do JWT para 30 minutos. Implementar refresh token com sliding expiration. Exigir re-login completo após 12 horas.

**ASVS:** 3.3.2

---

### REQ-SESSION-006 [X] P2 — Revogação de todas as sessões após troca de senha

**O que:** Oferecer opção de encerrar todas as sessões ativas após troca de senha.

**Gap:** Sem endpoint de revogação de tokens. Depende exclusivamente do Auth0.

**ASVS:** 3.3.3

---

### REQ-SESSION-007 [X] P3 — Dashboard de sessões ativas

**O que:** Usuário pode visualizar e encerrar sessões/dispositivos ativos.

**Gap:** Sem endpoint de sessões ativas. Sem visibilidade para o usuário.

**ASVS:** 3.3.4

---

## SEC-ACL — Controle de Acesso

### REQ-ACL-001 [OK] — RBAC com enforcement no backend

**O que:** Todas as verificações de acesso são feitas no servidor. Frontend guards são apenas UX.

**Como é atendido:**
- **Arquivo:** `app/policies/permissions.py` — função `require_permission("x:y")`
- **Matriz RBAC:** `behavior/rbac.md` — 3 roles (admin, influenciador, vendedor) com permissões granulares
- **Roles via Auth0:** `indiqr-admin`, `indiqr-influenciador`, `indiqr-vendedor`
- **Roles no JWT:** claim `https://indiqr.lealcyber.com/roles` assinada pelo Auth0
- **Frontend:** guards de role apenas para visibilidade de menu/rotas (UX); nunca como enforcement de segurança

**ASVS:** 1.4.1, 4.1.1, 4.1.2, 4.1.3

---

### REQ-ACL-002 [OK] — Mecanismo único de controle de acesso

**O que:** Um único ponto de verificação de acesso para todos os endpoints.

**Como é atendido:**
- `require_permission("x:y")` como ponto único de enforcement
- Matriz documentada em `behavior/rbac.md`:

| Permission | admin | influenciador | vendedor |
|------------|:-----:|:------------:|:--------:|
| `company:manage` | ✓ | — | — |
| `member:manage` | ✓ | — | — |
| `campaign:create` | ✓ | — | — |
| `campaign:read` | ✓ (todas) | ✓ (suas) | — |
| `campaign:close` | ✓ | ✓ (sair) | — |
| `conversion:validate` | — | — | ✓ |
| `conversion:read` | ✓ (todas) | ✓ (suas) | ✓ (suas) |
| `qrcode:download` | — | ✓ | — |

**ASVS:** 1.4.4, 4.1.4

---

### REQ-ACL-003 [OK] — Proteção contra IDOR (Insecure Direct Object Reference)

**O que:** Usuários não podem acessar recursos de outras empresas ou outros usuários.

**Como é atendido:**
- **Testes:** `tests/security/test_idor.py` — 15 cenários de cross-company access e enumeration resistance:
  - Cross-company members → 403
  - Cross-company invitations → 403
  - Cross-company campaigns → 403
  - Cross-company conversions → lista vazia
  - Cross-company redemption validation → 403
  - Cross-company token deletion → 403
  - Cross-company invitation cancellation → 404
- **Queries:** Todas as queries SQLAlchemy filtram por `company_id` do usuário autenticado

**ASVS:** 4.2.1

---

### REQ-ACL-004 [OK] — Enumeration resistance (403 vs 404)

**O que:** Respostas de erro não revelam existência de recursos de outras empresas.

**Como é atendido:**
- Recursos de outras empresas → 403 (não 404), impedindo enumeração de membros
- Campanhas inexistentes → 404 (distinção intencional — recursos internos)
- Convites de outras empresas → 404 (não revela existência)
- `tests/security/test_idor.py` — `test_member_list_no_enumeration`, `test_campaign_no_enumeration`, `test_conversion_no_enumeration`

**ASVS:** 4.2.1 (enumeration resistance)

---

### REQ-ACL-005 [OK] — Falha segura em controle de acesso

**O que:** Quando uma verificação de acesso falha, o sistema nega acesso de forma segura.

**Como é atendido:**
- Falha de permissão → 403 sem vazar existência do recurso
- Erro interno → 500 genérico (`{"detail": "Internal server error"}`)
- `tests/security/test_error_hardening.py` verifica supressão de stack traces
- Nenhuma informação de banco de dados ou Auth0 vaza em erros

**ASVS:** 4.1.5

---

### REQ-ACL-006 [X] P2 — Anti-CSRF para operações autenticadas

**O que:** Proteção contra Cross-Site Request Forgery.

**Gap:** SPA com JWT no header `Authorization` — CSRF não é vetor tradicional para APIs que não usam cookies. No entanto, não há token CSRF explícito para operações state-changing. Baixo risco prático devido ao modelo stateless, mas documentado para completude.

**ASVS:** 4.2.2

---

### REQ-ACL-007 [X] P2 — Step-up authentication para ações críticas

**O que:** Exigir re-autenticação ou fator adicional para operações de alto risco.

**Gap:** Sem step-up authentication. Operações como remover membro, encerrar campanha, validar resgate de alto valor não exigem confirmação adicional.

**Ação recomendada:** Implementar re-autenticação (senha ou OTP) antes de ações destrutivas ou de alto valor financeiro.

**ASVS:** 4.3.3

---

## SEC-INPUT — Validação e Sanitização de Entrada

### REQ-INPUT-001 [OK] — Validação de entrada no backend com tipos fortes

**O que:** Todo input do cliente é validado no servidor usando tipos fortes e allow lists.

**Como é atendido:**
- **Pydantic models** em todos os endpoints FastAPI com constraints:
  - `minLength`, `maxLength` — limites de tamanho
  - `pattern` — regex (`slug: ^[a-z0-9-]+$`, `code: ^\d{6}$`)
  - `enum` — valores permitidos (role, status, modelo)
  - `format` — validação de formato (email, uuid, date-time)
  - `minimum`, `maximum`, `exclusiveMinimum` — limites numéricos
- **OpenAPI spec:** `api/openapi.yaml` define constraints formais para todos os schemas
- **Frontend:** React Hook Form + Zod com regras equivalentes

**ASVS:** 1.5.3, 5.1.3, 5.1.4

---

### REQ-INPUT-002 [OK] — Proteção contra Mass Parameter Assignment

**O que:** Impedir que o cliente atribua campos não permitidos via binding automático.

**Como é atendido:**
- Pydantic models definem explicitamente quais campos são aceitos
- FastAPI rejeita campos não definidos no schema (comportamento padrão)
- Sem binding automático de `request.body` para models do SQLAlchemy

**ASVS:** 5.1.2

---

### REQ-INPUT-003 [OK] — Proteção contra HTTP Parameter Pollution

**O que:** Tratar corretamente parâmetros duplicados em query strings e formulários.

**Como é atendido:**
- `tests/security/test_input_sanitization.py` — `test_http_parameter_pollution` especificado
- Backend usa apenas o primeiro valor ou rejeita com 422

**ASVS:** 5.1.1

---

### REQ-INPUT-004 [OK] — Queries parametrizadas (SQL Injection prevention)

**O que:** Todas as queries de banco de dados usam parâmetros bind, nunca concatenação de strings.

**Como é atendido:**
- **SQLAlchemy 2.0 ORM** — todas as queries são parametrizadas por padrão
- `app/database/postgres.py` — engine + SessionLocal
- Sem SQL raw com concatenação de strings
- **Testes:** `tests/security/test_input_sanitization.py` — 4 cenários de SQL injection:
  - `test_sql_injection_company_name` — nome literal ou reject
  - `test_sql_injection_slug` — 422 (pattern)
  - `test_sql_injection_campaign_name` — 201 (literal) ou 422
  - `test_sql_injection_search_param` — 422 (page não inteiro)

**ASVS:** 5.3.4, 5.3.5

---

### REQ-INPUT-005 [OK] — Proteção contra XSS

**O que:** Prevenir injeção de scripts no frontend via escaping e sanitização.

**Como é atendido:**
- **React JSX:** escaping automático de todas as variáveis interpoladas em JSX
- **API retorna JSON** (não HTML) — responsabilidade de escaping no frontend
- **Testes:** `tests/security/test_input_sanitization.py` — 3 cenários XSS:
  - `test_xss_in_shop_name` — nome escapado
  - `test_xss_in_campaign_name` — nome escapado
  - `test_xss_in_company_name` — nome escapado
- Frontend Zod + React Hook Form para validação client-side

**ASVS:** 5.3.1, 5.3.2, 5.3.3

---

### REQ-INPUT-006 [OK] — Proteção contra template injection

**O que:** Impedir injeção em templates (email, PDF).

**Como é atendido:**
- **Emails:** `app/services/email_service.py` — templates com parâmetros tipados, sem interpolação de strings arbitrárias
- **PDF:** `app/services/card_pdf_service.py` — ReportLab com dados estruturados
- Sem templates server-side renderizados com input de usuário (SPA no frontend)

**ASVS:** 5.2.5

---

### REQ-INPUT-007 [OK] — Proteção contra SSRF

**O que:** Impedir que o servidor faça requisições para URLs controladas por usuários.

**Como é atendido:**
- Sem endpoints que aceitam URLs como parâmetro
- URLs externas são fixas (Auth0, Resend, Neon, R2, Grafana Cloud)
- Configurações de endpoints definidas em variáveis de ambiente

**ASVS:** 5.2.6

---

### REQ-INPUT-008 [OK] — Sem code execution dinâmico

**O que:** Não utilizar `eval()`, `exec()` ou funções similares.

**Como é atendido:**
- Backend Python sem `eval()`, `exec()`, `compile()` ou `__import__` dinâmico
- Frontend React sem `eval()` ou `dangerouslySetInnerHTML` (exceto se estritamente necessário e sanitizado)
- Pydantic para parsing de JSON (não `eval`)

**ASVS:** 5.2.4, 5.5.4

---

### REQ-INPUT-009 [OK] — Proteção contra JSON injection

**O que:** Parsing seguro de JSON, sem avaliação de código.

**Como é atendido:**
- FastAPI usa `jsonable_encoder` para serialização
- Pydantic valida estrutura e tipos antes de processar
- Frontend usa `JSON.parse` nativo via fetch/Axios

**ASVS:** 5.3.6

---

### REQ-INPUT-010 [OK] — Proteção contra desserialização insegura

**O que:** Não utilizar formatos de serialização perigosos com dados não confiáveis.

**Como é atendido:**
- Apenas JSON como formato de troca de dados
- Pydantic para validação e parsing de JSON
- Sem `pickle`, `marshal`, `yaml.load` (unsafe) ou serialização binária
- JWT com assinatura RS256 (verificada antes de decodificar)

**ASVS:** 1.5.2, 5.5.1, 5.5.3

---

### REQ-INPUT-011 [OK] — Proteção contra XXE (XML External Entity)

**O que:** Parsers XML configurados para prevenir entidades externas.

**Como é atendido:**
- Sem parsing de XML — JSON é o formato padrão
- FastAPI não expõe endpoints XML
- Sem bibliotecas de parsing XML na stack

**ASVS:** 5.5.2

---

### REQ-INPUT-012 [OK] — Limites de payload (tamanho e profundidade)

**O que:** Rejeitar payloads excessivamente grandes ou aninhados.

**Como é atendido:**
- `tests/security/test_input_sanitization.py`:
  - `test_large_json_payload_rejected` — 10MB → 413 ou 422
  - `test_deeply_nested_json_rejected` — 100 níveis → 422
- `MAX_UPLOAD_SIZE_MB` configurável (default 5 MB)
- FastAPI limita tamanho de corpo por padrão

**ASVS:** 5.1.4 (limites)

---

### REQ-INPUT-013 [OK] — Proteção contra command injection e LFI/RFI

**O que:** Impedir injeção de comandos de SO e inclusão de arquivos.

**Como é atendido:**
- Sem chamadas ao sistema operacional com input de usuário (`os.system`, `subprocess`)
- Sem inclusão de arquivos baseada em input de usuário
- QRCode e PDF gerados server-side via bibliotecas, sem caminhos de arquivo fornecidos pelo usuário

**ASVS:** 5.3.8, 5.3.9

---

## SEC-CRYPTO — Criptografia

### REQ-CRYPTO-001 [X] P1 — Criptografia em nível de aplicação para dados sensíveis em repouso

**O que:** Dados sensíveis (PII) devem ser criptografados em nível de aplicação, não apenas em nível de infraestrutura.

**Gap:**
- PostgreSQL Neon oferece criptografia server-side, mas sem criptografia em nível de coluna
- Dados como `Usuario.email` e valores financeiros (`Conversion.valor_bruto`, `Resgate.valor`) não são criptografados no banco

**Ação recomendada:** Implementar criptografia em nível de coluna usando AES-256-GCM com chaves gerenciadas via Akeyless. Priorizar: `Usuario.email`, valores financeiros.

**ASVS:** 6.1.1, 6.1.2, 6.1.3

---

### REQ-CRYPTO-002 [~] P2 — Uso de CSPRNG para todos os valores aleatórios

**O que:** Toda geração de valores aleatórios de segurança usa gerador criptograficamente seguro.

**Como é parcialmente atendido:**
- Python `secrets` module usado para OTP de resgate
- UUID via `uuid4()` para tokens
- JWT RS256 usa aleatoriedade criptográfica do Auth0

**Gap:** Verificar se todos os geradores aleatórios usam `secrets` (e não `random`). OTP de 6 dígitos (~20 bits de entropia) está no limite mínimo aceitável.

**Ação recomendada:** Auditoria de todos os usos de `random.*` no código. Substituir por `secrets.*` onde aplicável.

**ASVS:** 6.2.3, 6.2.8

---

### REQ-CRYPTO-003 [X] P2 — Algoritmos de criptografia autenticada (AEAD)

**O que:** Criptografia simétrica deve usar modos autenticados (GCM, CCM) com verificação de integridade.

**Gap:** Sem criptografia simétrica em nível de aplicação implementada. Quando implementada (REQ-CRYPTO-001), deve usar AES-256-GCM.

**Ação recomendada:** Especificar AES-256-GCM como algoritmo padrão para criptografia de dados em repouso.

**ASVS:** 6.2.5, 6.2.7

---

### REQ-CRYPTO-004 [X] P1 — Hash de OTP com salt

**O que:** Códigos OTP devem ser armazenados como hash (com salt), não em texto plano.

**Gap:** Mesmo gap de REQ-AUTH-007. `ResgateToken.code` armazenado em texto plano.

**Ação recomendada:** Implementar `hash(code + per_token_salt)` usando SHA-256. Salt único por token, armazenado junto ao hash.

**ASVS:** 2.7.5, 6.2.2

---

## SEC-ERROR — Tratamento de Erros e Logging

### REQ-ERROR-001 [OK] — Stack traces nunca retornados em produção

**O que:** Respostas de erro em produção não contêm stack traces, caminhos de arquivo ou detalhes internos.

**Como é atendido:**
- `tests/security/test_error_hardening.py` — 6 cenários:
  - `test_500_response_no_stack_trace` — apenas `{"detail": "Internal server error"}`
  - `test_422_response_no_internal_details` — apenas mensagens Pydantic
  - `test_database_error_no_leak` — sem nomes de tabela/coluna/constraint
  - `test_auth0_error_no_leak` — sem tenant, client_id ou token M2M
  - `test_debug_mode_disabled_in_production` — sem `X-Debug-*` headers
  - `test_server_header_not_versioned` — sem versão do servidor

**ASVS:** 7.2.1, 7.2.2, 7.2.3

---

### REQ-ERROR-002 [OK] — Dados sensíveis mascarados em logs

**O que:** Logs de aplicação nunca contêm tokens, códigos OTP ou segredos em texto plano.

**Como é atendido:**
- `tests/security/test_token_handling.py` — 5 cenários:
  - `test_otp_code_masked_in_application_logs` — código mascarado (`***921` ou `[REDACTED]`)
  - `test_otp_code_not_in_error_responses` — não ecoa código tentado
  - `test_qrcode_token_not_in_error_responses` — não ecoa token
  - `test_campaign_short_token_not_leaked_in_url_logs` — token mascarado
  - `test_invitation_token_not_leaked` — token não ecoado em 404

**ASVS:** 7.1.4

---

### REQ-ERROR-003 [OK] — Logs estruturados em JSON com rastreabilidade

**O que:** Logs em formato estruturado (JSON) com trace_id e request_id para correlação.

**Como é atendido:**
- **OpenTelemetry** → Grafana Cloud (Tempo + Loki)
- `app/core/telemetry.py` — configuração OTel (herdado do Recon)
- `app/core/logging_config.py` — JSON structured logging
- Campos: `trace_id`, `request_id`, timestamp, nível
- Middleware ASGI preserva contexto OTel entre requests
- `OTEL_SERVICE_NAME = "indiqr-api"`

**ASVS:** 1.7.1, 1.7.2, 7.1.1, 7.1.2

---

### REQ-ERROR-004 [OK] — Logs transmitidos para sistema remoto

**O que:** Logs são enviados para sistema centralizado de análise, fora do servidor de aplicação.

**Como é atendido:**
- OTel exporters → Grafana Cloud (Tempo para traces, Loki para logs)
- Logs não armazenados apenas localmente no container
- Acesso aos logs controlado via Grafana Cloud

**ASVS:** 7.4.1

---

### REQ-ERROR-005 [OK] — Logs de eventos de segurança

**O que:** Eventos de segurança (403, ações administrativas) são registrados nos logs.

**Como é atendido:**
- Middleware de logging captura todas as requisições/respostas
- Respostas 403 logadas com contexto do request
- Ações administrativas (criar empresa, convidar membro, criar campanha) logadas
- Campos incluídos: timestamp, IP, user ID (via trace_id), ação

**ASVS:** 7.3.2, 7.3.3, 7.3.4

---

### REQ-ERROR-006 [~] P2 — Logs de tentativas de autenticação inválidas

**O que:** Registrar tentativas de autenticação com credenciais inválidas para detecção de ataques.

**Como é parcialmente atendido:**
- Auth0 logging próprio captura tentativas de login
- IndiQR logging captura requests autenticados (com trace_id vinculado ao usuário)

**Gap:** Falta logging explícito de tentativas inválidas de autenticação na aplicação IndiQR (ex: OTP inválido, token expirado).

**ASVS:** 7.3.1

---

### REQ-ERROR-007 [X] P1 — Alertas de segurança configurados

**O que:** Alertas automáticos para eventos de segurança anômalos.

**Gap:** Sem alertas configurados no Grafana Cloud para eventos como:
- Múltiplas tentativas de OTP inválido (possível brute force)
- Acesso cross-company anômalo (possível IDOR probe)
- Picos de erros 401/403
- Criação massiva de campanhas ou convites

**Ação recomendada:** Configurar alertas no Grafana Cloud com thresholds e notificações (email/Slack).

**ASVS:** 7.4.4

---

### REQ-ERROR-008 [OK] — Proteção contra log injection

**O que:** Impedir que dados de usuário injetem entradas falsas ou quebrem o formato de logs.

**Como é atendido:**
- JSON structured logging — valores são automaticamente escapados no formato JSON
- Campos de log são estruturados, não concatenados como string
- Dados de input não controlam o formato dos logs

**ASVS:** 7.4.2

---

## SEC-DATA — Proteção de Dados

### REQ-DATA-001 [OK] — TLS em todas as conexões

**O que:** Todos os dados em trânsito são criptografados via TLS.

**Como é atendido:**
- **Frontend ↔ API:** HTTPS (Cloudflare ↔ GKE ingress)
- **API ↔ Auth0:** HTTPS com validação de certificado
- **API ↔ Neon (PostgreSQL):** TLS
- **API ↔ Resend (email):** HTTPS
- **API ↔ R2 (storage):** HTTPS
- **API ↔ Grafana Cloud:** HTTPS
- TLS 1.2+ em todas as conexões

**ASVS:** 8.2.1, 9.1.1, 9.1.2, 9.1.3

---

### REQ-DATA-002 [X] P2 — Cache-Control headers para dados sensíveis

**O que:** Respostas com dados pessoais ou financeiros devem incluir headers de cache apropriados.

**Gap:** Sem headers de cache configurados para endpoints com dados sensíveis. Respostas de API podem ser cacheadas por proxies intermediários.

**Ação recomendada:** Adicionar `Cache-Control: no-store, no-cache, must-revalidate, private` em endpoints com dados pessoais e financeiros.

**ASVS:** 8.3.5

---

### REQ-DATA-003 [X] P2 — Verificação de armazenamento em Web Storage

**O que:** Dados sensíveis não devem ser persistidos em localStorage ou sessionStorage.

**Como é parcialmente atendido:**
- JWT em memória via Auth0 SDK (OK)

**Gap:** Verificar se TanStack Query (React Query) não persiste cache com dados sensíveis em localStorage/sessionStorage. Sem auditoria formal.

**ASVS:** 8.3.6

---

### REQ-DATA-004 [~] P1 — Minimização de dados e classificação técnica

**O que:** Coletar apenas dados necessários. Classificar tecnicamente todos os dados.

**Como é parcialmente atendido:**
- `Usuario` model: apenas email + auth_id (mínimo necessário)
- `Company` model: name + slug

**Gap (documentado em `privacidade/analise-conformidade.md`):**
- Sem classificação técnica formal (PII, financeiro, auth) com níveis de proteção
- Sem endpoint de exclusão de dados (`DELETE /user/me`)
- Sem endpoint de exportação de dados (`GET /user/me/export`)
- Sem mecanismo de consentimento LGPD implementado

**Ação recomendada:** Ver [IND-46](/IND/issues/IND-46) — plano de ação detalhado.

**ASVS:** 8.1.1, 8.1.3

---

### REQ-DATA-005 [~] P2 — Consentimento LGPD implementado no código

**O que:** Mecanismos de coleta e registro de consentimento conforme LGPD.

**Como é parcialmente atendido:**
- Política de privacidade documentada em `privacidade/politica-de-privacidade.md`
- Análise de conformidade em `privacidade/analise-conformidade.md` (nota C)

**Gap:** Sem implementação no código. Sem campo `consentiu_privacy_policy` no modelo `Usuario`. Sem endpoint de consentimento.

**ASVS:** 8.1.1

---

## SEC-COMM — Comunicações

### REQ-COMM-001 [OK] — CORS restrito a origens autorizadas

**O que:** Cross-Origin Resource Sharing configurado apenas para origens permitidas.

**Como é atendido:**
- `tests/security/test_cors_headers.py` — 3 cenários:
  - `test_cors_preflight_returns_correct_headers` — origin `https://indiqr.lealcyber.com` → headers CORS corretos
  - `test_cors_disallowed_origin_blocked` — origin `https://evil.com` → sem headers CORS
  - `test_cors_credentials_header` — `Access-Control-Allow-Credentials: true` quando permitido
- Origens autorizadas: `https://indiqr.lealcyber.com`, `http://localhost:5174`
- Sem wildcard (`*`) CORS origins

**ASVS:** 14.3.3

---

### REQ-COMM-002 [OK] — Certificados TLS válidos e verificados

**O que:** Todos os certificados TLS são válidos, não expirados e verificados.

**Como é atendido:**
- Cloudflare fornece certificados para o frontend
- GKE ingress com certificados gerenciados
- Conexões externas com validação de certificado

**ASVS:** 9.2.1

---

### REQ-COMM-003 [X] P2 — HSTS (HTTP Strict Transport Security)

**O que:** Header HSTS força navegadores a usar apenas HTTPS.

**Gap:** Cloudflare suporta HSTS mas sem verificação de configuração ativa. Sem header `Strict-Transport-Security` confirmado.

**Ação recomendada:** Habilitar HSTS no Cloudflare (incluindo `includeSubDomains` e `preload`).

**ASVS:** 9.2.3

---

### REQ-COMM-004 [X] P0 — Headers de segurança HTTP

**O que:** Configurar headers de segurança HTTP na API e frontend.

**Gap:** Nenhum dos seguintes headers está configurado:
- `Content-Security-Policy` — prevenção de XSS
- `X-Content-Type-Options: nosniff` — prevenção de MIME sniffing
- `X-Frame-Options: DENY` — prevenção de clickjacking
- `Referrer-Policy: strict-origin-when-cross-origin` — controle de referrer
- `Permissions-Policy` — restrição de APIs do browser

**Ação recomendada:** Configurar no ingress (GKE) ou no middleware FastAPI. Para o frontend, configurar via Cloudflare Pages headers ou meta tags.

**ASVS:** 13.2.4, 14.1.2

---

## SEC-BIZ — Lógica de Negócio

### REQ-BIZ-001 [OK] — Workflows de negócio com validação de estado

**O que:** Transições de estado seguem sequências definidas e são validadas.

**Como é atendido:**
- **Campanha:** `aguardando_aceite` → `ativa` → `encerrada`
- **Convite:** `pending` → `accepted` | `revoked`
- **QRCode:** `active` → `inactive` (após conversão)
- **ResgateToken:** `pendente` → `usado` | `expirado`
- Verificações de status em cada transição (ex: campanha ativa não pode ser aceita novamente)
- Documentado em `behavior/campaigns.md`, `behavior/companies.md`, `behavior/redemptions.md`

**ASVS:** 11.2.2, 11.2.4

---

### REQ-BIZ-002 [OK] — Registros financeiros imutáveis

**O que:** Conversões e resgates são imutáveis após confirmação.

**Como é atendido:**
- **ADR-004:** `Conversion` — sem `updated_at`, sem cancelamento/estorno no MVP
- **ADR-007:** `Resgate` — sem `updated_at`, imutável após confirmação
- **Testes:** `tests/security/test_race_conditions.py` — atomicidade verificada

**ASVS:** 11.2.1

---

### REQ-BIZ-003 [OK] — Proteção contra race conditions em operações concorrentes

**O que:** Operações de alto valor (conversão, resgate) são atômicas e resistentes a condições de corrida.

**Como é atendido:**
- `tests/security/test_race_conditions.py` — 5 cenários:
  - `test_concurrent_validate_same_qrcode_one_succeeds` — 5 validações simultâneas, apenas 1 sucede
  - `test_concurrent_validate_different_qrcodes_all_succeed` — 5 QRCodes diferentes, todos sucedem
  - `test_concurrent_validate_same_otp_one_succeeds` — 3 validações simultâneas, apenas 1 sucede
  - `test_concurrent_token_generation_same_type` — apenas 1 token ativo por tipo
  - `test_concurrent_accept_same_invitation_one_succeeds` — 2 aceites simultâneos, apenas 1 sucede

**ASVS:** 1.11.2, 1.11.3

---

### REQ-BIZ-004 [~] P2 — Limites de negócio (rate limiting de operações)

**O que:** Limitar frequência de operações de negócio para prevenir abuso.

**Como é parcialmente atendido:**
- `page_size` limitado a 1-100 (pagination)
- Paginação em todos os endpoints de lista

**Gap:** Sem limites em:
- Número de campanhas por empresa
- Convites por hora
- Geração de tokens OTP por influenciador
- Criação de empresas por usuário

**Ação recomendada:** Implementar limites de negócio no backend: máximo de campanhas ativas por empresa, máximo de convites por hora, cooldown entre gerações de OTP.

**ASVS:** 11.1.1, 11.2.5

---

## SEC-FILES — Arquivos e Recursos

### REQ-FILES-001 [OK] — Downloads com Content-Type correto

**O que:** Arquivos servidos pela aplicação usam Content-Type apropriado.

**Como é atendido:**
- **QRCode PNG:** `app/services/qrcode_service.py` — `Content-Type: image/png`
- **Card PDF:** `app/services/card_pdf_service.py` — `Content-Type: application/pdf`
- Ambos gerados on-the-fly (não armazenados em disco)

**ASVS:** 12.2.1

---

### REQ-FILES-002 [~] P1 — Validação de upload de arquivos

**O que:** Uploads de arquivo devem ser validados quanto a tipo, tamanho e conteúdo.

**Como é parcialmente atendido:**
- `MAX_UPLOAD_SIZE_MB` configurável (default 5 MB) — planejado para upload de mídia da vitrine (P2)

**Gap:** Upload de mídia ainda não implementado no MVP. Quando implementado, precisa de:
1. Validação de tipo MIME (allow list: image/png, image/jpeg, image/webp)
2. Scan de malware (ClamAV ou similar)
3. Sanitização de nomes de arquivo (UUID)
4. Armazenamento em R2 (fora da raiz web)
5. CSP header para domínio de mídia separado

**ASVS:** 12.1.1, 12.1.2, 12.1.3, 12.3.1, 12.3.3

---

## SEC-CONFIG — Configuração Segura

### REQ-CONFIG-001 [OK] — Build pipeline com verificações de segurança

**O que:** Pipeline de CI/CD inclui verificações automáticas de segurança.

**Como é atendido:**
- **Gitleaks** — detecção de secrets no código-fonte
- **Trivy** — scan de vulnerabilidades em containers
- **Ruff** — linting Python
- **Bandit** — SAST Python (análise estática de segurança)
- **Schemathesis** — contract fuzzing contra OpenAPI spec
- **Spectral** — linting de OpenAPI spec
- GHCR com SHA tags para rastreabilidade

**ASVS:** 1.14.3, 1.14.4, 10.2.1, 10.2.2

---

### REQ-CONFIG-002 [OK] — Separação de ambientes

**O que:** Ambientes dev, staging e produção são separados.

**Como é atendido:**
- 3 modos de auth: `auth0` (prod) / `local_jwks` (staging) / `mock` (test)
- Kubernetes namespace `indiqr` (GKE)
- Docker/docker-compose para staging
- Preview deploys Cloudflare Pages para PRs
- Staging validation no pipeline antes do deploy

**ASVS:** 14.2.4

---

### REQ-CONFIG-003 [OK] — Containers non-root

**O que:** Containers não executam como root.

**Como é atendido:**
- Docker images configuradas com `USER` não-root (herdado do framework Recon)
- Kubernetes security context com `runAsNonRoot: true`

**ASVS:** 14.4.1

---

### REQ-CONFIG-004 [OK] — Informações de versão não expostas

**O que:** Headers de resposta não revelam versão do servidor ou tecnologia.

**Como é atendido:**
- `tests/security/test_error_hardening.py` — `test_server_header_not_versioned`
- Sem `X-Powered-By` header
- Sem `Server` header com versão

**ASVS:** 14.3.1

---

### REQ-CONFIG-005 [OK] — Métodos HTTP controlados

**O que:** Apenas métodos HTTP necessários são expostos.

**Como é atendido:**
- FastAPI expõe apenas GET, POST, DELETE (conforme OpenAPI spec)
- Sem métodos órfãos ou automáticos
- OPTIONS para CORS preflight

**ASVS:** 14.3.2

---

### REQ-CONFIG-006 [OK] — Dependências monitoradas

**O que:** Dependências de terceiros são monitoradas para vulnerabilidades conhecidas.

**Como é atendido:**
- Trivy scan no CI/CD (container vulnerability)
- Dependabot disponível via GitHub
- Dependências versionadas em requirements.txt/package.json

**ASVS:** 14.2.1

---

### REQ-CONFIG-007 [X] P3 — Containers com filesystem read-only

**O que:** Filesystem dos containers deve ser read-only quando possível.

**Gap:** Containers sem filesystem read-only configurado. QRCode/PDF gerados em memória (não gravam em disco), então o requisito é viável.

**Ação recomendada:** Configurar `readOnlyRootFilesystem: true` no security context do Kubernetes.

**ASVS:** 14.4.2

---

### REQ-CONFIG-008 [~] P2 — Revisão periódica de hardening

**O que:** Configurações de segurança são revisadas periodicamente.

**Como é parcialmente atendido:**
- CI/CD executa verificações a cada push/PR
- Pipeline cobre SAST, SCA, secret scanning e contract testing

**Gap:** Sem processo formal de revisão periódica de hardening (ex: quarterly security review). Sem checklist de hardening do Kubernetes, Docker, PostgreSQL.

**ASVS:** 14.2.3

---

## SEC-API — API e Web Services

### REQ-API-001 [OK] — OpenAPI spec completa e atualizada

**O que:** API documentada em formato OpenAPI, mantida sincronizada com a implementação.

**Como é atendido:**
- `api/openapi.yaml` — OpenAPI 3.0.3, 1102 linhas
- Documenta todos os endpoints, schemas, parâmetros e security schemes
- Schemathesis valida implementação contra spec (contract testing)
- Spectral linting da spec

**ASVS:** 13.1.1

---

### REQ-API-002 [OK] — Autenticação em todos os endpoints (exceto health)

**O que:** Todos os endpoints exigem autenticação, exceto os explicitamente públicos.

**Como é atendido:**
- `security: bearerAuth: []` no OpenAPI — aplicado globalmente
- `GET /health` — único endpoint sem auth
- Convite preview (`GET /companies/invitations/preview/{token}`) — público por design

**ASVS:** 13.1.5

---

### REQ-API-003 [OK] — Validação de schema JSON

**O que:** Toda requisição é validada contra schema antes de ser processada.

**Como é atendido:**
- FastAPI + Pydantic validam automaticamente request bodies contra modelos
- OpenAPI spec define schemas formais
- Schemathesis faz fuzzing para detectar desvios

**ASVS:** 13.1.3

---

### REQ-API-004 [OK] — Uso correto de métodos HTTP

**O que:** API RESTful usa métodos HTTP com semântica correta.

**Como é atendido:**
- GET — leitura (idempotente)
- POST — criação
- DELETE — remoção
- Semântica documentada no OpenAPI
- Sem GET para operações mutáveis

**ASVS:** 13.2.3

---

### REQ-API-005 [OK] — Mensagens de erro sem detalhes internos

**O que:** Respostas de erro da API não revelam stack traces, queries ou detalhes de infraestrutura.

**Como é atendido:**
- 500 → `{"detail": "Internal server error"}`
- 422 → apenas campos Pydantic com erro
- 401 → "Token expirado" / "Token inválido" (sem detalhes do token)
- `tests/security/test_error_hardening.py` — 6 cenários de verificação

**ASVS:** 13.4.2

---

## Resumo de Gaps — Backlog Prioritizado

### P0 — Crítico (risco imediato, implementar primeiro)

| Gap | Requisito | Descrição |
|-----|-----------|-----------|
| **Rate limiting** | REQ-AUTH-004, REQ-API-004 | Sem proteção contra brute force. OTP de 6 dígitos vulnerável. |
| **OTP em texto plano** | REQ-AUTH-007, REQ-CRYPTO-004 | `ResgateToken.code` sem hash. DB comprometido = todos OTPs expostos. |
| **Headers de segurança HTTP** | REQ-COMM-004 | Sem CSP, HSTS, X-Content-Type-Options, X-Frame-Options. |

### P1 — Alto (implementar em até 30 dias)

| Gap | Requisito | Descrição |
|-----|-----------|-----------|
| **Threat Modeling** | REQ-ARCH-002 | Sem processo formal de modelagem de ameaças. |
| **Política de chaves criptográficas** | REQ-ARCH-007 | Sem política de ciclo de vida de chaves. |
| **MFA** | REQ-AUTH-005 | Sem MFA configurado como obrigatório. |
| **Criptografia em repouso** | REQ-CRYPTO-001 | Sem criptografia em nível de coluna para PII. |
| **Re-autenticação periódica** | REQ-SESSION-005 | Sem re-autenticação após 12h/30min. |
| **Alertas de segurança** | REQ-ERROR-007 | Sem alertas para eventos anômalos. |
| **Validação de upload** | REQ-FILES-002 | Upload de mídia sem validação de tipo/scan. |

### P2 — Médio (implementar em até 60 dias)

| Gap | Requisito | Descrição |
|-----|-----------|-----------|
| **Guia de codificação segura** | REQ-ARCH-005 | Sem documento formal para onboarding. |
| **Revogação de token no logout** | REQ-SESSION-004 | JWT válido até expirar. |
| **Anti-CSRF** | REQ-ACL-006 | Sem token CSRF explícito. |
| **Step-up authentication** | REQ-ACL-007 | Sem re-autenticação para ações críticas. |
| **CSPRNG auditoria** | REQ-CRYPTO-002 | Verificar uso de `secrets` vs `random`. |
| **Cache-Control headers** | REQ-DATA-002 | Sem headers de cache para dados sensíveis. |
| **Web Storage auditoria** | REQ-DATA-003 | Verificar TanStack Query persistência. |
| **Limites de negócio** | REQ-BIZ-004 | Sem limites em campanhas/convites. |
| **Revisão de hardening** | REQ-CONFIG-008 | Sem processo formal de revisão. |

### P3 — Baixo (roadmap, implementar quando possível)

| Gap | Requisito | Descrição |
|-----|-----------|-----------|
| **HSTS** | REQ-COMM-003 | Habilitar via Cloudflare. |
| **Revogação de todas as sessões** | REQ-SESSION-006 | Após troca de senha. |
| **Dashboard de sessões ativas** | REQ-SESSION-007 | Visibilidade para usuário. |
| **FIDO2/WebAuthn** | REQ-AUTH-010 | Suporte futuro. |
| **Filesystem read-only** | REQ-CONFIG-007 | Containers Kubernetes. |

---

## Metodologia

Esta especificação foi elaborada a partir de:

1. **OWASP ASVS 4.0.3** — Application Security Verification Standard, Nível 2
2. **Análise documental** do repositório `indiqr-spec`:
   - `architecture.md` — arquitetura completa
   - `frontend/architecture.md` — arquitetura frontend
   - `behavior/security.md` — especificação de testes de segurança
   - `behavior/rbac.md` — matriz de controle de acesso
   - `api/openapi.yaml` — contrato da API (OpenAPI 3.0.3)
   - `decisions/001-007-*.md` — ADRs
   - `privacidade/analise-conformidade.md` — análise LGPD
3. **Estrutura de diretórios** e stack conforme `architecture.md`
4. **Evidências de implementação** extraídas dos arquivos de spec, testes e configuração

**Referências cruzadas:**
- [IND-46](/IND/issues/IND-46) — Análise de Conformidade LGPD
- [IND-48](/IND/issues/IND-48) — Benchmark OWASP ASVS (origem desta especificação)
- [IND-44](/IND/issues/IND-44) — Implementação da suíte de testes de segurança
