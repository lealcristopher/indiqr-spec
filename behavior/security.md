# Security — Especificação de Testes

> Área P2 do plano de cobertura IND-38. Define os cenários de teste de segurança
> para a nova camada `tests/security/`, cobrindo OWASP top-10, IDOR, JWT, race
> conditions e práticas de hardening.

---

## Estrutura

Os testes de segurança residem em `tests/security/` no repositório `api-indiqr`:

```
tests/security/
├── conftest.py
├── test_token_handling.py
├── test_error_hardening.py
├── test_idor.py
├── test_jwt_validation.py
├── test_race_conditions.py
├── test_input_sanitization.py
└── test_cors_headers.py
```

---

## 1. Token Handling (`test_token_handling.py`)

### OTP not leaked in logs

- [ ] `test_otp_code_masked_in_application_logs`
  Configurar log capture (caplog fixture). Gerar código OTP via
  `/redemptions/tokens`. Verificar que os logs do request e response
  NÃO contêm o código de 6 dígitos em texto plano. Verificar que
  aparece mascarado (ex: `***921` ou `[REDACTED]`).

- [ ] `test_otp_code_not_in_error_responses`
  Enviar código inválido para `/redemptions/validate`. Verificar que
  a resposta de erro NÃO ecoa o código tentado. Mensagem deve ser
  genérica: "Código inválido" (sem repetir o valor recebido).

- [ ] `test_qrcode_token_not_in_error_responses`
  Enviar QRCode token inválido para `/conversions/preview`. Resposta
  NÃO deve ecoar o token no corpo ou headers.

### Short token handling

- [ ] `test_campaign_short_token_not_leaked_in_url_logs`
  Acessar `/campaigns/public/{short_token}`. Verificar que logs de
  acesso (middleware log) não registram o token completo. Parâmetros
  de path sensíveis devem ser mascarados.

- [ ] `test_invitation_token_not_leaked`
  Acessar `/companies/invitations/preview/{token}`. Resposta de erro
  404 não ecoa o token.

---

## 2. Error Hardening (`test_error_hardening.py`)

### No stack traces in error responses

- [ ] `test_500_response_no_stack_trace`
  Provocar erro interno (ex: desligar mock do DB, injetar exceção via
  dependency override). Verificar que a resposta 500 contém apenas
  `{"detail": "Internal server error"}` sem traceback, nomes de
  arquivo, ou caminhos do servidor.

- [ ] `test_422_response_no_internal_details`
  Enviar payload JSON malformado. Verificar que resposta 422 contém
  apenas mensagens de validação do Pydantic, sem stack trace.

- [ ] `test_database_error_no_leak`
  Simular erro de constraint UNIQUE no PostgreSQL. Verificar que a
  resposta não vaza o nome da tabela, coluna, ou constraint. Mensagem
  amigável: "Recurso já existe" ou similar.

- [ ] `test_auth0_error_no_leak`
  Simular falha na Auth0 Management API. Resposta não vaza tenant
  name, client ID, ou token M2M. Mensagem genérica: "Erro de
  autorização — tente novamente".

### Debug information

- [ ] `test_debug_mode_disabled_in_production`
  Verificar que `DEBUG=False` (ou equivalente) impede respostas com
  debug toolbar, `X-Debug-*` headers, ou modo verbose de exceções.

- [ ] `test_server_header_not_versioned`
  Verificar que headers de resposta não incluem versão do servidor.
  `Server` header deve ser genérico ou ausente.

---

## 3. IDOR — Insecure Direct Object Reference (`test_idor.py`)

### Cross-company access

- [ ] `test_cannot_access_other_company_members`
  Usuário da empresa A tenta `GET /companies/{company_B_id}/members` → 403.

- [ ] `test_cannot_access_other_company_invitations`
  Usuário da empresa A tenta `GET /companies/{company_B_id}/invitations` → 403.

- [ ] `test_cannot_access_other_campaign`
  Influenciador da empresa A tenta `GET /campaigns/{campaign_B_id}` → 403.
  (campaign_B pertence à empresa B)

