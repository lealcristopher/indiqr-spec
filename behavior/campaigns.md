# Campaigns — Regras de Negócio

## Ciclo de Vida

```
[criada pelo admin]
       │
       ▼
aguardando_aceite ──── influenciador recusa ──► encerrada
       │
       │ influenciador aceita
       ▼
     ativa ──── admin encerra ──────────────► encerrada
       │
       └── influenciador sai ────────────── ► encerrada
```

## Criação

- Somente `indiqr-admin` pode criar campanhas
- A campanha pertence à empresa do admin que a criou
- Campos obrigatórios:

| Campo | Tipo | Regra |
|-------|------|-------|
| `name` | string | obrigatório, min_length=1 |
| `influenciador_email` | email | usuário deve existir na plataforma com role `indiqr-influenciador` |
| `remuneracao_modelo` | enum | `fixo` ou `percentual` |
| `remuneracao_valor` | decimal | > 0 |
| `desconto_pct` | decimal | opcional; se informado, deve ser > 0 e ≤ 100 |

- Ao criar: status `aguardando_aceite`; email de convite enviado ao influenciador com os termos
- Parâmetros de remuneração e desconto são **imutáveis após o aceite**

## Convite de Campanha

Email enviado ao influenciador contém:
- Nome da campanha e da empresa
- Modelo de remuneração (ex: "R$ 50,00 por conversão" ou "10% do valor da venda")
- Desconto ao cliente final (se houver)
- Botões de aceitar e recusar

## Aceite / Recusa pelo Influenciador

### Aceite
- Status → `ativa`
- QRCode gerado (UUID único, `active=True`)
- Email notificando o admin
- Material de divulgação (PDF) fica disponível

### Recusa
- Status → `encerrada`
- Email notificando o admin
- QRCode não é gerado

## Encerramento

### Pelo Admin
- Disponível apenas para campanhas `ativas`
- Status → `encerrada`
- QRCode invalidado (`active=False`)
- Email notificando o influenciador

### Pelo Influenciador (sair da campanha)
- Disponível apenas para campanhas `ativas`
- Status → `encerrada`
- QRCode invalidado
- Email notificando o admin

## QRCode

- Um QRCode por campanha por influenciador (relação 1:1 com campanha)
- Codifica token UUID que identifica a campanha + influenciador no escaneamento
- Estático — não expira por tempo
- Invalidado imediatamente ao encerrar campanha (`active=False`)
- Tentativas de escaneamento com QRCode inativo retornam erro

## Material de Divulgação (PDF)

- Disponível apenas para campanhas `ativas`
- Template fixo: QRCode + nome da campanha/empresa + instrução ao cliente
- Retornado como `application/pdf` no endpoint `GET /campaigns/{id}/card.pdf`
- Pós-MVP: personalização com logo e cores da empresa

## Visibilidade

- Admin: vê todas as campanhas da sua empresa
- Influenciador: vê apenas campanhas em que foi convidado (qualquer status)
- Vendedor: sem acesso ao módulo de campanhas

## Notificações por Email

| Evento | Destinatário |
|--------|-------------|
| Campanha criada (convite) | Influenciador |
| Influenciador aceitou | Admin |
| Influenciador recusou | Admin |
| Admin encerrou campanha | Influenciador |
| Influenciador saiu da campanha | Admin |
