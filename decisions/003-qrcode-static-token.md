# ADR-003: QRCode Estático com Token UUID + Short Token Web

**Status:** Aceito (revisado em 2026-04)
**Data:** 2026-03

## Contexto

O QRCode precisa ser escaneável múltiplas vezes (uma por conversão) ao longo da campanha, mas inválido imediatamente ao encerrar a campanha.

O fluxo de vendas foi concebido inicialmente para app mobile (câmera → scan). Para viabilizar a versão web antes do app mobile, foi introduzido um `short_token` como alias legível para o token UUID.

## Decisão

### Token UUID (QR)
QRCode estático: codifica um UUID gerado uma vez por campanha×influenciador. O UUID é armazenado no banco com flag `active`. A validação consulta o banco — se `active=False` ou campanha não está `ativa`, retorna erro.

### Short Token (Web)
Cada QRCode recebe também um `short_token` de 6 caracteres alfanuméricos (ex: `XpT250`), único globalmente, gerado na criação do QRCode. O endpoint `POST /conversions/validate` aceita **tanto** o UUID quanto o short_token no campo `qrcode_token` — se o valor não for um UUID válido, o sistema tenta lookup por short_token.

O `short_token` é exibido ao influenciador na plataforma web e impresso no card PDF abaixo do QR, para que possa ser compartilhado verbalmente ou digitado pelo vendedor na web.

## Por que não QRCode dinâmico

- QRCode dinâmico (com JWT ou token rotacionado) aumenta complexidade sem benefício no MVP
- A segurança anti-fraude vem de outro lugar: o vendedor precisa estar autenticado no app para registrar a conversão, o que rastreia cumplicidade

## Segurança

- Influenciador não tem acesso ao fluxo de confirmação — não pode registrar conversões para si mesmo
- Cada conversão registra o `vendedor_id` — conluio vendedor×influenciador é rastreável
- Short token tem espaço de 62^6 ≈ 56 bilhões — brute force inviável em contexto autenticado
- QRCode compartilhado digitalmente é aceitável: quem valida é o vendedor autenticado

## Consequências

- Geração simples: `uuid.uuid4()` + lib `qrcode[pil]` → PNG; `short_token` = 6 chars `[a-zA-Z0-9]`
- Invalidação imediata ao encerrar campanha: `UPDATE qrcodes SET active=False WHERE campaign_id=?`
- Sem necessidade de rotação ou expiração por tempo
- Card PDF exibe QR + short_token; vendedor web digita o código manualmente
- App mobile futuro usará a câmera para escanear o UUID via QR