- [ ] `test_cannot_access_other_conversion`
  Vendedor da empresa A tenta `GET /conversions/` e recebe apenas
  conversões próprias (da empresa A). Nenhuma conversão da empresa B
  aparece na listagem.

- [ ] `test_cannot_validate_redemption_other_company`
  Vendedor da empresa A tenta `POST /redemptions/validate` com código
  gerado por influenciador da empresa B → 403.

- [ ] `test_cannot_delete_other_redemption_token`
  Influenciador A tenta `DELETE /redemptions/tokens/{token_B_id}` → 403.

- [ ] `test_cannot_cancel_other_invitation`
  Admin da empresa A tenta `DELETE /companies/{company_A_id}/invitations/{invitation_B_id}`
  (invitation_B pertence à empresa B) → 404 (não revela existência).

### Enumeration resistance

- [ ] `test_member_list_no_enumeration`
  Acessar `GET /companies/{company_id}/members` com ID de empresa que
  existe mas usuário não é membro → 403 (não 404). Sem distinção entre
  "não existe" e "sem acesso".

- [ ] `test_campaign_no_enumeration`
  Acessar `GET /campaigns/{id}` de campanha de outra empresa → 403.
  `GET /campaigns/{id}` de campanha inexistente → 404. O atacante não
  consegue distinguir entre campanha inexistente e sem acesso? (Sim —
  nesse caso o comportamento é diferente por design, pois campanhas
  são recursos internos.)

- [ ] `test_conversion_no_enumeration`
  `GET /conversions/` com campaign_id de outra empresa → lista vazia
  (não 403, para não revelar existência da campanha).

---

## 4. JWT Validation (`test_jwt_validation.py`)

### Token expiration

- [ ] `test_expired_token_returns_401`
  Gerar JWT com `exp` no passado (via local_jwks ou mock). Chamar
  qualquer endpoint autenticado → 401. Mensagem: "Token expirado".

- [ ] `test_expired_token_specific_message`
  Verificar que mensagem 401 é informativa mas não vaza detalhes do
  token: algo como `{"detail": "Token has expired"}`.

### Invalid audience

- [ ] `test_wrong_audience_returns_401`
  Gerar JWT com `aud` diferente de `https://indiqr-api.lealcyber.com`
  (ex: `https://outro-servico.lealcyber.com`). Chamar endpoint → 401.
  Mensagem: "Token audience inválido".

- [ ] `test_missing_audience_returns_401`
  JWT sem claim `aud` → 401.

### Invalid issuer

- [ ] `test_wrong_issuer_returns_401`
  JWT com `iss` diferente do esperado → 401.

### Missing roles claim

- [ ] `test_missing_roles_claim_returns_403`
  JWT válido mas sem a claim `https://indiqr.lealcyber.com/roles` →
  403. Mensagem: "Permissão insuficiente".

### Malformed token

- [ ] `test_malformed_token_returns_401`
  Header `Authorization: Bearer not-a-jwt` → 401.

- [ ] `test_empty_token_returns_401`
  Header `Authorization: Bearer ` (vazio) → 401.

- [ ] `test_no_auth_header_returns_401`
  Sem header Authorization → 401.

### Signature tampering

- [ ] `test_tampered_signature_returns_401`
  JWT com último caractere alterado → 401. Mensagem: "Token inválido".

---

## 5. Race Conditions (`test_race_conditions.py`)

### Concurrent conversion validation

- [ ] `test_concurrent_validate_same_qrcode_one_succeeds`
  Disparar 5 validações simultâneas (`asyncio.gather`) do mesmo
  QRCode token (ativo). Apenas 1 deve retornar 201. As demais
  retornam 409 ou 422.
  Verificar que apenas 1 registro `Conversion` foi criado no banco.
  Verificar que `QRCode.active` passou para `false`.

- [ ] `test_concurrent_validate_different_qrcodes_all_succeed`
  5 QRCodes ativos diferentes, validações simultâneas → todas 201.
  Verificar 5 conversões criadas.

### Concurrent redemption validation

- [ ] `test_concurrent_validate_same_otp_one_succeeds`
  Disparar 3 validações simultâneas do mesmo código OTP pendente.
  Apenas 1 → 201. Demais → 422 ("Código já utilizado").
  Verificar que apenas 1 `Resgate` foi criado.

