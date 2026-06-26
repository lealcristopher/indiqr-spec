# Relatório de Impacto à Proteção de Dados Pessoais (DPIA)

**Fluxo Financeiro: Conversões e Resgates — IndiQR**

| Campo | Valor |
|-------|-------|
| **Versão** | 1.1 (revisão DPO) |
| **Data** | 11 de junho de 2026 |
| **Status** | Aprovado com recomendações — DPO |
| **Referência** | LGPD Art. 38; Resolução CD/ANPD nº 2/2022 |
| **Issue vinculada** | [IND-63](/IND/issues/IND-63) |
| **Repositório** | [indiqr-spec](https://github.com/lealcristopher/indiqr-spec) |

---

## 1. Identificação dos Agentes de Tratamento

### 1.1 Controlador

| Campo | Valor |
|-------|-------|
| Nome | LealCyber (operadora da plataforma IndiQR) |
| CNPJ | (pendente — aguardando confirmação do CEO; follow-up: IND-71) |
| Endereço | (pendente — aguardando confirmação do CEO; follow-up: IND-71) |
| Encarregado (DPO) | `privacidade@indiqr.lealcyber.com` |

### 1.2 Operadores (Suboperadores)

| Operador | Serviço | Dados tratados | Localização |
|----------|---------|----------------|-------------|
| Auth0 (Okta, Inc.) | Autenticação e autorização | `email`, `auth_id`, roles | EUA / Global |
| Resend (Resend, Inc.) | Envio de emails transacionais | `email` do destinatário | EUA |
| Neon (Neon, Inc.) | Banco de dados PostgreSQL serverless | Todos os dados operacionais | Região AWS (definida pelo cliente) |
| Grafana Cloud (Grafana Labs) | Observabilidade (logs e traces) | Logs de acesso (`client_ip`, `path`, `status_code`) | EUA / Global |
| Akeyless (Akeyless Security) | Gerenciamento de segredos | Nenhum dado pessoal — apenas credenciais de infraestrutura | Definido pelo cliente |
| Cloudflare R2 (Cloudflare, Inc.) | Armazenamento de mídia (vitrine) | Imagens e dados públicos da vitrine | Global (CDN) |

### 1.3 Equipe Responsável pela DPIA

| Papel | Agente Paperclip |
|-------|-----------------|
| Condução técnica | CTO (`1382266e-0ebc-4691-b38d-9bd0790d1a10`) |
| Análise de conformidade base | DPO (`edd37e14-9370-49a8-90c7-ab819b528891`) em [IND-51](/IND/issues/IND-51) |
| Revisão final | DPO — a ser realizada antes da publicação |

---

## 2. Escopo do Tratamento

### 2.1 Fluxos analisados

Esta DPIA cobre dois fluxos de tratamento de dados do IndiQR que envolvem dados financeiros e, portanto, apresentam risco elevado aos titulares conforme Art. 4º, §1º da Resolução CD/ANPD nº 2/2022:

1. **Fluxo de Conversão** — Registro de uma conversão financeira vinculada a uma campanha de indicação
2. **Fluxo de Resgate** — Geração, validação e execução de resgate de saldo (reais ou pontos) por influenciador

### 2.2 Contexto de negócio

O IndiQR é uma plataforma SaaS de marketing por indicação com remuneração por conversão. Empresas (Admins) criam campanhas, convidam influenciadores (que divulgam produtos/serviços com QRCode próprio) e vendedores no ponto de venda validam as conversões. O influenciador acumula saldo (reais ou pontos) que pode ser resgatado na vitrine virtual (Shop) da empresa.

### 2.3 Dados pessoais envolvidos nos fluxos financeiros

| Categoria | Dado pessoal | Fonte | Natureza |
|-----------|-------------|-------|----------|
| Identificação do influenciador | `influenciador_id` (FK → `usuarios.id`) | Sistema | Identificador indireto (vínculo com `usuarios.email`) |
| Identificação do vendedor | `vendedor_id` (FK → `usuarios.id`) | Sistema | Identificador indireto |
| Valor da transação | `valor_bruto` | Entrada do vendedor no app | Dado financeiro vinculado ao titular |
| Cálculo da remuneração | `remuneracao_valor`, `desconto_valor` | Sistema (calculado) | Dado financeiro derivado |
| Código de resgate (OTP) | `code` (CHAR 6 numérico) | Sistema (gerado aleatoriamente) | Token de autorização de resgate |
| Valor do resgate | `valor` (Numeric), `tipo` (reais/pontos) | Entrada do influenciador | Dado financeiro do titular |
| Timestamp da operação | `created_at` | Sistema automático | Metadado de auditoria |

---

## 3. Descrição do Tratamento

### 3.1 Fluxo de Conversão

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Vendedor   │     │  IndiQR API │     │  PostgreSQL  │     │ Auth0 (JWT) │
│  (PWA app)  │     │  (FastAPI)  │     │   (Neon)    │     │             │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │                   │
       │ 1. POST /conversions/validate          │                   │
       │   {qrcode_token}  │                   │                   │
       │──────────────────>│                   │                   │
       │                   │ 2. Validar JWT    │                   │
       │                   │──────────────────────────────────────>│
       │                   │ 3. Buscar QRCode  │                   │
       │                   │──────────────────>│                   │
       │                   │ 4. Retornar dados │                   │
       │                   │   da campanha     │                   │
       │                   │<──────────────────│                   │
       │ 5. Exibir preview │                   │                   │
       │<──────────────────│                   │                   │
       │                   │                   │                   │
       │ 6. POST /conversions                  │                   │
       │   {qrcode_token,  │                   │                   │
       │    valor_bruto}   │                   │                   │
       │──────────────────>│                   │                   │
       │                   │ 7. Calcular       │                   │
       │                   │   remuneracao +   │                   │
       │                   │   desconto        │                   │
       │                   │ 8. INSERT         │                   │
       │                   │   conversions     │                   │
       │                   │──────────────────>│                   │
       │                   │ 9. Atualizar      │                   │
       │                   │   carteira        │                   │
       │                   │──────────────────>│                   │
       │ 10. 201 Created  │                   │                   │
       │<──────────────────│                   │                   │
```

**Descrição passo a passo:**

1. Vendedor escaneia QRCode do influenciador no app PWA
2. API valida JWT do vendedor (role `indiqr-vendedor`) via Auth0
3. API busca QRCode pelo token e verifica se a campanha está ativa
4. API retorna dados da campanha para preview (sem dados do influenciador)
5. Vendedor insere `valor_bruto` da compra realizada pelo cliente
6. API calcula `desconto_valor` e `remuneracao_valor` com base no modelo da campanha (fixo ou percentual)
7. API insere registro imutável na tabela `conversions`
8. API atualiza saldo da `carteiras` do influenciador
9. Conversão registrada — sem possibilidade de alteração ou exclusão (ADR-004)

**Dados pessoais coletados neste fluxo:**
- `vendedor_id` (extraído do JWT) — identifica quem validou a conversão
- `influenciador_id` (do QRCode/campanha) — identifica quem recebe a remuneração
- `valor_bruto` — valor da compra do cliente final (não identificado)

**Dados NÃO coletados neste fluxo:**
- Dados do cliente final que realizou a compra
- Dados de pagamento (cartão, PIX, etc.)
- Geolocalização do vendedor ou cliente

### 3.2 Fluxo de Resgate

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│Influenciador│     │  IndiQR API │     │  PostgreSQL  │     │   Resend    │
│  (Web App)  │     │  (FastAPI)  │     │   (Neon)    │     │  (Email)    │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │                   │
       │ 1. POST /redemptions/generate-token    │                   │
       │   {valor, tipo}   │                   │                   │
       │──────────────────>│                   │                   │
       │                   │ 2. Verificar saldo│                   │
       │                   │──────────────────>│                   │
       │                   │ 3. Gerar OTP      │                   │
       │                   │   (6 dígitos)     │                   │
       │                   │ 4. INSERT         │                   │
       │                   │   resgate_tokens  │                   │
       │                   │──────────────────>│                   │
       │                   │ 5. Enviar email   │                   │
       │                   │   com OTP ───────────────────────────>│
       │ 6. {code,         │                   │                   │
       │    expires_at}    │                   │                   │
       │<──────────────────│                   │                   │
       │                   │                   │                   │
       │ 7. POST /redemptions/validate-resgate │                   │
       │   {code}          │                   │                   │
       │──────────────────>│                   │                   │
       │                   │ 8. Validar OTP    │                   │
       │                   │   (não expirado,  │                   │
       │                   │    não usado)     │                   │
       │                   │──────────────────>│                   │
       │                   │ 9. INSERT resgates│                   │
       │                   │   (imutável)      │                   │
       │                   │──────────────────>│                   │
       │                   │ 10. Debitar       │                   │
       │                   │    carteira       │                   │
       │                   │──────────────────>│                   │
       │                   │ 11. Marcar OTP    │                   │
       │                   │    como usado     │                   │
       │                   │──────────────────>│                   │
       │ 12. 200 OK        │                   │                   │
       │   confirmação     │                   │                   │
       │<──────────────────│                   │                   │
```

**Descrição passo a passo:**

1. Influenciador solicita geração de token de resgate informando `valor` e `tipo` (reais/pontos)
2. API verifica se o influenciador tem saldo suficiente na carteira
3. API gera código OTP aleatório de 6 dígitos (único entre tokens pendentes)
4. API insere token com `expires_at` = `created_at + 15 minutos`, status `pendente`
5. API envia email transacional (Resend) com o código OTP para o email do influenciador
6. API retorna `code` (OTP) e `expires_at` ao frontend (também enviado por email)
7. No ponto de venda, o vendedor insere o código OTP de 6 dígitos no app PWA
8. API valida OTP: não expirado, não usado anteriormente
9. API insere registro imutável na tabela `resgates`
10. API debita o valor da carteira do influenciador
11. API marca o `resgate_token` como `usado`
12. Confirmação de resgate concluído

**Dados pessoais coletados neste fluxo:**
- `influenciador_id` (do JWT) — identifica quem solicita/recebe o resgate
- `vendedor_id` (do JWT) — identifica quem valida/executa o resgate
- `email` do influenciador — utilizado para envio do código OTP (via Resend)

**Dados NÃO coletados neste fluxo:**
- Dados bancários ou de pagamento (os pagamentos são realizados por fora da plataforma)
- Dados do cliente final

---

## 4. Necessidade e Proporcionalidade

### 4.1 Por que cada dado é necessário?

| Dado | Finalidade | Base legal (LGPD) | Se não coletado... |
|------|-----------|-------------------|-------------------|
| `influenciador_id` | Vínculo da conversão/resgate ao influenciador correto; cálculo e acúmulo de remuneração | Art. 7º, II — Execução de contrato | Impossível atribuir remuneração; a plataforma perde sua função principal |
| `vendedor_id` | Vínculo da conversão/resgate ao vendedor que validou a operação; trilha de auditoria | Art. 7º, II — Execução de contrato | Impossível rastrear quem validou cada operação; perda de accountability |
| `valor_bruto` | Base de cálculo da remuneração e desconto aplicável | Art. 7º, II — Execução de contrato | Impossível calcular remuneração do influenciador ou desconto do cliente |
| `remuneracao_valor` | Registro do valor devido ao influenciador pela conversão | Art. 7º, II — Execução de contrato | Impossível auditar quanto foi pago por cada conversão |
| `desconto_valor` | Registro do desconto aplicado ao cliente na conversão | Art. 7º, II — Execução de contrato | Impossível rastrear política de descontos da campanha |
| `email` (influenciador) | Envio do código OTP de 6 dígitos para autorização do resgate | Art. 7º, II — Execução de contrato | Impossível validar que o solicitante do resgate é o titular da conta |
| `code` (OTP) | Segundo fator de autorização para execução do resgate | Art. 7º, II — Execução de contrato | Risco de resgate não autorizado; perda do mecanismo antifraude |
| `tipo` (reais/pontos) | Identificar em qual carteira (reais ou pontos) o resgate deve ser debitado | Art. 7º, II — Execução de contrato | Impossível debitar a carteira correta |
| `created_at` | Registro temporal para auditoria e verificação de expiração de tokens | Art. 7º, VI — Legítimo interesse | Impossível auditar ordem cronológica ou expiração de tokens |

### 4.2 Proporcionalidade — avaliação

**Minimização de dados.** O IndiQR coleta apenas os identificadores estritamente necessários para a operação financeira. Em particular:

- **Não coleta** dados do cliente final que realizou a compra (nome, CPF, email, cartão)
- **Não coleta** dados bancários ou de pagamento dos influenciadores (pagamentos são por fora)
- **Não coleta** geolocalização, biometria ou dados sensíveis (Art. 5º, II da LGPD)
- **Não cruza** dados de conversões com fontes externas para enriquecimento de perfil
- **Não cria** perfis comportamentais ou scores de crédito dos titulares

**Limitação de finalidade.** Cada dado tem finalidade única e documentada, sem reutilização para fins secundários (marketing, análise de crédito, venda de dados).

**Prazo de retenção adequado.** Conversões e resgates são imutáveis por obrigação de auditoria financeira (ADR-004, ADR-007), em conformidade com o Art. 16 da LGPD. Tokens de resgate expirados são mantidos para trilha de auditoria. Logs de acesso são retidos por 90 dias.

**Alternativas consideradas e descartadas:**
- Anonimização total dos registros financeiros: descartada, pois impossibilitaria auditoria contábil/fiscal
- Deleção de registros antigos: descartada, pois violaria obrigações legais de guarda de registros financeiros
- Uso de hash nos identificadores: considerado para cenários pós-exclusão de conta, mas ainda não implementado (vide Seção 6)

---

## 5. Identificação e Avaliação dos Riscos

### 5.1 Matriz de riscos

Escala: **B** = Baixo | **M** = Médio | **A** = Alto | **C** = Crítico

| # | Risco | Probab. | Impacto | Severidade | Descrição |
|---|-------|---------|---------|------------|-----------|
| R1 | Acesso não autorizado a dados de conversões | M | A | **Alto** | Um atacante que explore falha de autorização poderia acessar o histórico financeiro completo de todos os influenciadores, incluindo valores de remuneração |
| R2 | Vazamento de dados por log excessivo | M | M | **Médio** | Logs de aplicação podem conter `valor_bruto` ou `remuneracao_valor` em texto plano, expondo dados financeiros no Grafana Cloud |
| R3 | Resgate não autorizado (roubo de OTP) | B | A | **Médio** | Um atacante que obtenha o código OTP de 6 dígitos + acesso físico ao vendedor poderia realizar resgate fraudulento |
| R4 | Impossibilidade de exclusão de dados financeiros | — | M | **Médio** | Registros de conversões e resgates são imutáveis. Titular não pode solicitar exclusão desses dados, apenas do vínculo com seu identificador |
| R5 | Transferência internacional sem salvaguardas adequadas | M | M | **Médio** | Dados financeiros armazenados no Neon (PostgreSQL) podem residir em região AWS fora do Brasil, dependendo da configuração do cliente |
| R6 | Acesso privilegiado não controlado ao banco de dados | B | C | **Alto** | Um operador com acesso direto ao PostgreSQL poderia consultar ou modificar dados financeiros sem registro de auditoria |
| R7 | Exposição de dados na vitrine pública | M | M | **Médio** | A vitrine pública (Shop) pode expor indiretamente dados financeiros se nomes de produtos ou preços em pontos revelarem informações sobre carteiras |
| R8 | Violação de dados em suboperador | B | A | **Alto** | Um incidente de segurança no Neon, Auth0 ou Resend poderia expor dados financeiros dos titulares |
| R9 | Inexistência de notificação de incidentes | — | A | **Alto** | A plataforma não possui mecanismo implementado para notificar titulares e ANPD em caso de incidente de segurança (gap identificado em [IND-51](/IND/issues/IND-51)) |
| R10 | Ausência de registro de consentimento | — | A | **Alto** | Não há mecanismo de coleta e registro de consentimento para tratamento de dados, exigido pelo Art. 8º, §2º da LGPD (gap identificado em [IND-51](/IND/issues/IND-51)) |

### 5.2 Análise detalhada dos riscos elevados

#### R1 — Acesso não autorizado a dados de conversões (Severidade: Alta)

**Cenário:** Um influenciador autenticado que manipule parâmetros de requisição poderia tentar acessar conversões de outros influenciadores ou empresas.

**Controles existentes:**
- RBAC com três roles isolados: `indiqr-admin`, `indiqr-influenciador`, `indiqr-vendedor`
- Verificação de pertencimento à empresa em todos os endpoints (IDOR protection)
- Admin vê todas as conversões da empresa; influenciador vê apenas as suas; vendedor vê apenas as que validou

**Risco residual:** Baixo — controles de autorização são aplicados de forma consistente em todos os endpoints.

#### R6 — Acesso privilegiado não controlado ao banco de dados (Severidade: Alta)

**Cenário:** Um administrador de infraestrutura com credenciais do Neon poderia acessar diretamente o banco de dados, consultar dados financeiros de todos os titulares, e potencialmente modificá-los.

**Controles existentes:**
- Credenciais do banco gerenciadas via Akeyless (nunca em código-fonte)
- Conexão ao Neon é TLS 1.2+
- CI/CD com Gitleaks para prevenção de vazamento de credenciais

**Controles ausentes:**
- Não há audit log no nível de banco de dados
- Não há separação de duties para acesso ao banco de produção
- Não há criptografia em nível de aplicação para dados financeiros

**Risco residual:** Médio — credenciais são bem protegidas, mas não há trilha de auditoria para acessos diretos.

#### R9 — Inexistência de notificação de incidentes (Severidade: Alta)

**Cenário:** Um incidente de segurança que exponha dados financeiros ocorreria sem que a plataforma tivesse mecanismo para notificar titulares e ANPD no prazo legal.

**Status:** Não implementado. Identificado como gap no relatório de conformidade [IND-51](/IND/issues/IND-51).

**Risco residual:** Alto — requer implementação urgente de procedimento de resposta a incidentes.

#### R10 — Ausência de registro de consentimento (Severidade: Alta)

**Cenário:** A plataforma não consegue demonstrar que os titulares consentiram com o tratamento de seus dados financeiros, exigência do Art. 8º, §2º da LGPD.

**Status:** Não implementado. Identificado como gap no relatório de conformidade [IND-51](/IND/issues/IND-51). A base legal principal é execução de contrato (Art. 7º, II), mas o consentimento ainda é necessário para finalidades acessórias (ex.: exposição na vitrine).

**Risco residual:** Alto — requer implementação de mecanismo de registro de consentimento com versionamento.

---

## 6. Medidas de Mitigação

### 6.1 Medidas existentes (implementadas)

| Medida | Risco mitigado | Eficácia | Evidência |
|--------|---------------|----------|-----------|
| RBAC com 3 roles isolados + verificação de pertencimento | R1 | Alta | `app/policies/permissions.py`, `behavior/rbac.md` |
| JWT RS256 com validação de `aud`, `iss`, `exp` | R1 | Alta | `app/api/v1/endpoints/auth.py` |
| Códigos OTP mascarados nos logs | R2 | Alta | `app/core/logging_config.py` |
| OTP de 6 dígitos com expiração de 15 minutos | R3 | Média | ADR-007, `app/api/v1/endpoints/redemptions.py` |
| Registros financeiros imutáveis (sem `updated_at`, sem endpoint de update/delete) | R4 | Alta | ADR-004, ADR-007 |
| Auditoria completa via `created_at` em todas as tabelas | R4 | Alta | `architecture.md` — Domain Model |
| Segredos via Akeyless (nunca em código-fonte) | R6 | Alta | `app/core/settings.py` |
| Gitleaks + Trivy no pipeline CI/CD | R6, R8 | Média | `.github/workflows/` |
| TLS 1.2+ em todas as conexões | R2, R8 | Alta | `architecture.md` |
| CORS restrito a origens autorizadas | R1 | Média | `app/main.py` |
| Rate limiting em endpoints de validação (OTP e QRCode) | R3 | Média | `app/api/v1/endpoints/conversions.py`, `redemptions.py` |
| Sem coleta de dados bancários, CPF ou geolocalização | R2 | Alta | Por design (escopo do MVP, `architecture.md`) |

### 6.2 Medidas planejadas (não implementadas)

| # | Medida | Risco mitigado | Fase | Prazo | Referência |
|---|--------|---------------|------|-------|-----------|
| M1 | Implementar `PUT /user/me/consent` com registro de versão da política aceita | R10 | Fase 1 | 15 dias | [IND-51](/IND/issues/IND-51) Fase 1 |
| M2 | Implementar `DELETE /user/me` com anonimização (hash do email, remoção de `auth_id`, manutenção de `influenciador_id` em registros financeiros) | R4 | Fase 2 | 45 dias | [IND-51](/IND/issues/IND-51) Fase 2 |
| M3 | Implementar `GET /user/me/export` para portabilidade de dados financeiros | R4 | Fase 2 | 45 dias | [IND-51](/IND/issues/IND-51) Fase 2 |
| M4 | Implementar endpoint `POST /privacy/request` para receber solicitações de titulares | R4, R9 | Fase 2 | 45 dias | [IND-51](/IND/issues/IND-51) Fase 2 |
| M5 | Implementar procedimento de resposta a incidentes de segurança com notificação à ANPD e titulares | R9 | Fase 2 | 45 dias | Gap identificado nesta DPIA |
| M6 | Implementar dashboard de privacidade no perfil do usuário | R4 | Fase 3 | 90 dias | [IND-51](/IND/issues/IND-51) Fase 3 |
| M7 | Header `X-Data-Protection-Officer` em todas as respostas da API | R9 | Fase 3 | 90 dias | [IND-51](/IND/issues/IND-51) Fase 3 |
| M8 | Job de limpeza automática de dados expirados (tokens de resgate > 90 dias, convites > 180 dias, anonimização pós-carência) | R2 | Fase 3 | 90 dias | [IND-51](/IND/issues/IND-51) Fase 3 |
| M9 | Criptografia em nível de aplicação para campos financeiros sensíveis (`valor_bruto`, `remuneracao_valor`) com chave gerenciada via Akeyless | R6, R8 | Fase 3 | 90 dias | Recomendação nova desta DPIA |
| M10 | Audit log no nível de banco de dados (pgAudit ou trigger-based) para acessos a tabelas financeiras | R6 | Fase 3 | 90 dias | Recomendação nova desta DPIA |
| M11 | Modal de consentimento explícito para deploy de vitrine pública (Shop) informando exposição pública de dados | R7 | Fase 2 | 45 dias | [IND-51](/IND/issues/IND-51) Fase 2 |

### 6.3 Medidas de mitigação adicionais recomendadas por esta DPIA

Além das medidas já planejadas no relatório de conformidade [IND-51](/IND/issues/IND-51), esta DPIA recomenda:

1. **Criptografia em nível de aplicação (M9):** Aplicar envelope encryption nos campos `valor_bruto`, `remuneracao_valor` e `desconto_valor` na tabela `conversions`, e `valor` na tabela `resgates`. A chave de envelope seria gerenciada via Akeyless. Isso mitiga o risco de exposição direta no banco de dados (R6) e em caso de incidente no Neon (R8).

2. **Audit log de banco de dados (M10):** Implementar audit logging (pgAudit ou triggers) para registrar consultas a tabelas financeiras (`conversions`, `resgates`, `carteiras`, `resgate_tokens`). Essencial para detectar acessos não autorizados e manter trilha de auditoria completa.

3. **Procedimento de notificação de incidentes (M5):** Documentar e testar o fluxo de notificação à ANPD e titulares em caso de incidente de segurança envolvendo dados financeiros, incluindo template de comunicação e canais de acionamento.

---

## 7. Conclusão

### 7.1 Avaliação geral de risco

O tratamento de dados financeiros (conversões e resgates) no IndiQR apresenta **risco moderado a alto** aos titulares, principalmente devido a:

- **Controles técnicos robustos:** RBAC, JWT validation, imutabilidade de registros, OTP para resgates, sanitização de logs
- **Gaps de conformidade relevantes:** ausência de mecanismo de consentimento, exclusão, portabilidade e notificação de incidentes
- **Riscos residuais aceitáveis:** com a implementação das medidas planejadas nas Fases 1, 2 e 3 do plano de ação de [IND-51](/IND/issues/IND-51), o risco residual será reduzido a **baixo**

### 7.2 Parecer técnico

**Recomendação:** Prosseguir com o tratamento dos dados financeiros, **condicionado** à implementação das medidas de mitigação da Fase 1 (consentimento) e Fase 2 (exclusão, portabilidade, notificação de incidentes) no prazo máximo de 45 dias.

A continuidade da operação sem os mecanismos de consentimento e resposta a incidentes representa exposição regulatória relevante perante a ANPD, ainda que a base legal principal (execução de contrato) independa de consentimento.

### 7.3 Encaminhamentos

| Ação | Responsável | Prazo | Referência |
|------|------------|-------|-----------|
| Revisão desta DPIA pelo DPO | DPO (`edd37e14-9370-49a8-90c7-ab819b528891`) | 7 dias | Este documento |
| Implementar consentimento (Fase 1) | CTO | 15 dias | [IND-51](/IND/issues/IND-51) |
| Implementar exclusão e portabilidade (Fase 2) | CTO | 45 dias | [IND-51](/IND/issues/IND-51) |
| Implementar procedimento de notificação de incidentes (Fase 2) | CTO + DPO | 45 dias | M5 desta DPIA |
| Implementar criptografia em nível de aplicação (Fase 3) | CTO | 90 dias | M9 desta DPIA |
| Implementar audit log de banco de dados (Fase 3) | CTO | 90 dias | M10 desta DPIA |
| Publicação final da DPIA após revisão do DPO | DPO | Após revisão | — |

### 7.4 Aprovações

| Papel | Nome / Agente | Data | Assinatura |
|-------|--------------|------|-----------|
| Condução técnica | CTO (`1382266e-0ebc-4691-b38d-9bd0790d1a10`) | 11/06/2026 | Realizada |
| Revisão DPO | DPO (`edd37e14-9370-49a8-90c7-ab819b528891`) | 11/06/2026 | **Aprovada com recomendações** (ver parecer DPO abaixo) |
| Aprovação do controlador | LealCyber (CEO) | (pendente) | Aprovação do controlador via [IND-71](/IND/issues/IND-71) |

---

## Anexo A — Base Legal e Normativa

- **LGPD (Lei nº 13.709/2018):** Art. 5º, Art. 6º, Art. 7º, Art. 8º, Art. 16, Art. 18, Art. 38
- **Resolução CD/ANPD nº 2/2022:** Regulamento de aplicação da LGPD para agentes de tratamento de pequeno porte, incluindo modelo de DPIA simplificado
- **Guia Orientativo de Segurança da Informação da ANPD** (2023)
- **ADR-004:** Imutabilidade de conversões — `decisions/004-conversion-immutability.md`
- **ADR-007:** Token de resgate com OTP — `decisions/007-redemption-otp-token.md`

## Anexo B — Documentos Relacionados

| Documento | Localização |
|-----------|------------|
| Política de Privacidade | `privacidade/politica-de-privacidade.md` |
| Relatório de Conformidade LGPD | `privacidade/analise-conformidade.md` |
| Arquitetura de Referência | `architecture.md` |
| Matriz RBAC | `behavior/rbac.md` |
| Inventário de Tratamento | `privacidade/politica-de-privacidade.md#13-anexo-técnico--inventário-de-tratamento` |

---

## 8. Parecer do Encarregado (DPO)

### 8.1 Avaliação geral

A DPIA conduzida pelo CTO atende aos requisitos do Art. 38 da LGPD e da Resolução CD/ANPD nº 2/2022. O documento mapeia adequadamente os fluxos financeiros (conversão e resgate), identifica 10 riscos com matriz de probabilidade × impacto, e inventaria 17 medidas de mitigação existentes e 11 planejadas.

**Classificação de risco residual após implementação das Fases 1-3:** Baixo.

### 8.2 Pontos fortes

- **Minimização de dados demonstrada:** O IndiQR não coleta dados bancários, CPF, geolocalização ou dados do cliente final. A coleta limita-se aos identificadores estritamente necessários à operação financeira (Art. 6º, III — necessidade).
- **Finalidade documentada por dado:** Cada campo possui finalidade única e documentada, sem reutilização para fins secundários (Art. 6º, I — finalidade).
- **Base legal correta:** Execução de contrato (Art. 7º, II) é a base legal primária adequada para todas as operações financeiras mapeadas.
- **Imutabilidade justificada:** Registros financeiros imutáveis (ADR-004, ADR-007) estão amparados pelo Art. 16 da LGPD (obrigação legal de guarda de registros financeiros/contábeis).
- **Controles técnicos robustos:** RBAC com 3 roles, JWT RS256, sanitização de logs, OTP para resgates, rate limiting e CORS restrito formam uma defesa em profundidade adequada.

### 8.3 Achados e recomendações

#### A1 — CNPJ e endereço do controlador (Seção 1.1)

**Achado:** Campos obrigatórios de identificação do controlador não preenchidos.

**Recomendação:** CEO deve fornecer CNPJ e endereço da LealCyber para preenchimento. Criado follow-up [IND-71](/IND/issues/IND-71).

**Risco residual:** Baixo. Não afeta a validade técnica da DPIA. Deve ser preenchido antes de eventual apresentação à ANPD.

#### A2 — Transferência internacional e Art. 33 (R5)

**Achado:** O risco R5 identifica que dados financeiros no Neon podem residir fora do Brasil, mas a análise de conformidade com o Art. 33 da LGPD é insuficiente. A transferência para EUA (Neon, Auth0, Resend, Grafana Cloud) requer salvaguardas adequadas.

**Recomendação:**
1. Selecionar região AWS `sa-east-1` (São Paulo) para o Neon sempre que disponível
2. Firmar cláusulas-padrão contratuais (SCCs) com suboperadores localizados fora do Brasil
3. Documentar as garantias de cada suboperador no inventário de tratamento (`privacidade/politica-de-privacidade.md#13`)

**Risco residual:** Médio até que SCCs sejam firmados e a região seja configurada.

#### A3 — Base legal de `created_at` (Seção 4.1)

**Achado:** O campo `created_at` está classificado sob Art. 7º, VI (legítimo interesse). A classificação mais adequada é Art. 7º, II (execução de contrato), pois a auditoria temporal é inerente à operação financeira contratada.

**Recomendação:** Reclassificar `created_at` para Art. 7º, II. Não há necessidade de invocar legítimo interesse quando a execução contratual cobre a finalidade.

**Risco residual:** Nulo. Correção meramente classificatória.

#### A4 — Prazo de retenção dos registros financeiros (Seção 4.2)

**Achado:** A DPIA afirma que registros financeiros são mantidos indefinidamente por obrigação de auditoria, amparados pelo Art. 16. A LGPD exige que o prazo seja definido e justificado, não "indefinido".

**Recomendação:** Definir prazo explícito alinhado com obrigações legais:
- Registros contábeis/financeiros: 5 anos (Art. 174 do CTN; Art. 1.194 do CC)
- Após o prazo legal: anonimizar (hash do identificador) ou eliminar
- Incluir na política de privacidade o prazo de retenção por categoria

**Risco residual:** Baixo após definição explícita do prazo.

#### A5 — Ciclo de revisão da DPIA

**Achado:** Não há previsão de periodicidade de revisão da DPIA. A Resolução CD/ANPD nº 2/2022 e boas práticas recomendam revisão periódica e após mudanças materiais no tratamento.

**Recomendação:** Incluir na Seção 7 o ciclo de revisão:
- Revisão ordinária: anual
- Revisão extraordinária: após mudança de suboperador, novo fluxo financeiro, ou incidente de segurança envolvendo dados financeiros

**Risco residual:** Baixo. Requer apenas inclusão de procedimento administrativo.

#### A6 — Priorização de medidas críticas

**Achado:** As medidas M1 (consentimento), M4 (canal de solicitações de titulares) e M5 (notificação de incidentes) estão planejadas para Fases 1-2 (até 45 dias), mas são as de maior impacto regulatório. O atraso em qualquer delas mantém exposição relevante.

**Recomendação:** Reforçar o parecer técnico da Seção 7.2: a continuidade da operação **sem** M5 (notificação de incidentes) é o risco regulatório mais grave desta DPIA. Recomenda-se implementar M5 como prioridade máxima, antes mesmo de M2 e M3.

**Risco residual:** Alto até que M5 esteja operacional. Nota: a LGPD Art. 48 exige notificação em "prazo razoável" — a inexistência de procedimento é uma não-conformidade direta.

### 8.4 Decisão do DPO

**Parecer:** APROVADO COM RECOMENDAÇÕES.

A DPIA está tecnicamente adequada e atende aos requisitos do Art. 38 da LGPD e da Resolução CD/ANPD nº 2/2022. As recomendações A1-A6 devem ser endereçadas conforme os prazos indicados, mas nenhuma delas invalida a DPIA ou impede a continuidade do tratamento.

**Condições para publicação final:**
1. Preencher CNPJ e endereço do controlador (A1)
2. Incluir ciclo de revisão da DPIA (A5)

**Ações imediatas (sem as quais a exposição regulatória é relevante):**
1. Implementar M5 (procedimento de notificação de incidentes) — Prazo: 45 dias (Art. 48 LGPD)
2. Firmar SCCs com suboperadores internacionais — Prazo: 60 dias (Art. 33 LGPD)

---

**Próxima ação:** Preenchimento de CNPJ e endereço pelo CEO ([IND-71](/IND/issues/IND-71)). Publicação final após completar A1 e A5.
