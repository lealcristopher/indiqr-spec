# Conversions — Regras de Negócio

## Fluxo de Validação — Web (Short Token)

1. Vendedor acessa `/vender` (autenticado via Auth0)
2. Vendedor digita o `short_token` da campanha (6 chars, ex: `XpT250`) — obtido com o influenciador
3. Vendedor informa o `valor_bruto` da compra
4. Sistema exibe tela de confirmação com os dados informados
5. Vendedor confirma → `POST /conversions/validate` com `{ qrcode_token: shortToken, valor_bruto }`
6. API valida, calcula e retorna a conversão criada com desconto e remuneração
7. Tela de sucesso exibe breakdown: valor bruto, desconto, valor líquido, comissão

## Fluxo de Validação — App Mobile (QR Scan) — Pós-MVP

1. Vendedor abre o app (autenticado via Auth0)
2. Vendedor informa o `valor_bruto` da compra
3. Vendedor escaneia o QRCode apresentado pelo influenciador/cliente
4. Sistema valida:
   - QRCode existe e está `active=True`
   - Campanha associada está com status `ativa`
5. App exibe resumo da operação:
   - Valor bruto da compra
   - Desconto aplicado ao cliente (valor em R$, se houver)
   - Valor final a cobrar do cliente
   - Remuneração calculada para o influenciador
6. Vendedor confirma com botão explícito
7. Conversão registrada; app exibe confirmação

O cliente acompanha visualmente no app do vendedor — sem conta na plataforma.

## Cálculo Automático

```
se remuneracao_modelo = "fixo":
    remuneracao_valor = campaign.remuneracao_valor

se remuneracao_modelo = "percentual":
    remuneracao_valor = valor_bruto * campaign.remuneracao_valor / 100

se campaign.desconto_pct não nulo:
    desconto_valor = valor_bruto * campaign.desconto_pct / 100
    valor_final_cliente = valor_bruto - desconto_valor
senão:
    desconto_valor = 0
    valor_final_cliente = valor_bruto
```

Todos os valores são armazenados calculados (não recalculados depois).

## Registro

Cada conversão contém:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `campaign_id` | FK | Campanha associada |
| `qrcode_id` | FK | QRCode escaneado |
| `influenciador_id` | FK | Influenciador vinculado à campanha |
| `vendedor_id` | FK | Vendedor que confirmou |
| `valor_bruto` | Numeric | Valor informado pelo vendedor |
| `desconto_valor` | Numeric | Desconto concedido ao cliente |
| `remuneracao_valor` | Numeric | Remuneração calculada para o influenciador |
| `created_at` | timestamp | Momento da confirmação |

## Imutabilidade

- Registros são **imutáveis após confirmação**
- Sem `updated_at` no modelo
- Sem cancelamento ou estorno no MVP
- O log completo é preservado mesmo após encerramento da campanha

## Validações de Erro

| Situação | HTTP | Mensagem |
|----------|------|---------|
| UUID ou short_token não encontrado | 404 | QRCode inválido |
| QRCode inativo (`active=False`) | 404 | QRCode inválido ou inativo |
| Campanha não está `ativa` | 422 | Campanha não está ativa |
| `valor_bruto` ≤ 0 | 422 | Valor inválido |

## Visibilidade

| Role | Vê |
|------|-----|
| `indiqr-admin` | Todas as conversões da empresa (filtros: campanha, período, vendedor) |
| `indiqr-influenciador` | Apenas conversões das próprias campanhas |
| `indiqr-vendedor` | Apenas conversões registradas por ele mesmo |

## Pós-MVP

- Cancelamento/estorno pelo Admin com log de motivo
- Exportação CSV
- Webhook de notificação por conversão
