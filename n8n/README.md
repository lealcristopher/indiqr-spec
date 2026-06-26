# Fluxo n8n — Chat Qualificação de Leads

## Visão Geral

Workflow n8n que processa leads capturados pelo chat de qualificação da landing page IndiQR e envia um email automático de acompanhamento.

## Nós do Fluxo

### 1. Webhook — `lead-chat`

- **Path:** `/webhook/lead-chat`
- **Método:** POST
- **Payload esperado:**
  ```json
  {
    "step": 0,
    "lead": {
      "nome": "Nome do Lead",
      "email": "lead@email.com",
      "telefone": "(11) 99999-9999",
      "empresa": "Nome da Empresa"
    }
  }
  ```
- Este webhook já é chamado pelo chat widget na landing page.

### 2. Buscar Template Email (HTTP Request)

- **Método:** GET
- **URL:** `https://private.indiqr.com.br/email/template_lead_qualification.html`
- **Response Format:** `string`
- Busca o template HTML hospedado no Cloudflare R2.

### 3. Preparar Dados do Email (Set)

Substitui os placeholders do template pelos dados do lead:

| Campo | Expressão |
|-------|-----------|
| `htmlContent` | `={{ $json['data'].replace('{%NOME%}', $items('Webhook').first().json.lead.nome).replace('{%URL_CTA%}', 'https://private.indiqr.com.br/preview/ebooks/marketing_de_indicacao.html') }}` |
| `leadEmail` | `={{ $items('Webhook').first().json.lead.email }}` |
| `leadName` | `={{ $items('Webhook').first().json.lead.nome }}` |

**Placeholders no template:**
- `{%NOME%}` → Nome do lead (coletado no chat)
- `{%URL_CTA%}` → URL fixa do e-book

### 4. Enviar Email Lead (Resend)

- **Resource:** `email`
- **Operation:** `send`
- **From:** `IndiQR <onboarding@resend.dev>`
- **To:** `{{ leadEmail }}`
- **Subject:** `Obrigado pelo seu interesse na IndiQR!`
- **HTML:** `{{ htmlContent }}`

### Credenciais

O nó Resend requer uma API Key configurada nas credenciais do n8n com a chave da API Resend (`RESEND_API_KEY`).

## Conteúdo do Email

O template `template_lead_qualification.html` envia:

1. **Saudação personalizada** — "Olá {NOME},"
2. **Título** — "Obrigado pelo seu interesse!"
3. **Corpo** — Agradecimento + aviso de contato futuro + e-book exclusivo
4. **CTA** — Botão "Baixar E-book Exclusivo" → `https://private.indiqr.com.br/preview/ebooks/marketing_de_indicacao.html`

## Upload do Template

O template `template_lead_qualification.html` deve ser enviado ao Cloudflare R2:

```bash
./scripts/upload-email-template-to-r2.sh
```

O script já faz upload de todos os templates da pasta `email/` para o bucket.
