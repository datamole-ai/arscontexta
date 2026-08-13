#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: run-claude-turn.sh RUN_ROOT LABEL PROMPT [--setup] [--resume SESSION_ID]

Run one Claude scenario turn from RUN_ROOT/vault and save its stream and stderr
logs under RUN_ROOT/logs. Pass --setup for setup turns so Claude loads the
repository plugin. Use --resume only for a setup follow-up.
EOF
}

die() {
  printf 'run-claude-turn: %s\n' "$1" >&2
  exit 2
}

if [ "${1:-}" = '-h' ] || [ "${1:-}" = '--help' ]; then
  usage
  exit 0
fi

if [ "$#" -lt 3 ]; then
  usage >&2
  exit 2
fi

run_root_input="$1"
label="$2"
prompt_input="$3"
resume_session=""
setup_turn=false
shift 3

while [ "$#" -gt 0 ]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    --setup)
      [ "$setup_turn" = false ] || die '--setup may be specified only once'
      setup_turn=true
      shift
      ;;
    --resume)
      [ "$#" -ge 2 ] || die '--resume requires a session ID'
      [ -z "$resume_session" ] || die '--resume may be specified only once'
      resume_session="$2"
      shift 2
      ;;
    *)
      die "unknown option: $1"
      ;;
  esac
done

if [ -n "$resume_session" ] && [ "$setup_turn" = false ]; then
  die '--resume requires --setup'
fi

script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
repo_root="$(CDPATH= cd -- "$script_dir/../.." && pwd)"

[ -d "$run_root_input" ] || die "run root does not exist: $run_root_input"
run_root="$(CDPATH= cd -- "$run_root_input" && pwd)"

case "$label" in
  ''|[!A-Za-z0-9]*|*[!A-Za-z0-9._-]*) die "invalid label: $label" ;;
esac

[ -f "$prompt_input" ] || die "prompt does not exist: $prompt_input"
prompt_dir="$(CDPATH= cd -- "$(dirname -- "$prompt_input")" && pwd)"
prompt="$prompt_dir/$(basename -- "$prompt_input")"

case "$prompt" in
  "$run_root/prompts/"*) ;;
  *) die "prompt must be saved under $run_root/prompts" ;;
esac

[ -s "$prompt" ] || die "prompt is empty: $prompt"
[ -d "$run_root/vault" ] || die "vault directory does not exist: $run_root/vault"
[ -d "$run_root/logs" ] || die "logs directory does not exist: $run_root/logs"
[ -d "$run_root/claude-config" ] || die "Claude config directory does not exist: $run_root/claude-config"
[ -f "$repo_root/tests/claude-scenario-settings.json" ] || die 'scenario settings are missing'
command -v claude >/dev/null 2>&1 || die 'claude is not available on PATH'

stream_log="$run_root/logs/$label.stream.jsonl"
stderr_log="$run_root/logs/$label.stderr.log"

if [ -e "$stream_log" ] || [ -e "$stderr_log" ]; then
  die "logs already exist for $label; refusing to overwrite a recorded turn"
fi

if [ -f "$repo_root/.env" ]; then
  set -a
  # shellcheck disable=SC1090
  . "$repo_root/.env"
  set +a
fi

export CLAUDE_CONFIG_DIR="$run_root/claude-config"

claude_args=(
  -p
  --settings "$repo_root/tests/claude-scenario-settings.json"
  --permission-mode auto
  --model sonnet
  --effort high
  --output-format stream-json
  --include-partial-messages
  --verbose
)

if [ "$setup_turn" = true ]; then
  claude_args+=(--plugin-dir "$repo_root")
fi

if [ -n "$resume_session" ]; then
  claude_args+=(--resume "$resume_session")
fi

cd "$run_root/vault"

set +e
claude "${claude_args[@]}" < "$prompt" 2> "$stderr_log" | tee "$stream_log"
pipeline_status=("${PIPESTATUS[@]}")
set -e

claude_status="${pipeline_status[0]}"
tee_status="${pipeline_status[1]}"

if [ "$tee_status" -ne 0 ]; then
  printf 'run-claude-turn: failed to record stream log: %s\n' "$stream_log" >&2
  exit 74
fi

exit "$claude_status"
