# Inventário de Telas

Todas as rotas protegidas redirecionam para Auth0 Universal Login se não autenticado. A role do usuário determina qual grupo de rotas está disponível.

---

## Rotas Públicas (sem autenticação)

| Rota | Tela | Descrição |
|------|------|-----------|
| `/convite/:token` | Prévia do convite | Exibe nome da empresa e role. Botão "Aceitar" redireciona para login se não autenticado. |
| `/callback` | Auth0 callback | Processa retorno do Auth0, redireciona para `/` |
| `/privacidade/solicitacao` | Formulário de Direitos do Titular | Formulário LGPD para solicitação de acesso, correção, exclusão, portabilidade, revogação ou reclamação (Arts. 18, 41) |

---

## Fluxo de Consentimento (intercepta todas as rotas)

| Tela | Gatilho | Descrição |
|------|---------|-----------|
| Aceite de Política | `consentiu_privacy_policy == false` após login | Modal full-screen bloqueante. Exibe resumo da política, link para versão completa, botão "Aceitar". PUT /user/me/consent. |
| Banner de Atualização | `privacy_policy_version < current_version` | Banner persistente no topo informando que a política foi atualizada. Não bloqueante, mas visível em todas as telas. |
| Revogação de Consentimento | `/perfil#privacidade` > "Revogar" | Modal de confirmação, depois DELETE /user/me/consent. Redireciona para tela de aceite. |

---

## Rotas Compartilhadas (qualquer role autenticada)

| Rota | Tela | Descrição |
|------|------|-----------|
| `/` | Redirect inteligente | Redireciona para dashboard da role do usuário |
| `/perfil` | Perfil do usuário | Dados do usuário, abas: Geral / Privacidade. GET /user/me. |
| `/conversoes` | Minhas conversões | Lista paginada de conversões filtrada pela role do usuário + `<Pagination />` (20 por página) |

### Tela: Perfil do Usuário

- Aba Geral: email, roles (badges), data de cadastro
- Aba Privacidade:
  - Status do consentimento: "Consentiu em [data] — versão [v]" ou "Não consentiu"
  - Botão "Revogar consentimento" (se consentiu)
  - Link para política de privacidade
  - Opção "Solicitar exportação de dados" → GET /user/me/export (ver [F4](/IND/issues/IND-54))
  - Opção "Solicitar exclusão de dados" → DELETE /user/me (ver [F4](/IND/issues/IND-54))

---

## Admin (`indiqr-admin`)

| Rota | Tela | Endpoint(s) |
|------|------|-------------|
| `/empresas` | Lista de empresas | `GET /companies/` |
| `/empresas/nova` | Criar empresa | `POST /companies/` |
| `/empresas/:id` | Painel da empresa | `GET /companies/` |
| `/empresas/:id/membros` | Membros | `GET /companies/:id/members` |
| `/empresas/:id/convites` | Convites pendentes | `GET /companies/:id/invitations` |
| `/empresas/:id/campanhas` | Campanhas da empresa | `GET /campaigns/` |
| `/campanhas/nova` | Criar campanha | `POST /campaigns/` |
| `/campanhas/:id` | Detalhe da campanha | `GET /campaigns/:id` |
| `/campanhas/:id/conversoes` | Conversões da campanha | `GET /campaigns/:id/conversions` |
| `/loja/config` | Configuração da vitrine | `GET /shop/mine` |
| `/loja/deploy` | Publicar vitrine | `POST /shop/{handle}/deploy` |

### Tela: Lista de Empresas
- Cards com nome, slug, nº de membros, nº de campanhas ativas
- Botão "Nova Empresa"
- Se sem empresas: empty state com CTA para criar
- Paginação: cards paginados com `<Pagination />` (20 por página)

### Tela: Painel da Empresa
- Abas: Visão Geral / Membros / Convites / Campanhas
- Visão Geral: stats (total campanhas, ativas, conversões do mês)

### Tela: Membros
- Tabela: email, role (badge colorido), data de entrada, ação remover
- Botão "Convidar membro" (abre modal)
- Modal de convite: campo email + select de role (influenciador/vendedor)
- Proteção: não exibe botão remover para o único admin
- Paginação: tabela paginada com `<Pagination />` (20 por página)

