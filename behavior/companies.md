# Companies — Regras de Negócio

## Criação de Empresa

- Qualquer usuário com role `indiqr-admin` pode criar uma empresa
- O criador torna-se automaticamente membro com role `admin`
- `slug` deve ser único globalmente
- `name` e `slug` são obrigatórios e não podem ser vazios (`min_length=1`)

## Membros

### Tipos de membro

| Role | Descrição |
|------|-----------|
| `admin` | Gerencia campanhas, convida e remove membros |
| `influenciador` | Recebe convites de campanha, baixa material |
| `vendedor` | Valida QRCodes no ponto de venda |

### Convite

- Admin envia convite por email com role especificada (`influenciador` ou `vendedor`)
- Email enviado via Resend com link de aceite
- Convite tem status: `pending` | `accepted` | `revoked`
- Sem expiração automática no MVP
- Admin pode revogar convite pendente a qualquer momento
- Não é possível convidar um email que já seja membro da empresa

### Aceite

- URL de preview pública mostra nome da empresa antes do login (`GET /companies/invitations/preview/{token}`)
- Usuário precisa estar autenticado para aceitar
- Ao aceitar:
  - `CompanyMember` criado com a role especificada no convite
  - Role Auth0 correspondente atribuída via Management API
  - Status do convite atualizado para `accepted`
- Convite inválido (revogado, já aceito, inexistente) → 404

### Remoção de membro

- Somente admin pode remover membros
- Admin não pode se auto-remover se for o único admin da empresa
- Ao remover:
  - `CompanyMember` deletado
  - Se o usuário não é membro de nenhuma outra empresa com aquela role → role Auth0 revogada

## Listagem

- `GET /companies/` retorna apenas empresas das quais o usuário é membro
- Admins veem todas as informações; influenciadores e vendedores veem nome e slug

## Validações

| Campo | Regra |
|-------|-------|
| `name` | obrigatório, `min_length=1` |
| `slug` | obrigatório, `min_length=1`, único globalmente, apenas `a-z0-9-` |
| `role` no convite | deve ser `influenciador` ou `vendedor` (admin não pode ser convidado) |
