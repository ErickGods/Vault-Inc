---
tags: [skill, architecture, media-pipeline]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Media Pipeline, Image Pipeline]
---

# Media Pipeline

## Overview

Um Media Pipeline é a cadeia completa de processamento de arquivos de mídia: do upload do cliente até a entrega otimizada via CDN. Engloba validação, processamento assíncrono, múltiplos formatos de saída, geração de thumbnails e lazy loading. A stack tipicamente combina [[cloudinary]] ou processamento próprio (Sharp/FFmpeg), armazenamento em [[s3-storage-patterns]], entrega via [[dns-and-cdn]], e backends em [[fastapi]] ou [[nextjs]]. Containerizado com [[docker]] para portabilidade.

> [!info] Build vs Buy
> Use [[cloudinary]] quando transformações on-the-fly e CDN integrada justificam o custo. Construa pipeline próprio com Sharp + S3 + CloudFront quando volume é alto, transformações são previsíveis e controle total é necessário.

## Core Concepts

### Fluxo End-to-End

```
Cliente → [1] Signed URL Request → Backend
                                      ↓
                               [2] Presigned PUT URL (S3 raw/)
                                      ↓
Cliente → [3] Upload direto → S3 raw/
                                      ↓
                               [4] S3 Event → SQS
                                      ↓
                               [5] Worker (Docker) ← consome fila
                                      ↓
                 ┌─────────────────────────────────┐
                 │ [6] Validate → Process → Store   │
                 │  • format check (magic bytes)    │
                 │  • virus scan                    │
                 │  • resize/convert (Sharp/FFmpeg) │
                 │  • generate variants             │
                 │  • upload to S3 processed/       │
                 └─────────────────────────────────┘
                                      ↓
                               [7] CDN invalidation (se necessário)
                                      ↓
                               [8] Webhook → Backend → DB update
                                      ↓
Cliente ← [9] Serve via CDN Edge ← CloudFront/Cloudflare
```

### Image Optimization com Sharp

Sharp é um wrapper Node.js para libvips — ordens de magnitude mais rápido que ImageMagick para processamento em lote:

```typescript
import sharp from 'sharp'
import { S3Client, GetObjectCommand, PutObjectCommand } from '@aws-sdk/client-s3'

const VARIANTS = [
  { suffix: 'lg',   width: 1920, quality: 85 },
  { suffix: 'md',   width: 1024, quality: 82 },
  { suffix: 'sm',   width: 512,  quality: 80 },
  { suffix: 'thumb',width: 200,  quality: 75, fit: 'cover' as const },
]

async function processImage(bucket: string, rawKey: string): Promise<void> {
  // 1. Download do S3
  const s3 = new S3Client({ region: process.env.AWS_REGION })
  const { Body } = await s3.send(new GetObjectCommand({ Bucket: bucket, Key: rawKey }))
  const inputBuffer = Buffer.from(await Body!.transformToByteArray())

  // 2. Extrair metadata sem decodificar pixels (muito rápido)
  const meta = await sharp(inputBuffer).metadata()
  if (!['jpeg','png','webp','gif','avif'].includes(meta.format ?? '')) {
    throw new Error(`Unsupported format: ${meta.format}`)
  }

  // 3. Processar variantes em paralelo
  const baseId = rawKey.replace('raw/', '').replace(/\.[^.]+$/, '')
  await Promise.all(VARIANTS.map(async (variant) => {
    const pipeline = sharp(inputBuffer)
      .resize({
        width: variant.width,
        fit: variant.fit ?? 'inside',
        withoutEnlargement: true,
      })
      .webp({ quality: variant.quality, effort: 4 })   // effort: 0 (fast) - 6 (slow)

    const buffer = await pipeline.toBuffer()
    await s3.send(new PutObjectCommand({
      Bucket: bucket,
      Key: `processed/${baseId}_${variant.suffix}.webp`,
      Body: buffer,
      ContentType: 'image/webp',
      CacheControl: 'public, max-age=31536000, immutable',
      Metadata: {
        'original-key': rawKey,
        'original-format': meta.format ?? 'unknown',
        'original-width': String(meta.width),
        'original-height': String(meta.height),
      },
    }))
  }))

  // 4. Gerar LQIP (Low Quality Image Placeholder)
  const lqip = await sharp(inputBuffer)
    .resize(20)
    .webp({ quality: 20 })
    .toBuffer()
  const lqipBase64 = `data:image/webp;base64,${lqip.toString('base64')}`
  // Armazenar lqipBase64 no DB junto com os URLs das variantes
}
```