### Tela: Convites
- Tabela: email, role, status (pending/accepted/revoked), data
- Botão "Revogar" em convites pending
- Paginação: tabela paginada com `<Pagination />` (20 por página)

### Tela: Campanhas da Empresa
- Lista com nome, influenciador, status (badge), data de criação
- Botão "Nova Campanha"
- Filtro por status
- Paginação: lista paginada com `<Pagination />` (20 por página)

### Tela: Criar Campanha
- Formulário:
  - Nome da campanha (text)
  - Empresa (select — pré-preenchida se vinda do painel)
  - Influenciador (select dos membros influenciadores da empresa)
  - Modelo de remuneração: Fixo / Percentual (radio)
  - Valor de remuneração (numeric)
  - Desconto (%) — opcional
- Resumo calculado em tempo real antes de submeter
- Submit → email enviado ao influenciador automaticamente

### Tela: Detalhe da Campanha (Admin)
- Cabeçalho: nome, empresa, status (badge grande), influenciador
- Parâmetros imutáveis exibidos (remuneração, desconto)
- Botão "Encerrar campanha" (apenas se não encerrada) — confirmação modal
- Aba Conversões: tabela paginada com vendedor, valor bruto, desconto, remuneração, data + `<Pagination />` (20 por página)

### Tela: Configuração da Vitrine (Loja)
- Formulário de configuração da loja: nome, email, Instagram, WhatsApp
- Upload de mídia (logo, hero, categorias, produtos)
- Botão "Publicar" que aciona modal de consentimento

### Modal: Consentimento de Publicação (antes do deploy)
- Lista explícita dos dados que ficarão públicos na vitrine
- Checkbox obrigatório: "Autorizo a publicação destes dados conforme a Política de Privacidade"
- Link para política de privacidade
- Botão "Publicar" habilitado apenas após checkbox marcado
- Ao confirmar: registra consentimento + executa deploy

---

## Influenciador (`indiqr-influenciador`)

| Rota | Tela | Endpoint(s) |
|------|------|-------------|
| `/campanhas` | Minhas campanhas | `GET /campaigns/` |
| `/campanhas/:id` | Detalhe da campanha | `GET /campaigns/:id` |
| `/campanhas/:id/aceitar` | Aceite de campanha | `POST /campaigns/:id/accept` |

### Tela: Minhas Campanhas
- Cards por status: Aguardando aceite / Ativas / Encerradas
- Cada card: nome, empresa, modelo de remuneração, data
- Paginação: cards paginados com `<Pagination />` (20 por página) — cada grupo de status é uma lista paginada independente

### Tela: Detalhe da Campanha (Influenciador)

**Se `aguardando_aceite`:**
- Exibe: nome da campanha, empresa, modelo de remuneração, desconto
- Botões: "Aceitar" (verde) e "Recusar" (outline vermelho) com confirmação
- Aceitar → status vira `ativa` + QRCode gerado

**Se `ativa`:**
- Seção de materiais:
  - Botão "Baixar QRCode" → `GET /campaigns/:id/qrcode` (download PNG)
  - Botão "Baixar Card PDF" → `GET /campaigns/:id/card.pdf` (download PDF)
  - Preview do QRCode em tela (img tag com a URL do endpoint)
- Botão "Sair da campanha" (encerra a participação) — confirmação modal
- Aba Conversões: tabela paginada com vendedor, valor bruto, desconto, remuneração, data + `<Pagination />` (20 por página)

**Se `encerrada`:**
- Badge "Encerrada" + histórico de conversões somente leitura

---

## Vendedor (`indiqr-vendedor`) — PWA Mobile-first

| Rota | Tela | Endpoint(s) |
|------|------|-------------|
| `/vender` | Scanner + validação | `POST /conversions/validate` |
| `/conversoes` | Histórico pessoal | `GET /conversions/` |

### Tela: Scanner / Validação (fluxo principal)

**Passo 1 — Valor:**
- Campo numérico grande: "Valor da compra (R$)"
- Teclado numérico (mobile)
- Botão "Escanear QRCode"

**Passo 2 — Scanner:**
- Câmera ativa com overlay de enquadramento
- Leitura automática ao detectar QRCode
- Botão voltar

