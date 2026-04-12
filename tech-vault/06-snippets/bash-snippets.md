---
tags: [snippet, bash]
status: active
level: advanced
updated: 2026-04-05
aliases: [Bash Snippets]
created: 2026-04-05
---

# Bash Snippets

Snippets prontos para uso em scripts de automação, CI/CD, e administração de sistemas. Referências cruzadas com [[git-advanced]], [[docker]], [[python-snippets]], [[git-cheatsheet]] e [[docker-snippets]].

---

## Boilerplate Seguro

```bash
#!/usr/bin/env bash
# Template base para scripts robustos
set -euo pipefail
IFS=$'\n\t'

# Trap para cleanup em erro ou saída
TMPDIR_LOCAL=$(mktemp -d)
trap 'rm -rf "$TMPDIR_LOCAL"; echo "Cleanup done." >&2' EXIT ERR INT TERM

# Logger simples
log()  { echo "[$(date '+%Y-%m-%dT%H:%M:%S')] INFO  $*" >&2; }
warn() { echo "[$(date '+%Y-%m-%dT%H:%M:%S')] WARN  $*" >&2; }
die()  { echo "[$(date '+%Y-%m-%dT%H:%M:%S')] ERROR $*" >&2; exit 1; }

# Verificar dependências
require() {
  for cmd in "$@"; do
    command -v "$cmd" &>/dev/null || die "Required command not found: $cmd"
  done
}

require curl jq git
```

---

## File Operations

```bash
# Criar backup com timestamp
backup_file() {
  local file="$1"
  local backup="${file}.bak.$(date +%Y%m%d_%H%M%S)"
  cp -p "$file" "$backup"
  echo "Backup criado: $backup"
}

# Verificar se diretório existe e criar se necessário
ensure_dir() {
  local dir="$1"
  [[ -d "$dir" ]] || mkdir -p "$dir"
}

# Buscar e substituir em múltiplos arquivos
replace_in_files() {
  local pattern="$1"
  local replacement="$2"
  local dir="${3:-.}"
  find "$dir" -type f -name "*.txt" -exec \
    sed -i "s|${pattern}|${replacement}|g" {} +
}

# Sincronizar diretórios com log de mudanças
sync_dirs() {
  local src="$1" dst="$2"
  rsync -av --delete --log-file="/tmp/rsync_$(date +%Y%m%d).log" \
    "$src/" "$dst/"
}

# Encontrar arquivos maiores que N MB
find_large_files() {
  local dir="${1:-.}"
  local size_mb="${2:-100}"
  find "$dir" -type f -size +"${size_mb}M" \
    -printf '%s %p\n' | sort -rn | head -20
}
```

---

## Process Management

```bash
# Executar comando com timeout
run_with_timeout() {
  local timeout="$1"; shift
  timeout "$timeout" "$@" || {
    local code=$?
    [[ $code -eq 124 ]] && die "Command timed out after ${timeout}s"
    die "Command failed with exit code $code"
  }
}

# Verificar se processo está rodando
is_running() {
  local name="$1"
  pgrep -x "$name" &>/dev/null
}

# Matar processo por nome com graceful shutdown
kill_gracefully() {
  local name="$1"
  local pid
  pid=$(pgrep -x "$name" || true)
  [[ -z "$pid" ]] && return 0
  kill -TERM "$pid"
  sleep 5
  kill -0 "$pid" 2>/dev/null && kill -KILL "$pid" || true
}

# Executar em background com PID tracking
run_background() {
  local cmd=("$@")
  "${cmd[@]}" &
  local pid=$!
  echo "$pid" > "/tmp/${cmd[0]}.pid"
  log "Started ${cmd[0]} with PID $pid"
}

# Monitorar uso de memória de um processo
watch_memory() {
  local pid="$1"
  while kill -0 "$pid" 2>/dev/null; do
    ps -o pid,rss,vsz,comm -p "$pid" | tail -1
    sleep 5
  done
}
```

---

## Text Processing: awk, sed, jq

```bash
# awk: somar coluna 3 de CSV
sum_column() {
  awk -F',' 'NR>1 {sum += $3} END {print sum}' "$1"
}

# awk: filtrar linhas onde campo > valor
awk_filter() {
  local file="$1" col="$2" threshold="$3"
  awk -F',' -v col="$col" -v thr="$threshold" \
    'NR>1 && $col > thr {print}' "$file"
}

# sed: remover comentários e linhas vazias
strip_comments() {
  sed -e 's/#.*//' -e '/^[[:space:]]*$/d' "$1"
}

# sed: substituição multilinha (GNU sed)
fix_multiline() {
  sed -i ':a;N;$!ba;s/foo\nbar/baz/g' "$1"
}

# jq: extrair campo de array de objetos
jq_extract() {
  local file="$1" field="$2"
  jq -r ".[].${field}" "$file"
}

# jq: filtrar e transformar JSON
jq_transform() {
  local input="$1"
  jq '[.[] | select(.status == "active") | {id, name, email: .contact.email}]' \
    "$input"
}

# jq: merge de dois arquivos JSON
jq_merge() {
  jq -s '.[0] * .[1]' "$1" "$2"
}
```

---

## Networking: curl, ssh, scp

