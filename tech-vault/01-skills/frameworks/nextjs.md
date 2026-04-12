---
tags: [skill, frameworks, nextjs]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Next.js, NextJS]
---

# Next.js

## Overview

Next.js é o framework [[react]] full-stack mais adotado do ecossistema JavaScript. Com o App Router (introduzido no Next.js 13 e estabilizado no 14/15), a arquitetura mudou radicalmente: React Server Components são o padrão, Client Components são opt-in via `"use client"`, e Server Actions eliminam a necessidade de API routes para mutações simples. O resultado é menos JavaScript no cliente, streaming nativo e um modelo mental mais próximo do servidor.

> [!info] App Router vs Pages Router
> O Pages Router ainda é suportado e válido para projetos legados. O App Router não é apenas uma refatoração de rotas — ele implica uma mudança de paradigma sobre onde o código executa (servidor vs cliente).

Integra-se com [[typescript]] nativamente, com deploy preferencial na [[vercel-ai-sdk]] ecosystem e suporte completo a [[docker]] para self-hosting. Ver [[deployment-strategies]] para containerização e edge deployment.

---

## Core Concepts

### Server Components vs Client Components

```tsx
// app/users/page.tsx — Server Component (default)
// Runs on server only: can use secrets, DB, fs
import { db } from "@/lib/db"

export default async function UsersPage() {
  const users = await db.user.findMany()  // Direct DB call — no API needed
  return (
    <ul>
      {users.map(u => <li key={u.id}>{u.name}</li>)}
    </ul>
  )
}

// app/users/search.tsx — Client Component
"use client"
import { useState, useTransition } from "react"

export function SearchBar({ onSearch }: { onSearch: (q: string) => void }) {
  const [isPending, startTransition] = useTransition()
  return (
    <input
      onChange={e => startTransition(() => onSearch(e.target.value))}
      placeholder={isPending ? "Searching..." : "Search users"}
    />
  )
}
```

### Server Actions

```tsx
// app/actions/user.ts
"use server"
import { revalidatePath } from "next/cache"
import { redirect } from "next/navigation"
import { z } from "zod"

const CreateUserSchema = z.object({
  name: z.string().min(2),
  email: z.string().email(),
})

export async function createUser(formData: FormData) {
  const parsed = CreateUserSchema.safeParse({
    name: formData.get("name"),
    email: formData.get("email"),
  })
  if (!parsed.success) return { error: parsed.error.flatten() }

  await db.user.create({ data: parsed.data })
  revalidatePath("/users")
  redirect("/users")
}

// Usage in a Server Component form
export default function NewUserForm() {
  return (
    <form action={createUser}>
      <input name="name" />
      <input name="email" type="email" />
      <button type="submit">Create</button>
    </form>
  )
}
```

### Caching Layers

```tsx
// 1. Request Memoization — automatic within a single render tree
async function getUser(id: string) {
  // If called multiple times in one render, only one fetch occurs
  const res = await fetch(`/api/users/${id}`)
  return res.json()
}

// 2. Data Cache — persists across requests (opt out with cache: "no-store")
async function getProducts() {
  const res = await fetch("https://api.example.com/products", {
    next: { revalidate: 3600 },  // ISR: revalidate every hour
  })
  return res.json()
}

// 3. Full Route Cache — static generation at build time
export const dynamic = "force-static"  // or "force-dynamic"
export const revalidate = 60  // seconds

// 4. Router Cache — client-side prefetch cache (cannot be disabled easily)
```

---

## Patterns

### Parallel Routes & Intercepting Routes

```
app/
  layout.tsx
  @modal/        ← parallel route slot
    (.)photo/    ← intercepting route (same-level)
      [id]/
        page.tsx
  photo/
    [id]/
      page.tsx
  page.tsx
```

```tsx
// app/layout.tsx — receives @modal as a prop
export default function RootLayout({
  children,
  modal,
}: {
  children: React.ReactNode
  modal: React.ReactNode
}) {
  return (
    <html>
      <body>
        {children}
        {modal}
      </body>
    </html>
  )
}
```

### Streaming with Suspense

```tsx
import { Suspense } from "react"

export default function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>
      <Suspense fallback={<StatsSkeleton />}>
        <StatsPanel />   {/* slow async component */}
      </Suspense>
      <Suspense fallback={<FeedSkeleton />}>
        <ActivityFeed /> {/* another slow component */}
      </Suspense>
    </div>
  )
}
// Both panels stream independently — no waterfall
```