### Video Transcoding com FFmpeg

```python
import subprocess
import json
from pathlib import Path

FFPROBE_CMD = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams"]
ENCODE_PROFILES = {
    "1080p": {"height": 1080, "vbitrate": "4000k", "abitrate": "192k"},
    "720p":  {"height": 720,  "vbitrate": "2500k", "abitrate": "128k"},
    "480p":  {"height": 480,  "vbitrate": "1000k", "abitrate": "96k"},
    "360p":  {"height": 360,  "vbitrate": "600k",  "abitrate": "64k"},
}

def probe_video(path: str) -> dict:
    result = subprocess.run(FFPROBE_CMD + [path], capture_output=True)
    data = json.loads(result.stdout)
    video_stream = next(s for s in data["streams"] if s["codec_type"] == "video")
    return {"width": video_stream["width"], "height": video_stream["height"],
            "duration": float(video_stream.get("duration", 0)),
            "codec": video_stream["codec_name"]}

def transcode_hls(input_path: str, output_dir: str, max_height: int = 1080) -> list[str]:
    """Gera HLS multi-bitrate (DASH-compatible)."""
    meta = probe_video(input_path)
    profiles = {k: v for k, v in ENCODE_PROFILES.items()
                if v["height"] <= min(meta["height"], max_height)}

    output_files = []
    for profile_name, params in profiles.items():
        output_path = f"{output_dir}/{profile_name}/index.m3u8"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            "ffmpeg", "-i", input_path,
            "-vf", f"scale=-2:{params['height']}",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-b:v", params["vbitrate"], "-maxrate", params["vbitrate"],
            "-bufsize", f"{int(params['vbitrate'][:-1]) * 2}k",
            "-c:a", "aac", "-b:a", params["abitrate"],
            "-hls_time", "6", "-hls_list_size", "0",
            "-hls_segment_filename", f"{output_dir}/{profile_name}/%03d.ts",
            "-f", "hls", output_path,
        ]
        subprocess.run(cmd, check=True)
        output_files.append(output_path)
    return output_files
```

### Thumbnail Generation e LQIP

```python
# Thumbnail com timestamp específico
def extract_thumbnail(video_path: str, timestamp: float = 5.0) -> bytes:
    cmd = [
        "ffmpeg", "-ss", str(timestamp), "-i", video_path,
        "-vframes", "1", "-vf", "scale=640:-2",
        "-f", "image2", "-vcodec", "libwebp", "pipe:1",
    ]
    result = subprocess.run(cmd, capture_output=True, check=True)
    return result.stdout  # bytes do WebP

# LQIP via Sharp (Node) — já mostrado acima
# Alternativa Python: Pillow
from PIL import Image
import io, base64

def generate_lqip_python(image_bytes: bytes) -> str:
    img = Image.open(io.BytesIO(image_bytes))
    img.thumbnail((20, 20), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="WEBP", quality=20)
    return f"data:image/webp;base64,{base64.b64encode(buf.getvalue()).decode()}"
```

## Patterns

### Responsive Images com srcset

```typescript
// next.js component com LQIP blur placeholder
interface MediaImageProps {
  src: string           // base public_id ou S3 key
  lqip: string          // base64 data URI
  variants: { url: string; width: number }[]
  alt: string
}

export function MediaImage({ src, lqip, variants, alt }: MediaImageProps) {
  const srcSet = variants.map(v => `${v.url} ${v.width}w`).join(', ')
  return (
    <img
      src={variants.find(v => v.width === 1024)?.url ?? variants[0].url}
      srcSet={srcSet}
      sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 800px"
      alt={alt}
      loading="lazy"
      decoding="async"
      style={{
        backgroundImage: `url(${lqip})`,
        backgroundSize: 'cover',
      }}
    />
  )
}
```

