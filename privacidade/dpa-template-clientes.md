# Template de Data Processing Agreement (DPA) — Clientes IndiQR

**Modelo:** Controlador-Operador
**Referencia LGPD:** Arts. 26, 33, 35, 37, 38, 39
**Issue:** [IND-64](/IND/issues/IND-64)
**Versao:** 1.0 — 11 de junho de 2026

---

## Preambulo

Este **Acordo de Tratamento de Dados Pessoais** ("DPA") e celebrado entre:

- **CONTROLADOR:** Empresa cliente contratante dos servicos IndiQR ("Cliente"), qualificada no contrato de prestacao de servicos principal;
- **OPERADOR:** **LealCyber Tecnologia Ltda.**, inscrita no CNPJ sob o nº [CNPJ], com sede em [endereco], operadora da plataforma **IndiQR** ("IndiQR" ou "Operador").

Em complemento ao contrato de prestacao de servicos principal ("Contrato Principal"), este DPA regula o tratamento de dados pessoais realizado pelo Operador em nome do Controlador, em conformidade com a **Lei Geral de Protecao de Dados Pessoais (LGPD — Lei nº 13.709/2018)**.

---

## 1. Definicoes

1.1 Os termos "dado pessoal", "dado pessoal sensivel", "titular", "controlador", "operador", "tratamento", "suboperador", "DPIA" e "ANPD" tem os significados definidos no Art. 5º da LGPD.

1.2 "Servicos" refere-se a plataforma SaaS IndiQR de marketing por indicacao com remuneracao por conversao.

1.3 "Dados do Cliente" refere-se aos dados pessoais de titulares inseridos, carregados ou de outra forma fornecidos pelo Cliente a plataforma IndiQR.

---

## 2. Papeis das Partes (LGPD Art. 37, 38, 39)

2.1 **Controlador (Cliente):** O Cliente e o controlador dos Dados do Cliente. Cabe ao Cliente:
   - Definir as finalidades do tratamento (Art. 38)
   - Obter as bases legais adequadas para o tratamento (Art. 7º, 11)
   - Fornecer avisos de privacidade aos titulares
   - Responder a requisicoes de titulares
   - Realizar DPIA quando exigido (Art. 38, VI)

2.2 **Operador (IndiQR/LealCyber):** O IndiQR e o operador dos Dados do Cliente. Cabe ao IndiQR:
   - Tratar os dados conforme instrucoes documentadas do Controlador (Art. 39)
   - Garantir a seguranca dos dados (Art. 46)
   - Notificar o Controlador sobre incidentes de seguranca (Art. 48)
   - Submeter-se a auditorias do Controlador (Art. 39)
   - Eliminar ou devolver os dados ao termino do contrato (Art. 40)

---

## 3. Categorias de Dados Tratados

3.1 **Dados de administradores da empresa:**
   - `email`, `auth_id` (identificador de autenticacao)
   - `name` (nome da empresa), `slug`

3.2 **Dados de influenciadores (indicadores):**
   - `email`, `auth_id`
   - Vinculo com campanhas (`influenciador_id`)
   - Dados de carteira: `saldo_reais`, `saldo_pontos`
   - Historico de conversoes e resgates

3.3 **Dados de vendedores:**
   - `email`, `auth_id`
   - Vinculo com empresa (`vendedor_id`)

3.4 **Dados de convites:**
   - `email` do convidado, `role`

3.5 **Dados de vitrine (Shop):**
   - Nome da empresa, tagline, email de contato
   - URLs de Instagram e WhatsApp
   - Imagens (logo, hero, produtos, galeria)
   - Nomes e precos de produtos

---

## 4. Finalidades do Tratamento

O Operador tratara os Dados do Cliente exclusivamente para as seguintes finalidades:

