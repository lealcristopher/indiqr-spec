# Consentimento — Regras de Negócio (LGPD Arts. 7-8)

## Base Legal (LGPD)

| Artigo | Dispositivo | Requisito |
|--------|------------|-----------|
| Art. 7, I | Consentimento do titular | Consentimento prévio, livre, informado e inequívoco |
| Art. 8, caput | Manifestação | Consentimento por escrito ou outro meio que demonstre vontade |
| Art. 8, §2 | Ônus da prova | Controlador deve comprovar que o consentimento foi obtido |
| Art. 8, §5 | Revogação | Consentimento é revogável a qualquer momento |
| Art. 18, IX | Direito do titular | Revogar consentimento a qualquer momento |

## Tipos de Consentimento

A plataforma opera com 3 tipos distintos de consentimento:

| Tipo | Constante | Descrição | Base Legal (LGPD) |
|------|-----------|-----------|-------------------|
| `privacy_policy` | Política de Privacidade | Aceite da política de privacidade da plataforma | Art. 7, I |
| `shop_publication` | Vitrine Pública | Autorização para exposição pública dos dados da vitrine (Shop) | Art. 7, I |
| `transactional_emails` | Emails Transacionais | Autorização para recebimento de emails transacionais (convites, notificações) | Art. 7, I |

Cada tipo é independente: revogar um não afeta os outros. O titular pode gerenciar cada consentimento separadamente (LGPD Art. 8, §5: revogação granular).

## Modelo Usuario — Campos de Consentimento

### Campos legados (backward-compatible)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `consentiu_privacy_policy` | `boolean` | Indica se o usuário consentiu com a política de privacidade |
| `consentiu_privacy_policy_at` | `datetime` (nullable) | Timestamp do último consentimento |
| `privacy_policy_version` | `string` (nullable) | Versão da política aceita (ex: `v2.0`) |

### Registro de consentimento (novo — F3)

Cada consentimento é armazenado como um registro independente (`consent_records`) com:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `type` | `enum` | Tipo de consentimento (`privacy_policy`, `shop_publication`, `transactional_emails`) |
| `granted` | `boolean` | Status atual do consentimento |
| `version` | `string` (nullable) | Versão da política/documento aceito |
| `granted_at` | `datetime` | Timestamp da concessão |
| `ip_address` | `string` (nullable) | IP de origem |

### Regras

- `consentiu_privacy_policy` deve ser `false` por default (opt-in — LGPD Art. 7, I)
- Nenhum tratamento de dados pessoais (exceto autenticação essencial) pode ocorrer antes do consentimento
- Se `privacy_policy_version` armazenada for inferior à versão atual, o frontend deve solicitar renovação do consentimento
- Consentimentos de tipos diferentes são independentes: revogar `shop_publication` não afeta `privacy_policy`

## GET /user/me/consent — Listar Consentimentos Ativos

### Comportamento

1. Usuário autenticado consulta seus consentimentos
2. Backend retorna array de `ConsentRecord` com todos os consentimentos ativos
3. Consentimentos revogados não aparecem na listagem

### Resposta (200)

```json
{
  "consents": [
    {
      "type": "privacy_policy",
      "granted": true,
      "version": "v2.0",
      "granted_at": "2026-06-10T14:30:00Z",
      "ip_address": "192.0.2.1"
    },
    {
      "type": "shop_publication",
      "granted": true,
      "version": null,
      "granted_at": "2026-06-10T14:35:00Z",
      "ip_address": "192.0.2.1"
    }
  ]
}
```

### Validações

| Regra | Código |
|-------|--------|
| Usuário deve estar autenticado | 401 |

### RBAC

- Qualquer usuário autenticado pode listar os próprios consentimentos

## PUT /user/me/consent — Registrar Consentimento

### Comportamento

1. Usuário autenticado envia `{ "privacy_policy_version": "v2.0", "types": ["privacy_policy", "transactional_emails"] }`
2. Backend registra consentimento para cada tipo solicitado:
   - `privacy_policy`: atualiza campos legados (`consentiu_privacy_policy = true`, etc.)
   - `shop_publication`: registra no modelo `Shop`
   - `transactional_emails`: registra preferência de email
3. Backend gera 1 entrada de auditoria por tipo de consentimento registrado
4. Resposta inclui `ip_address` e array `consents` com todos os consentimentos ativos

### Validações

| Regra | Código |
|-------|--------|
| `privacy_policy_version` obrigatório e não vazio | 422 |
| Usuário deve estar autenticado | 401 |
| Consentimentos repetidos para a mesma versão e tipo são idempotentes (200, não 409) | — |
| `types` deve ser array válido de `ConsentType` | 422 |

### RBAC

- Qualquer usuário autenticado (qualquer role) pode consentir
- Usuário sem role também pode consentir (basta estar autenticado)

