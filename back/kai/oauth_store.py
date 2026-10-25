import os
import json
import time
from pathlib import Path
from mcp.client.auth import TokenStorage
from mcp.shared.auth import OAuthClientInformationFull, OAuthToken

class FileTokenStorage(TokenStorage):
    def __init__(self, name: str):
        self.path = Path(os.getenv("MCP_AUTH_DIR", ".mcp_auth")) / f"{name}.json"
        self.path.parent.mkdir(exist_ok=True)

    def _read(self):
        return json.loads(self.path.read_text()) if self.path.exists() else {}

    def _write(self, data):
        self.path.write_text(json.dumps(data))

    async def get_tokens(self):
        d = self._read()
        t = d.get("tokens")
        if not t:
            return None
        saved_at = d.get("saved_at") or self.path.stat().st_mtime
        exp = t.get("expires_in")
        if exp:
            t = {**t, "expires_in": max(1, int(exp - (time.time() - saved_at)))}
        return OAuthToken(**t)

    async def set_tokens(self, tokens):
        d = self._read()
        d["tokens"] = tokens.model_dump(mode="json")
        d["saved_at"] = time.time()
        self._write(d)

    async def get_client_info(self):
        d = self._read().get("client_info")
        return OAuthClientInformationFull(**d) if d else None

    async def set_client_info(self, info):
        d = self._read(); d["client_info"] = info.model_dump(mode="json"); self._write(d)