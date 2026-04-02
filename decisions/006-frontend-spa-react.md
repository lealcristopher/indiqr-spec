# ADR-006: Frontend SPA React + Cloudflare Pages

**Data:** 2026-04
**Status:** Proposto

---

## Contexto

O IndiQR tem três perfis de usuário com experiências distintas: admin (gestão de empresas e campanhas), influenciador (aceite de campanhas e download de materiais) e vendedor (scanner de QRCode mobile). O backend está completo e disponível em `https://indiqr-api.lealcyber.com`.

---

## Decisão

**React 18 + Vite + TypeScript**, hospedado no **Cloudflare Pages** em `indiqr.lealcyber.com`, com **PWA** habilitada para o fluxo do vendedor.

---

## Alternativas Consideradas

### Next.js
- **Prós:** SSR/SSG nativos, melhor SEO
- **Contra:** SSR é desnecessário — todas as páginas requerem autenticação; adiciona complexidade de deploy (Node.js runtime)
- **Descartado**

### Vue / Angular
- **Contra:** Ecossistema do time é React (base no Recon); sem vantagem técnica para o domínio
- **Descartado**

### Remix
- **Contra:** Mesmo problema do Next.js; overhead desnecessário para uma app autenticada
- **Descartado**

---

## Justificativas

**React + Vite:**
- Stack SPA é suficiente — nenhuma rota é pública além do preview de convite e callback Auth0
- Vite tem build time muito menor que CRA/webpack
- TypeScript permite gerar types a partir do OpenAPI (`openapi-typescript`)

**Cloudflare Pages:**
- Já existe infraestrutura Cloudflare no projeto (web-relay, DNS)
- Deploy automático via git push sem configuração adicional
- Preview deploys por PR incluídos no plano gratuito
- CDN global sem custo adicional
- Variáveis de ambiente por ambiente (preview vs production)

**shadcn/ui + Tailwind:**
- Componentes copiados para o projeto (sem lock-in de biblioteca)
- Tailwind alinha com velocidade de desenvolvimento
- Acessibilidade via Radix UI primitives

**Auth0 React SDK:**
- Tenant já configurado; SDK oficial gerencia token refresh automaticamente
- `getAccessTokenSilently()` usado no interceptor Axios

**TanStack Query:**
- Cache de server state evita re-fetches desnecessários
- Loading/error states uniformes em toda a app
- Invalidação de cache por mutation (ex: aceitar campanha → recarrega lista)

**PWA para vendedor:**
- Vendedor usa celular no ponto de venda
- Conexão pode ser instável
- `vite-plugin-pwa` adiciona service worker com cache da shell
- Manifest permite instalação como app nativo no Android

---

## Consequências

- Types gerados do OpenAPI mantêm frontend sincronizado com o contrato da API
- Cloudflare Pages tem limite de 500 deploys/mês no plano gratuito (suficiente para MVP)
- PWA requer HTTPS (já garantido pelo Cloudflare)
- Auth0 Universal Login centraliza UX de login (sem tela customizada no MVP)
- Scanner de QRCode requer permissão de câmera — UX deve solicitar explicitamente