### Concurrent token generation

- [ ] `test_concurrent_token_generation_same_type`
  Influenciador gera 2 tokens simultâneos do mesmo tipo.
  Apenas 1 token ativo ao final; o anterior foi cancelado ou o
  segundo rejeitado com 409 ("token ativo existente").

### Concurrent invitation acceptance

- [ ] `test_concurrent_accept_same_invitation_one_succeeds`
  2 chamadas simultâneas para `POST /companies/invitations/{token}/accept`.
  Apenas 1 → 200. Outra → 404 ou 409.

---

## 6. Input Sanitization (`test_input_sanitization.py`)

### SQL injection

- [ ] `test_sql_injection_company_name`
  `POST /companies/` com body `{"name": "'; DROP TABLE companies; --", "slug": "test"}`.
  Deve criar empresa com nome literal ou rejeitar na validação.
  Verificar que tabela `companies` ainda existe após o request.

- [ ] `test_sql_injection_slug`
  `slug` com `"1; DELETE FROM companies WHERE 1=1"` → 422 (slug
  inválido, pattern `^[a-z0-9-]+$`).

- [ ] `test_sql_injection_campaign_name`
  Campanha com nome contendo SQL injection → 201 (nome literal)
  ou 422.

- [ ] `test_sql_injection_search_param`
  `GET /companies/?page=1 OR 1=1` → 422 (page não inteiro).

### XSS

- [ ] `test_xss_in_shop_name`
  Criar produto com nome `<script>alert(1)</script>`. GET /shop/mine
  retorna o nome escapado ou sanitizado. O conteúdo HTML não deve
  ser interpretável.

- [ ] `test_xss_in_campaign_name`
  Criar campanha com nome contendo HTML. GET /campaigns retorna nome
  escapado.

- [ ] `test_xss_in_company_name`
  Criar empresa com nome HTML. Resposta JSON deve conter o texto
  escapado.

### Parameter pollution

- [ ] `test_http_parameter_pollution`
  Enviar `?role=admin&role=vendedor` no convite. O backend deve usar
  apenas o primeiro ou rejeitar com 422.

### Large payloads

- [ ] `test_large_json_payload_rejected`
  Enviar JSON com 10MB de dados. Verificar que FastAPI rejeita com
  413 ou 422 antes de processar.

- [ ] `test_deeply_nested_json_rejected`
  Enviar JSON com 100 níveis de nesting. Não causa stack overflow.
  Resposta 422 ou timeout via middleware.

---

## 7. CORS Headers (`test_cors_headers.py`)

- [ ] `test_cors_preflight_returns_correct_headers`
  `OPTIONS /api/v1/companies/` com `Origin: https://indiqr.lealcyber.com`
  → 200. Headers: `Access-Control-Allow-Origin`, `Access-Control-Allow-Methods`,
  `Access-Control-Allow-Headers`.

- [ ] `test_cors_disallowed_origin_blocked`
  `Origin: https://evil.com` → CORS headers ausentes ou `Access-Control-Allow-Origin`
  não é `*` nem `https://evil.com`.

- [ ] `test_cors_credentials_header`
  Resposta inclui `Access-Control-Allow-Credentials: true` quando
  origin é permitida.

---

## 8. Rate Limiting (se implementado)

> Marcado como condicional — implementar apenas se o rate-limiter
> estiver ativo no middleware.

- [ ] `test_rate_limit_on_brute_force_otp`
  20 tentativas de `POST /redemptions/validate` com códigos aleatórios
  em 10 segundos → 429 após o limite. Verificar header `Retry-After`.

- [ ] `test_rate_limit_reset`
  Após retry-after, novas tentativas são aceitas.

---

## Dependências de Teste

- **pytest-asyncio** para testes de race condition
- **caplog fixture** (built-in pytest) para captura de logs
- **httpx.AsyncClient** para enviar requests simultâneos
- **factory fixtures** existentes (create_company, create_campaign, etc.)
- **local_jwks** (`AUTH_MODE=local_jwks`) para gerar JWTs com claims
  arbitrárias nos testes de JWT validation
