---
tags: [skill, architecture, cloudinary]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Cloudinary]
---

# Cloudinary

## Overview

Cloudinary é uma plataforma de gerenciamento de mídia na nuvem que oferece upload, armazenamento, transformação e entrega de imagens e vídeos via CDN global. Integra-se ao [[media-pipeline]] como camada de processamento e distribuição, eliminando a necessidade de infraestrutura própria de media serving. Comparado ao armazenamento direto em [[s3-storage-patterns]], o Cloudinary adiciona transformações on-the-fly e CDN nativa sem configuração adicional.

> [!info] Quando usar Cloudinary vs S3 puro
> Use Cloudinary quando precisar de transformações dinâmicas (resize, crop, format conversion) sem pre-processing. Use [[s3-storage-patterns]] direto quando o armazenamento for o único requisito e o custo por transformação for proibitivo.

## Core Concepts

### Upload API

**Signed Upload** — requer assinatura HMAC-SHA1 gerada no backend:

```python
# fastapi + cloudinary
import cloudinary
import cloudinary.uploader
import hashlib, time

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
)

def generate_upload_signature(params: dict) -> dict:
    timestamp = int(time.time())
    params_to_sign = {**params, "timestamp": timestamp}
    # Sort keys alphabetically, exclude api_key and file
    sorted_params = "&".join(
        f"{k}={v}" for k, v in sorted(params_to_sign.items())
        if k not in ("api_key", "file", "resource_type")
    )
    signature_string = sorted_params + settings.CLOUDINARY_API_SECRET
    signature = hashlib.sha1(signature_string.encode()).hexdigest()
    return {
        "signature": signature,
        "timestamp": timestamp,
        "api_key": settings.CLOUDINARY_API_KEY,
        "cloud_name": settings.CLOUDINARY_CLOUD_NAME,
    }
```

**Unsigned Upload com Upload Presets** — para uploads diretos do browser sem expor credenciais. Configure o preset no dashboard com restrições de tamanho, formato e pasta.

**Direct Upload do Backend:**

```python
result = cloudinary.uploader.upload(
    file,
    folder="products/2026",
    public_id=f"product_{product_id}",
    overwrite=True,
    resource_type="auto",          # detecta image/video/raw automaticamente
    eager=[
        {"width": 800, "crop": "scale", "format": "webp"},
        {"width": 400, "crop": "thumb", "gravity": "face"},
    ],
    eager_async=True,              # processa em background
    eager_notification_url="https://api.example.com/webhooks/cloudinary",
    tags=["product", "active"],
)
public_id = result["public_id"]
secure_url = result["secure_url"]
```

### Transformações On-the-Fly

A URL de transformação é composta: `https://res.cloudinary.com/{cloud}/image/upload/{transformations}/{public_id}`

```
# Resize + WebP + qualidade automática
https://res.cloudinary.com/mycloud/image/upload/w_800,h_600,c_fill,f_auto,q_auto/products/shoe_001

# Crop inteligente por rosto + border radius + overlay de texto
https://res.cloudinary.com/mycloud/image/upload/w_400,c_thumb,g_face,r_20/l_text:Arial_24_bold:Sale/fl_layer_apply,g_south_east/products/shoe_001

# Chaining: resize → sharpen → watermark
https://res.cloudinary.com/mycloud/image/upload/w_1200/e_sharpen:100/l_logo,o_40,g_south_east/products/shoe_001
```

**Parâmetros críticos:**
- `f_auto` — entrega WebP para browsers compatíveis, AVIF quando suportado
- `q_auto` — qualidade adaptativa baseada em análise de conteúdo (q_auto:best, q_auto:good, q_auto:eco, q_auto:low)
- `c_fill` / `c_crop` / `c_thumb` / `c_scale` / `c_fit` / `c_lfill` — modos de crop
- `g_auto` / `g_face` / `g_faces` / `g_custom` — gravity para cropping inteligente
- `dpr_auto` — device pixel ratio automático via Client Hints

### Named Transformations

Encapsulam sequências complexas para reutilização e controle de versão:

```python
# Criar via API
cloudinary.api.create_transformation(
    "product_thumbnail",
    {"width": 400, "height": 400, "crop": "fill", "gravity": "auto",
     "format": "webp", "quality": "auto:good", "fetch_format": "auto"}
)

# Uso na URL
# /image/upload/t_product_thumbnail/products/shoe_001
```

### Signed URLs (Security)

Para ativos privados ou com acesso temporário:

```python
from cloudinary.utils import cloudinary_url

url, options = cloudinary_url(
    "private/document_001.pdf",
    resource_type="raw",
    type="authenticated",
    sign_url=True,
    expires_at=int(time.time()) + 3600,  # 1 hora
)
```

