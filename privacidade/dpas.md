# Registro de Data Processing Agreements (DPAs) — IndiQR

**Data:** 11 de junho de 2026
**Responsável:** DPO (Encarregado de Proteção de Dados)
**Referência LGPD:** Arts. 26 (operador), 33 (transferência internacional), 35 (cláusulas-padrão)
**Issue:** [IND-65](/IND/issues/IND-65)
**Issue pai:** [IND-62](/IND/issues/IND-62)

---

## 1. Declaração de Incorporação

A **LealCyber** (operadora da plataforma IndiQR), na qualidade de **controladora** dos dados de seus próprios usuários e **operadora** dos dados processados em nome das empresas-clientes, firma o presente registro para documentar os Data Processing Agreements (DPAs) vigentes com cada suboperador da plataforma.

Cada DPA listado abaixo foi incorporado por referência mediante aceitação dos termos de serviço do respectivo suboperador (mecanismo "clickwrap" ou "browsewrap"), conforme prática padrão de mercado para serviços SaaS/PaaS/IaaS. Os DPAs são juridicamente vinculantes entre a LealCyber e cada suboperador, contendo cláusulas-padrão contratuais (SCCs) e/ou certificações de Data Privacy Framework (DPF) como salvaguardas para transferência internacional de dados pessoais, em conformidade com:

- **LGPD Art. 33** — transferência internacional com garantias de proteção adequada
- **LGPD Art. 35** — cláusulas-padrão contratuais como mecanismo válido
- **LGPD Art. 26** — obrigações do operador e suboperadores

---

## 2. Registro de DPAs por Suboperador

### 2.1 Auth0 (Okta, Inc.)

| Campo | Valor |
|-------|-------|
| **Fornecedor** | Okta, Inc. (Auth0 é produto da Okta) |
| **Serviço** | Autenticação como serviço (Identity-as-a-Service) |
| **URL do DPA** | `https://www.okta.com/content/dam/okta---digital/en_us/legal/data-processing-addendum-2026-01.pdf` |
| **Página de confiança** | `https://www.okta.com/legal/trustandcompliance/` |
| **Versão referenciada** | Janeiro 2026 |
| **Mecanismo de aceite** | Aceitação dos termos de serviço Auth0/Okta + incorporação por referência |
| **SCCs incluídas?** | Sim — EU SCCs (Controller-to-Processor e Processor-to-Processor) incorporadas ao DPA |
| **DPF aplicável?** | Sim — Okta, Inc. é participante ativo do EU-US Data Privacy Framework, UK Extension e Swiss-US DPF |
| **Certificações** | SOC 2 Type II, ISO 27001, ISO 27017, ISO 27018, GDPR compliant, Global PRP |
| **Status** | **Vigente** — Aceito mediante utilização do serviço Auth0 |

### 2.2 Resend (Plus Five Five, Inc.)

| Campo | Valor |
|-------|-------|
| **Fornecedor** | Plus Five Five, Inc. (Resend) |
| **Serviço** | Envio de emails transacionais (API de email) |
| **URL do DPA** | `https://resend.com/legal/dpa` |
| **Versão referenciada** | 31 de dezembro de 2025 |
| **Mecanismo de aceite** | Aceitação dos Terms of Service do Resend + DPA incorporado por referência |
| **SCCs incluídas?** | Sim — EU SCCs (Modules 1, 2 e 3), UK SCCs (via UK Addendum) |
| **DPF aplicável?** | Sim — Resend é certificado no EU-US DPF e UK Extension ao EU-US DPF |
| **Certificações** | SOC 2 Type II, GDPR compliant, EU-US DPF, UK Extension DPF |
| **Status** | **Vigente** — Aceito mediante utilização do serviço Resend |

### 2.3 Neon (Neon, LLC, afiliada da Databricks, Inc.)

| Campo | Valor |
|-------|-------|
| **Fornecedor** | Neon, LLC (afiliada da Databricks, Inc.) |
| **Serviço** | Banco de dados PostgreSQL serverless |
| **URL do DPA** | `https://www.databricks.com/sites/default/files/legal/dpa-20230721.pdf` (DPA da Databricks, aplicável ao Neon via Product Specific Schedule) |
| **Página de termos** | `https://neon.com/platform-terms` |
| **Versão referenciada** | 21 de julho de 2023 (DPA Databricks) |
| **Mecanismo de aceite** | Aceitação dos termos do Neon Platform Services Product Specific Schedule + Databricks MCSA |
| **SCCs incluídas?** | Sim — EU SCCs incorporadas ao DPA da Databricks |
| **DPF aplicável?** | Databricks, Inc. é participante do EU-US DPF |
| **Certificações** | SOC 2 Type II, ISO 27001, ISO 27701, GDPR compliant, HIPAA compliant |
| **Status** | **Vigente** — Aceito mediante utilização do serviço Neon |
| **Observação** | Residência de dados: recomenda-se configurar região `sa-east-1` (São Paulo) para que dados permaneçam em território brasileiro, eliminando necessidade de mecanismo de transferência |

### 2.4 Cloudflare R2 (Cloudflare, Inc.)

| Campo | Valor |
|-------|-------|
| **Fornecedor** | Cloudflare, Inc. |
| **Serviço** | Armazenamento de objetos (R2) para mídia da vitrine e deploy de site estático |
| **URL do DPA** | `https://www.cloudflare.com/cloudflare-customer-dpa/` |
| **Versão referenciada** | Versão 6.4, efetiva em 3 de abril de 2026 |
| **Mecanismo de aceite** | Aceitação do Cloudflare Self-Serve Subscription Agreement + DPA incorporado |
| **SCCs incluídas?** | Sim — EU SCCs (Modules 2 e 3), UK Addendum, Swiss FADP |
| **DPF aplicável?** | Sim — Cloudflare, Inc. é participante ativo do EU-US DPF, UK Extension e Swiss-US DPF |
| **Outros mecanismos** | Global Cross-Border Privacy Rules (CBPR) System e Global Privacy Recognition for Processors (PRP) System |
| **Certificações** | SOC 2 Type II, ISO 27001, ISO 27701, GDPR compliant, EU-US DPF, UK Extension DPF, Swiss-US DPF, Global PRP certified |
| **Status** | **Vigente** — Aceito mediante utilização do serviço Cloudflare R2 |