```bash
# curl com retry e backoff exponencial
curl_retry() {
  local url="$1"
  local max_retries=5
  local retry_delay=1
  for i in $(seq 1 "$max_retries"); do
    if curl -fsSL --connect-timeout 10 --max-time 30 "$url" -o /tmp/response; then
      cat /tmp/response
      return 0
    fi
    warn "Attempt $i/$max_retries failed. Retrying in ${retry_delay}s..."
    sleep "$retry_delay"
    retry_delay=$((retry_delay * 2))
  done
  die "All $max_retries attempts failed for $url"
}

# curl: POST JSON com autenticação
api_post() {
  local url="$1" token="$2" payload="$3"
  curl -fsSL -X POST "$url" \
    -H "Authorization: Bearer $token" \
    -H "Content-Type: application/json" \
    -d "$payload"
}

# SSH tunnel em background
ssh_tunnel() {
  local local_port="$1" remote_host="$2" remote_port="$3" jump_host="$4"
  ssh -fNL "${local_port}:${remote_host}:${remote_port}" \
    -o StrictHostKeyChecking=no \
    -o ServerAliveInterval=60 \
    "$jump_host"
  log "Tunnel: localhost:${local_port} -> ${remote_host}:${remote_port}"
}

# scp com compressão e progresso
scp_transfer() {
  local src="$1" user="$2" host="$3" dest="$4"
  scp -C -r -o StrictHostKeyChecking=no \
    "$src" "${user}@${host}:${dest}"
}

# Verificar porta aberta
check_port() {
  local host="$1" port="$2" timeout="${3:-3}"
  timeout "$timeout" bash -c "echo >/dev/tcp/${host}/${port}" 2>/dev/null
}
```

---

## Loops & Conditionals

```bash
# Loop com índice e elemento
for_indexed() {
  local -n arr=$1
  for i in "${!arr[@]}"; do
    echo "[$i] ${arr[$i]}"
  done
}

# Processar arquivos linha a linha (seguro com espaços)
process_lines() {
  local file="$1"
  while IFS= read -r line || [[ -n "$line" ]]; do
    [[ -z "$line" || "$line" == \#* ]] && continue
    echo "Processing: $line"
  done < "$file"
}

# Retry loop genérico
retry_loop() {
  local max="$1"; shift
  local count=0
  until "$@" || (( ++count >= max )); do
    warn "Attempt $count failed, retrying..."
    sleep $((count * 2))
  done
  (( count < max )) || die "Failed after $max attempts"
}

# Select menu interativo
show_menu() {
  local options=("Deploy" "Rollback" "Status" "Quit")
  PS3="Choose action: "
  select opt in "${options[@]}"; do
    case $REPLY in
      1) deploy;;
      2) rollback;;
      3) show_status;;
      4) break;;
      *) warn "Invalid option";;
    esac
  done
}
```

---

## Cron Patterns

```bash
# Verificar se cron job já está rodando (lock file)
acquire_lock() {
  local lockfile="/tmp/${1}.lock"
  exec 200>"$lockfile"
  flock -n 200 || die "Another instance is running (lock: $lockfile)"
  echo $$ >&200
}

# Cron com output para log rotativo
# Adicionar ao crontab:
# 0 2 * * * /usr/local/bin/backup.sh >> /var/log/backup.log 2>&1

# Wrapper para cron com notificação em falha
cron_wrapper() {
  local script="$1"
  local logfile="/var/log/$(basename "$script" .sh).log"
  if ! bash "$script" >> "$logfile" 2>&1; then
    mail -s "CRON FAILURE: $script" admin@example.com < "$logfile"
  fi
}

# Limpar logs antigos (rodar via cron diário)
cleanup_logs() {
  local log_dir="${1:-/var/log/app}"
  local days="${2:-30}"
  find "$log_dir" -name "*.log" -mtime +"$days" -delete
  log "Deleted logs older than $days days from $log_dir"
}
```

---

## One-Liners Úteis

```bash
# Monitorar novo arquivo em diretório
inotifywait -m /tmp -e create --format '%f' | while read file; do echo "New: $file"; done

# Mostrar 10 maiores diretórios
du -sh /var/* 2>/dev/null | sort -rh | head -10

# Descompactar qualquer arquivo
extract() {
  case "$1" in
    *.tar.gz|*.tgz)  tar xzf "$1";;
    *.tar.bz2|*.tbz) tar xjf "$1";;
    *.tar.xz)        tar xJf "$1";;
    *.zip)           unzip "$1";;
    *.gz)            gunzip "$1";;
    *.bz2)           bunzip2 "$1";;
    *.xz)            unxz "$1";;
    *)               die "Unknown format: $1";;
  esac
}

# Converter CSV para JSON com jq
csv_to_json() {
  local file="$1"
  local headers
  headers=$(head -1 "$file" | tr ',' '\n')
  awk -F',' 'NR>1{print}' "$file" | \
    jq -Rn --argjson h "$(echo "$headers" | jq -Rsc 'split("\n")[:-1]')" \
    '[inputs | split(",") | . as $v | [$h, $v] | transpose | map({(.[0]): .[1]}) | add]'
}

# Port scan simples
portscan() {
  for port in $(seq 1 1024); do
    (echo >/dev/tcp/"$1"/"$port") 2>/dev/null && echo "Open: $port"
  done
}
```

---

> [!tip] Script Template
> Sempre comece scripts com `set -euo pipefail` e defina um `trap` de cleanup. Isso evita bugs silenciosos e garante que recursos temporários sejam liberados.

> [!warning] Compatibilidade
> Snippets com `local -n` (nameref) requerem Bash 4.3+. macOS usa Bash 3.x por padrão — instale via Homebrew.

> [!info] Ver também
> - Comandos Git avançados: [[git-advanced]] e [[git-cheatsheet]]
> - Containerização: [[docker]] e [[docker-snippets]]
> - Scripts Python equivalentes: [[python-snippets]]
