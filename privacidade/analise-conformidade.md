# Análise de Conformidade com a Política de Privacidade

**Data:** 10 de junho de 2026
**Alcance:** Repositórios `api-indiqr` e `indiqr-shop-frontend`
**Referência:** Política de Privacidade em `privacidade/politica-de-privacidade.md`

---

## Sumário Executivo

A plataforma IndiQR implementa **boas práticas de segurança** (RBAC, JWT validation, input sanitization, log masking, error hardening) mas **não possui mecanismos de consentimento, exclusão de dados, exportação de dados ou transparência ativa**. A nota geral de conformidade com a Política de Privacidade e a LGPD é **C (parcialmente conforme)**.

---

## Checklist de Conformidade

| # | Requisito | api-indiqr | indiqr-shop-frontend | Status |
|---|-----------|------------|----------------------|--------|
| 1 | Finalidade e base legal documentadas | Documentado na Política (não no código) | — | C |
| 2 | Consentimento explícito para dados sensíveis | Especificado (F1) | Não implementado | C |
| 3 | Mecanismo de revogação de consentimento | Especificado (F3) | Não implementado | C |
| 4 | Exclusão / anonimização de dados pessoais | Não implementado (não há endpoint) | — | D |
| 5 | Exportação / portabilidade de dados | Não implementado (não há endpoint) | — | D |
| 6 | Transparência — link para política | Não implementado | Não implementado | D |
| 7 | Segurança — autenticação | JWT RS256 com validação aud/iss | Auth0 SDK | A |
| 8 | Segurança — autorização (RBAC) | 3 roles isolados com verificação por endpoint | Guards por role | A |
| 9 | Segurança — IDOR protection | Sim (403/404 sem vazamento de existência) | — | A |
| 10 | Segurança — sanitização de logs | Sim (OTP mascarado, sem stack trace) | — | A |
| 11 | Segurança — validação de entrada | Pydantic com schemas restritivos | Zod + React Hook Form | A |
| 12 | Segurança — CORS | Origens autorizadas restritas | — | A |
| 13 | Segurança — rate limiting | Parcial (implementado parcialmente) | — | B |
| 14 | Notificação de incidentes de segurança | Não implementado | — | D |
| 15 | Retenção — política de prazos | Documentado na Política (não no código) | — | C |
| 16 | Retenção — limpeza automática | Não implementado | — | D |
| 17 | Compartilhamento — inventário de terceiros | Documentado na Política (não no código) | — | C |
| 18 | Cookies — ausência de tracking | Sem cookies de tracking ou analytics | Sem cookies de tracking ou analytics | A |
| 19 | DPO — canal de contato | Em implementação ([IND-54](/IND/issues/IND-54)) | — | C→B |
| 20 | Vitrine pública — consentimento explícito | Não implementado (deploy é silencioso) | — | D |

**Legenda:** A = Conforme | B = Parcialmente conforme | C = Documentado mas não implementado | D = Não conforme / Não implementado

---

## Análise Detalhada por Domínio

### 1. Consentimento (Art. 7º, I e Art. 8º da LGPD)

**Problema:** O código não implementa nenhum mecanismo de coleta, registro ou verificação de consentimento.

**Impacto:** Sem registro de consentimento, a plataforma não consegue demonstrar que o titular concordou com o tratamento de dados, exigência do Art. 8º, §2º da LGPD.

**Ações necessárias:**

1. Adicionar campo `consentiu_privacy_policy` (boolean + timestamp) ao modelo `Usuario`
2. Implementar endpoint `PUT /api/v1/user/me/consent` que registra a versão da política aceita
3. No frontend, implementar tela de aceite obrigatório no primeiro login após atualização da política
4. Na vitrine (Shop), implementar modal de confirmação antes do deploy que informe sobre a exposição pública dos dados e registre o consentimento

### 2. Direitos do Titular — Exclusão (Art. 18, IV e VI)

**Problema:** Não existe endpoint para exclusão ou anonimização de dados pessoais.

**Impacto:** Impossibilidade de atender solicitações de titulares que queiram excluir seus dados.

**Ações necessárias:**

1. Implementar `DELETE /api/v1/user/me` com as seguintes etapas:
   - Remover roles do Auth0 via Management API (`DELETE /api/v2/users/{auth_id}/roles`)
   - Anonimizar `usuarios.email` (substituir por hash irreversível)
   - Remover `usuarios.auth_id` (desvincula da conta Auth0)
   - Manter registros de conversões e resgates com `influenciador_id` e `vendedor_id` (obrigação legal de auditoria)
   - Soft-delete de campanhas e convites associados
2. Implementar período de carência de 30 dias antes da exclusão definitiva (com notificação por email)
3. Documentar claramente que registros financeiros (conversões e resgates) são imutáveis

### 3. Direitos do Titular — Portabilidade (Art. 18, V)

**Problema:** O endpoint `GET /api/v1/user/me` retorna apenas `id`, `email`, `roles` e `company_id`.

**Impacto:** Impossibilidade de atender solicitações de portabilidade.