## DELETE /user/me/consent — Revogar Consentimento

### Comportamento

1. Usuário autenticado envia `{ "type": "shop_publication" }` (ou sem body para default `privacy_policy`)
2. Backend localiza o consentimento ativo do tipo solicitado
3. Backend atualiza:
   - `granted = false`
   - Registra `revoked_at = now()`
4. Backend dispara ações em cascata conforme o tipo (ver § Efeitos em Cascata)
5. Backend registra trilha de auditoria com `action = consent_revoked`
6. Resposta inclui `type`, `revoked_at`, `previous_version` e `cascade_effects`

### Validações

| Regra | Código |
|-------|--------|
| Usuário deve estar autenticado | 401 |
| Tipo de consentimento não encontrado ou já revogado | 422 |

### RBAC

- Qualquer usuário autenticado pode revogar o próprio consentimento

### Efeitos em Cascata

| Tipo revogado | Ação em cascata | Observação |
|---------------|----------------|------------|
| `privacy_policy` | `privacy_policy_revoked` | `consentiu_privacy_policy = false`. Frontend bloqueia operações até novo consentimento. |
| `shop_publication` | `shop_unpublished` | Vitrine é despublicada (status = unpublished). Dados deixam de ser expostos publicamente. |
| `transactional_emails` | `transactional_emails_stopped` | Emails transacionais são desativados. Convites e notificações deixam de ser enviados. |

### Regras de negócio da revogação

- A revogação não apaga dados já processados sob consentimento anterior (Art. 8, §5: "não compromete a licitude do tratamento realizado sob amparo do consentimento anteriormente manifestado")
- Para exclusão definitiva de dados, o titular deve usar `DELETE /user/me` (ver [F4](/IND/issues/IND-54))
- Após revogação, o frontend não deve permitir operações que dependam do consentimento revogado até que novo consentimento seja dado
- Revogar `privacy_policy` não revoga automaticamente `shop_publication` ou `transactional_emails` — cada tipo é independente
- Revogação de `shop_publication` despublica a vitrine mas não remove os dados — o admin pode republicar após novo consentimento

## Trilha de Auditoria (AuditLogEntry)

### Requisitos LGPD

- Art. 8, §2: ônus da prova — o controlador deve demonstrar que obteve consentimento
- Registro imutável com: quem, qual tipo, qual versão, quando, de qual IP

### Campos

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | `integer` | Chave primária |
| `action` | `enum` | `consent_granted` ou `consent_revoked` |
| `usuario_id` | `integer` | FK para Usuario |
| `consent_type` | `enum` | Tipo de consentimento afetado |
| `ip_address` | `string` (nullable) | IP de origem da requisição |
| `metadata` | `object` (nullable) | Dados adicionais (ex: `{ "privacy_policy_version": "v2.0" }`) |
| `created_at` | `datetime` | Timestamp do registro |

### Regras

- Cada chamada a `PUT /user/me/consent` gera 1 entrada por tipo com `action = consent_granted`
- Cada chamada a `DELETE /user/me/consent` gera 1 entrada com `action = consent_revoked`
- Entradas de auditoria são imutáveis após criação
- `ip_address` é coletado do header `X-Forwarded-For` (ou `request.client.host` como fallback)
- Se o proxy não encaminhar IP, `ip_address` pode ser `null`

## Consentimento para Vitrine Pública (Shop)

### Contexto

O endpoint `POST /shop/{handle}/deploy` publica dados da empresa publicamente. A empresa deve consentir explicitamente com a exposição desses dados.

### Regras

- Antes do deploy, o frontend deve:
  1. Listar quais dados da empresa ficarão públicos (nome, email, Instagram, WhatsApp, logo, etc.)
  2. Solicitar consentimento explícito via modal
- O consentimento da vitrine é registrado como `consent_records` com `type = shop_publication`
- Este consentimento também gera entrada de auditoria (`action = consent_granted`, `consent_type = shop_publication`)

### Revogação do consentimento de vitrine

- Quando o titular revoga `shop_publication` via `DELETE /user/me/consent { "type": "shop_publication" }`:
  - O backend despublica a vitrine (status = unpublished)
  - Os dados da vitrine deixam de ser expostos publicamente
  - A resposta inclui `cascade_effects: ["shop_unpublished"]`
  - Uma entrada de auditoria é registrada com `action = consent_revoked`
- O admin pode republicar a vitrine após novo consentimento

## Fluxo no Frontend

### Primeiro Login

```
Login → GET /user/me → consentiu_privacy_policy == false
  → Tela de aceite bloqueante (modal full-screen)
  → Exibe resumo da política + link para política completa
  → Botão "Aceitar" → PUT /user/me/consent
  → consentiu_privacy_policy = true
  → Redireciona para dashboard da role
```

### Atualização de Política

