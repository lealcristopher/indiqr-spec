# Registro de DPAs — IndiQR

**Responsavel:** DPO
**Referencia LGPD:** Arts. 26 (operador), 33 (transferencia internacional), 35 (clausulas-padrao)
**Issue:** [IND-64](/IND/issues/IND-64)
**Ultima atualizacao:** 11 de junho de 2026

---

## 1. Status de Execucao de DPAs com Suboperadores

### Procedimento de Assinatura

Cada DPA deve ser formalmente aceito pelo representante legal da LealCyber (CEO). O procedimento padrao e:

1. Acessar o link do DPA do fornecedor
2. Revisar os termos (foco: categorias de dados, finalidade, suboperadores do fornecedor, jurisdicao, notificacao de breaches)
3. Executar o DPA conforme mecanismo do fornecedor (click-through, DocuSign, ou contrato bilateral)
4. Armazenar copia do DPA executado neste diretorio com nome `{fornecedor}-dpa-executado.{formato}`
5. Registrar data de execucao e metodo na tabela abaixo

### Tabela de Status

| Suboperador | Link do DPA | Mecanismo de Transferencia | Status | Data de Execucao | Metodo | Arquivo |
|-------------|-------------|---------------------------|--------|-----------------|--------|---------|
| **Auth0 (Okta)** | https://www.okta.com/agreements/data-processing-addendum/ | EU-US DPF + EU SCCs | Pendente | — | — | — |
| **Resend** | https://resend.com/legal/dpa | EU SCCs | Pendente | — | — | — |
| **Neon** | https://neon.tech/legal/dpa | Residencia de dados (sa-east-1) + EU SCCs | Em configuracao ([IND-73](/IND/issues/IND-73)) | — | — | — |
| **Cloudflare R2** | https://www.cloudflare.com/cloudflare-customer-dpa/ | EU-US DPF + EU SCCs | Pendente | — | — | — |
| **Grafana Cloud** | https://grafana.com/legal/dpa/ | EU SCCs | Pendente | — | — | — |
| **Akeyless** | Nao aplicavel | Nao aplicavel (nao processa PII) | N/A | N/A | N/A | N/A |

### Notas

- **Auth0 (Okta):** DPA incorporado ao contrato de servico. Okta e participante ativo do EU-US Data Privacy Framework. O DPA padrao do Okta inclui EU SCCs como salvaguarda adicional.
- **Resend:** DPA com EU SCCs incorporadas. Verificar se Resend e participante ativo do DPF (status atual: nao confirmado).
- **Neon:** Regiao `sa-east-1` (Sao Paulo) em configuracao ([IND-73](/IND/issues/IND-73)) para residencia de dados no Brasil, eliminando a necessidade de mecanismo de transferencia internacional. O DPA do Neon com EU SCCs serve como salvaguarda secundaria.
- **Cloudflare R2:** Cloudflare e participante ativo do EU-US DPF. DPA padrao inclui EU SCCs.
- **Grafana Cloud:** DPA com EU SCCs. Verificar status DPF do Grafana Labs (status atual: nao confirmado).
- **Akeyless:** Nao processa dados pessoais de usuarios. Apenas credenciais de infraestrutura. Transferencia internacional de PII nao se aplica.

---

## 2. Armazenamento Seguro

### Diretorio

```
privacidade/dpas/
├── README.md                          # Este documento
├── auth0-okta-dpa-executado.{formato} # Pendente
├── resend-dpa-executado.{formato}     # Pendente
├── neon-dpa-executado.{formato}       # Pendente
├── cloudflare-dpa-executado.{formato} # Pendente
├── grafana-dpa-executado.{formato}    # Pendente
└── .gitignore                         # Restringe visibilidade
```

### Controle de Acesso

- Copias de DPAs executados sao documentos contratuais sensiveis.
- **NAO devem ser commitados em repositorio publico.**
- Armazenar em repositorio interno seguro (ex: Google Drive corporativo, Vault compartilhado) com acesso restrito a CEO, DPO e CTO.
- Este diretorio no repositorio publico contem apenas este README de rastreamento.
- O `.gitignore` neste diretorio exclui qualquer arquivo que nao seja este README.

---

## 3. Trilha de Auditoria

Cada execucao de DPA deve ser registrada com:

- Data de execucao
- Metodo (click-through / assinatura eletronica / contrato bilateral)
- Identificador ou referencia do contrato (se fornecido pelo suboperador)
- Versao do DPA vigente na data de execucao
- Agente responsavel pela execucao (CEO)

---

## 4. Renovacao e Monitoramento

- **Periodicidade de revisao:** Anual ou quando o suboperador notificar alteracao no DPA.
- **Gatilhos de revisao:** Alteracao nos servicos contratados, mudanca na localizacao dos dados, notificacao de breach pelo suboperador.
- **Responsavel:** DPO, com apoio do CTO para aspectos tecnicos.

---

**Versao do documento:** `privacidade/dpas/README.md`
**Repositorio:** [indiqr-spec](https://github.com/lealcristopher/indiqr-spec)
**Issue:** [IND-64](/IND/issues/IND-64)
