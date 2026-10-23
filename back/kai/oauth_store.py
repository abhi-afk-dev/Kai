import os
import json
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
        d = self._read().get("tokens")
        return OAuthToken(**d) if d else None

    async def set_tokens(self, tokens):
        d = self._read(); d["tokens"] = tokens.model_dump(mode="json"); self._write(d)

    async def get_client_info(self):
        d = self._read().get("client_info")
        return OAuthClientInformationFull(**d) if d else None

    async def set_client_info(self, info):
        d = self._read(); d["client_info"] = info.model_dump(mode="json"); self._write(d)