> [!warning] Nunca exponha API Secret no frontend
> O API Secret é usado para assinar URLs e deve existir apenas no servidor. Para uploads frontend, use signed upload parameters gerados no backend ou upload presets sem assinatura com restrições adequadas.

## Patterns

### Responsive Breakpoints Automáticos

```python
result = cloudinary.uploader.upload(
    image_file,
    responsive_breakpoints={
        "create_derived": True,
        "bytes_step": 20000,
        "min_width": 200,
        "max_width": 1920,
        "transformation": {"crop": "fill", "aspect_ratio": "16:9", "format": "webp"},
    }
)
# Retorna array de breakpoints com width, height, bytes, url para srcset
breakpoints = result["responsive_breakpoints"][0]["breakpoints"]
srcset = ", ".join(f"{bp['secure_url']} {bp['width']}w" for bp in breakpoints)
```

### Webhook para Eager Transformations

```python
# FastAPI endpoint para processar notificações do Cloudinary
from fastapi import Request, Header
import hashlib, hmac

@router.post("/webhooks/cloudinary")
async def cloudinary_webhook(
    request: Request,
    x_cld_signature: str = Header(...),
    x_cld_timestamp: str = Header(...),
):
    body = await request.body()
    # Validar assinatura
    payload_to_sign = body.decode() + x_cld_timestamp
    expected = hmac.new(
        settings.CLOUDINARY_API_SECRET.encode(),
        payload_to_sign.encode(),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(expected, x_cld_signature):
        raise HTTPException(status_code=401)

    data = await request.json()
    if data["notification_type"] == "eager":
        # Eager transformations concluídas — atualizar DB
        await update_asset_variants(data["public_id"], data["eager"])
```

### Integração com Next.js

```typescript
// next.config.js
const nextConfig = {
  images: {
    loader: 'custom',
    loaderFile: './lib/cloudinary-loader.ts',
  },
}

// lib/cloudinary-loader.ts
export default function cloudinaryLoader({
  src, width, quality,
}: { src: string; width: number; quality?: number }) {
  const params = ['f_auto', 'c_limit', `w_${width}`, `q_${quality ?? 'auto'}`]
  return `https://res.cloudinary.com/${process.env.NEXT_PUBLIC_CLOUDINARY_CLOUD_NAME}/image/upload/${params.join(',')}/${src}`
}
```

Veja [[nextjs]] para configuração do Image component e [[fastapi]] para endpoints de upload.

## Gotchas

> [!danger] Transformações criam derived assets — custo acumulativo
> Cada combinação única de transformação gera um derived asset armazenado. Com muitas variantes dinâmicas, o custo de storage explode. Use Named Transformations para controlar o número de variantes e habilite "Derived images deletion" para limpeza automática.

> [!warning] Rate limits na Upload API
> O plano gratuito tem limites de créditos de transformação. Eager transformations síncronas bloqueiam a resposta — prefira `eager_async=True` com webhook notification para produção.

> [!tip] CDN Cache Invalidation é cara
> Invalidar cache no Cloudinary CDN (via `cloudinary.api.delete_resources()` ou explicit invalidation) tem custo. Prefira versioning de public_id (e.g., `product_001_v2`) em vez de overwrite + invalidation.

**Pasta vs. Tags:** Pastas são hierarquias de public_id (`folder/subfolder/file`). Tags são metadados planos para busca. Use pastas para organização estrutural e tags para filtros transversais.

**Resource Types:** `image`, `video`, `raw` — arquivos PDF e outros binários precisam de `resource_type="raw"` explícito.

## Snippets

```python
# Upload com moderação de conteúdo (AWS Rekognition integrado)
result = cloudinary.uploader.upload(
    file,
    moderation="aws_rek",
    detection="object_detection",
)
if result.get("moderation", [{}])[0].get("status") == "rejected":
    raise ValueError("Conteúdo rejeitado pela moderação")
```

```python
# Deletar assets por tag (bulk cleanup)
cloudinary.api.delete_resources_by_tag("temp_upload")

# Listar com cursor para paginação
result = cloudinary.api.resources(
    type="upload", prefix="products/", max_results=100, next_cursor=cursor
)
```

## References

- [Cloudinary Upload API Docs](https://cloudinary.com/documentation/image_upload_api_reference)
- [Transformation Reference](https://cloudinary.com/documentation/transformation_reference)
- [Named Transformations](https://cloudinary.com/documentation/named_transformations)
- [Signed URLs](https://cloudinary.com/documentation/advanced_url_delivery_options#generating_delivery_urls_using_the_sdks)

## Related

- [[media-pipeline]] — pipeline completo de upload → process → serve
- [[s3-storage-patterns]] — armazenamento de origem antes do Cloudinary
- [[dns-and-cdn]] — CDN delivery e edge caching
- [[fastapi]] — backend para signed uploads e webhooks
- [[nextjs]] — integração com Image component