### Middleware

```ts
// middleware.ts (root level)
import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

export function middleware(request: NextRequest) {
  const token = request.cookies.get("auth-token")?.value

  if (!token && request.nextUrl.pathname.startsWith("/dashboard")) {
    return NextResponse.redirect(new URL("/login", request.url))
  }

  // Add custom headers
  const response = NextResponse.next()
  response.headers.set("X-Frame-Options", "DENY")
  return response
}

export const config = {
  matcher: ["/dashboard/:path*", "/api/:path*"],
}
```

### Route Handlers

```ts
// app/api/webhooks/stripe/route.ts
import { headers } from "next/headers"
import { NextRequest, NextResponse } from "next/server"
import Stripe from "stripe"

export async function POST(req: NextRequest) {
  const body = await req.text()
  const sig = (await headers()).get("stripe-signature")!

  let event: Stripe.Event
  try {
    event = stripe.webhooks.constructEvent(body, sig, process.env.STRIPE_SECRET!)
  } catch {
    return NextResponse.json({ error: "Invalid signature" }, { status: 400 })
  }

  switch (event.type) {
    case "checkout.session.completed":
      await handleCheckout(event.data.object)
      break
  }
  return NextResponse.json({ received: true })
}
```

### Image Optimization

```tsx
import Image from "next/image"

// next/image handles: WebP conversion, lazy loading, CLS prevention
export function ProductCard({ product }) {
  return (
    <Image
      src={product.imageUrl}
      alt={product.name}
      width={400}
      height={300}
      placeholder="blur"
      blurDataURL={product.blurHash}
      sizes="(max-width: 768px) 100vw, 33vw"
      priority={false}
    />
  )
}
```

---

## Gotchas

> [!danger] "use client" não significa "apenas client"
> Componentes marcados com `"use client"` ainda são renderizados no servidor para o HTML inicial (SSR). A diretiva indica que o componente também hidrata no cliente — não que é exclusivo do browser.

> [!warning] Server Actions e validação dupla
> Server Actions rodam no servidor mas são expostas como endpoints HTTP implícitos. Sempre valide inputs com Zod no servidor — nunca confie apenas na validação client-side.

```ts
// ERRADO — confia em dados sem validar
export async function deleteUser(id: string) {
  await db.user.delete({ where: { id } }) // qualquer id pode ser deletado!
}

// CORRETO — valida autenticação e autorização
export async function deleteUser(id: string) {
  const session = await getServerSession()
  if (!session || session.user.role !== "admin") throw new Error("Forbidden")
  await db.user.delete({ where: { id } })
}
```

> [!warning] Cache de dados e `revalidatePath`
> `revalidatePath` invalida o Full Route Cache, mas não garante que outros usuários vejam dados frescos imediatamente se você usa CDN em frente ao Next.js. Combine com `Cache-Control: no-cache` em headers para dados críticos.

---

## Snippets

### generateMetadata dinâmico

```tsx
export async function generateMetadata({ params }: { params: { id: string } }) {
  const product = await getProduct(params.id)
  return {
    title: product.name,
    description: product.description,
    openGraph: {
      images: [{ url: product.imageUrl }],
    },
  }
}
```

### Loading UI com skeleton

```tsx
// app/dashboard/loading.tsx — automatically shown during navigation
export default function DashboardSkeleton() {
  return (
    <div className="animate-pulse space-y-4">
      <div className="h-8 bg-gray-200 rounded w-1/3" />
      <div className="h-32 bg-gray-200 rounded" />
    </div>
  )
}
```

### useOptimistic para mutations

```tsx
"use client"
import { useOptimistic, useTransition } from "react"

export function LikeButton({ post }) {
  const [optimisticLikes, addOptimisticLike] = useOptimistic(
    post.likes,
    (state, increment: number) => state + increment,
  )
  const [, startTransition] = useTransition()

  return (
    <button onClick={() => {
      startTransition(async () => {
        addOptimisticLike(1)
        await likePost(post.id)
      })
    }}>
      {optimisticLikes} likes
    </button>
  )
}
```

---

## References

- [Next.js App Router Docs](https://nextjs.org/docs/app)
- [Caching in Next.js](https://nextjs.org/docs/app/building-your-application/caching)
- [Server Actions](https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions-and-mutations)

---

## Related

- [[react]]
- [[typescript]]
- [[vercel-ai-sdk]]
- [[docker]]
- [[deployment-strategies]]
