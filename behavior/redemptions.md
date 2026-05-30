# Resgates — Regras de Negócio

## Conceito

Um **resgate** é o registro de débito no saldo acumulado de um influenciador — equivalente ao pagamento pelo trabalho de indicação. O ciclo completo é:

```
Conversões → saldo acumulado → Resgate → saldo debitado
```

O resgate é iniciado pelo **influenciador** (que gera o código) e confirmado pelo **vendedor** (que digita o código no app). Isso mantém a mesma dinâmica de presença física do fluxo de conversão.

---

## Saldo Disponível

O saldo é derivado em tempo real — não há campo armazenado.

```
saldo_reais  = Σ(remuneracao_valor WHERE campanha.usa_pontos = false)
             - Σ(resgates.valor       WHERE tipo = "reais")

saldo_pontos = Σ(remuneracao_valor WHERE campanha.usa_pontos = true)
             - Σ(resgates.valor       WHERE tipo = "pontos")
```

Ambos nunca ficam negativos — a validação ocorre no momento do resgate (não na geração do código).

---

## Fluxo Completo

### Passo 1 — Influenciador gera código de resgate

1. Influenciador acessa `/resgates` no app
2. Vê saldo disponível (R$ e/ou pts, separados)
3. Seleciona tipo: **R$** ou **pontos**
4. Informa o valor a resgatar
5. `POST /redemptions/tokens` → backend valida que o saldo comporta o valor e gera o código
6. App exibe:
   - Código numérico de 6 dígitos (ex: `483 921`) com formatação espaçada
   - Countdown de 15 minutos
   - Instrução: "Mostre este código ao vendedor"
7. Código expira automaticamente após 15 min ou ao ser usado

### Passo 2 — Vendedor registra o resgate

1. Vendedor acessa `/vender` → aba **Resgate**
2. Digita o código de 6 dígitos
3. App chama `GET /redemptions/preview?code=483921` — exibe prévia:
   - Influenciador: [email]
   - Valor: R$ XX,XX ou XXX pts
4. Vendedor confirma → `POST /redemptions/validate { code }`
5. Resgate registrado e imutável
6. Tela de sucesso; opção "Novo resgate"

---

## Modelo de Dados

### ResgateToken

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID | PK |
| `influenciador_id` | FK | Usuário que gerou |
| `valor` | Numeric(10,2) | Valor a resgatar |
| `tipo` | enum | `reais` \| `pontos` |
| `code` | CHAR(6) | Código numérico, único globalmente |
| `status` | enum | `pendente` \| `usado` \| `expirado` |
| `expires_at` | timestamp | `created_at + 15 min` |
| `created_at` | timestamp | — |

- Um influenciador pode ter no máximo **1 token ativo por tipo** ao mesmo tempo
- Gerar novo token cancela o anterior do mesmo tipo
- `code` gerado com 6 dígitos numéricos (`random.randint(100000, 999999)` com verificação de unicidade entre tokens `pendente`)

### Resgate

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID | PK |
| `resgate_token_id` | FK | Token que originou o resgate |
| `influenciador_id` | FK | Copiado do token (desnormalizado para auditoria) |
| `vendedor_id` | FK | Vendedor que confirmou |
| `valor` | Numeric(10,2) | Valor efetivamente resgatado |
| `tipo` | enum | `reais` \| `pontos` |
| `created_at` | timestamp | — |

Resgates são **imutáveis após confirmação** (mesmo princípio de ADR-004 aplicado a conversões).

---

## Validações

### Na geração do token (`POST /redemptions/tokens`)

| Situação | HTTP | Detalhe |
|----------|------|---------|
| `valor` ≤ 0 | 422 | Valor inválido |
| `valor` > saldo disponível | 422 | Saldo insuficiente (R$ X,XX disponível) |
| `tipo` inválido | 422 | Tipo deve ser "reais" ou "pontos" |
| Saldo em pontos = 0 e tipo = pontos | 422 | Sem saldo em pontos para resgatar |