**Passo 3 — Prévia:**
- Card de confirmação com:
  - Nome da campanha e influenciador
  - Valor bruto: R$ X,XX
  - Desconto: R$ X,XX (se houver) → Valor do cliente: R$ X,XX
  - Remuneração do influenciador: R$ X,XX
- Botão "Confirmar" (grande, verde) — ação irreversível
- Botão "Cancelar"

**Passo 4 — Confirmação:**
- Tela de sucesso com resumo
- Botão "Nova venda" (reinicia fluxo)

**Erros tratados na UI:**
- QRCode inválido → "QRCode não reconhecido. Verifique o material do influenciador."
- Campanha encerrada → "Esta campanha foi encerrada. O desconto não se aplica."
- Valor ≤ 0 → validação inline antes de escanear

### Tela: Histórico do Vendedor
- Lista cronológica paginada das conversões registradas pelo vendedor
- Cada item: campanha, influenciador, valor bruto, desconto, remuneração, data
- Somente leitura
- Paginação: `<Pagination />` (20 por página)

---

## Tela: Formulário de Direitos do Titular (LGPD)

**Rota:** `/privacidade/solicitacao` (pública)
**Endpoint:** `POST /privacy/request`

### Layout

- Cabeçalho: "Seus Direitos — Lei Geral de Proteção de Dados"
- Subtítulo: "Preencha o formulário abaixo para exercer seus direitos previstos no Art. 18 da LGPD"
- Card centralizado com formulário e fundo `bg-card`

### Campos

| Campo | Tipo | Validação | Descrição |
|-------|------|-----------|-----------|
| Tipo de solicitação | Radio group | Obrigatório | 6 opções com ícone, label em português e breve descrição |
| Descrição | Textarea | 10-2000 caracteres | Detalhamento livre do pedido |
| Email de contato | Input email | Formato email, obrigatório se anônimo | Preenchido automaticamente e desabilitado se usuário autenticado |

### Opções de Tipo (radio group)

```
( ) Acesso — Confirmar existência de tratamento e acessar meus dados
( ) Correção — Corrigir dados incompletos, inexatos ou desatualizados
( ) Exclusão — Solicitar exclusão de dados desnecessários ou excessivos
( ) Portabilidade — Exportar meus dados para outro fornecedor
( ) Revogação — Revogar consentimento previamente concedido
( ) Reclamação — Registrar reclamação sobre o tratamento dos dados
```

### Comportamento

1. **Submissão:** botão "Enviar Solicitação" → `POST /privacy/request`
2. **Sucesso (201):**
   - Tela de confirmação com check verde e número de protocolo
   - Texto: "Solicitação #123 registrada. O DPO responderá em até 15 dias úteis no email informado."
   - Botão "Nova Solicitação" para reiniciar o formulário
3. **Erro de validação (422):**
   - Mensagens inline por campo: "A descrição deve ter no mínimo 10 caracteres", "Tipo de solicitação é obrigatório"
4. **Erro de rede:**
   - Toast: "Erro ao enviar solicitação. Tente novamente." + botão retry
5. **Email (opcional se autenticado):**
   - O campo `email_contato` só é obrigatório para usuários NÃO autenticados
   - Se autenticado, o email é extraído do JWT e o campo aparece preenchido e desabilitado com label "Email (da sua conta)"
   - Se anônimo, campo ativo com placeholder "seu@email.com" e label "Email para contato"

### Estados de UI

| Estado | Comportamento |
|--------|--------------|
| Default | Formulário limpo, nenhum tipo selecionado |
| Validação | Erros inline nos campos, submit habilitado apenas com formulário válido |
| Submitting | Botão "Enviando..." com spinner, campos desabilitados |
| Sucesso | Card de confirmação com número de protocolo e instruções |
| Erro de rede | Toast com botão retry, formulário mantém dados preenchidos |
| Erro 422 | Campos com erro mantêm valor, mensagens de validação exibidas |

---

## Estados Globais de UI

| Estado | Comportamento |
|--------|--------------|
| Loading | Skeleton screens (não spinner genérico) |
| Erro de rede | Toast + botão retry |
| Sessão expirada | Redirect automático para login Auth0 |
| Role sem acesso | Redirect para `/` (rota adequada à role) |
| Empty state | Ilustração + CTA contextual |
