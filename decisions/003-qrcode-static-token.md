# ADR-003: QRCode Estático com Token UUID

**Status:** Aceito
**Data:** 2026-03

## Contexto

O QRCode precisa ser escaneável múltiplas vezes (uma por conversão) ao longo da campanha, mas inválido imediatamente ao encerrar a campanha.

## Decisão

QRCode estático: codifica um UUID gerado uma vez por campanha×influenciador. O UUID é armazenado no banco com flag `active`. A validação consulta o banco — se `active=False` ou campanha não está `ativa`, retorna erro.

## Por que não QRCode dinâmico

- QRCode dinâmico (com JWT ou token rotacionado) aumenta complexidade sem benefício no MVP
- A segurança anti-fraude vem de outro lugar: o vendedor precisa estar autenticado no app para registrar a conversão, o que rastreia cumplicidade

## Segurança

- Influenciador não tem acesso ao fluxo de confirmação — não pode registrar conversões para si mesmo
- Cada conversão registra o `vendedor_id` — conluio vendedor×influenciador é rastreável
- QRCode compartilhado digitalmente é aceitável: quem valida é o vendedor autenticado

## Consequências

- Geração simples: `uuid.uuid4()` + lib `qrcode[pil]` → PNG
- Invalidação imediata ao encerrar campanha: `UPDATE qrcodes SET active=False WHERE campaign_id=?`
- Sem necessidade de rotação ou expiração por tempo
