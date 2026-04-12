---
tags: [reference, regex]
status: active
level: advanced
updated: 2026-04-05
aliases: [Regex Cheatsheet, Regular Expressions]
created: 2026-04-05
---

# Regex Cheatsheet

Referência rápida de expressões regulares para uso com [[python]], [[typescript]], [[bash-snippets]], [[git-cheatsheet]] e análise de algoritmos em [[big-o-notation]].

---

## Quantificadores

| Padrão | Descrição | Exemplo | Match |
|--------|-----------|---------|-------|
| `*` | Zero ou mais | `ab*c` | `ac`, `abc`, `abbc` |
| `+` | Um ou mais | `ab+c` | `abc`, `abbc` |
| `?` | Zero ou um (opcional) | `colou?r` | `color`, `colour` |
| `{n}` | Exatamente n | `\d{4}` | `2024` |
| `{n,}` | Pelo menos n | `\w{3,}` | `foo`, `hello` |
| `{n,m}` | Entre n e m | `\d{2,4}` | `12`, `123`, `1234` |
| `*?` | Zero ou mais (lazy) | `<.*?>` | `<b>` em `<b>text</b>` |
| `+?` | Um ou mais (lazy) | `".+?"` | `"a"` em `"a" and "b"` |
| `??` | Zero ou um (lazy) | `https??` | `http` antes de `https` |

> [!tip] Greedy vs Lazy
> Por padrão, quantificadores são **greedy** (consomem o máximo possível). Adicione `?` para torná-los **lazy** (consomem o mínimo possível). Ex: `<.+>` em `<a><b>` retorna `<a><b>`, enquanto `<.+?>` retorna `<a>`.

---

## Grupos

| Padrão | Tipo | Descrição | Exemplo |
|--------|------|-----------|---------|
| `(abc)` | Capturante | Captura e numera o grupo | `(foo)(bar)` → grupo 1: `foo` |
| `(?:abc)` | Não-capturante | Agrupa sem capturar | `(?:foo|bar)+` |
| `(?P<name>abc)` | Nomeado (Python) | Grupo com nome | `(?P<year>\d{4})` |
| `(?<name>abc)` | Nomeado (JS/PCRE) | Grupo com nome | `(?<year>\d{4})` |
| `\1`, `\2` | Backreference | Referência a grupo capturado | `(\w+)\s\1` → palavras repetidas |
| `(?P=name)` | Backreference nomeada | Referência por nome (Python) | `(?P<q>['"]).*(?P=q)` |
| `(?>abc)` | Atômico | Grupo sem backtracking | `(?>a*)a` nunca dá match |

---

## Lookahead & Lookbehind

| Padrão | Tipo | Descrição | Exemplo |
|--------|------|-----------|---------|
| `(?=...)` | Lookahead positivo | O que vem a frente existe | `\d+(?= dólares)` |
| `(?!...)` | Lookahead negativo | O que vem a frente NÃO existe | `foo(?!bar)` |
| `(?<=...)` | Lookbehind positivo | O que vem atrás existe | `(?<=\$)\d+` |
| `(?<!...)` | Lookbehind negativo | O que vem atrás NÃO existe | `(?<!\$)\d+` |

```python
import re

# Lookahead: encontrar número seguido de "USD"
pattern = r'\d+(?=\s?USD)'
re.findall(pattern, "100 USD e 200 BRL")  # ['100']

# Lookbehind: extrair valor após "$"
pattern = r'(?<=\$)\d+\.?\d*'
re.findall(pattern, "Total: $42.50")  # ['42.50']

# Lookahead negativo: "foo" não seguido de "bar"
re.findall(r'foo(?!bar)', "foobar fooqwe")  # ['foo'] (apenas o segundo)
```

---

## Character Classes

| Padrão | Descrição | Equivalente |
|--------|-----------|-------------|
| `\d` | Dígito decimal | `[0-9]` |
| `\D` | Não-dígito | `[^0-9]` |
| `\w` | Alfanumérico + underscore | `[a-zA-Z0-9_]` |
| `\W` | Não-word char | `[^a-zA-Z0-9_]` |
| `\s` | Espaço em branco | `[ \t\n\r\f\v]` |
| `\S` | Não-espaço | `[^ \t\n\r\f\v]` |
| `\b` | Word boundary | Posição entre `\w` e `\W` |
| `\B` | Non-word boundary | Oposto de `\b` |
| `.` | Qualquer char exceto `\n` | (com flag `s`, inclui `\n`) |
| `[abc]` | Qualquer de a, b, c | — |
| `[^abc]` | Nenhum de a, b, c | — |
| `[a-z]` | Range de a até z | — |
| `[a-zA-Z]` | Letras maiúsculas e minúsculas | — |

---

## Anchors & Assertions

| Padrão | Descrição | Exemplo |
|--------|-----------|---------|
| `^` | Início da string/linha | `^Hello` |
| `$` | Fim da string/linha | `world$` |
| `\A` | Início absoluto da string | `\Afoo` (ignora modo multiline) |
| `\Z` | Fim absoluto da string | `bar\Z` |
| `\b` | Word boundary | `\bword\b` |
| `\B` | Non-word boundary | `\Bion` em "motion" |