### Na confirmação (`POST /redemptions/validate`)

| Situação | HTTP | Detalhe |
|----------|------|---------|
| Código não encontrado | 404 | Código inválido |
| Token expirado | 422 | Código expirado — solicite um novo |
| Token já usado | 422 | Código já utilizado |
| Saldo insuficiente no momento do resgate | 422 | Saldo insuficiente (race condition protection) |
| Vendedor = Influenciador | 403 | Não é possível resgatar para si mesmo |

---

## Visibilidade

| Role | Vê |
|------|-----|
| `indiqr-admin` | Todos os resgates da empresa, saldo atual de cada influenciador |
| `indiqr-influenciador` | Próprios resgates + saldo atual (R$ e pts) |
| `indiqr-vendedor` | Resgates confirmados por ele (histórico) |

---

## Imutabilidade e Auditoria

- Sem `updated_at` no modelo `Resgate`
- Token permanece no banco após uso (status `usado`) — trilha de auditoria completa
- Tokens expirados permanecem com status `expirado` — auditável
- Sem cancelamento ou estorno de resgate no MVP

---

## Pós-MVP

- QRCode gerado pelo influenciador (análogo ao QR de campanha) para o vendedor escanear
- Resgate parcial com múltiplos códigos simultâneos (hoje: 1 código ativo por tipo)
- Estorno pelo admin com log de motivo e aprovação em dois níveis
- Notificação por email ao influenciador quando resgate for confirmado
- Exportação CSV dos resgates por período

---

## Testes

> Esta feature tem superfície de segurança maior que conversões — um resgate envolve transferência de valor real. A cobertura de testes deve ser **mais rigorosa que o padrão do restante do sistema**.

### Testes Unitários (`tests/unit/`)

**Geração de código OTP**
- [ ] Código gerado tem exatamente 6 dígitos numéricos (sem letras)
- [ ] Código gerado está no intervalo [100000, 999999]
- [ ] Dois tokens gerados consecutivamente têm códigos diferentes (colisão não silenciosa)
- [ ] `expires_at` = `created_at + 15 minutos` (exato)

**Cálculo de saldo**
- [ ] Saldo inicial = 0 (sem conversões nem resgates)
- [ ] Saldo = Σ remuneracao_valor das conversões reais quando não há resgates
- [ ] Saldo = Σ remuneracao_valor − Σ resgates quando há resgates
- [ ] Saldo de pontos e saldo de reais são independentes (sem contaminação cruzada)
- [ ] Saldo nunca retorna negativo após série de resgates parciais

**Validação de geração de token**
- [ ] Rejeita valor ≤ 0
- [ ] Rejeita valor > saldo disponível (erro descritivo com saldo atual)
- [ ] Rejeita tipo inválido (não "reais" nem "pontos")
- [ ] Aceita valor exatamente igual ao saldo (resgate total)
- [ ] Aceita valor parcial menor que o saldo

**Status do token**
- [ ] Token recém-criado tem status `pendente`
- [ ] Token expirado (expires_at no passado) → `get_status()` retorna `expirado`
- [ ] Token após uso tem status `usado`
- [ ] Token cancelado explicitamente tem status `expirado`

---

### Testes de Integração (`tests/integration/`)

**POST /redemptions/tokens**
- [ ] Influenciador autenticado cria token com saldo suficiente → 201 + código de 6 dígitos
- [ ] Influenciador sem saldo → 422 com mensagem de saldo insuficiente
- [ ] Criar segundo token do mesmo tipo cancela o anterior (status → `expirado`)
- [ ] Criar token de tipo diferente NÃO cancela o existente (R$ e pts independentes)
- [ ] Vendedor tenta criar token → 403 (permission `redemption:request` ausente)
- [ ] Admin tenta criar token → 403

**GET /redemptions/preview**
- [ ] Código válido e pendente → 200 com influenciador_email, valor, tipo
- [ ] Código expirado → 422 "Código expirado"
- [ ] Código já usado → 422 "Código já utilizado"
- [ ] Código não existe → 404
- [ ] Código alfanumérico (formato de campanha) → 404 (não confunde os namespaces)

