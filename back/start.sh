#!/bin/sh
set -e
mkdir -p "$MCP_AUTH_DIR" "$WORKSPACE_MCP_CREDENTIALS_DIR"

# Seed Canva tokens only if not already on the volume
if [ -n "$CANVA_AUTH_B64" ] && [ ! -f "$MCP_AUTH_DIR/canva.json" ]; then
  echo "$CANVA_AUTH_B64" | base64 -d > "$MCP_AUTH_DIR/canva.json"
  echo "Seeded Canva auth"
fi

# Google tokens (only if not already on the volume)
TARGET="$WORKSPACE_MCP_CREDENTIALS_DIR/$GOOGLE_CREDS_FILENAME"
if [ -n "$GOOGLE_CREDS_B64" ] && [ ! -f "$TARGET" ]; then
  echo "$GOOGLE_CREDS_B64" | base64 -d > "$TARGET"
  echo "Seeded Google credentials"
fi

# Workspace MCP in the background, restarted if it dies.
# PORT is overridden for this process only: the server prefers Railway's
# injected PORT, which belongs to uvicorn here.
(
  while true; do
    env PORT=8001 WORKSPACE_MCP_PORT=8001 \
      /opt/wsvenv/bin/workspace-mcp --transport streamable-http --single-user --tool-tier core
    echo "workspace-mcp exited, restarting in 3s"
    sleep 3
  done
) &

exec uvicorn back.asgi:application --host 0.0.0.0 --port "${PORT:-8000}"