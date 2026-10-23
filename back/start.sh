#!/bin/sh
set -e
mkdir -p "$MCP_AUTH_DIR"

# Seed Canva tokens only if not already on the volume
if [ -n "$CANVA_AUTH_B64" ] && [ ! -f "$MCP_AUTH_DIR/canva.json" ]; then
  echo "$CANVA_AUTH_B64" | base64 -d > "$MCP_AUTH_DIR/canva.json"
  echo "Seeded Canva auth"
fi

exec uvicorn back.asgi:application --host 0.0.0.0 --port "${PORT:-8000}"