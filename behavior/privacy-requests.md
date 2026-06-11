# Privacy Requests — Regras de Negócio e Especificação de Testes

> Canal do DPO e formulário de solicitação de direitos do titular (LGPD Arts. 18, 41).
> Issue: [IND-54](/IND/issues/IND-54)

---

## Visão Geral

Atende aos direitos dos titulares de dados previstos no Art. 18 da LGPD:

| Direito | Tipo de Solicitação | Descrição |
|---------|---------------------|-----------|
| Confirmação e acesso (I, II) | `acesso` | Solicitar confirmação da existência de tratamento e acesso aos dados |
| Correção (III) | `correcao` | Solicitar correção de dados incompletos, inexatos ou desatualizados |
| Anonimização, bloqueio ou eliminação (IV) | `exclusao` | Solicitar exclusão de dados desnecessários, excessivos ou tratados em desconformidade |
| Portabilidade (V) | `portabilidade` | Solicitar portabilidade dos dados a outro fornecedor de serviço ou produto |
| Revogação de consentimento (§5) | `revogacao` | Revogar consentimento previamente concedido |
| Reclamação (§1) | `reclamacao` | Registrar reclamação contra o controlador perante a autoridade nacional |

Fluxo:

1. Titular acessa o formulário público (sem necessidade de autenticação)
2. Preenche tipo de solicitação, descrição textual e email de contato (opcional se autenticado)
3. Sistema registra a solicitação no banco com status `aberto`
4. Email de notificação é enviado ao DPO (`privacidade@indiqr.lealcyber.com`) via Resend
5. DPO trata a solicitação e atualiza o status: `aberto` → `em_andamento` → `concluido`

---

## Endpoints

| Método | Path | Auth | Descrição |
|--------|------|------|-----------|
| `POST` | `/privacy/request` | Público | Registrar solicitação de direitos do titular |

---

## Regras de Negócio

### Registro de Solicitação (`POST /privacy/request`)

- Endpoint público, sem autenticação (LGPD Art. 18 garante direitos a qualquer titular)
- Campos obrigatórios: `tipo`, `descricao`
- `tipo` deve ser um dos valores: `acesso`, `correcao`, `exclusao`, `portabilidade`, `revogacao`, `reclamacao`
- `descricao` deve ter entre 10 e 2000 caracteres
- `email_contato` é opcional. Se o usuário estiver autenticado, o email é extraído do token JWT e `email_contato` é ignorado. Se anônimo, `email_contato` é recomendado (opcional) para que o DPO possa responder
- Status inicial: `aberto`
- Cria registro de auditoria (`AuditLogEntry` com action `privacy_request_created`)

### Notificação ao DPO

- Após registro bem-sucedido, envia email ao DPO via Resend para `privacidade@indiqr.lealcyber.com`
- Email contém: tipo da solicitação, descricao completa, email de contato do titular, data/hora
- Formato HTML com template consistente com os demais emails da plataforma
- Falha no envio de email não reverte o registro (graceful degradation — registro fica salvo)
- Função de envio: `send_privacy_request_notification(request_id, tipo, descricao, email_contato)`

### Tracking de Status

| Status | Significado |
|--------|------------|
| `aberto` | Solicitação registrada, aguardando triagem do DPO |
| `em_andamento` | DPO está tratando a solicitação |
| `concluido` | Solicitação atendida ou respondida |

A transição de status é feita pelo DPO (via ferramenta interna, fora do escopo deste endpoint público).

### Modelo de Dados

Tabela `PrivacyRequest`:

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | SERIAL PK | Identificador único |
| `tipo` | VARCHAR(20) NOT NULL | Tipo da solicitação (enum) |
| `descricao` | TEXT NOT NULL | Descrição textual (10-2000 chars) |
| `email_contato` | VARCHAR(255) | Email de contato do titular (nullable) |
| `usuario_id` | INTEGER FK→Usuario | Preenchido se usuário autenticado (nullable) |
| `status` | VARCHAR(30) NOT NULL DEFAULT 'aberto' | Status do atendimento |
| `created_at` | TIMESTAMPTZ NOT NULL DEFAULT NOW() | Data de criação |
| `updated_at` | TIMESTAMPTZ NOT NULL DEFAULT NOW() | Data da última atualização |

Constraints:
- `tipo` CHECK IN ('acesso', 'correcao', 'exclusao', 'portabilidade', 'revogacao', 'reclamacao')
- `status` CHECK IN ('aberto', 'em_andamento', 'concluido')

---

## Especificação de Testes

### Unit — `tests/unit/test_privacy_email_service.py`

#### Envio de email ao DPO

- [ ] `test_send_privacy_request_notification_calls_resend_api`
  Chama `send_privacy_request_notification(...)` e verifica que `requests.post`
  foi chamado com `RESEND_API_URL` e body contendo `to: "privacidade@indiqr.lealcyber.com"`.

