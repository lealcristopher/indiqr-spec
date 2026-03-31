# ADR-002: Sem Elasticsearch

**Status:** Aceito
**Data:** 2026-03

## Contexto

O Recon usa Elasticsearch para prompts e dados HackerOne (busca full-text). IndiQR não tem nenhum caso de uso de busca full-text no MVP.

## Decisão

Todos os dados do IndiQR em PostgreSQL (schema `indiqr`). Sem Elasticsearch.

## Consequências

- Stack mais simples: sem serviço ES em docker-compose, sem index managers, sem opensearch-py
- Busca de conversões por período/vendedor/campanha via SQL (suficiente para o volume MVP)
- Se busca full-text for necessária futuramente (ex: busca de influenciadores), adicionar ES apenas então