---

## Flags

| Flag | Python | JS | Descrição |
|------|--------|----|-----------|
| Case insensitive | `re.I` ou `(?i)` | `i` | Ignora maiúsculas/minúsculas |
| Multiline | `re.M` ou `(?m)` | `m` | `^` e `$` para cada linha |
| Dotall | `re.S` ou `(?s)` | `s` | `.` inclui `\n` |
| Verbose | `re.X` ou `(?x)` | — | Permite espaços e comentários |
| Unicode | `re.U` | `u` | Modo Unicode (padrão no Python 3) |
| Global | — | `g` | Busca todas as ocorrências |
| Sticky | — | `y` | Match apenas na posição atual |

```python
# Verbose mode: regex legível com comentários
pattern = re.compile(r"""
    ^                   # início da string
    (?P<area>\d{2})     # código de área (2 dígitos)
    [\s\-.]?            # separador opcional
    (?P<prefix>\d{4,5}) # prefixo
    [\s\-.]?            # separador opcional
    (?P<line>\d{4})     # número final
    $                   # fim da string
""", re.VERBOSE)
```

---

## Padrões Comuns

### Email

```regex
^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$
```

| Parte | Descrição |
|-------|-----------|
| `[a-zA-Z0-9._%+\-]+` | Local part (antes do @) |
| `@` | Arroba literal |
| `[a-zA-Z0-9.\-]+` | Domínio |
| `\.[a-zA-Z]{2,}` | TLD (2+ letras) |

### URL

```regex
^https?://(?:www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_+.~#?&/=]*)$
```

### Endereço IP (IPv4)

```regex
^(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)$
```

### Semver (Versionamento Semântico)

```regex
^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<pre>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+(?P<build>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$
```

Exemplo: `1.2.3`, `2.0.0-alpha.1`, `1.0.0+build.42`

### Data (YYYY-MM-DD)

```regex
^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$
```

### Telefone Brasileiro

```regex
^(?:\+55\s?)?(?:\(?\d{2}\)?[\s\-]?)(?:9\d{4}|[2-8]\d{3})[\s\-]?\d{4}$
```

Exemplos: `(11) 98765-4321`, `+55 11 987654321`, `11987654321`

### UUID

```regex
^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$
```

### Cartão de Crédito (mascarar)

```regex
# Para substituir: re.sub(r'\b(\d{4})\d{8}(\d{4})\b', r'\1 **** **** \2', text)
\b(\d{4})\d{8}(\d{4})\b
```

### JWT Token

```regex
^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$
```

---

## Exemplos Python

```python
import re

# Compilar para reusar (mais eficiente)
EMAIL_RE = re.compile(r'^[a-zA-Z0-9._%+\-]+@[\w\-]+\.[a-zA-Z]{2,}$', re.I)

def validate_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email))

# Extrair todos os grupos nomeados
DATE_RE = re.compile(r'(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})')

def parse_date(text: str) -> dict | None:
    m = DATE_RE.search(text)
    return m.groupdict() if m else None

# Substituição com função
def mask_cpf(text: str) -> str:
    return re.sub(r'(\d{3})\.\d{3}\.\d{3}-(\d{2})', r'\1.***.***/\2', text)

# finditer para posições
def find_all_emails(text: str) -> list[dict]:
    return [
        {"email": m.group(), "start": m.start(), "end": m.end()}
        for m in re.finditer(r'[\w.+\-]+@[\w\-]+\.[a-z]{2,}', text, re.I)
    ]
```

---

## Exemplos TypeScript/JavaScript

```typescript
// Grupos nomeados no JS (ES2018+)
const DATE_PATTERN = /(?<year>\d{4})-(?<month>\d{2})-(?<day>\d{2})/;

function parseDate(text: string): Record<string, string> | null {
  const match = text.match(DATE_PATTERN);
  return match?.groups ?? null;
}

// Replace com função
const maskCard = (text: string): string =>
  text.replace(/\b(\d{4})\d{8}(\d{4})\b/g, '$1 **** **** $2');

// matchAll para todas as ocorrências
function extractUrls(text: string): string[] {
  const URL_RE = /https?:\/\/[^\s"'<>]+/g;
  return [...text.matchAll(URL_RE)].map(m => m[0]);
}
```

---

> [!info] Testadores Online
> - [regex101.com](https://regex101.com) — com explicações de cada parte
> - [regexr.com](https://regexr.com) — visualização interativa
> - Python: `python -c "import re; help(re)"` no terminal

> [!warning] Performance
> Evite backtracking catastrófico (ex: `(a+)+b` em strings longas). Prefira classes de caractere específicas e grupos atômicos `(?>...)` quando disponível. Complexidade de regex pode ser O(2^n) no pior caso — veja [[big-o-notation]].

> [!info] Ver também
> - Uso com Python: [[python]] e [[python-snippets]] via [[bash-snippets]]
> - Filtros de log no Git: [[git-cheatsheet]]
> - TypeScript patterns: [[typescript]]