### 2.5 Grafana Cloud (Grafana Labs)

| Campo | Valor |
|-------|-------|
| **Fornecedor** | Grafana Labs |
| **Serviço** | Observabilidade — coleta de logs, métricas e traces (OpenTelemetry) |
| **URL do DPA** | `https://grafana.com/legal/dpa/` |
| **Mecanismo de aceite** | Aceitação dos termos de serviço Grafana Cloud + DPA incorporado por referência |
| **SCCs incluídas?** | Sim — EU SCCs conforme inventário de suboperadores |
| **DPF aplicável?** | Verificar status de certificação DPF do Grafana Labs |
| **Certificações** | SOC 2 Type II, GDPR compliant |
| **Status** | **Vigente** — Aceito mediante utilização do serviço Grafana Cloud |
| **Observação** | A página do DPA do Grafana requer verificação de acessibilidade. Em caso de indisponibilidade, solicitar cópia diretamente ao fornecedor via `privacy@grafana.com`. |

### 2.6 Akeyless (Akeyless Security)

| Campo | Valor |
|-------|-------|
| **Fornecedor** | Akeyless Security |
| **Serviço** | Gerenciamento de segredos (secrets management) |
| **URL do DPA** | Não aplicável — Akeyless **não processa dados pessoais de usuários** |
| **Mecanismo de aceite** | Aceitação dos termos de serviço Akeyless |
| **SCCs incluídas?** | Não aplicável — sem transferência de dados pessoais |
| **DPF aplicável?** | Não aplicável |
| **Certificações** | SOC 2 Type II, ISO 27001, FIPS 140-2 |
| **Status** | **Não aplicável** — Suboperador de infraestrutura que não processa PII |

---

## 3. Resumo de Salvaguardas de Transferência Internacional

| Suboperador | País sede | Mecanismo Primário | Mecanismo Secundário | Status LGPD |
|-------------|-----------|-------------------|---------------------|-------------|
| Auth0 (Okta) | EUA | EU-US DPF | EU SCCs (DPA Okta) | Art. 33, II, "a" e "b" — garantias adequadas |
| Resend | EUA | EU-US DPF | EU SCCs (DPA Resend) | Art. 33, II, "a" e "b" — garantias adequadas |
| Neon | EUA (configurável) | Residência de dados (`sa-east-1`) | EU SCCs (DPA Databricks) | Art. 33, II, "b" — ou sem transferência se sa-east-1 |
| Cloudflare R2 | EUA (global) | EU-US DPF | EU SCCs (DPA Cloudflare) + Global PRP | Art. 33, II, "a" e "b" — garantias adequadas |
| Grafana Cloud | EUA | EU SCCs (DPA Grafana Labs) | — | Art. 33, II, "b" — garantias adequadas |
| Akeyless | Israel/EUA | N/A (não processa PII) | N/A | Não aplicável |

### Legenda de bases legais LGPD Art. 33:
- **II, "a"**: Transferência para país com nível de proteção adequado reconhecido (via DPF)
- **II, "b"**: Cláusulas-padrão contratuais (SCCs) como garantia de conformidade

---

## 4. Armazenamento e Auditoria

### 4.1 Localização das cópias

- **Repositório de especificação:** `privacidade/dpas.md` (este documento) — contém o registro e referências
- **DPAs completos dos fornecedores:** Disponíveis nos URLs listados na Seção 2. As versões correntes podem ser verificadas a qualquer momento nos respectivos sites.
- **Recomendação de arquivamento:** Baixar e armazenar cópias PDF datadas de cada DPA em diretório seguro com acesso restrito (ex: Google Drive corporativo com permissionamento apenas para CEO e DPO) para auditoria. Este diretório deve conter:
  - Cópia do DPA em PDF
  - Data de download/arquivamento
  - Hash SHA-256 para verificação de integridade

### 4.2 Periodicidade de revisão

- **Revisão anual** de todos os DPAs para verificar atualizações nos termos dos fornecedores
- **Revisão imediata** se houver alteração material nos serviços, na estrutura societária do fornecedor, ou no status de certificações (DPF, ISO, SOC 2)
- **Monitoramento de subprocessadores:** Cada DPA prevê notificação prévia de novos subprocessadores (30 dias Cloudflare, 14 dias Resend)

---

## 5. Próximos Passos

1. [ ] CEO: Assinar executivamente os DPAs via DocuSign onde disponível (ex: Okta oferece versão executável em `https://powerforms.docusign.net/a18dd438-f9f3-4fd9-916e-584816fceba9`)
2. [ ] CEO + DPO: Arquivar cópias PDF dos DPAs em repositório seguro corporativo para trilha de auditoria
3. [ ] DPO: Verificar acessibilidade do DPA do Grafana Labs e solicitar cópia diretamente se necessário
4. [ ] CTO: Configurar região Neon para `sa-east-1` (São Paulo) — ver [IND-73](/IND/issues/IND-73)
5. [x] DPO: Disponibilizar template de DPA controlador-operador para empresas-clientes

---

**Versão do documento:** `privacidade/dpas.md`
**Repositório:** [indiqr-spec](https://github.com/lealcristopher/indiqr-spec)
**Referência:** [IND-65](/IND/issues/IND-65)
