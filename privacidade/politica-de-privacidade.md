# Política de Privacidade — IndiQR

**Última atualização:** 11 de junho de 2026

---

## 1. Introdução

O **IndiQR** é uma plataforma SaaS de marketing por indicação com remuneração por conversão, operada por **LealCyber** ("nós", "nosso" ou "IndiQR"). Esta Política de Privacidade descreve como coletamos, usamos, armazenamos e protegemos os dados pessoais dos usuários da plataforma, em conformidade com a **Lei Geral de Proteção de Dados Pessoais (LGPD — Lei nº 13.709/2018)**.

Ao utilizar a plataforma IndiQR, você declara estar ciente e concordar com os termos desta Política de Privacidade.

---

## 2. Dados Pessoais Coletados

### 2.1 Dados fornecidos pelo titular

| Categoria | Dados | Momento da coleta |
|-----------|-------|-------------------|
| Identificação | `email` | Criação de conta via Auth0 |
| Identificação | `auth_id` (identificador Auth0) | Autenticação via Auth0 |
| Empresa | `name` (nome), `slug` | Criação de empresa |
| Campanha | `name` (nome), parâmetros financeiros | Criação de campanha |
| Convite | `email` do convidado, `role` | Convite de membro ou campanha |
| Vitrine (Shop) | `handle`, `name`, `tagline`, `instagram_url`, `whatsapp_url`, `email` | Configuração da vitrine |
| Mídia | Imagens (logo, hero, produtos, galeria) | Upload na vitrine |
| Conversão | `valor_bruto` da compra | Registro de conversão |
| Resgate | `valor`, `tipo` (reais/pontos), `code` (OTP de 6 dígitos) | Solicitação e validação de resgate |

### 2.2 Dados coletados automaticamente

| Categoria | Dados | Finalidade |
|-----------|-------|------------|
| Logs de acesso | `client_ip`, `method`, `path`, `status_code`, `request_id` | Monitoramento e segurança da plataforma |
| Telemetria | `trace_id`, `span_id` (OpenTelemetry) | Observabilidade e diagnóstico de erros |

### 2.3 Dados de terceiros

Recebemos do **Auth0** (provedor de autenticação) o `email` e `auth_id` do usuário autenticado. O Auth0 é responsável pelo tratamento dos dados de login e senha — o IndiQR **não armazena senhas**.

---

## 3. Finalidades do Tratamento

Tratamos os dados pessoais para as seguintes finalidades:

| Finalidade | Dados utilizados | Base legal (LGPD) |
|------------|-----------------|-------------------|
| Autenticação e controle de acesso | `email`, `auth_id`, roles | Art. 7º, II — Execução de contrato |
| Criação e gestão de empresas | `name`, `slug` | Art. 7º, II — Execução de contrato |
| Gestão de campanhas e convites | `email` do influenciador, parâmetros da campanha | Art. 7º, II — Execução de contrato |
| Envio de emails transacionais | `email` do destinatário, nome da empresa/campanha | Art. 7º, II — Execução de contrato |
| Rastreamento de conversões | `valor_bruto`, IDs de campanha/influenciador/vendedor | Art. 7º, II — Execução de contrato |
| Gestão de carteira e resgates | `saldo_reais`, `saldo_pontos`, códigos OTP | Art. 7º, II — Execução de contrato |
| Vitrine virtual (Shop) | Dados da vitrine, imagens, URLs públicas | Art. 7º, II — Execução de contrato / Art. 7º, I — Consentimento (para exposição pública) |
| Monitoramento e segurança | Logs de acesso, IP, traces | Art. 7º, VI — Legítimo interesse |
| Diagnóstico de erros | Telemetria (traces, logs) | Art. 7º, VI — Legítimo interesse |

### 3.1 Consentimento específico — Vitrine pública

Ao configurar uma vitrine virtual (Shop) e publicá-la via `POST /shop/{handle}/deploy`, o administrador da empresa consente expressamente com a **exposição pública** dos seguintes dados no site estático gerado:

- Nome da empresa, tagline
- URLs de Instagram e WhatsApp
- Email de contato da vitrine
- Nomes, descrições e preços (em pontos) dos produtos
- Imagens de logo, hero, categorias e produtos

Estes dados ficam acessíveis publicamente em `{SHOP_BASE_URL}/{handle}/` e indexáveis por mecanismos de busca.

---

## 4. Compartilhamento de Dados com Terceiros

### 4.1 Suboperadores (data processors)

