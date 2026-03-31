# ADR-004: Imutabilidade das Conversões

**Status:** Aceito
**Data:** 2026-03

## Contexto

Conversões registram transações financeiras (base para pagamento ao influenciador). Precisam ser auditáveis e confiáveis para ambas as partes.

## Decisão

Conversões são imutáveis após confirmação:
- Sem `updated_at` no modelo
- Sem endpoint de cancelamento ou estorno no MVP
- Valores calculados armazenados (não recalculados)

## Consequências

- Admin e influenciador podem confiar no histórico como fonte da verdade
- Erros de digitação do vendedor (valor errado) não podem ser corrigidos — acerto fora da plataforma
- Pós-MVP: endpoint de estorno com log de motivo e aprovação do admin
- `INSERT`-only simplifica auditoria e backup incremental