**POST /redemptions/validate**
- [ ] Código válido, saldo suficiente, vendedor autenticado → 201 + resgate registrado
- [ ] Verificar que token muda para status `usado` após sucesso
- [ ] Verificar que saldo diminui corretamente após resgate
- [ ] Código expirado → 422
- [ ] Código já usado → 422 (idempotência — segunda chamada com mesmo código rejeitada)
- [ ] Influenciador tentando validar o próprio código → 403
- [ ] Admin tentando validar → 403 (apenas vendedor pode)
- [ ] Saldo ficou insuficiente entre geração e validação (race) → 422

**GET /redemptions/** (influenciador)
- [ ] Retorna apenas resgates do próprio influenciador
- [ ] Outro influenciador não aparece na lista
- [ ] Ordenado por `created_at` DESC

**GET /redemptions/** (vendedor)
- [ ] Retorna apenas resgates confirmados pelo próprio vendedor
- [ ] Não inclui resgates de outros vendedores

**DELETE /redemptions/tokens/{id}**
- [ ] Influenciador cancela próprio token pendente → status `expirado`
- [ ] Influenciador tenta cancelar token de outro influenciador → 403
- [ ] Cancelar token já expirado/usado → 422

---

### Testes E2E (`tests/e2e/`)

**Fluxo feliz completo**
- [ ] Influenciador acumula saldo via conversão
- [ ] Influenciador gera código de resgate para valor parcial
- [ ] Vendedor valida o código → resgate registrado
- [ ] Saldo do influenciador reflete o débito
- [ ] Influenciador gera segundo código para o saldo restante → sucesso
- [ ] Influenciador tenta gerar código para valor maior que saldo restante → erro

**Fluxo de pontos**
- [ ] Conversão de campanha `usa_pontos=true` acumula saldo em pontos
- [ ] Resgate de pontos debita saldo de pontos, não de reais
- [ ] Saldo de reais permanece inalterado após resgate de pontos

**Expiração**
- [ ] Token gerado com `expires_at` no passado (injeção direta no DB) → preview retorna 422
- [ ] Validate com token expirado → 422

**Isolamento entre empresas**
- [ ] Vendedor da empresa A tenta validar código gerado por influenciador da empresa B → 403

---

### Testes de Segurança

**Enumeração de códigos**
- [ ] 100 tentativas com códigos aleatórios por IP em 1 minuto → rate limit (se implementado) ou sem information disclosure (erro genérico 404 sem timing oracle)
- [ ] Erro para código inválido não revela se o código existe ou não (mesma mensagem para "não existe" e "já expirado" — ou intencionalmente diferenciado: ver ADR-007)

**Elevação de privilégio**
- [ ] Influenciador não pode chamar `POST /redemptions/validate` (não pode debitar o próprio saldo sem vendedor)
- [ ] Vendedor não pode chamar `POST /redemptions/tokens` (não pode gerar códigos)
- [ ] Usuário sem role não tem acesso a nenhum endpoint

**Injeção / manipulação de valor**
- [ ] O valor resgatado é sempre o valor do token — vendedor não pode alterar o valor na validação
- [ ] Tentativa de alterar `valor` no body de `POST /redemptions/validate` não tem efeito (campo ignorado ou rejeitado)

**Race condition**
- [ ] Duas chamadas simultâneas de `POST /redemptions/validate` com o mesmo código → apenas uma é bem-sucedida (idempotência via lock ou status check atômico)

**IDOR (Insecure Direct Object Reference)**
- [ ] `DELETE /redemptions/tokens/{id}` com ID de outro influenciador → 403 (não 404, para não revelar existência)
- [ ] `GET /redemptions/{id}` com ID de resgate de outro usuário → 403

**Token leakage**
- [ ] Código OTP não aparece em logs de aplicação (mascarado ou omitido)
- [ ] Resposta de erro não ecoa o código tentado de volta
