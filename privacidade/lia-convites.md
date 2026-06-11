# LIA — Legitimate Interest Assessment / Avaliação de Legítimo Interesse

**Produto:** IndiQR — Plataforma SaaS de Marketing de Indicação
**Versão do documento:** 1.0
**Data:** 2026-06-11
**Responsável:** CTO / DPO
**Legislação de referência:** LGPD — Lei nº 13.709/2018, Art. 7, IX e Art. 10
**Escopo:** Envio de convites por email para participação em empresa ou campanha

---

## 1. Finalidade do Tratamento

### 1.1 Descrição

O IndiQR envia emails de convite para dois fins distintos:

1. **Convite para empresa**: Um administrador convida uma pessoa (por email) a se juntar à sua empresa na plataforma como influenciador ou vendedor.
2. **Convite para campanha**: Um administrador convida um influenciador já membro da empresa a participar de uma campanha de marketing específica.

Em ambos os casos, o dado pessoal tratado é o **endereço de email** do convidado.

### 1.2 Contexto de negócio

O IndiQR é uma plataforma SaaS de marketing por indicação. O modelo de negócio depende de:
- Empresas que criam e gerenciam campanhas
- Influenciadores que promovem campanhas via QR codes
- Vendedores que validam conversões

Sem a capacidade de convidar membros, a plataforma não consegue formar a rede necessária para seu funcionamento. O convite por email é o **único canal de aquisição de membros** disponível na plataforma.

---

## 2. Necessidade do Tratamento

### 2.1 Por que o email é necessário

| Alternativa considerada | Viabilidade | Motivo da rejeição |
|-------------------------|-------------|-------------------|
| Convite por link compartilhável (WhatsApp, redes sociais) | Tecnicamente viável | O administrador precisaria do contato prévio do convidado em outro canal; email é o identificador universal e o único dado de contato que o admin possui do convidado |
| Cadastro público (self-service) | Implementado como via complementar (`membership_requests`) | Não cobre o caso em que o admin quer convidar proativamente uma pessoa específica |
| Convite por telefone/SMS | Inviável | A plataforma não coleta telefone; custo operacional elevado |
| Convite presencial (QR code em tela) | Inviável | Não escala; não se aplica a convites remotos |

**Conclusão:** O email é o **dado mínimo necessário** e o **único canal viável** para o envio de convites proativos. O tratamento limita-se ao endereço de email e ao cargo pretendido (role), que são os dados estritamente necessários para a finalidade (Art. 10, §1º LGPD).

### 2.2 Dados tratados

| Dado | Finalidade | Retenção |
|------|-----------|----------|
| Email do convidado | Envio do convite; identificação na aceitação | Até aceitação, recusa, revogação ou opt-out |
| Cargo pretendido (role) | Definir permissões após aceitação | Mesmo ciclo do convite |
| Token de convite (UUID) | Link seguro de aceitação | Idem |
| Timestamps (criação, aceitação) | Auditoria | Idem |

---

## 3. Balancing Test (Teste de Ponderação)

### 3.1 Interesse legítimo do controlador (Art. 7, IX)

O controlador (empresa-cliente do IndiQR) tem interesse legítimo em:
- Expandir sua rede de influenciadores e vendedores
- Convidar pessoas específicas que possam agregar valor ao seu negócio
- Utilizar a plataforma conforme contratada (SaaS de marketing de indicação)

A IndiQR, como operadora, viabiliza tecnicamente esse convite em nome do controlador.

### 3.2 Direitos e expectativas do titular

| Direito do titular | Avaliação |
|-------------------|-----------|
| **Expectativa razoável** | Um convite profissional único para participar de uma plataforma de marketing é razoável e esperado no contexto B2B/B2C. Não se trata de marketing de massa. |
| **Direito de oposição (Art. 18, §2º)** | O titular pode recusar o convite simplesmente ignorando-o. Pode também exercer opt-out a qualquer momento, cancelando futuros convites. |
| **Direito de acesso (Art. 18, I)** | O titular pode solicitar informações sobre convites recebidos. |
| **Direito de eliminação (Art. 18, VI)** | Dados de convites não aceitos são elimináveis mediante solicitação. |
| **Direito à informação (Art. 9)** | O email de convite informa a identidade do controlador, a finalidade e o meio de opt-out. |

### 3.3 Ponderação

| Fator | Peso a favor do controlador | Peso a favor do titular |
|-------|---------------------------|------------------------|
| Natureza do dado | Email é dado pessoal, mas de baixa sensibilidade | — |
| Volume de emails | Um convite por relação (não é comunicação em massa) | — |
| Relação prévia | Geralmente existe relação comercial ou profissional prévia (o admin conhece o convidado) | — |
| Expectativa do titular | — | Moderada: titular pode não esperar o convite |
| Facilidade de oposição | Opt-out imediato disponível em todo email | Oposição trivial (1 clique) |
| Consequência da recusa | Nenhuma — titular não sofre qualquer prejuízo | — |
| Interesse do controlador | Legítimo: expansão de rede é essencial ao SaaS | — |

