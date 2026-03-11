#!/usr/bin/env bash
# wenyan-formatter — Markdown → styled HTML (render) or WeChat GZH draft (publish)
# Wraps @wenyan-md/cli via npx; requires Node.js 18+.
#
# Usage:
#   bash format.sh [options]
#
# Actions:
#   render  (default) — convert Markdown to styled HTML, save to --out-dir
#   publish           — render + upload images + push to WeChat GZH draft box
#
# Input (one required):
#   --file <path>      local Markdown file path
#   --content <text>   inline Markdown string (will be piped via stdin)
#
# Options:
#   --action <render|publish>   default: render
#   --theme <id>                theme ID (see SKILL.md for list); default: default
#   --highlight <id>            code highlight theme; default: solarized-light
#   --custom-theme <path>       path to custom CSS file
#   --no-mac-style              disable Mac-style code block header
#   --no-footnote               disable link→footnote conversion
#   --out-dir <path>            output directory (render only); default: ./tmp/wenyan-<ts>
#   --server <url>              Wenyan Server URL (publish only, bypasses IP whitelist)
#   --api-key <key>             API key for Wenyan Server (publish only)
#
# Environment (publish only):
#   WECHAT_APP_ID      WeChat GZH app ID
#   WECHAT_APP_SECRET  WeChat GZH app secret
set -euo pipefail

# ---------- defaults ----------
ACTION="render"
FILE=""
CONTENT=""
THEME="default"
HIGHLIGHT="solarized-light"
CUSTOM_THEME=""
OUT_DIR=""
SERVER=""
API_KEY=""
MAC_STYLE_FLAG="--mac-style"
FOOTNOTE_FLAG="--footnote"

# ---------- argument parsing ----------
while [[ $# -gt 0 ]]; do
    case "$1" in
        --action)       ACTION="$2";       shift 2 ;;
        --file)         FILE="$2";         shift 2 ;;
        --content)      CONTENT="$2";      shift 2 ;;
        --theme)        THEME="$2";        shift 2 ;;
        --highlight)    HIGHLIGHT="$2";    shift 2 ;;
        --custom-theme) CUSTOM_THEME="$2"; shift 2 ;;
        --out-dir)      OUT_DIR="$2";      shift 2 ;;
        --server)       SERVER="$2";       shift 2 ;;
        --api-key)      API_KEY="$2";      shift 2 ;;
        --no-mac-style) MAC_STYLE_FLAG="--no-mac-style"; shift ;;
        --no-footnote)  FOOTNOTE_FLAG="--no-footnote";   shift ;;
        *)
            echo "[error] Unknown argument: $1" >&2
            exit 1
            ;;
    esac
done

# ---------- validate action ----------
if [[ "$ACTION" != "render" && "$ACTION" != "publish" ]]; then
    echo "[error] --action must be 'render' or 'publish', got: $ACTION" >&2
    exit 1
fi

# ---------- validate input ----------
if [[ -z "$FILE" && -z "$CONTENT" ]]; then
    echo "[error] Provide either --file <path> or --content <markdown>" >&2
    exit 1
fi

if [[ -n "$FILE" && ! -f "$FILE" ]]; then
    echo "[error] File not found: $FILE" >&2
    exit 1
fi

# ---------- check node/npx ----------
if ! command -v node &>/dev/null; then
    echo "[error] node not found. Install Node.js 18+ first." >&2
    exit 1
fi

NODE_VER=$(node -e "process.stdout.write(process.version)")
NODE_MAJOR=$(echo "$NODE_VER" | sed 's/v//' | cut -d. -f1)
if [[ "$NODE_MAJOR" -lt 18 ]]; then
    echo "[error] Node.js 18+ required, found $NODE_VER" >&2
    exit 1
fi

if ! command -v npx &>/dev/null; then
    echo "[error] npx not found. It should ship with Node.js." >&2
    exit 1
fi