- [ ] `test_send_privacy_request_notification_includes_request_details`
  Verifica que o HTML do email contém: tipo da solicitação, descrição truncada
  (primeiros 200 chars), email de contato do titular.

- [ ] `test_send_privacy_request_notification_subject_contains_request_type`
  Subject do email contém o tipo da solicitação (ex: "Solicitação de acesso").

- [ ] `test_email_send_failure_graceful_degradation`
  Resend retorna 500 → função retorna `False` ou `None`, sem lançar exceção.

- [ ] `test_network_error_does_not_crash`
  `requests.post` levanta `ConnectionError` → função não crasha.

- [ ] `test_timeout_does_not_crash`
  `requests.post` levanta `TimeoutError` → função não crasha.

- [ ] `test_privacy_request_email_renders_valid_html`
  HTML gerado contém `<!doctype`, `<html`, `<body` ou `<table`.

#### Validação de tipos

- [ ] `test_privacy_request_type_mapping`
  Cada tipo gera um assunto de email apropriado em português:
  `acesso` → "Solicitação de Acesso", `correcao` → "Solicitação de Correção",
  `exclusao` → "Solicitação de Exclusão", `portabilidade` → "Solicitação de Portabilidade",
  `revogacao` → "Revogação de Consentimento", `reclamacao` → "Reclamação".

### E2E — `tests/e2e/test_privacy_api.py`

#### Fluxo feliz — anônimo

- [ ] `test_privacy_request_anonymous_success`
  1. `POST /privacy/request` com body `{"tipo": "acesso", "descricao": "Gostaria de acessar todos os meus dados pessoais armazenados.", "email_contato": "titular@example.com"}` → 201
  2. Response contém `id`, `tipo: "acesso"`, `status: "aberto"`, `created_at`
  3. Mock do email_service confirma chamada para DPO

#### Fluxo feliz — autenticado

- [ ] `test_privacy_request_authenticated_success`
  1. Usuário autenticado faz `POST /privacy/request` com body `{"tipo": "exclusao", "descricao": "Solicito a exclusão dos meus dados da plataforma."}` → 201
  2. `usuario_id` é preenchido com o ID do usuário autenticado
  3. `email_contato` é preenchido com o email do token JWT

#### Validações

- [ ] `test_privacy_request_missing_tipo`
  Body sem `tipo` → 422.

- [ ] `test_privacy_request_missing_descricao`
  Body sem `descricao` → 422.

- [ ] `test_privacy_request_descricao_too_short`
  `descricao` com menos de 10 caracteres → 422.

- [ ] `test_privacy_request_descricao_too_long`
  `descricao` com mais de 2000 caracteres → 422.

- [ ] `test_privacy_request_invalid_tipo`
  `tipo: "outro"` → 422. Mensagem indica valores válidos.

- [ ] `test_privacy_request_invalid_email`
  `email_contato: "nao-e-um-email"` → 422.

#### Tipos de solicitação

- [ ] `test_privacy_request_all_tipos_accepted`
  Teste parametrizado: cada um dos 6 tipos (`acesso`, `correcao`, `exclusao`,
  `portabilidade`, `revogacao`, `reclamacao`) é aceito com 201.

---

## Dependências de Teste

- **email_service mock** — `send_privacy_request_notification`
- **client fixtures:** `any_authenticated_client`, `unauthenticated_client`
- **factory fixtures:** `create_user`

---

## DPO Footer (Frontend)

### Requisito

Todas as telas da plataforma devem incluir no footer:

- **Contato do DPO:** `privacidade@indiqr.lealcyber.com` com link `mailto:`
- **Política de Privacidade:** link para `https://indiqr.lealcyber.com/privacidade/politica-de-privacidade.html`
- **Formulário de Direitos:** link para `/privacidade/solicitacao` (rota SPA que renderiza o formulário)

### Comportamento

- O footer é um componente `<Footer />` importado pelo root layout
- Visível em todas as rotas (públicas e protegidas), sem exceção
- Estilo: rodapé simples com fundo `bg-muted`, texto pequeno, centralizado em mobile, espaçado em desktop
- Links abrem na mesma aba (rotas internas) exceto política de privacidade (nova aba)

### Tela: Formulário de Direitos do Titular

- **Rota:** `/privacidade/solicitacao` (pública, sem autenticação)
- **Descrição:** Formulário para titulares exercerem seus direitos LGPD
- **Campos:**
  - Tipo de solicitação: radio buttons com ícones e labels em português
  - Descrição: textarea com placeholder e contador de caracteres (10/2000)
  - Email de contato: campo de email (preenchido automaticamente se autenticado)
- **Comportamento:**
  - Submit → `POST /privacy/request` via axios
  - Sucesso: tela de confirmação com número de protocolo (id da solicitação) e mensagem de que o DPO responderá em até 15 dias úteis
  - Erro 422: mensagens de validação inline por campo
  - Erro de rede: toast com botão retry
  - Se autenticado, email_contato é desabilitado (extraído do JWT)
