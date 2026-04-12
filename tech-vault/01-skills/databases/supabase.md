---
tags: [skill, databases, supabase]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Supabase]
---

# Supabase

## Overview

Supabase é uma plataforma open-source que empacota [[postgresql]] com Auth, Realtime, Storage, Edge Functions e uma API REST auto-gerada (PostgREST). O diferencial técnico é que tudo roda sobre Postgres real — sem abstrações proprietárias que limitam acesso direto ao banco.

Integra nativamente com [[nextjs]] e [[react]] via client SDK e, no backend, complementa [[fastapi]] quando você precisa de lógica além do que PostgREST fornece. Segredos e variáveis de ambiente são gerenciados com boas práticas de [[secrets-management]].

---

## Core Concepts

### Row Level Security (RLS)

RLS é o mecanismo central de segurança do Supabase — policies definidas no banco garantem que cada usuário só acessa seus próprios dados, independente de como a API é chamada.

```sql
-- Habilitar RLS na tabela
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- Policy: usuário só vê seus próprios posts
CREATE POLICY "users_own_posts_select"
ON posts FOR SELECT
USING (auth.uid() = user_id);

-- Policy: usuário só insere com seu próprio user_id
CREATE POLICY "users_own_posts_insert"
ON posts FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- Policy: tenant isolation (multi-tenant SaaS)
CREATE POLICY "tenant_isolation"
ON documents FOR ALL
USING (
  tenant_id = (
    SELECT tenant_id FROM profiles
    WHERE id = auth.uid()
  )
);

-- Policy com role check via JWT claims
CREATE POLICY "admins_read_all"
ON audit_logs FOR SELECT
USING (
  (auth.jwt() ->> 'role') = 'admin'
  OR auth.uid() = actor_id
);
```

> [!warning] RLS com Service Role Key
> A `service_role` key bypassa RLS completamente. Nunca exponha essa key no frontend. Use apenas em Edge Functions ou backend com acesso restrito.

### Auth — JWT e OAuth

```typescript
// Client-side: sign in with OAuth
import { createClient } from '@supabase/supabase-js'
const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

// OAuth redirect
const { data, error } = await supabase.auth.signInWithOAuth({
  provider: 'github',
  options: {
    redirectTo: `${window.location.origin}/auth/callback`,
    scopes: 'repo read:user'
  }
})

// Magic link (passwordless)
await supabase.auth.signInWithOtp({
  email: 'user@example.com',
  options: { emailRedirectTo: 'https://app.com/auth/confirm' }
})

// Get session + access token (JWT)
const { data: { session } } = await supabase.auth.getSession()
// session.access_token is a JWT signed by Supabase
// session.expires_at — refresh before expiry

// Listen to auth state changes
supabase.auth.onAuthStateChange((event, session) => {
  if (event === 'TOKEN_REFRESHED') { /* update stored token */ }
  if (event === 'SIGNED_OUT') { /* redirect to login */ }
})
```

**Custom JWT Claims** — enrich the JWT with app-specific data via database function hook:

```sql
-- Called automatically before JWT is issued
CREATE OR REPLACE FUNCTION public.custom_access_token_hook(event JSONB)
RETURNS JSONB LANGUAGE plpgsql STABLE AS $$
DECLARE
  claims JSONB;
  user_role TEXT;
BEGIN
  SELECT role INTO user_role FROM profiles WHERE id = (event ->> 'user_id')::UUID;
  claims := event -> 'claims';
  claims := jsonb_set(claims, '{role}', to_jsonb(user_role));
  RETURN jsonb_set(event, '{claims}', claims);
END;
$$;
```

### Realtime — Channels, Presence, Broadcast

```typescript
// Postgres Changes — listen to DB mutations via logical replication
const channel = supabase
  .channel('order-updates')
  .on(
    'postgres_changes',
    {
      event: 'UPDATE',
      schema: 'public',
      table: 'orders',
      filter: `customer_id=eq.${userId}`  // server-side filter
    },
    (payload) => {
      console.log('Order updated:', payload.new)
    }
  )
  .subscribe()

// Broadcast — ephemeral messages between clients (no DB persistence)
const gameChannel = supabase.channel('game:room:42')
  .on('broadcast', { event: 'player_move' }, ({ payload }) => {
    updateGameState(payload)
  })
  .subscribe()

await gameChannel.send({
  type: 'broadcast',
  event: 'player_move',
  payload: { x: 100, y: 200, player_id: userId }
})

// Presence — track online users with sync
const presenceChannel = supabase.channel('room:lobby')
  .on('presence', { event: 'sync' }, () => {
    const state = presenceChannel.presenceState()
    // { 'userId1': [{ online_at, user_id, ... }], ... }
    setOnlineUsers(Object.keys(state))
  })
  .subscribe(async (status) => {
    if (status === 'SUBSCRIBED') {
      await presenceChannel.track({ user_id: userId, online_at: new Date().toISOString() })
    }
  })
```

### Edge Functions (Deno)

Edge Functions rodam no Deno runtime na borda (Cloudflare Workers-like), próximas ao usuário.

