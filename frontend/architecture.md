# Frontend Architecture

## Visão Geral

SPA React servida como site estático + PWA para o fluxo do vendedor. Três experiências distintas sob o mesmo domínio, separadas por role Auth0.

**URL de produção:** `https://indiqr.lealcyber.com`
**Repo:** `lealcristopher/indiqr-web`

---

## Stack

| Camada | Tecnologia | Motivo |
|--------|-----------|--------|
| Framework | React 18 + Vite | SPA simples, build rápido, sem SSR necessário |
| Linguagem | TypeScript | Tipos alinhados com os schemas do OpenAPI |
| Roteamento | React Router v6 | Padrão SPA, suporte a rotas protegidas |
| Server state | TanStack Query v5 | Cache, loading states, refetch automático |
| Auth | Auth0 React SDK (`@auth0/auth0-react`) | Integração direta com o tenant já configurado |
| UI | shadcn/ui + Tailwind CSS | Componentes acessíveis, customizáveis, sem lock-in |
| QR Scan | `html5-qrcode` | Acesso à câmera no browser, suporte mobile |
| QR Geração | Backend gera — frontend só exibe PNG | Sem geração client-side |
| PDF | Backend gera — frontend faz download direto | `GET /campaigns/{id}/card.pdf` |
| PWA | Vite PWA plugin (`vite-plugin-pwa`) | Para o fluxo do vendedor (mobile-first) |
| HTTP | Axios com interceptor de token | Injeta Bearer automaticamente |
| Forms | React Hook Form + Zod | Validação client-side alinhada com as regras do backend |
| Hosting | Cloudflare Pages | Deploy automático via git push, CDN global |

---

## Auth0

O tenant já existe (compartilhado com Recon). Configuração específica IndiQR:

| Item | Valor |
|------|-------|
| SPA App | `indiqr-web` |
| Audience | `https://indiqr-api.lealcyber.com` |
| Roles claim | `https://indiqr.lealcyber.com/roles` |
| Callback URLs | `https://indiqr.lealcyber.com/callback`, `http://localhost:5174/callback` |
| Logout URLs | `https://indiqr.lealcyber.com`, `http://localhost:5174` |

**Fluxo de auth:**
1. Usuário acessa rota protegida
2. Auth0 SDK redireciona para Universal Login
3. Após login, token JWT incluído em todas as chamadas via interceptor Axios
4. Claims de roles lidos do token para controle de navegação e visibilidade

---

## Estrutura de pastas

```
src/
├── api/               # Funções de chamada à API (um arquivo por recurso)
│   ├── companies.ts
│   ├── campaigns.ts
│   └── conversions.ts
├── components/        # Componentes reutilizáveis
│   ├── ui/            # shadcn/ui (gerados)
│   └── shared/        # Componentes do domínio (CampaignCard, StatusBadge, Pagination, etc.)
├── hooks/             # Custom hooks (useCurrentUser, useRoles, usePaginatedQuery, etc.)
├── pages/             # Uma pasta por rota
│   ├── admin/
│   ├── influencer/
│   ├── seller/
│   └── public/        # Convite preview (sem auth)
├── router/            # Definição de rotas + guards por role
├── store/             # Estado global mínimo (ex: empresa selecionada)
└── lib/               # axios instance, auth0 config, zod schemas, types
```

---

## Paginação

Todos os endpoints de lista retornam respostas paginadas no formato:

```typescript
// src/lib/types.ts
interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}
```

### Hook compartilhado: `usePaginatedQuery`

```typescript
// src/hooks/usePaginatedQuery.ts
import { useQuery, keepPreviousData } from '@tanstack/react-query';

function usePaginatedQuery<T>(
  key: string[],
  url: string,
  page: number,
  pageSize: number = 20
) {
  return useQuery<PaginatedResponse<T>>({
    queryKey: [...key, page, pageSize],
    queryFn: () =>
      fetch(`${url}?page=${page}&page_size=${pageSize}`).then((r) => r.json()),
    placeholderData: keepPreviousData,
  });
}
```

### Componente compartilhado: `<Pagination />`

```tsx
// src/components/shared/Pagination.tsx
interface PaginationProps {
  page: number;
  pages: number;
  onPageChange: (page: number) => void;
}
```

Comportamento:
- Botões "Anterior" (desabilitado na pág 1) e "Próximo" (desabilitado na última)
- Indicador: "Página X de Y"
- Opcional: seletor de `page_size` com opções 20, 50, 100

### Endpoints paginados

| Endpoint | Schema |
|----------|--------|
| `GET /companies/` | `PaginatedResponse<Company>` |
| `GET /companies/{id}/members` | `PaginatedResponse<Member>` |
| `GET /companies/{id}/invitations` | `PaginatedResponse<Invitation>` |
| `GET /campaigns/` | `PaginatedResponse<CampaignSummary>` |
| `GET /campaigns/{id}/conversions` | `PaginatedResponse<Conversion>` |
| `GET /conversions/` | `PaginatedResponse<Conversion>` |
| `GET /redemptions/` | `PaginatedResponse<Redemption>` |

### Parâmetros

| Parâmetro | Tipo | Default | Range |
|-----------|------|---------|-------|
| `page` | `integer` | `1` | >= 1 |
| `page_size` | `integer` | `20` | 1–100 |

---

## Interceptor Axios

```typescript
// src/lib/axios.ts
instance.interceptors.request.use(async (config) => {
  const token = await getAccessTokenSilently({
    authorizationParams: { audience: 'https://indiqr-api.lealcyber.com' }
  });
  config.headers.Authorization = `Bearer ${token}`;
  return config;
});
```

---

## PWA (Vendedor)

O fluxo do vendedor é mobile-first e deve funcionar com conexão instável:

- Manifest com `display: standalone`, ícone, theme color
- Service worker em modo `networkFirst` para as chamadas de API
- Cache offline da shell da aplicação
- Tela de instalação sugerida no primeiro acesso mobile

---

## CI/CD

```
git push main
    ↓
Cloudflare Pages build (npm run build)
    ↓
Deploy automático em indiqr.lealcyber.com
```

- Preview deploys automáticos em PRs (`*.indiqr.pages.dev`)
- Variáveis de ambiente configuradas no dashboard Cloudflare Pages:
  - `VITE_API_URL=https://indiqr-api.lealcyber.com`
  - `VITE_AUTH0_DOMAIN=<auth0_domain>`
  - `VITE_AUTH0_CLIENT_ID=<indiqr_web_client_id>`
  - `VITE_AUTH0_AUDIENCE=https://indiqr-api.lealcyber.com`
