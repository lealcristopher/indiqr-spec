# Membership Requests — Regras de Negócio e Especificação de Testes

> Área P2 do plano de cobertura IND-38. Detalha o comportamento e os cenários de
> teste esperados para o fluxo completo de membership requests (solicitação de
> entrada em empresa por iniciativa do usuário, complementar ao fluxo de convite).

---

## Visão Geral

Diferente do fluxo de convite (onde o admin convida um email), o fluxo de
**membership request** permite que um usuário autenticado solicite entrada em
uma empresa:

1. Usuário descobre uma empresa (ex: por slug público)
2. Usuário envia `POST /companies/{slug}/membership-requests` com role desejada
3. Admin da empresa recebe notificação e revisa a solicitação
4. Admin pode **aceitar** ou **recusar**, opcionalmente com mensagem
5. Se aceito, usuário torna-se membro com a role solicitada

---

## Endpoints

| Método | Path | Descrição |
|--------|------|-----------|
| `POST` | `/companies/{slug}/membership-requests` | Solicitar entrada na empresa |
| `GET` | `/companies/{slug}/membership-requests` | Listar solicitações pendentes (admin) |
| `GET` | `/companies/{slug}/membership-requests/preview/{token}` | Preview público da solicitação |
| `POST` | `/companies/{slug}/membership-requests/{token}/accept` | Admin aceita solicitação |
| `POST` | `/companies/{slug}/membership-requests/{token}/decline` | Admin recusa solicitação |

---

## Regras de Negócio

### Solicitação (`POST /membership-requests`)

- Usuário deve estar autenticado
- `slug` identifica a empresa-alvo (não `company_id` — slug é público)
- Role solicitada deve ser `influenciador` ou `vendedor` (admin não pode ser
  solicitado)
- Usuário não pode já ser membro da empresa → **409**
- Usuário não pode ter solicitação pendente para a mesma empresa → **409**
- Empresa deve existir → **404**

### Preview (`GET /membership-requests/preview/{token}`)

- Público, sem autenticação
- Mostra: nome da empresa, email do solicitante, role solicitada
- Token inválido ou já processado → **404**

### Aceite (`POST /membership-requests/{token}/accept`)

- Apenas admin da empresa-alvo pode aceitar
- Cria `CompanyMember` com a role solicitada
- Atribui role Auth0 correspondente
- Marca solicitação como `accepted`
- Token já processado → **404**

### Recusa (`POST /membership-requests/{token}/decline`)

- Apenas admin da empresa-alvo pode recusar
- Opcional: campo `message` (string) com motivo
- Marca solicitação como `declined`
- Email de notificação enviado ao solicitante (se message informada, incluída
  no email)
- Token já processado → **404**

### Cross-company validation

- Admin da empresa A não pode acessar solicitações da empresa B
- Preview de solicitação de empresa B com token válido → **404** (não vaza
  existência da empresa)
- Tentativa de aceitar/recusar solicitação de outra empresa → **404**

---

## Especificação de Testes

### E2E — `tests/e2e/test_companies_api.py`

#### Fluxo completo feliz

- [ ] `test_membership_request_full_lifecycle`
  1. Usuário A (não-membro) faz `POST /companies/{slug}/membership-requests`
     com `role=influenciador` → 201. Retorna token e status `pending`.
  2. `GET /companies/{slug}/membership-requests/preview/{token}` (sem auth)
     → 200. Contém company_name, email do solicitante, role.
  3. Admin da empresa faz `GET /companies/{slug}/membership-requests`
     → 200. Lista contém 1 solicitação pendente.
  4. Admin faz `POST .../accept` → 200. Retorna Member criado.
  5. `GET /companies/{company_id}/members` agora inclui usuário A.
  6. Usuário A agora pode acessar recursos da empresa (ex: campanhas).

#### Decline com mensagem

- [ ] `test_membership_request_decline_with_message`
  1. Usuário solicita entrada.
  2. Admin faz `POST .../decline` com body `{"message": "Perfil não se encaixa"}`
     → 200. Solicitação marcada como `declined`.
  3. `GET .../membership-requests` (admin) não inclui mais a solicitação
     (ou lista com filtro de status).
  4. Email enviado ao solicitante contendo a mensagem de decline (verificar
     via mock do email_service).

- [ ] `test_membership_request_decline_without_message`
  1. Admin faz `POST .../decline` sem body → 200.
  2. Email enviado com mensagem padrão (não vazia).

#### Validações de solicitação

- [ ] `test_membership_request_company_not_found`
  `POST /companies/slug-inexistente/membership-requests` → 404.

- [ ] `test_membership_request_already_member`
  Membro existente tenta solicitar entrada na mesma empresa → 409.
  Mensagem: "Usuário já é membro desta empresa".

- [ ] `test_membership_request_duplicate_pending`
  Usuário com solicitação pendente tenta solicitar novamente → 409.
  Mensagem: "Já existe uma solicitação pendente para esta empresa".

- [ ] `test_membership_request_admin_role_rejected`
  Usuário solicita `role=admin` → 422. Mensagem indica que role deve
  ser `influenciador` ou `vendedor`.

- [ ] `test_membership_request_invalid_role`
  Usuário solicita `role=superadmin` → 422.

- [ ] `test_membership_request_missing_role`
  Body sem campo `role` → 422.

- [ ] `test_membership_request_unauthenticated`
  Sem token → 401.

#### Preview

- [ ] `test_membership_request_preview_valid_token`
  `GET .../preview/{token}` com token pendente → 200. Contém company_name,
  email, role. NÃO contém campos internos (id, company_id, status).

- [ ] `test_membership_request_preview_invalid_token`
  Token inexistente → 404.

- [ ] `test_membership_request_preview_already_accepted`
  Token de solicitação já aceita → 404.

- [ ] `test_membership_request_preview_declined`
  Token de solicitação recusada → 404.

#### Aceite

- [ ] `test_accept_membership_request_invalid_token`
  `POST .../accept` com token inexistente → 404.

- [ ] `test_accept_membership_request_non_admin_blocked`
  Membro influenciador da empresa tenta aceitar solicitação → 403.

- [ ] `test_accept_membership_request_cross_company`
  Admin da empresa A tenta aceitar solicitação da empresa B → 404.

- [ ] `test_accept_membership_request_creates_auth0_role`
  Após aceite, verificar que o mock do auth0_service foi chamado com
  `assign_role(user_id, "indiqr-influenciador")`.

#### Recusa

- [ ] `test_decline_membership_request_invalid_token`
  `POST .../decline` com token inexistente → 404.

- [ ] `test_decline_membership_request_non_admin_blocked`
  Vendedor tenta recusar → 403.

- [ ] `test_decline_membership_request_sends_email`
  Admin recusa com mensagem. Verificar mock: `send_email` chamado
  com destinatário = email do solicitante, body contendo mensagem.

#### Cross-company validation

- [ ] `test_cross_company_membership_request_not_listed`
  Admin da empresa A lista solicitações da empresa A. Solicitação da
  empresa B não aparece.

- [ ] `test_cross_company_membership_request_access_denied`
  Admin da empresa A tenta `GET .../membership-requests` da empresa B
  → 403.

- [ ] `test_cross_company_membership_accept_blocked`
  Admin da empresa A tenta aceitar solicitação da empresa B → 404
  (não revela que o token existe em outra empresa).

---

## Dependências de Teste

- **email_service mock** já existente nos testes de invitation
- **auth0_service mock** já existente
- **factory fixtures:** `create_company`, `create_user`, `create_member`
- **client fixtures por role:** `admin_client`, `influenciador_client`,
  `vendedor_client`, `unauthenticated_client`
