# Fluxos de Usuário

---

## Fluxo 1 — Onboarding do Admin (primeira vez)

```
Acessa indiqr.lealcyber.com
    ↓
Auth0 Universal Login (signup ou login com conta que tem role indiqr-admin)
    ↓
Callback → GET /user/me → sem empresas
    ↓
Empty state "Crie sua primeira empresa"
    ↓
Formulário: nome + slug
    ↓
POST /companies/ → empresa criada, admin adicionado como membro
    ↓
Painel da empresa (vazia)
    ↓
CTA "Convidar membros"
```

---

## Fluxo 2 — Convite e Aceite de Membro

```
ADMIN
    └─ Abre painel da empresa → aba Membros
    └─ Clica "Convidar membro"
    └─ Modal: email + role (influenciador | vendedor)
    └─ POST /companies/:id/invitations
    └─ Email enviado pelo backend (Resend)

CONVIDADO (recebe email)
    └─ Clica link no email → /convite/:token
    └─ Tela pública: "Você foi convidado para [Empresa] como [Role]"
    └─ Botão "Aceitar convite"
    └─ Se não autenticado → redirect Auth0 login → volta para /convite/:token
    └─ POST /companies/invitations/:token/accept
    └─ Membro adicionado + role atribuída no Auth0
    └─ Redirect para dashboard da role
```

---

## Fluxo 3 — Ciclo Completo de Campanha

```
ADMIN
    └─ POST /campaigns/
       (nome, influenciador da empresa, remuneração, desconto)
    └─ Email enviado ao influenciador

INFLUENCIADOR (recebe email)
    └─ Login → /campanhas
    └─ Card "aguardando_aceite" aparece
    └─ Abre detalhe → vê parâmetros da campanha
    └─ Clica "Aceitar"
    └─ POST /campaigns/:id/accept
    └─ Status → ativa
    └─ QRCode gerado no backend
    └─ Seção de materiais aparece: baixar PNG / PDF
    └─ Admin notificado por email

INFLUENCIADOR usa o QRCode
    └─ Imprime card PDF e distribui para vendedores parceiros
    └─ Ou compartilha PNG para uso digital

VENDEDOR registra conversão
    └─ (ver Fluxo 4)

ADMIN encerra campanha
    └─ DELETE /campaigns/:id
    └─ QRCode invalidado no backend
    └─ Influenciador notificado
    └─ Novas validações rejeitadas (422)

OU

INFLUENCIADOR sai da campanha
    └─ Botão "Sair da campanha" no detalhe
    └─ DELETE /campaigns/:id
    └─ QRCode invalidado
    └─ Admin notificado
```

---

## Fluxo 4 — Registrar Conversão (Vendedor)

```
Vendedor abre PWA no celular
    └─ Já autenticado (session ativa) → /vender
    └─ Não autenticado → Auth0 login → /vender

Passo 1: Valor
    └─ Campo "Valor da compra: R$ ____"
    └─ Validação: > 0
    └─ Botão "Escanear QRCode"

Passo 2: Scanner
    └─ Câmera abre
    └─ Cliente apresenta QRCode (impresso ou digital)
    └─ QRCode lido automaticamente

Passo 3: Prévia (chamada ao backend)
    └─ POST /conversions/validate
       { qrcode_token, valor_bruto, session_id: "preview" }
       [ou o backend calcula sem persistir — ver nota abaixo]
    └─ Exibe:
       Campanha: [nome]
       Influenciador: [nome/email]
       Valor bruto: R$ 200,00
       Desconto: R$ 10,00 (5%)
       ─────────────────────
       Cobrar do cliente: R$ 190,00
       Remuneração: R$ 20,00
    └─ Botão "Confirmar" | Botão "Cancelar"

Passo 4: Confirmação
    └─ POST /conversions/validate (confirmação real — persistida)
    └─ Tela: "Venda registrada com sucesso!"
    └─ Resumo final exibido (para mostrar ao cliente se necessário)
    └─ Botão "Nova venda"
```

> **Nota:** O endpoint `POST /conversions/validate` já persiste na primeira chamada.
> A prévia é calculada client-side usando as fórmulas do behavior/conversions.md,
> sem chamar a API. A chamada real acontece só no "Confirmar".

---

## Fluxo 5 — Recusa de Campanha (Influenciador)