**Resultado da ponderação:** O interesse legítimo do controlador **prevalece** sobre os direitos do titular, considerando:
1. A baixa sensibilidade do dado (apenas email)
2. O baixo volume (convite único por relação)
3. A facilidade de oposição (opt-out imediato)
4. A ausência de consequências negativas para o titular que recusar
5. A transparência do processo (informação clara no email)

---

## 4. Medidas de Mitigação (Salvaguardas)

### 4.1 Medidas técnicas

| Medida | Status | Descrição |
|--------|--------|-----------|
| **Opt-out imediato** | Implementado | Todo email de convite contém link de opt-out. Ao clicar, o email é removido permanentemente da lista de convites. |
| **Registro de opt-out** | Implementado | Cada opt-out é registrado com timestamp e email na tabela `email_opt_outs`. |
| **Bloqueio de reenvio** | Implementado | O sistema verifica a tabela de opt-outs antes de criar qualquer convite. Emails opt-out recebem HTTP 422. |
| **LIA documentado** | Implementado | Cada convite registra a base legal (`lia_basis`), a justificativa (`lia_justification`) e o responsável (`lia_completed_by_id`) na tabela `invitations`. |
| **Hash de tokens** | Implementado | Tokens de convite são gerados com `secrets.token_urlsafe(32)` (256 bits de entropia). |
| **Hash de OTP** | Implementado | Códigos OTP de resgate são armazenados como SHA-256 com salt (migração 012). |
| **Audit trail** | Implementado | Tabela `lia_assessments` registra cada LIA com UUID, entidade, base legal, justificativa e responsável. |

### 4.2 Medidas organizacionais

| Medida | Status |
|--------|--------|
| Política de Privacidade publicada | Implementado (`privacidade/politica-de-privacidade.md`) |
| DPIA (Relatório de Impacto) | Implementado (`docs/DPIA_LGPD_IndiQR.md`) |
| DPO nomeado | `privacidade@indiqr.lealcyber.com` |
| Prazo de retenção | Convites expiram com a revogação ou aceitação; opt-outs são permanentes |
| Transparência no email | Todo email informa: identidade do controlador, finalidade, base legal (legítimo interesse, Art. 10) e link de opt-out |

### 4.3 Salvaguardas específicas do Art. 10, §2º

O §2º do Art. 10 exige que o controlador adote **medidas de transparência** sobre o tratamento baseado em legítimo interesse. O IndiQR implementa:

1. **Transparência no email de convite**: Cada email inclui um rodapé informando:
   - Que a mensagem foi enviada com base em legítimo interesse (Art. 10 LGPD)
   - Link para opt-out (cancelamento de recebimento)
   - Email do DPO para dúvidas sobre tratamento de dados

2. **Transparência na Política de Privacidade**: A base legal de legítimo interesse para convites está documentada na política.

3. **Registro auditável**: O campo `lia_justification` no convite e a tabela `lia_assessments` permitem auditoria completa de cada decisão de tratamento.

---

## 5. Conclusão

### 5.1 Decisão

**O legítimo interesse (Art. 7, IX c/c Art. 10 LGPD) é base legal adequada para o envio de convites por email no IndiQR.**

Esta conclusão é sustentada por:

1. **Necessidade**: O email é o dado estritamente necessário e o único canal viável para o envio de convites proativos (Art. 10, §1º).
2. **Proporcionalidade**: O tratamento limita-se a um email por relação, sem comunicação em massa.
3. **Expectativa razoável**: O contexto B2B/B2C torna razoável o recebimento de um convite profissional.
4. **Salvaguardas robustas**: Opt-out imediato, registro auditável, transparência no email e na política de privacidade.
5. **Prevalência do interesse**: O interesse do controlador em expandir sua rede de negócios prevalece sobre o baixo impacto ao titular, que pode opor-se trivialmente.

### 5.2 Validade

Esta avaliação deve ser revisada:
- Anualmente (próxima revisão: Junho/2027)
- Sempre que houver mudança significativa na finalidade, nos dados tratados ou na legislação aplicável
- Em caso de incidente de segurança ou reclamação da ANPD

### 5.3 Aprovação

| Papel | Nome | Data | Assinatura |
|-------|------|------|-----------|
| CTO (elaboração) | CTO | 2026-06-11 | Aprovado tecnicamente |
| DPO (revisão) | Pendente | — | Aguardando revisão |

---

## Anexo A — Base legal alternativa: Consentimento

Embora o legítimo interesse seja a base legal primária, o consentimento (Art. 7, I) permanece como base legal alternativa disponível para os casos em que:

- O titular solicitar explicitamente ser convidado (via `POST /membership-requests`)
- O controlador preferir operar sob consentimento explícito

Nesses casos, o campo `lia_basis` no convite pode ser alterado para `consent`, e o consentimento deve ser registrado na tabela `consent_records`.

---

## Anexo B — Referências

- [LGPD — Lei nº 13.709/2018](http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/L13709.htm)
- [Guia Orientativo da ANPD — Legítimo Interesse](https://www.gov.br/anpd/pt-br)
- [DPIA IndiQR](../../indiqr/docs/DPIA_LGPD_IndiQR.md)
- [Política de Privacidade IndiQR](politica-de-privacidade.md)
- [Análise de Conformidade LGPD](analise-conformidade.md)
