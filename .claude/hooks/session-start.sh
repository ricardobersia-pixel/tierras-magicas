#!/bin/bash
set -euo pipefail

# Solo en sesiones de Claude Code en la nube
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-.}"

# Instala las dependencias solo si cambió algún archivo que las define desde la última instalación exitosa
hashes=node_modules/.session-start.sha256
if ! sha256sum --check --status "$hashes" 2>/dev/null; then
  # Borrar los hashes antes, para que una instalación fallida se repita la próxima vez
  rm -f "$hashes"

  npm install --no-audit --no-fund

  sha256sum .claude/hooks/session-start.sh package.json package-lock.json 2>/dev/null > "$hashes" || rm -f "$hashes"
fi