```
Influenciador → /campanhas → card "aguardando_aceite"
    └─ Abre detalhe
    └─ Clica "Recusar"
    └─ Modal confirmação: "Tem certeza? Esta ação não pode ser desfeita."
    └─ POST /campaigns/:id/decline
    └─ Status → encerrada
    └─ Admin notificado por email
    └─ Card some da lista de campanhas ativas
```

---

## Fluxo 6 — Remoção de Membro

```
Admin → painel da empresa → aba Membros
    └─ Clica "Remover" no membro
    └─ Modal: "Remover [email] da empresa? Esta ação revoga o acesso."
    └─ DELETE /companies/:id/members/:uid
    └─ Membro removido da lista
    └─ Se o membro removido não tiver outras empresas com a role:
       role revogada no Auth0 pelo backend (silencioso)
```

---

## Estados do QRCode na UI do Influenciador

| Estado da campanha | QRCode exibido? | Botões disponíveis |
|-------------------|-----------------|-------------------|
| aguardando_aceite | Não | Aceitar / Recusar |
| ativa | Sim (preview + download) | Baixar PNG / Baixar PDF / Sair |
| encerrada | Não | — (só histórico) |

---

---

## Fluxo 7 — Consentimento de Privacidade (Primeiro Login)

```
Usuário faz login via Auth0 (qualquer role)
    ↓
Callback → GET /user/me → consentiu_privacy_policy == false
    ↓
Tela de aceite bloqueante (modal full-screen)
    ↓
Exibe:
  - Título: "Política de Privacidade"
  - Resumo dos pontos principais (dados coletados, finalidade, direitos)
  - Link: "Ler política completa" → /privacidade
    ↓
Usuário clica "Aceitar"
    ↓
PUT /user/me/consent { privacy_policy_version: "v2.0" }
    ↓
consentiu_privacy_policy = true
    ↓
Redireciona para dashboard da role
```

> **Nota:** Sem consentimento, o usuário não consegue acessar nenhuma funcionalidade
> além da tela de aceite. A proteção é implementada no frontend via guard de rota que
> verifica `consentiu_privacy_policy` após `GET /user/me`.

---

## Fluxo 8 — Renovação de Consentimento (Política Atualizada)

```
Usuário faz login (qualquer role)
    ↓
GET /user/me → privacy_policy_version < current_version
    ↓
Banner no topo (não bloqueante, mas persistente):
  "Nossa Política de Privacidade foi atualizada. Leia as mudanças e aceite para continuar."
    ↓
Usuário clica no banner → modal com diff/resumo das alterações
    ↓
Link: "Ver política completa" → /privacidade
    ↓
Botão "Aceitar nova versão"
    ↓
PUT /user/me/consent { privacy_policy_version: "v2.1" }
    ↓
Banner desaparece, usuário continua normalmente
```

---

## Fluxo 9 — Consentimento para Deploy de Vitrine (Shop)

```
Admin → /loja/config → Botão "Publicar"
    ↓
Modal de consentimento:
  - Título: "Confirmação de Publicação"
  - Lista dos dados que ficarão públicos:
    • Nome da empresa
    • Email de contato
    • Instagram
    • WhatsApp
    • Logo e imagens
    • Produtos e categorias
  - Checkbox: "Declaro que li e aceito a Política de Privacidade e autorizo
    a publicação destes dados publicamente."
  - Link para política de privacidade
    ↓
Admin marca checkbox e clica "Publicar"
    ↓
Registra consentimento do shop + deploy
    ↓
Redireciona para preview da vitrine publicada
```

---

## Fluxo 10 — Revogação de Consentimento

```
Usuário → /perfil → Aba Privacidade
    ↓
Seção "Consentimento":
  - Status atual: "Consentiu em [data] — versão [v]" ou "Não consentiu"
  - Link para política de privacidade
  - Botão "Revogar consentimento"
    ↓
Modal de confirmação:
  "Ao revogar, seus dados não serão mais tratados para finalidades que dependem
   de consentimento. Registros anteriores permanecem por obrigação legal.
   Deseja continuar?"
    ↓
Usuário confirma
    ↓
DELETE /user/me/consent
    ↓
consentiu_privacy_policy = false
    ↓
Redireciona para tela de aceite (Fluxo 7)
```

---

## Navegação por Role

```
Login → GET /user/me → extrai roles do token

indiqr-admin        → /empresas
indiqr-influenciador → /campanhas
indiqr-vendedor     → /vender

Usuário sem role    → tela "Aguardando acesso"
                      (conta criada mas ainda não convidado)
```