```
Login → GET /user/me → privacy_policy_version < current_version
  → Banner no topo: "Política de Privacidade atualizada. Leia e aceite para continuar."
  → Link para diff/change log da política
  → Botão "Aceitar nova versão" → PUT /user/me/consent com nova versão
```

### Deploy de Vitrine

```
Admin → /loja/config → Botão "Publicar"
  → Modal: "Os seguintes dados ficarão públicos: ..."
  → Link para política de privacidade
  → Checkbox: "Autorizo a publicação destes dados conforme política"
  → Botão "Publicar" → registra consentimento → deploy
```

### Perfil do Usuário — Gerenciamento de Consentimentos (F3)

```
Usuário → /perfil → Aba "Privacidade"
  → Lista de consentimentos ativos (GET /user/me/consent)
  → Cada tipo exibe toggle com status atual:
    - Política de Privacidade: [ATIVO] — versão v2.0, aceito em 10/06/2026
    - Vitrine Pública: [ATIVO] — autorizado em 10/06/2026
    - Emails Transacionais: [ATIVO] — autorizado em 10/06/2026
  → Toggle "Revogar" → modal de confirmação:
    "Ao revogar o consentimento de Vitrine Pública, sua vitrine será despublicada
     e os dados deixarão de ser exibidos publicamente. Deseja continuar?"
  → Confirmação → DELETE /user/me/consent { "type": "shop_publication" }
  → Toast: "Consentimento revogado. Vitrine despublicada."
  → Email de confirmação enviado ao titular (via Resend)
```

## Testes

### E2E — F1 (consentimento base) (`tests/e2e/test_consent_api.py`)

1. `test_consentiu_privacy_policy_false_by_default` — confirma que `GET /user/me` retorna `consentiu_privacy_policy: false` (opt-in)
2. `test_put_consent_success` — `PUT /user/me/consent` registra consentimento, retorna campos esperados
3. `test_put_consent_idempotent` — consentir com mesma versão duas vezes retorna 200 em ambas
4. `test_put_consent_missing_version` — 422 se `privacy_policy_version` ausente
5. `test_put_consent_empty_version` — 422 se `privacy_policy_version` vazio
6. `test_delete_consent_success` — `DELETE /user/me/consent` revoga, `consentiu_privacy_policy` volta a ser false
7. `test_delete_consent_returns_previous_version` — resposta inclui versão anterior
8. `test_unauthenticated_consent` — 401 sem token JWT
9. `test_no_role_user_can_consent` — usuário sem role também pode consentir
10. `test_audit_log_created_on_grant` — trilha de auditoria criada ao conceder consentimento
11. `test_audit_log_created_on_revoke` — trilha de auditoria criada ao revogar consentimento
12. `test_consent_race_condition` — consentimentos concorrentes não corrompem estado

### E2E — F3 (revogação granular e efeitos em cascata) (`tests/e2e/test_consent_revocation_api.py`)

13. `test_get_consent_list_empty` — `GET /user/me/consent` retorna array vazio para usuário sem consentimentos
14. `test_get_consent_list_active` — `GET /user/me/consent` retorna consentimentos ativos com type, version, granted_at
15. `test_get_consent_list_excludes_revoked` — consentimentos revogados não aparecem na listagem
16. `test_put_consent_with_types` — `PUT /user/me/consent` com `types: ["privacy_policy", "transactional_emails"]` registra ambos
17. `test_revoke_specific_type` — `DELETE /user/me/consent { "type": "shop_publication" }` revoga apenas o tipo especificado
18. `test_revoke_default_type` — `DELETE /user/me/consent` sem body revoga `privacy_policy` (default)
19. `test_revoke_independent_types` — revogar `shop_publication` não afeta `privacy_policy` nem `transactional_emails`
20. `test_revoke_already_revoked` — 422 ao revogar consentimento já revogado
21. `test_revoke_invalid_type` — 422 ao revogar tipo inexistente
22. `test_revoke_shop_unpublishes_vitrine` — revogar `shop_publication` despublica vitrine, cascade_effects inclui `shop_unpublished`
23. `test_revoke_shop_does_not_affect_other_shops` — vitrine de empresa A não é afetada por revogação de usuário B
24. `test_revoke_transactional_emails_cascade` — revogar `transactional_emails` inclui `transactional_emails_stopped` nos cascade_effects
25. `test_revoke_audit_log_has_consent_type` — entrada de auditoria de revogação inclui campo `consent_type`
26. `test_revoke_audit_log_has_timestamp` — entrada de auditoria de revogação tem `created_at` preciso (diferença < 5s da requisição)
27. `test_revoke_preserves_previous_grant_data` — após revogar, `GET /user/me/consent` não lista o consentimento, mas auditoria preserva histórico
28. `test_revoke_race_condition` — revogações concorrentes do mesmo tipo não corrompem estado
