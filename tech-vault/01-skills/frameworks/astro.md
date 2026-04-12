---
tags: [skill, frameworks, astro]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Astro]
---

# Astro

## Overview

Astro é o framework moderno para sites content-heavy que prioriza zero JavaScript no cliente por padrão. Sua arquitetura de **Islands** permite adicionar interatividade cirúrgica usando componentes de qualquer framework ([[react]], [[svelte]], Vue, etc.) sem comprometer a performance global. O resultado é HTML estático com hydration seletiva — o oposto de SPAs.

> [!info] Astro vs Next.js
> Enquanto [[nextjs]] é otimizado para apps full-stack com muita interatividade, Astro é ideal para sites de marketing, blogs, documentação e e-commerces com conteúdo predominantemente estático. A diferença no Lighthouse score pode ser de 30+ pontos.

Astro 4+ trouxe Content Collections tipadas, View Transitions nativas, e Astro DB. O sistema de adapters permite deploy em Node.js, Vercel, Cloudflare Workers e Netlify sem mudanças no código — ver [[deployment-strategies]]. [[typescript]] é suportado nativamente e integra com as Content Collections.

---

## Core Concepts

### Island Architecture

```astro
---
// src/pages/product/[id].astro
// This block runs on the server (or at build time)
import { getProduct } from "../lib/db"
import AddToCart from "../components/AddToCart.jsx"
import ReviewList from "../components/ReviewList.svelte"
import Header from "../components/Header.astro"  // pure Astro — no JS

const { id } = Astro.params
const product = await getProduct(id)
---

<html>
  <body>
    <!-- Pure HTML — zero JS -->
    <Header />
    <h1>{product.name}</h1>
    <p>{product.description}</p>

    <!-- Island: hydrates when visible (lazy) -->
    <ReviewList client:visible reviews={product.reviews} />

    <!-- Island: hydrates immediately on page load -->
    <AddToCart client:load productId={product.id} price={product.price} />
  </body>
</html>
```

### Client Directives

```astro
<!-- client:load — hydrate immediately (critical UI) -->
<ShoppingCart client:load />

<!-- client:idle — hydrate when browser is idle (requestIdleCallback) -->
<Recommendations client:idle />

<!-- client:visible — hydrate when enters viewport (IntersectionObserver) -->
<HeavyChart client:visible />

<!-- client:media — hydrate when media query matches -->
<MobileMenu client:media="(max-width: 768px)" />

<!-- client:only — skip SSR entirely, render only on client -->
<ThirdPartyWidget client:only="react" />
```

### Content Collections (Astro 4+)

```ts
// src/content/config.ts
import { defineCollection, z } from "astro:content"

const blog = defineCollection({
  type: "content",  // markdown/mdx
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    hero: z.string().optional(),
    tags: z.array(z.string()).default([]),
    draft: z.boolean().default(false),
  }),
})

const authors = defineCollection({
  type: "data",  // JSON/YAML
  schema: z.object({
    name: z.string(),
    bio: z.string(),
    avatar: z.string().url(),
    social: z.object({
      twitter: z.string().optional(),
      github: z.string().optional(),
    }),
  }),
})

export const collections = { blog, authors }
```

```astro
---
// src/pages/blog/[...slug].astro
import { getCollection, getEntry, render } from "astro:content"

export async function getStaticPaths() {
  const posts = await getCollection("blog", ({ data }) => !data.draft)
  return posts.map(post => ({
    params: { slug: post.slug },
    props: { post },
  }))
}

const { post } = Astro.props
const author = await getEntry("authors", post.data.authorId)
const { Content, headings } = await render(post)
---

<article>
  <h1>{post.data.title}</h1>
  <p>By {author.data.name}</p>
  <Content />
</article>
```

---

## Patterns

### SSR Adapters

```ts
// astro.config.mjs — switch between adapters
import { defineConfig } from "astro/config"
import node from "@astrojs/node"
import vercel from "@astrojs/vercel/serverless"
import cloudflare from "@astrojs/cloudflare"

export default defineConfig({
  output: "server",  // or "static" or "hybrid"
  adapter: node({ mode: "standalone" }),  // Self-host with Node
  // adapter: vercel(),                   // Vercel serverless
  // adapter: cloudflare(),               // Cloudflare Workers
})
```

### Hybrid Rendering

```astro
---
// src/pages/dashboard.astro
// This page is dynamic (SSR)
export const prerender = false

// src/pages/about.astro
// This page is static even in SSR mode
export const prerender = true
---
```

### Middleware

```ts
// src/middleware.ts
import { defineMiddleware, sequence } from "astro:middleware"

const auth = defineMiddleware(async (context, next) => {
  const token = context.cookies.get("auth-token")?.value

  if (!token && context.url.pathname.startsWith("/dashboard")) {
    return context.redirect("/login")
  }

  if (token) {
    context.locals.user = await validateToken(token)
  }

  return next()
})

const logger = defineMiddleware(async (context, next) => {
  const start = Date.now()
  const response = await next()
  console.log(`${context.request.method} ${context.url.pathname} — ${Date.now() - start}ms`)
  return response
})

export const onRequest = sequence(logger, auth)
```

