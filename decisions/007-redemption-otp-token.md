# ADR-007: OTP Numérico para Código de Resgate

**Status:** Aceito
**Data:** 2026-04

## Contexto

O fluxo de resgate exige que o influenciador apresente um código ao vendedor, de forma análoga ao `short_token` de campanha. Isso cria um risco de **confusão de tokens**:

| Token | Propósito | Direção | Visibilidade |
|-------|-----------|---------|--------------|
| `short_token` de campanha | Registrar uma venda | Influenciador → vendedor | Pública e permanente |
| Código de resgate (novo) | Receber pagamento | Influenciador → vendedor | Efêmera, privada |

O influenciador pode inadvertidamente:
- Mostrar o código de resgate quando o vendedor pede o token de campanha para uma venda
- Mostrar o token de campanha quando quer receber um pagamento

Qualquer confusão compromete a confiança: usar o código errado não causaria pagamento acidental (os endpoints são distintos), mas causaria frustração e suporte desnecessário.

## Problema

Os dois tokens chegam ao vendedor pelo mesmo canal (digitação manual, pelo menos até ter câmera). A diferenciação precisa ser:

1. **Visual** — o influenciador sabe exatamente qual código está mostrando
2. **Estrutural** — os formatos são distinguíveis mesmo sem contexto
3. **Comportamental** — o vendedor entra no fluxo certo antes de digitar qualquer coisa

## Decisão

### Formato diferente por design

| | Token de campanha | Código de resgate |
|--|--|--|
| Formato | 6 chars alfanuméricos | 6 dígitos numéricos |
| Exemplo | `XpT250` | `483 921` |
| Expiração | Permanente (dura a campanha) | 15 minutos |
| Gerado por | Sistema no aceite da campanha | Influenciador sob demanda |
| Propósito | Habilitar vendas | Solicitar pagamento |

A diferença alfanumérico vs. numérico é reconhecível a olho nu sem precisar ler um rótulo. Um código de 6 dígitos nunca será confundido com `XpT250`.

### Contexto de entrada no app do vendedor

O app do vendedor oferece **duas ações distintas** em `/vender`:

```
┌─────────────────────────────┐
│  [💰 Registrar Venda]       │  → digita short_token alfanumérico
│  [💳 Registrar Resgate]     │  → digita código numérico
└─────────────────────────────┘
```

O vendedor seleciona a ação antes de qualquer digitação. Se digitar o código errado no fluxo errado, o backend retorna erro claro:
- Código numérico no fluxo de venda → `404 QRCode inválido`
- Short token alfanumérico no fluxo de resgate → `404 Código inválido`

### UI do influenciador

A tela de resgate exibe o código com rótulo explícito e visual diferenciado:

```
┌──────────────────────────────────────┐
│  💳 CÓDIGO DE RESGATE                │
│                                      │
│         483 921                      │  ← fonte grande, apenas dígitos
│                                      │
│  Válido por: 12:43                   │  ← countdown
│  Mostre ao vendedor para receber     │
│  R$ 50,00 do seu saldo               │
│                                      │
│  [Cancelar código]                   │
└──────────────────────────────────────┘
```

A tela de campanha exibe o QR com rótulo diferente:

```
┌──────────────────────────────────────┐
│  📢 QR CODE DA CAMPANHA              │
│                                      │
│  [████ QR IMAGE ████]                │
│  Código: XpT250                      │  ← alfanumérico, visualmente distinto
│                                      │
│  Compartilhe com clientes            │
└──────────────────────────────────────┘
```

## Alternativas Consideradas

### Alternativa A — Mesmo formato com prefixo (`RSG-483921`)

**Rejeitada.** Prefixo pode ser omitido ao falar oralmente. "Qual é o código?" → "Quatrocentos e oitenta e três, novecentos e vinte e um" — o prefixo some.

### Alternativa B — Código gerado pelo backend com UUID curto

**Rejeitada.** UUID curto seria alfanumérico, colapsando a distinção visual com o `short_token` de campanha.

### Alternativa C — Dois apps separados (vendas vs. resgates)

**Rejeitada.** Aumenta fricção de onboarding. O vendedor já tem o app; separar em dois apps por operação viola o princípio de menor fricção.

### Alternativa D — Token bidirecional (backend distingue automaticamente)

**Rejeitada para MVP.** Permitir que o mesmo campo aceite os dois tipos de token coloca a distinção somente no backend, sem feedback visual ao usuário antes de submeter. Pode ser adotado pós-MVP como conveniência adicional.

## Consequências

- Vendedor precisa escolher o fluxo antes de digitar o código — uma tela a mais, mas elimina ambiguidade
- Backend valida formato antes de fazer lookup: código numérico de 6 dígitos → redemption; qualquer outra coisa → QR/short_token
- Sem colisão possível entre os dois namespaces
- Quando QRCode for implementado para resgates (pós-MVP), o QR codificará o OTP numérico; o leitor pode distinguir pelo conteúdo
