#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP_ROOT="$(mktemp -d)"

cleanup() {
  local status=$?
  rm -rf "$TMP_ROOT"
  exit "$status"
}
trap cleanup EXIT

prepare_fixture() {
  local fixture="$1"

  mkdir -p \
    "$fixture/scripts/lib" \
    "$fixture/openclaw" \
    "$fixture/config-templates" \
    "$fixture/home" \
    "$fixture/fakebin" \
    "$fixture/.git"

  cp "$PROJECT_ROOT/scripts/install.sh" "$fixture/scripts/install.sh"
  chmod +x "$fixture/scripts/install.sh"

  cat > "$fixture/scripts/apply-addons.sh" <<'SH'
#!/usr/bin/env bash
echo "apply-addons-called" >> "$PROJECT_FIXTURE/apply.log"
SH
  chmod +x "$fixture/scripts/apply-addons.sh"

  cat > "$fixture/scripts/lib/crew-workspaces.sh" <<'SH'
#!/usr/bin/env bash
seed_builtin_crew_workspaces() {
  echo "seed-called" >> "$PROJECT_FIXTURE/seed.log"
}
SH

  cat > "$fixture/config-templates/openclaw.json" <<'JSON'
{}
JSON

  cat > "$fixture/openclaw.version" <<'VERSION'
OPENCLAW_VERSION=fixture-version
OPENCLAW_COMMIT=targetcommit
VERSION

  cat > "$fixture/fakebin/pnpm" <<'SH'
#!/usr/bin/env bash
echo "pnpm $*" >> "$PROJECT_FIXTURE/pnpm.log"
exit 0
SH
  chmod +x "$fixture/fakebin/pnpm"

  cat > "$fixture/fakebin/uname" <<'SH'
#!/usr/bin/env bash
echo "Darwin"
SH
  chmod +x "$fixture/fakebin/uname"
}

write_fake_git() {
  local fixture="$1"
  local current_commit="$2"
  local target_available="$3"

  cat > "$fixture/fakebin/git" <<SH
#!/usr/bin/env bash
echo "git \$*" >> "\$PROJECT_FIXTURE/git.log"

if [ "\${1:-}" = "-C" ]; then
  shift 2
fi

case "\${1:-} \${2:-} \${3:-}" in
  "remote get-url origin")
    echo "https://github.com/TeamWiseFlow/wiseflow.git"
    exit 0
    ;;
  "fetch origin master")
    echo "simulated wiseflow fetch failure" >&2
    exit 1
    ;;
  "rev-parse HEAD")
    echo "$current_commit"
    exit 0
    ;;
  "cat-file -e targetcommit^{tree}")
    [ "$target_available" = "true" ] && exit 0
    exit 1
    ;;
  "fetch origin --tags"|"fetch --unshallow origin"|"fetch --deepen=200 origin")
    echo "simulated openclaw fetch failure" >&2
    exit 1
    ;;
  "checkout targetcommit")
    [ "$target_available" = "true" ] && exit 0
    exit 1
    ;;
  "reset --hard HEAD")
    exit 0
    ;;
  *)
    exit 0
    ;;
esac
SH
  chmod +x "$fixture/fakebin/git"
}

assert_true() {
  local condition="$1"
  local message="$2"
  if ! eval "$condition"; then
    echo "ASSERT FAILED: $message"
    exit 1
  fi
}

echo "[TEST] wiseflow fetch failure should continue when local openclaw matches target"
MATCH_FIXTURE="$TMP_ROOT/match"
prepare_fixture "$MATCH_FIXTURE"
write_fake_git "$MATCH_FIXTURE" "targetcommit" "true"
PROJECT_FIXTURE="$MATCH_FIXTURE" \
HOME="$MATCH_FIXTURE/home" \
PATH="$MATCH_FIXTURE/fakebin:$PATH" \
  "$MATCH_FIXTURE/scripts/install.sh" --skip-crew > "$MATCH_FIXTURE/install.log" 2>&1

assert_true "[ -f '$MATCH_FIXTURE/apply.log' ]" "install did not continue to apply-addons after wiseflow fetch failure"
assert_true "grep -q 'Continuing with local wiseflow code' '$MATCH_FIXTURE/install.log'" "missing local wiseflow fallback message"

echo "[TEST] install should stop when required openclaw commit is unavailable locally"
MISMATCH_FIXTURE="$TMP_ROOT/mismatch"
prepare_fixture "$MISMATCH_FIXTURE"
write_fake_git "$MISMATCH_FIXTURE" "localold" "false"
if PROJECT_FIXTURE="$MISMATCH_FIXTURE" \
  HOME="$MISMATCH_FIXTURE/home" \
  PATH="$MISMATCH_FIXTURE/fakebin:$PATH" \
    "$MISMATCH_FIXTURE/scripts/install.sh" --skip-crew > "$MISMATCH_FIXTURE/install.log" 2>&1; then
  echo "ASSERT FAILED: install succeeded despite missing required openclaw commit"
  exit 1
fi

assert_true "[ ! -f '$MISMATCH_FIXTURE/apply.log' ]" "install continued after openclaw version mismatch"
assert_true "grep -q 'does not match required openclaw.version' '$MISMATCH_FIXTURE/install.log'" "missing openclaw mismatch failure message"

echo "ALL TESTS PASSED"