### Queue-based Processing

Workers consomem eventos S3 via SQS para processamento assíncrono desacoplado:

```python
# Worker em FastAPI background task ou processo standalone
import boto3, json, time

sqs = boto3.client("sqs", region_name="us-east-1")

def poll_and_process():
    while True:
        messages = sqs.receive_message(
            QueueUrl=QUEUE_URL,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=20,        # long polling
            VisibilityTimeout=300,     # 5 min para processar
        ).get("Messages", [])

        for msg in messages:
            try:
                body = json.loads(msg["Body"])
                s3_event = json.loads(body["Message"]) if "Message" in body else body
                for record in s3_event.get("Records", []):
                    bucket = record["s3"]["bucket"]["name"]
                    key = record["s3"]["object"]["key"]
                    process_media(bucket, key)

                sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=msg["ReceiptHandle"])
            except Exception as e:
                # Não deleta — visibilidade expira e retorna à fila (até DLQ)
                logger.error(f"Processing failed for {msg['MessageId']}: {e}")
```

### Content Moderation

```python
rekognition = boto3.client("rekognition", region_name="us-east-1")

def moderate_image(bucket: str, key: str) -> bool:
    """Retorna True se imagem é segura."""
    response = rekognition.detect_moderation_labels(
        Image={"S3Object": {"Bucket": bucket, "Name": key}},
        MinConfidence=75,
    )
    unsafe_categories = {
        "Explicit Nudity", "Violence", "Visually Disturbing", "Hate Symbols"
    }
    flagged = [
        label for label in response["ModerationLabels"]
        if label["ParentName"] in unsafe_categories or label["Name"] in unsafe_categories
    ]
    return len(flagged) == 0
```

## Gotchas

> [!danger] Sharp não é thread-safe em todos os cenários — use worker pool
> Em processos Node.js com alta concorrência, Sharp pode travar ao processar muitos arquivos simultaneamente em pipelines de streaming. Use `worker_threads` ou Piscina para isolamento.

> [!warning] FFmpeg em Lambda tem limitações de tamanho e tempo de execução
> Lambda tem 15 min de timeout e 10 GB de ephemeral storage. Para vídeos longos, prefira AWS MediaConvert ou ECS Fargate task disparado por evento.

> [!tip] Sempre valide magic bytes, nunca apenas extensão
> Um `.jpg` pode ser um executável. Use `python-magic` ou `file-type` (Node) para verificar o content-type real antes de processar.

```python
import magic  # python-magic

def validate_media_type(data: bytes) -> str:
    detected = magic.from_buffer(data, mime=True)
    allowed = {"image/jpeg", "image/png", "image/webp", "image/gif",
               "image/avif", "video/mp4", "video/quicktime"}
    if detected not in allowed:
        raise ValueError(f"Tipo não permitido: {detected}")
    return detected
```

## Snippets

```bash
# Docker image com FFmpeg + Sharp deps
FROM node:20-alpine AS base
RUN apk add --no-cache ffmpeg vips-dev python3 make g++
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev
COPY . .
CMD ["node", "worker.js"]
```

## References

- [Sharp Docs](https://sharp.pixelplumbing.com/)
- [FFmpeg HLS Encoding Guide](https://ffmpeg.org/ffmpeg-formats.html#hls-1)
- [AWS MediaConvert](https://docs.aws.amazon.com/mediaconvert/)
- [Rekognition Content Moderation](https://docs.aws.amazon.com/rekognition/latest/dg/moderation.html)
- [LQIP Pattern](https://web.dev/articles/lazy-loading-images)

## Related

- [[cloudinary]] — alternativa managed para transformações on-the-fly
- [[s3-storage-patterns]] — armazenamento de origem e processed assets
- [[dns-and-cdn]] — entrega via CloudFront/Cloudflare para edge caching
- [[fastapi]] — API de upload e webhook de notificação
- [[nextjs]] — consumo de imagens otimizadas com srcset e blur placeholder
- [[docker]] — containerização do worker de processamento