| Finalidade | Base legal tipica (Controlador) | Art. LGPD |
|------------|-------------------------------|-----------|
| Autenticacao e controle de acesso a plataforma | Execucao de contrato | Art. 7º, II |
| Gestao de empresas, membros e campanhas | Execucao de contrato | Art. 7º, II |
| Envio de emails transacionais (convites, notificacoes) | Execucao de contrato | Art. 7º, II |
| Rastreamento de conversoes e remuneracao | Execucao de contrato | Art. 7º, II |
| Gestao de carteira e resgates (pontos/reais) | Execucao de contrato | Art. 7º, II |
| Publicacao de vitrine virtual (Shop) | Consentimento do Cliente | Art. 7º, I |
| Monitoramento e seguranca da plataforma | Legitimo interesse | Art. 7º, VI |
| Diagnostico de erros | Legitimo interesse | Art. 7º, VI |

---

## 5. Suboperadores (LGPD Art. 37, VI)

5.1 O Controlador autoriza o Operador a utilizar os seguintes suboperadores para o tratamento dos Dados do Cliente:

| Suboperador | Servico | Dados tratados | Localizacao | Mecanismo de transferencia |
|-------------|---------|---------------|-------------|---------------------------|
| **Auth0 (Okta, Inc.)** | Autenticacao | `email`, `auth_id`, roles | EUA | EU-US DPF + EU SCCs |
| **Resend, Inc.** | Email transacional | `email` destinatario, conteudo HTML | EUA (AWS us-east-1) | EU SCCs |
| **Neon, Inc.** | Banco de dados PostgreSQL | Todos os Dados do Cliente | Brasil (sa-east-1) ou EUA | Residencia de dados ou EU SCCs |
| **Cloudflare, Inc.** | Armazenamento de midia (R2) | Imagens e site estatico da vitrine | Global (CDN) | EU-US DPF + EU SCCs |
| **Grafana Labs** | Observabilidade (logs, traces) | Logs de acesso, telemetria | EUA / Global | EU SCCs |

5.2 **Akeyless Security** e utilizado para gerenciamento de segredos de infraestrutura e **nao processa dados pessoais**.

