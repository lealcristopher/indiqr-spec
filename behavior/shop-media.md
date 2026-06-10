# Shop Media — Regras de Negócio e Especificação de Testes

> Área P2 do plano de cobertura IND-38. Detalha o comportamento e os cenários de
> teste esperados para os endpoints de upload e gerenciamento de mídia da vitrine
> (`/shop`).

---

## Visão Geral

O admin da empresa pode montar uma vitrine virtual (`shop`) com:

- **Logo e hero** — identidade visual da loja
- **Categorias** com imagem
- **Produtos** com imagem principal + galeria

Todas as imagens são gerenciadas via upload multipart e armazenadas em
object storage (R2/S3). O endpoint `GET /shop/mine` retorna a vitrine completa
com URLs públicas de todas as mídias.

---

## Endpoints

| Método | Path | Descrição |
|--------|------|-----------|
| `GET` | `/shop/mine` | Vitrine do admin autenticado |
| `POST` | `/shop/logo` | Upload do logo (1 imagem) |
| `POST` | `/shop/hero` | Upload da imagem hero (1 imagem) |
| `POST` | `/shop/categories/{id}/image` | Upload da imagem da categoria |
| `POST` | `/shop/products/{id}/image` | Upload da imagem principal do produto |
| `POST` | `/shop/products/{id}/gallery` | Upload de imagem na galeria |
| `DELETE` | `/shop/products/{id}/gallery/{image_id}` | Remove imagem da galeria |
| `PUT` | `/shop/products/{id}/gallery/reorder` | Reordena galeria |

---

## Regras de Negócio

### Autenticação e autorização

- Todos os endpoints requerem autenticação JWT
- Apenas usuários com role `indiqr-admin` podem gerenciar a vitrine
- `GET /shop/mine` retorna a vitrine do admin autenticado (por company_id)
- Outros roles que tentarem acessar → **403**

### Upload de imagem

- Formato: `multipart/form-data`, campo `file`
- Tipos aceitos: `image/png`, `image/jpeg`, `image/webp`, `image/avif`
- Tamanho máximo: 5 MB (configurável via `MAX_UPLOAD_SIZE_MB`)
- Nome do arquivo: gerado automaticamente (UUID + extensão original)
- Upload duplicado (mesmo nome) não sobrescreve — gera novo UUID

### Logo e Hero

- Apenas 1 imagem ativa por vez para cada
- Novo upload substitui a imagem anterior (marca como inativa, não deleta)
- `GET /shop/mine` sempre retorna a imagem ativa mais recente

### Galeria de produtos

- Múltiplas imagens por produto (sem limite no MVP)
- Ordenação via campo `position` (integer, 0-based)
- `PUT .../gallery/reorder` recebe array de `image_id` na nova ordem
- DELETE marca imagem como removida (soft-delete), não remove do storage
- `GET /shop/mine` não retorna imagens deletadas

### Validações de integridade

| Campo | Regra |
|-------|-------|
| `file` no upload | obrigatório, não vazio, MIME de imagem |
| `category_id` | deve pertencer à vitrine do admin |
| `product_id` | deve pertencer à vitrine do admin |
| `image_id` no delete/reorder | deve existir e pertencer ao produto |

### Respostas de erro

| Situação | HTTP | Detalhe |
|----------|------|---------|
| Arquivo não enviado | 422 | `file` é obrigatório |
| Tipo MIME inválido | 422 | Tipo de arquivo não suportado |
| Tamanho excedido | 413 | Arquivo excede 5 MB |
| Categoria não encontrada | 404 | Categoria não pertence à sua vitrine |
| Produto não encontrado | 404 | Produto não pertence à sua vitrine |
| Imagem não encontrada | 404 | Imagem não pertence ao produto |
| Sem permissão (não-admin) | 403 | Apenas admin pode gerenciar a vitrine |

---

## Especificação de Testes

### E2E — `tests/e2e/test_shop_api.py`

#### GET /shop/mine

- [ ] `test_get_my_shop_with_data`
  Admin autenticado → 200 com objeto shop completo (logo, hero, categories, products).
  Verificar que URLs de mídia são públicas e acessíveis.

- [ ] `test_get_my_shop_no_shop`
  Admin sem vitrine criada → 404 com mensagem informativa.

- [ ] `test_get_my_shop_non_admin_blocked`
  Influenciador ou vendedor autenticado → 403.

- [ ] `test_get_my_shop_unauthenticated`
  Sem token → 401.

#### POST /shop/logo

- [ ] `test_upload_logo_valid_png`
  Admin envia PNG válido 100×100 → 201, resposta contém URL pública.

