# Inventário de Telas

Todas as rotas protegidas redirecionam para Auth0 Universal Login se não autenticado. A role do usuário determina qual grupo de rotas está disponível.

---

## Rotas Públicas (sem autenticação)

| Rota | Tela | Descrição |
|------|------|-----------|
| `/convite/:token` | Prévia do convite | Exibe nome da empresa e role. Botão "Aceitar" redireciona para login se não autenticado. |
| `/callback` | Auth0 callback | Processa retorno do Auth0, redireciona para `/` |

---

## Rotas Compartilhadas (qualquer role autenticada)

| Rota | Tela | Descrição |
|------|------|-----------|
| `/` | Redirect inteligente | Redireciona para dashboard da role do usuário |
| `/conversoes` | Minhas conversões | Lista de conversões filtrada pela role do usuário |

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

### Tela: Lista de Empresas
- Cards com nome, slug, nº de membros, nº de campanhas ativas
- Botão "Nova Empresa"
- Se sem empresas: empty state com CTA para criar

### Tela: Painel da Empresa
- Abas: Visão Geral / Membros / Convites / Campanhas
- Visão Geral: stats (total campanhas, ativas, conversões do mês)

### Tela: Membros
- Tabela: email, role (badge colorido), data de entrada, ação remover
- Botão "Convidar membro" (abre modal)
- Modal de convite: campo email + select de role (influenciador/vendedor)
- Proteção: não exibe botão remover para o único admin

### Tela: Convites
- Tabela: email, role, status (pending/accepted/revoked), data
- Botão "Revogar" em convites pending

### Tela: Campanhas da Empresa
- Lista com nome, influenciador, status (badge), data de criação
- Botão "Nova Campanha"
- Filtro por status

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
- Aba Conversões: tabela com vendedor, valor bruto, desconto, remuneração, data

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
- Aba Conversões: tabela com vendedor, valor bruto, desconto, remuneração, data

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
- Lista cronológica das conversões registradas pelo vendedor
- Cada item: campanha, influenciador, valor bruto, desconto, remuneração, data
- Somente leitura

---

## Estados Globais de UI

| Estado | Comportamento |
|--------|--------------|
| Loading | Skeleton screens (não spinner genérico) |
| Erro de rede | Toast + botão retry |
| Sessão expirada | Redirect automático para login Auth0 |
| Role sem acesso | Redirect para `/` (rota adequada à role) |
| Empty state | Ilustração + CTA contextual |