```ts
// src/env.d.ts — type locals
declare namespace App {
  interface Locals {
    user: { id: string; email: string } | null
  }
}
```

### View Transitions

```astro
---
// src/layouts/Base.astro
import { ViewTransitions } from "astro:transitions"
---

<html>
  <head>
    <ViewTransitions />
  </head>
  <body>{Astro.slots.render("default")}</body>
</html>
```

```astro
<!-- Custom transition on specific element -->
<img
  src={product.image}
  transition:name={`product-image-${product.id}`}
  transition:animate="fade"
/>

<!-- Persist element across navigations (e.g., media player) -->
<audio src={track.url} transition:persist />
```

### Astro DB

```ts
// db/config.ts
import { defineDb, defineTable, column } from "astro:db"

const Comment = defineTable({
  columns: {
    id: column.number({ primaryKey: true }),
    postSlug: column.text(),
    author: column.text(),
    body: column.text(),
    createdAt: column.date({ default: NOW }),
  },
})

export default defineDb({ tables: { Comment } })

// Usage in .astro
import { db, Comment, eq } from "astro:db"

const comments = await db
  .select()
  .from(Comment)
  .where(eq(Comment.postSlug, slug))
  .orderBy(Comment.createdAt)
```

### Integration with React Islands

```tsx
// src/components/InteractiveMap.tsx — React island
import { useState, useEffect } from "react"

interface Props {
  center: [number, number]
  markers: Array<{ lat: number; lng: number; label: string }>
}

export function InteractiveMap({ center, markers }: Props) {
  const [selected, setSelected] = useState<string | null>(null)

  useEffect(() => {
    // Leaflet initialization (browser-only)
    const L = require("leaflet")
    const map = L.map("map").setView(center, 13)
    // ...
  }, [])

  return <div id="map" style={{ height: "400px" }} />
}
```

```astro
---
import { InteractiveMap } from "../components/InteractiveMap.tsx"
const locations = await fetchLocations()
---

<!-- client:visible — only hydrate when scrolled into view -->
<InteractiveMap
  client:visible
  center={[40.7128, -74.0060]}
  markers={locations}
/>
```

---

## Gotchas

> [!danger] Props para islands devem ser serializáveis
> Props passadas para components com `client:*` são serializadas como JSON. Funções, Promises, classes customizadas e referências circulares não podem ser passadas como props para islands.

```astro
<!-- ERRADO — função não pode ser serializada -->
<Counter client:load onIncrement={() => console.log("incremented")} />

<!-- CORRETO — passe dados primitivos; defina handlers dentro do componente -->
<Counter client:load initialCount={5} />
```

> [!warning] `client:only` pula SSR completamente
> Com `client:only`, o componente não gera HTML no servidor — a página renderiza um placeholder vazio. Isso afeta SEO e pode causar CLS (Cumulative Layout Shift). Use apenas para widgets que dependem obrigatoriamente do browser (mapas, editores, etc.).

> [!warning] View Transitions e JavaScript de terceiros
> Navegações com View Transitions não disparam `DOMContentLoaded` nem recarregam scripts globais. Scripts de analytics, chat widgets e similar precisam escutar o evento `astro:page-load`.

```js
document.addEventListener("astro:page-load", () => {
  // Re-initialize third-party scripts after navigation
  analytics.page()
})
```

---

## Snippets

### API Endpoint

```ts
// src/pages/api/submit.ts
import type { APIRoute } from "astro"

export const POST: APIRoute = async ({ request, locals }) => {
  const body = await request.json()

  if (!body.email) {
    return new Response(JSON.stringify({ error: "Email required" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    })
  }

  await locals.db.subscribers.create({ email: body.email })
  return new Response(JSON.stringify({ success: true }), { status: 201 })
}
```

### Image Optimization

```astro
---
import { Image, Picture } from "astro:assets"
import heroImage from "../assets/hero.jpg"
---

<Image src={heroImage} alt="Hero" width={1200} height={600} format="webp" />

<Picture
  src={heroImage}
  formats={["avif", "webp"]}
  alt="Hero"
  widths={[400, 800, 1200]}
  sizes="(max-width: 800px) 100vw, 1200px"
/>
```

---

## References

- [Astro Docs](https://docs.astro.build/)
- [Content Collections](https://docs.astro.build/en/guides/content-collections/)
- [Astro DB](https://docs.astro.build/en/guides/astro-db/)
- [View Transitions](https://docs.astro.build/en/guides/view-transitions/)

---

## Related

- [[react]]
- [[svelte]]
- [[typescript]]
- [[nextjs]]
- [[deployment-strategies]]