- [ ] `test_upload_logo_valid_jpeg`
  Admin envia JPEG válido → 201, resposta contém URL pública.

- [ ] `test_upload_logo_replaces_previous`
  Admin envia logo A, depois logo B. GET /shop/mine retorna URL de B.
  Logo A permanece no storage mas não é retornada.

- [ ] `test_upload_logo_invalid_mime`
  Admin envia `text/plain` → 422. Mensagem menciona tipo não suportado.

- [ ] `test_upload_logo_no_file`
  Admin envia request sem campo `file` → 422.

- [ ] `test_upload_logo_empty_file`
  Admin envia arquivo de 0 bytes → 422.

- [ ] `test_upload_logo_exceeds_size_limit`
  Admin envia arquivo >5 MB → 413.

- [ ] `test_upload_logo_non_admin_blocked`
  Influenciador autenticado → 403.

#### POST /shop/hero

- [ ] `test_upload_hero_valid_image`
  Admin envia imagem hero válida → 201.

- [ ] `test_upload_hero_replaces_previous`
  Upload de hero B substitui hero A.

- [ ] `test_upload_hero_non_admin_blocked`
  Vendedor → 403.

#### POST /shop/categories/{id}/image

- [ ] `test_upload_category_image_success`
  Admin envia imagem para categoria existente → 201.

- [ ] `test_upload_category_image_not_found`
  `category_id` não pertence ao admin → 404.

- [ ] `test_upload_category_image_cross_company`
  Admin da empresa A tenta usar category_id da empresa B → 404
  (não vaza existência).

#### POST /shop/products/{id}/image

- [ ] `test_upload_product_image_success`
  Admin envia imagem principal → 201.

- [ ] `test_upload_product_image_replaces_previous`
  Imagem B substitui A no GET /shop/mine.

- [ ] `test_upload_product_image_not_found`
  `product_id` inválido → 404.

- [ ] `test_upload_product_image_non_admin_blocked`
  Influenciador → 403.

#### POST /shop/products/{id}/gallery

- [ ] `test_upload_gallery_image_success`
  Admin adiciona imagem à galeria → 201. Imagem aparece no array `gallery`.

- [ ] `test_upload_gallery_image_multiple`
  Admin envia 3 imagens consecutivas → 201 cada. GET /shop/mine retorna 3
  items na galeria, em ordem de criação.

- [ ] `test_upload_gallery_image_not_found`
  `product_id` inválido → 404.

#### DELETE /shop/products/{id}/gallery/{image_id}

- [ ] `test_delete_gallery_image_success`
  Admin remove imagem da galeria → 204. GET /shop/mine não inclui a imagem.

- [ ] `test_delete_gallery_image_not_found`
  `image_id` não existe → 404.

- [ ] `test_delete_gallery_image_wrong_product`
  `image_id` pertence a outro produto → 404.

- [ ] `test_delete_gallery_image_cross_company`
  Admin da empresa A tenta deletar imagem da empresa B → 404.

- [ ] `test_delete_gallery_image_non_admin_blocked`
  Vendedor → 403.

#### PUT /shop/products/{id}/gallery/reorder

- [ ] `test_reorder_gallery_success`
  Admin reordena 3 imagens: `[3, 1, 2]` → 200. GET /shop/mine retorna
  galeria na nova ordem.

- [ ] `test_reorder_gallery_incomplete_list`
  Admin envia apenas `[1, 2]` para 3 imagens → 422. Mensagem indica
  que todos os IDs devem ser incluídos.

- [ ] `test_reorder_gallery_invalid_id`
  Admin inclui ID inexistente → 422.

- [ ] `test_reorder_gallery_cross_company`
  Admin inclui ID de imagem de outra empresa → 422.

- [ ] `test_reorder_gallery_non_admin_blocked`
  Influenciador → 403.

#### Fluxo completo

- [ ] `test_shop_full_media_flow`
  1. Admin faz upload de logo, hero
  2. Admin cria categoria com imagem
  3. Admin cria produto com imagem principal + 2 imagens na galeria
  4. GET /shop/mine → todas as mídias com URLs públicas
  5. Admin reordena galeria → nova ordem confirmada
  6. Admin deleta 1 imagem da galeria → removida
  7. Admin substitui logo → logo antiga não aparece mais
  8. GET /shop/mine → estado final consistente

---

## Dependências de Infraestrutura

- **Object storage mock** para testes E2E: usar `moto` (S3 mock) ou
  dependency override que grava em `/tmp/test-uploads/` com limpeza
  automática após cada teste
- **Conftest fixture:** `mock_object_storage` que provê um bucket
  temporário isolado por teste