# ---------- publish: pre-flight checks ----------
if [[ "$ACTION" == "publish" ]]; then
    if [[ -z "${WECHAT_APP_ID:-}" || -z "${WECHAT_APP_SECRET:-}" ]]; then
        echo "[error] publish requires WECHAT_APP_ID and WECHAT_APP_SECRET to be set." >&2
        echo "[hint]  Set them via environment variables before calling this script." >&2
        exit 1
    fi

    # frontmatter title check (only when using --content, file is user's responsibility)
    if [[ -n "$CONTENT" ]]; then
        if ! echo "$CONTENT" | grep -qE '^---' || ! echo "$CONTENT" | grep -qE '^title:'; then
            echo "[warn] publish mode: --content should include frontmatter with 'title:' field." >&2
            echo "[warn] Missing title may cause WeChat API rejection." >&2
        fi
    fi
fi

# ---------- build npx args ----------
WENYAN_ARGS=("--yes" "@wenyan-md/cli" "$ACTION")

if [[ -n "$FILE" ]]; then
    WENYAN_ARGS+=("--file" "$FILE")
fi

WENYAN_ARGS+=("--theme" "$THEME")
WENYAN_ARGS+=("--highlight" "$HIGHLIGHT")
WENYAN_ARGS+=("$MAC_STYLE_FLAG")
WENYAN_ARGS+=("$FOOTNOTE_FLAG")

if [[ -n "$CUSTOM_THEME" ]]; then
    WENYAN_ARGS+=("--custom-theme" "$CUSTOM_THEME")
fi

if [[ "$ACTION" == "publish" ]]; then
    if [[ -n "$SERVER" ]]; then
        WENYAN_ARGS+=("--server" "$SERVER")
        if [[ -n "$API_KEY" ]]; then
            WENYAN_ARGS+=("--api-key" "$API_KEY")
        fi
    fi
fi

# ---------- render: prepare output directory ----------
if [[ "$ACTION" == "render" ]]; then
    TS=$(date +%s)
    if [[ -z "$OUT_DIR" ]]; then
        OUT_DIR="./tmp/wenyan-${TS}"
    fi
    mkdir -p "$OUT_DIR"
    HTML_FILE="${OUT_DIR}/output.html"

    echo "[info] Action: render | Theme: ${THEME} | Highlight: ${HIGHLIGHT}"
    echo "[info] Output dir: ${OUT_DIR}"

    # Run wenyan render → capture HTML output
    if [[ -n "$CONTENT" ]]; then
        HTML_CONTENT=$(echo "$CONTENT" | npx "${WENYAN_ARGS[@]}")
    else
        HTML_CONTENT=$(npx "${WENYAN_ARGS[@]}")
    fi

    # Wrap in minimal page for browser preview
    cat > "$HTML_FILE" <<HTML_EOF
<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>wenyan preview</title>
<style>
  body { max-width: 780px; margin: 40px auto; padding: 0 20px; font-family: sans-serif; }
</style>
</head>
<body>
${HTML_CONTENT}
</body>
</html>
HTML_EOF

    # Also save original Markdown for reference
    if [[ -n "$FILE" ]]; then
        cp "$FILE" "${OUT_DIR}/source.md"
        echo "[done] Source: ${OUT_DIR}/source.md"
    else
        echo "$CONTENT" > "${OUT_DIR}/source.md"
        echo "[done] Source: ${OUT_DIR}/source.md"
    fi

    echo "[done] HTML:   ${HTML_FILE}"
    echo "[done] Theme used: ${THEME}"

# ---------- publish ----------
else
    echo "[info] Action: publish | Theme: ${THEME}"
    if [[ -n "$SERVER" ]]; then
        echo "[info] Using server mode: ${SERVER}"
    else
        echo "[info] Using local mode (IP must be in WeChat whitelist)"
    fi

    if [[ -n "$CONTENT" ]]; then
        RESULT=$(echo "$CONTENT" | npx "${WENYAN_ARGS[@]}")
    else
        RESULT=$(npx "${WENYAN_ARGS[@]}")
    fi

    echo "[done] $RESULT"
fi