**Ações necessárias:**

1. Implementar `GET /api/v1/user/me/export` que retorna JSON estruturado com todos os dados do titular:
   - Dados do usuário (email, data de cadastro)
   - Empresas das quais é membro (com role)
   - Campanhas criadas ou participadas
   - Conversões associadas
   - Resgates e saldo de carteira
2. Formato de exportação: JSON ou CSV, conforme preferência do titular

### 4. Transparência Ativa

**Problema:** A plataforma não expõe link para a Política de Privacidade, não informa sobre coleta de dados no momento do cadastro, e não notifica sobre alterações na política.

**Ações necessárias:**

1. Adicionar link para `/privacidade` no footer da aplicação
2. Exibir banner de aceite da política no primeiro login e após atualizações
3. Adicionar campo `privacy_policy_version` em `GET /api/v1/user/me` para o frontend verificar se o usuário já aceitou a versão mais recente
4. Implementar `GET /api/v1/privacy` que retorna a política atual e sua versão

### 5. Retenção e Limpeza Automática

**Problema:** A política define períodos de retenção, mas não há mecanismo de limpeza automática.

**Ações necessárias:**

1. Implementar job agendado (cron) que:
   - Remove tokens de resgate expirados há mais de 90 dias (não mais necessários para auditoria)
   - Remove convites pendentes há mais de 180 dias
   - Anonimiza usuários que solicitaram exclusão após período de carência
2. Adicionar `scheduled_for_deletion_at` no modelo `Usuario`

### 6. Vitrine Pública — Exposição de Dados

**Problema:** O endpoint `POST /shop/{handle}/deploy` publica dados da empresa (nome, email, Instagram, WhatsApp) publicamente sem aviso explícito ou consentimento.

**Ações necessárias:**

1. Antes do deploy, exibir modal com resumo dos dados que ficarão públicos
2. Registrar consentimento específico (`consentiu_shop_publicacao: boolean + timestamp`)
3. Incluir no site estático gerado um link para política de privacidade e opção de contato do DPO

### 7. Canal do DPO

**Problema:** O email `privacidade@indiqr.lealcyber.com` está definido na política mas não referenciado em nenhum lugar da aplicação.

**Ações necessárias:**

1. Adicionar link para contato do DPO no footer da aplicação
2. Adicionar header HTTP `X-Data-Protection-Officer: privacidade@indiqr.lealcyber.com` nas respostas da API
3. Criar endpoint `POST /api/v1/privacy/request` para receber solicitações de titulares diretamente pela plataforma

---

## Conformidades Existentes (Pontos Positivos)

### Segurança de Autenticação
- JWT RS256 com validação rigorosa de `aud` (audience), `iss` (issuer) e `exp` (expiration)
- Três modos de auth para ambientes diferentes (auth0, local_jwks, mock)
- Tokens de convite com 32 caracteres URL-safe, não sequenciais

### Controle de Acesso (RBAC)
- Três roles isolados com verificação em todos os endpoints
- Permissões granulares via `require_permission("x:y")`
- Sem IDOR: endpoints retornam 403 ou lista vazia para recursos de outras empresas

### Proteção de Dados Sensíveis
- Códigos OTP de 6 dígitos mascarados nos logs (nunca em texto plano)
- Respostas de erro não ecoam tokens ou códigos tentados
- Stack traces nunca retornados em produção
- Sem debug mode em produção

### Segurança de Infraestrutura
- Segredos gerenciados via Akeyless (nunca em código-fonte)
- CI/CD com Gitleaks, Trivy, Ruff e Bandit
- Contrato API validado via Schemathesis
- TLS em todas as conexões de rede

### Frontend
- Sem cookies de tracking, analytics ou publicidade
- JWT em memória (não em localStorage/cookies)
- PWA com service worker para cache offline (sem armazenamento persistente de dados pessoais)

---

## Plano de Ação Recomendado

### Fase 1 — Crítico (0-15 dias)
- [ ] Implementar endpoint de consentimento (`PUT /user/me/consent`)
- [ ] Adicionar campo `consentiu_privacy_policy` ao modelo `Usuario`
- [ ] Frontend: tela de aceite da política no primeiro login
- [ ] Link para política no footer da aplicação

### Fase 2 — Essencial (15-45 dias)
- [ ] Implementar `DELETE /user/me` com anonimização
- [ ] Implementar `GET /user/me/export` para portabilidade
- [ ] Implementar endpoint de solicitação de direitos (`POST /privacy/request`)
- [ ] Modal de consentimento para deploy de vitrine pública

### Fase 3 — Recomendado (45-90 dias)
- [ ] Job de limpeza automática de dados expirados
- [ ] Sistema de versionamento da política de privacidade
- [ ] Notificação proativa de alterações na política
- [ ] Dashboard de privacidade no perfil do usuário
- [ ] Header `X-Data-Protection-Officer` nas respostas

---

**Responsável pela análise:** CTO (agente `1382266e-0ebc-4691-b38d-9bd0790d1a10`)
**Referência:** [IND-46](/IND/issues/IND-46)