5.3 O inventario completo de suboperadores com fluxos tecnicos de dados esta documentado em [privacidade/suboperadores.md](https://github.com/lealcristopher/indiqr-spec/blob/main/privacidade/suboperadores.md).

5.4 O Operador notificara o Controlador com antecedencia minima de 30 dias sobre a adicao ou substituicao de suboperadores, garantindo ao Controlador o direito de obterar-se.

---

## 6. Transferencia Internacional (LGPD Art. 33)

6.1 Alguns suboperadores estao localizados fora do Brasil. O Operador adota as seguintes salvaguardas para transferencias internacionais:

| Mecanismo | Suboperadores cobertos | Fundamento LGPD |
|-----------|----------------------|-----------------|
| **EU Standard Contractual Clauses (SCCs)** | Auth0, Resend, Cloudflare, Grafana Cloud | Art. 33, II, "b" — clausulas-padrao contratuais |
| **EU-US Data Privacy Framework (DPF)** | Auth0 (Okta), Cloudflare | Art. 33, I — pais com nivel adequado (via DPF) |
| **Residencia de dados no Brasil** | Neon (regiao `sa-east-1`, Sao Paulo) | Sem transferencia internacional — dados permanecem em territorio nacional |

6.2 Para Neon, o Operador priorizara a regiao `sa-east-1` (Sao Paulo) para que os dados do Cliente permanecam no Brasil.

---

## 7. Medidas de Seguranca (LGPD Art. 46)

O Operador implementa as seguintes medidas tecnicas e organizacionais:

| Medida | Implementacao |
|--------|---------------|
| Criptografia em transito | TLS 1.2+ em todas as conexoes |
| Criptografia em repouso | Server-side encryption (Neon, R2) |
| Controle de acesso | RBAC com 3 roles isolados (`indiqr-admin`, `indiqr-influenciador`, `indiqr-vendedor`) |
| Autenticacao | JWT RS256 com validacao de audience e issuer |
| Protecao contra IDOR | Todos os endpoints verificam pertencimento a empresa |
| Sanitizacao de logs | OTPs e tokens mascarados nos logs |
| Rate limiting | Protecao contra brute-force em endpoints sensiveis |
| Segredos | Gerenciados via Akeyless (nunca em codigo-fonte) |
| CI/CD | Gitleaks, Trivy, Ruff, Bandit, Schemathesis |
| Backup | Politica de backup do Neon (point-in-time recovery) |

---

## 8. Direitos dos Titulares (LGPD Art. 18)

8.1 O Operador auxiliara o Controlador no atendimento de requisicoes de titulares, fornecendo mecanismos tecnicos para:
   - Confirmacao de tratamento e acesso aos dados (via API `GET /api/v1/auth/me`)
   - Correcao de dados (via API `PATCH`)
   - Exclusao de dados (via API `DELETE`, com excecoes para registros de auditoria financeira)
   - Exportacao/portabilidade de dados

8.2 O Operador notificara o Controlador em ate 5 dias uteis sobre qualquer requisicao de titular recebida diretamente.

---

## 9. Notificacao de Incidentes (LGPD Art. 48)

9.1 O Operador notificara o Controlador sem atraso indevido (em ate 48 horas apos a confirmacao) sobre qualquer incidente de seguranca que possa afetar os Dados do Cliente.

9.2 A notificacao incluira:
   - Natureza do incidente
   - Categorias e numero aproximado de titulares afetados
   - Medidas tomadas ou propostas
   - Contato do Encarregado de Dados (DPO): `privacidade@indiqr.lealcyber.com`

---

## 10. Auditoria (LGPD Art. 39)

10.1 O Controlador podera auditar a conformidade do Operador, mediante aviso previo de 30 dias, em horario comercial e sem interrupcao das operacoes.

10.2 O Operador disponibilizara:
   - Relatorio de conformidade atualizado
   - Certificacoes dos suboperadores (SOC 2, ISO 27001)
   - Registros de tratamento de dados

10.3 Custos de auditoria serao arcados pelo Controlador, exceto se a auditoria revelar nao conformidade do Operador.

---

## 11. Termino e Destino dos Dados (LGPD Art. 40)

11.1 Ao termino do Contrato Principal, o Operador:
   - Mantera os dados por ate 30 dias para que o Controlador solicite exportacao
   - Eliminara todos os Dados do Cliente em ate 60 dias apos o termino, exceto registros de auditoria financeira (conversoes e resgates) que serao anonimizados conforme Art. 16 da LGPD
   - Fornecera ao Controlador uma exportacao completa dos dados em formato estruturado (JSON), mediante solicitacao

---

## 12. Disposicoes Gerais

12.1 **Vigencia:** Este DPA vigora enquanto durar a prestacao de servicos do Contrato Principal.

12.2 **Alteracoes:** Alteracoes neste DPA serao comunicadas com 30 dias de antecedencia.

12.3 **Lei aplicavel:** Este DPA e regido pela Lei Geral de Protecao de Dados Pessoais (LGPD — Lei nº 13.709/2018).

12.4 **Foro:** Conflitos serao dirimidos no foro da comarca de residencia do Controlador (Art. 21 da LGPD).

12.5 **Prevalencia:** Em caso de conflito entre este DPA e o Contrato Principal, prevalecerao as disposicoes deste DPA no que tange ao tratamento de dados pessoais.

---

## Anexo A — Instrucoes Documentadas do Controlador

O Controlador instrui o Operador a tratar os Dados do Cliente conforme as finalidades descritas na Secao 4 deste DPA e exclusivamente por meio das funcionalidades oferecidas pela plataforma IndiQR. O Operador nao utilizara os Dados do Cliente para finalidades alem das contratadas, exceto quando exigido por lei (Art. 39, II da LGPD).

---

## Anexo B — Informacoes de Contato

**Operador (IndiQR / LealCyber):**
- Encarregado de Dados (DPO): `privacidade@indiqr.lealcyber.com`

**Controlador (Cliente):**
- [A preencher no momento da contratacao]

---

## Assinaturas

| Parte | Representante | Data | Assinatura |
|-------|--------------|------|------------|
| **Operador** — LealCyber Tecnologia Ltda. | [Nome do representante legal] | __/__/____ | ______________ |
| **Controlador** — [Razao social do Cliente] | [Nome do representante legal] | __/__/____ | ______________ |

---

**Versao do documento:** `privacidade/dpa-template-clientes.md`
**Repositorio:** [indiqr-spec](https://github.com/lealcristopher/indiqr-spec)
**Issue:** [IND-64](/IND/issues/IND-64)
