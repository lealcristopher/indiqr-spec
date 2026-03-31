# RBAC — IndiQR

## Roles Auth0

| Role | Nome Auth0 | Atribuição |
|------|-----------|-----------|
| Admin | `indiqr-admin` | Signup padrão com role admin (fluxo de onboarding da empresa) |
| Influenciador | `indiqr-influenciador` | Signup autônomo com role padrão; recebe convites de campanha de admins |
| Vendedor | `indiqr-vendedor` | Convidado pelo Admin via email; sem signup autônomo |

A role é atribuída via Auth0 Management API no momento do aceite do convite (para Vendedor) ou no signup (para Admin/Influenciador via regra Auth0 Actions).

## Matriz de Permissões

| Permission | indiqr-admin | indiqr-influenciador | indiqr-vendedor |
|------------|:---:|:---:|:---:|
| `company:manage` | ✓ | — | — |
| `member:manage` | ✓ | — | — |
| `campaign:create` | ✓ | — | — |
| `campaign:read` | ✓ (todas da empresa) | ✓ (só as suas) | — |
| `campaign:close` | ✓ (encerra) | ✓ (sai da campanha) | — |
| `conversion:validate` | — | — | ✓ |
| `conversion:read` | ✓ (todas da empresa) | ✓ (só as suas) | ✓ (só as suas) |
| `qrcode:download` | — | ✓ | — |

## Ciclo de vida da role `indiqr-vendedor`

- **Atribuída:** ao aceitar convite de empresa (endpoint `POST /companies/invitations/{token}/accept`)
- **Revogada:** ao ser removido da empresa (endpoint `DELETE /companies/{id}/members/{uid}`), se não for membro de nenhuma outra empresa

## Configuração JWT

- Claim de roles: `https://indiqr.lealcyber.com/roles` (env `AUTH0_ROLES_CLAIM`)
- Audience: `https://indiqr-api.lealcyber.com` (env `AUTH0_AUDIENCE`)

## Visibilidade de dados por role

### Company

| Ação | admin | influenciador | vendedor |
|------|-------|---------------|---------|
| Listar empresas | próprias | próprias | próprias |
| Ver membros | ✓ | — | — |
| Convidar membro | ✓ | — | — |
| Remover membro | ✓ | — | — |

### Campaign

| Ação | admin | influenciador | vendedor |
|------|-------|---------------|---------|
| Criar | ✓ | — | — |
| Listar | todas da empresa | as suas | — |
| Ver detalhe | ✓ | próprias | — |
| Aceitar/recusar | — | próprias | — |
| Encerrar | ✓ | sair da própria | — |
| Baixar QRCode/PDF | — | próprias (ativas) | — |

### Conversion

| Ação | admin | influenciador | vendedor |
|------|-------|---------------|---------|
| Validar QRCode | — | — | ✓ |
| Listar | todas da empresa | próprias | próprias |