```typescript
// supabase/functions/process-webhook/index.ts
import { createClient } from 'jsr:@supabase/supabase-js@2'
import { corsHeaders } from '../_shared/cors.ts'

Deno.serve(async (req: Request) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // Service role client inside Edge Function (bypasses RLS when needed)
    const supabaseAdmin = createClient(
      Deno.env.get('SUPABASE_URL')!,
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    )

    // User-context client (respects RLS)
    const authHeader = req.headers.get('Authorization')!
    const supabaseUser = createClient(
      Deno.env.get('SUPABASE_URL')!,
      Deno.env.get('SUPABASE_ANON_KEY')!,
      { global: { headers: { Authorization: authHeader } } }
    )

    const body = await req.json()

    // Verify webhook signature
    const signature = req.headers.get('stripe-signature')
    const event = Stripe.webhooks.constructEvent(body, signature, Deno.env.get('STRIPE_WEBHOOK_SECRET')!)

    if (event.type === 'checkout.session.completed') {
      await supabaseAdmin.from('subscriptions').upsert({
        user_id: event.data.object.client_reference_id,
        stripe_subscription_id: event.data.object.subscription,
        status: 'active'
      })
    }

    return new Response(JSON.stringify({ ok: true }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), { status: 400 })
  }
})
```

```bash
# Deploy edge function
supabase functions deploy process-webhook --no-verify-jwt

# Set secrets
supabase secrets set STRIPE_WEBHOOK_SECRET=whsec_...
```

### Storage — Buckets, Policies, Transformations

```typescript
// Create bucket with RLS-like policies
// (configured in dashboard or SQL)

// Upload file
const { data, error } = await supabase.storage
  .from('avatars')
  .upload(`${userId}/avatar.webp`, file, {
    cacheControl: '3600',
    upsert: true,
    contentType: 'image/webp'
  })

// Get public URL with image transformation (Pro plan)
const { data: { publicUrl } } = supabase.storage
  .from('avatars')
  .getPublicUrl(`${userId}/avatar.webp`, {
    transform: {
      width: 200,
      height: 200,
      resize: 'cover',
      format: 'webp',
      quality: 80
    }
  })

// Signed URL for private buckets (expires in 1 hour)
const { data: { signedUrl } } = await supabase.storage
  .from('private-docs')
  .createSignedUrl(`${userId}/contract.pdf`, 3600)
```

```sql
-- Storage policy: users access only their own files
CREATE POLICY "user_owns_avatar"
ON storage.objects FOR ALL
USING (
  bucket_id = 'avatars' AND
  (storage.foldername(name))[1] = auth.uid()::text
);
```

### Database Migrations

```bash
# Initialize local Supabase
supabase init
supabase start  # starts local stack via Docker

# Create migration
supabase migration new add_user_profiles

# Apply migrations locally
supabase db push

# Pull schema from remote to local
supabase db pull

# Generate TypeScript types from schema
supabase gen types typescript --local > src/types/supabase.ts
```

### PostgREST Advanced Queries

```bash
# Nested selects (JOIN)
GET /rest/v1/posts?select=id,title,author:profiles(name,avatar_url)&order=created_at.desc&limit=20

# Filter with operators
GET /rest/v1/products?price=lte.100&category=in.(electronics,gadgets)&stock=gt.0

# Full-text search
GET /rest/v1/articles?fts=plfts(english).postgresql%20performance

# Upsert
POST /rest/v1/user_settings
Prefer: resolution=merge-duplicates
```

---

## Gotchas

> [!danger] RLS Desabilitado por Padrão
> Tabelas novas criadas no Supabase não têm RLS habilitado. Qualquer dado é acessível via `anon` key se não houver policies. Habilite RLS em toda tabela imediatamente após criar.

> [!warning] Realtime e Tabelas Grandes
> Postgres Changes usa logical replication — em tabelas com alto write throughput, o replication lag pode crescer. Filtre sempre por `filter: user_id=eq.${id}` para reduzir mensagens enviadas ao cliente.

> [!tip] TypeScript Types Auto-Generation
> Rode `supabase gen types typescript` após cada migration para manter os tipos sincronizados. Integre no CI para detectar type drift.

> [!warning] Edge Function Cold Starts
> Edge Functions têm cold start de 100-500ms. Para endpoints críticos de latência, use `--no-verify-jwt` e mantenha a função "warm" com pings periódicos ou use a opção `regionHint`.

> [!info] Self-hosting com Docker
> O `docker-compose.yml` oficial do Supabase inclui Postgres, PostgREST, GoTrue (Auth), Realtime, Storage e Kong (API gateway). Em produção self-hosted, configure `SITE_URL` e `JWT_SECRET` corretamente.

---

## References

- [Supabase Documentation](https://supabase.com/docs)
- [Row Level Security Guide](https://supabase.com/docs/guides/auth/row-level-security)
- [Edge Functions](https://supabase.com/docs/guides/functions)
- [Supabase Self-Hosting](https://supabase.com/docs/guides/self-hosting)

## Related

- [[postgresql]]
- [[nextjs]]
- [[react]]
- [[fastapi]]
- [[secrets-management]]