| Terceiro | Dados compartilhados | Finalidade | Localização | DPA |
|----------|---------------------|------------|-------------|-----|
| **Auth0** (Okta, Inc.) | `email`, `auth_id`, roles | Autenticação e autorização | EUA / Global | [DPA Okta](https://www.okta.com/agreements/data-processing-addendum/) |
| **Resend** (Resend, Inc.) | `email` do destinatário, conteúdo do email | Envio de emails transacionais | EUA | [DPA Resend](https://resend.com/legal/dpa) |
| **Cloudflare R2** (Cloudflare, Inc.) | Imagens da vitrine, dados públicos do site estático | Armazenamento de mídia e entrega de conteúdo | Global (CDN) | [DPA Cloudflare](https://www.cloudflare.com/cloudflare-customer-dpa/) |
| **Grafana Cloud** (Grafana Labs) | Logs de aplicação (path, client_ip, status_code) e traces OTel | Observabilidade e diagnóstico | EUA / Global | [DPA Grafana](https://grafana.com/legal/dpa/) |
| **Neon** (Neon, Inc.) — produção | Todos os dados da plataforma | Banco de dados PostgreSQL serverless | Definido pelo cliente (região AWS) | [DPA Neon](https://neon.tech/legal/dpa) |
| **Akeyless** (Akeyless Security) | Nenhum dado de usuário — credenciais de infraestrutura apenas | Gerenciamento de segredos | Definido pelo cliente | N/A (não processa PII) |

O registro completo de DPAs, incluindo mecanismos de transferência, certificações e status de vigência, está disponível no [Registro de DPAs](https://github.com/lealcristopher/indiqr-spec/blob/main/privacidade/dpas/README.md). Consulte tambem o [Inventario de Suboperadores](https://github.com/lealcristopher/indiqr-spec/blob/main/privacidade/suboperadores.md) para detalhamento tecnico dos fluxos de dados.

### 4.2 Transferência internacional

Alguns suboperadores estão sediados nos Estados Unidos ou operam infraestrutura global. Para assegurar nível adequado de proteção aos dados pessoais transferidos para fora do Brasil, o IndiQR adota os seguintes mecanismos de salvaguarda, em conformidade com o Art. 33 da LGPD:

#### 4.2.1 Mecanismos de transferência vigentes

| Mecanismo | Descrição | Base LGPD | Suboperadores cobertos |
|-----------|-----------|-----------|----------------------|
| **EU Standard Contractual Clauses (EU SCCs)** | Cláusulas-padrão contratuais aprovadas pela Comissão Europeia (Decisão 2021/914), incorporadas aos DPAs de cada suboperador | Art. 33, II, "b" | Auth0, Resend, Cloudflare R2, Grafana Cloud, Neon |
| **EU-US Data Privacy Framework (DPF)** | Certificação de proteção adequada sob o DPF, reconhecido pelo U.S. Department of Commerce | Art. 33, II, "a" | Auth0 (Okta), Cloudflare R2 |
| **Residência de dados no Brasil** | Dados armazenados em território nacional (Neon região `sa-east-1`, São Paulo), sem transferência internacional | Art. 33, caput — não há transferência | Neon (recomendação) |

#### 4.2.2 Situação por suboperador

| Suboperador | País sede | Mecanismo primário | Mecanismo secundário |
|-------------|-----------|-------------------|---------------------|
| Auth0 (Okta) | EUA | EU-US DPF | EU SCCs |
| Resend | EUA | EU SCCs | DPF (em verificação) |
| Cloudflare R2 | EUA | EU-US DPF | EU SCCs + Global PRP |
| Grafana Cloud | EUA | EU SCCs | — |
| Neon | EUA (configurável) | Residência de dados (`sa-east-1`) | EU SCCs |
| Akeyless | Israel/EUA | N/A — não processa dados pessoais | — |

#### 4.2.3 Compromissos adicionais

- **Notificação de mudanças:** Os DPAs com cada suboperador preveem notificação prévia em caso de adição ou substituição de subprocessadores (14 a 30 dias de antecedência)
- **Revisão periódica:** Os DPAs e certificações DPF são revisados anualmente ou sempre que houver alteração material nos serviços ou na estrutura societária do fornecedor
- **Due diligence:** Todos os suboperadores são avaliados quanto a certificações de segurança (SOC 2, ISO 27001) e conformidade com GDPR/LGPD antes da contratação
- **Cláusulas-padrão da ANPD:** Tão logo a ANPD publique as cláusulas-padrão brasileiras previstas no Art. 35 da LGPD, o IndiQR avaliará a adoção complementar dessas cláusulas, sem prejuízo dos mecanismos já vigentes

### 4.3 Compartilhamento legal

Podemos compartilhar dados pessoais quando exigido por lei, ordem judicial ou autoridade administrativa competente.

---

## 5. Armazenamento e Retenção

### 5.1 Local de armazenamento

- **Produção:** Banco de dados PostgreSQL serverless (Neon), arquivos em Cloudflare R2
- **Staging:** `docker-compose` com PostgreSQL local e S3 mock (`moto`)
- **Desenvolvimento:** PostgreSQL local ou SQLite em memória

### 5.2 Período de retenção

| Categoria de dados | Período de retenção |
|--------------------|---------------------|
| Dados de usuário (`usuarios`) | Enquanto a conta estiver ativa + até 30 dias após solicitação de exclusão |
| Dados de empresa e campanhas | Enquanto a empresa estiver ativa na plataforma |
| Conversões | **Indefinidamente** — registros imutáveis por design (ADR-004) para fins de auditoria financeira |
| Resgates | **Indefinidamente** — registros imutáveis para fins de auditoria financeira |
| Tokens de resgate (OTP) | Permanente com status (`usado`/`expirado`) para trilha de auditoria |
| Logs de acesso | 90 dias (Grafana Cloud Loki), rotacionados conforme configuração do tenant |
| Imagens da vitrine | Até exclusão pelo administrador ou encerramento da empresa |
| Convites pendentes | Até aceitação, expiração manual ou exclusão da empresa |

### 5.3 Imutabilidade de registros financeiros

**Conversões** e **Resgates** são imutáveis após confirmação, por decisão de arquitetura (ADR-004, ADR-007). Eles não possuem campo `updated_at` e não podem ser alterados ou excluídos pela interface — apenas cancelados via novo registro de estorno (pós-MVP). Esta decisão garante a integridade da auditoria financeira da plataforma.

---

## 6. Direitos do Titular (LGPD)

Todo titular de dados pessoais tem os seguintes direitos, conforme Art. 18 da LGPD:

| Direito | Descrição | Como exercer |
|---------|-----------|--------------|
| Confirmação | Saber se tratamos seus dados | Solicitação via email |
| Acesso | Obter cópia dos dados tratados | Solicitação via email |
| Correção | Solicitar correção de dados incompletos ou inexatos | PATCH via API ou solicitação via email |
| Anonimização, bloqueio ou eliminação | Quando dados forem desnecessários ou tratados em desconformidade | Solicitação via email |
| Portabilidade | Transferir dados a outro fornecedor | Solicitação via email |
| Eliminação | Excluir dados tratados com consentimento | Solicitação via email |
| Informação sobre compartilhamento | Saber com quais terceiros compartilhamos seus dados | Consultar esta Política |
| Revogação de consentimento | Retirar consentimento anteriormente dado | Solicitação via email |
| Revisão automatizada | Solicitar revisão de decisões automatizadas | Solicitação via email |

**Canal de exercício de direitos:** `privacidade@indiqr.lealcyber.com`

Prazo de resposta: até 15 dias úteis, conforme Art. 19 da LGPD.

**Exceções à exclusão:** Registros de conversões e resgates são imutáveis por razões de auditoria financeira e obrigação legal (Art. 16 da LGPD). Nesses casos, oferecemos anonimização (remoção do vínculo com o `influenciador_id` e `vendedor_id` identificáveis) quando o titular não for parte direta do registro financeiro.

---

## 7. Segurança da Informação

Adotamos as seguintes medidas técnicas para proteger os dados pessoais:

| Medida | Implementação |
|--------|---------------|
| Criptografia em trânsito | TLS 1.2+ em todas as conexões (Auth0, Resend, R2, Neon, Grafana Cloud) |
| Criptografia em repouso | PostgreSQL via Neon (server-side encryption), R2 (encryption at rest) |
| Autenticação JWT | Tokens RS256 com validação de `aud` (audience) e `iss` (issuer) |
| Controle de acesso (RBAC) | Três roles isolados: `indiqr-admin`, `indiqr-influenciador`, `indiqr-vendedor` |
| IDOR protection | Todos os endpoints verificam pertencimento à empresa antes de retornar dados |
| Soft-delete | Exclusões lógicas em `campaigns.deleted_at`, `shop_product_images` (não remove do storage) |
| Sanitização de logs | Códigos OTP são mascarados nos logs — nunca registrados em texto plano |
| Rate limiting | Proteção contra brute-force nos endpoints de validação de OTP e QRCode |
| Segredos | Gerenciados via Akeyless em produção, nunca em código-fonte |
| Gitleaks + Trivy | Varredura de segredos e vulnerabilidades no pipeline CI/CD |
| Ruff + Bandit | Análise estática de código no pipeline CI/CD |
| Schemathesis | Testes de contrato que validam a API contra a especificação OpenAPI |

### 7.1 Boas práticas de desenvolvimento

- Verificação de **enumeração**: endpoints não revelam se um recurso existe quando o usuário não tem acesso (retornam 403 ou lista vazia, não 404)
- **Sanitização de erro**: respostas de erro nunca incluem stack traces, nomes de tabela, ou tokens sensíveis
- **Validação de entrada**: todos os inputs passam por validação Pydantic; slugs restritos ao pattern `^[a-z0-9-]+$`
- **CORS restrito**: apenas origens autorizadas (`indiqr.lealcyber.com`, `app.indiqr.com.br`, `flyer.indiqr.com.br`, `indiqr-app.web.app`)

---

## 8. Cookies e Tecnologias Similares

### 8.1 Autenticação

A plataforma utiliza **JWT (JSON Web Token)** armazenado em memória pelo Auth0 React SDK para autenticação. **Não utilizamos cookies de rastreamento, publicidade ou analytics de terceiros.**

### 8.2 PWA (Vendedor)

O aplicativo do vendedor é uma **Progressive Web App (PWA)** que utiliza:

- **Service Worker** com estratégia `networkFirst` para cache de API (offline-first)
- **Manifesto** para instalação no dispositivo com `display: standalone`

Nenhum dado pessoal é armazenado persistentemente no dispositivo além do cache HTTP da aplicação.

---

## 9. Crianças e Adolescentes

A plataforma IndiQR não é direcionada a menores de 18 anos. Não coletamos intencionalmente dados de crianças ou adolescentes. Caso identifiquemos tal coleta, os dados serão removidos imediatamente.

---

## 10. Encarregado de Dados (DPO)

O encarregado pelo tratamento de dados pessoais do IndiQR pode ser contatado em:

- **Email:** `privacidade@indiqr.lealcyber.com`
- **Titular:** Encarregado de Proteção de Dados — IndiQR / LealCyber

---

## 11. Alterações nesta Política

Esta Política de Privacidade pode ser atualizada periodicamente. A data da última atualização estará sempre indicada no topo do documento. Alterações significativas serão comunicadas por email aos usuários ativos da plataforma com antecedência mínima de 15 dias.

---

## 12. Legislação Aplicável

Esta Política de Privacidade é regida pela **Lei Geral de Proteção de Dados Pessoais (LGPD — Lei nº 13.709/2018)** e demais normas do ordenamento jurídico brasileiro. Conflitos serão dirimidos no foro da comarca de residência do titular.

---

## 13. Anexo Técnico — Inventário de Tratamento

### 13.1 Tabelas com dados pessoais

| Tabela | Campos com dado pessoal | Natureza |
|--------|------------------------|----------|
| `usuarios` | `email`, `auth_id` | Identificação direta |
| `company_members` | `usuario_id`, `role` | Vínculo profissional |
| `invitations` | `email`, `role` | Dado de contato |
| `membership_requests` | `requester_id` | Vínculo de solicitação |
| `campaigns` | `influenciador_id` | Vínculo profissional |
| `conversions` | `influenciador_id`, `vendedor_id` | Rastreabilidade financeira |
| `carteiras` | `influenciador_id` | Saldo financeiro |
| `resgate_tokens` | `influenciador_id`, `code` (OTP) | Operação de resgate |
| `resgates` | `influenciador_id`, `vendedor_id` | Rastreabilidade financeira |
| `shops` | `email`, `instagram_url`, `whatsapp_url` | Dados públicos da vitrine |

### 13.2 Fluxos de dados entre sistemas

```
Usuário → Auth0 (login/senha) → JWT → IndiQR API
IndiQR API → Auth0 Management API (atribuição/revogação de roles)
IndiQR API → Resend (envio de emails transacionais)
IndiQR API → Cloudflare R2 (upload de mídia e deploy de site estático)
IndiQR API → Grafana Cloud OTLP (logs e traces)
IndiQR API → Neon PostgreSQL (todos os dados operacionais)
```

---

**Versão do documento:** `privacidade/politica-de-privacidade.md`
**Repositório:** [indiqr-spec](https://github.com/lealcristopher/indiqr-spec)
**Revisão aprovada por:** [IND-46](/IND/issues/IND-46)
