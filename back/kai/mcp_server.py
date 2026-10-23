import os
import traceback
from dotenv import load_dotenv
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client
from contextlib import asynccontextmanager
from exceptiongroup import BaseExceptionGroup
from mcp import ClientSession, StdioServerParameters
from mcp.client.streamable_http import streamable_http_client
from .oauth_store import FileTokenStorage
from mcp.client.auth import OAuthClientProvider
from mcp.shared.auth import OAuthClientMetadata
from pydantic import AnyUrl
import httpx2

load_dotenv()


def _leaf_exceptions(exc):
    if isinstance(exc, BaseExceptionGroup):
        for e in exc.exceptions:
            yield from _leaf_exceptions(e)
    else:
        yield exc


class UnifiedMCPManager:
    def __init__(self):
        self.servers = {}

    @staticmethod
    def _canva_auth():
        async def no_redirect(url):
            raise RuntimeError("Canva isn't authorized. Run: python -m kai.auth_canva")

        async def no_callback():
            raise RuntimeError("Canva isn't authorized. Run: python -m kai.auth_canva")

        return OAuthClientProvider(
            server_url="https://mcp.canva.com/mcp",
            client_metadata=OAuthClientMetadata(
                client_name="Kai",
                redirect_uris=[AnyUrl("http://localhost:3030/callback")],
                grant_types=["authorization_code", "refresh_token"],
                response_types=["code"],
            ),
            storage=FileTokenStorage("canva"),
            redirect_handler=no_redirect,
            callback_handler=no_callback,
        )

    async def initialize_all_servers(self):
        print("🔌 Registering all MCP endpoints and parameters...")

        # ==========================================
        # 1. GITHUB MCP (Local Subprocess via Stdio)
        # ==========================================
        self.servers["github"] = {
            "type": "stdio",
            "params": StdioServerParameters(
                command="npx",
                args=["--yes", "--quiet", "@modelcontextprotocol/server-github"],
                env={
                    **os.environ,
                    "GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv(
                        "GITHUB_PERSONAL_ACCESS_TOKEN", ""
                    ),
                    "CI": "true",
                    "LOG_LEVEL": "error",
                    "npm_config_loglevel": "silent",
                },
            ),
        }

        # ==========================================
        # 2. WORKSPACE MCP (Local Port)
        # ==========================================
        self.servers["workspace"] = {
            "type": "http",
            "url": os.getenv("WORKSPACE_MCP_URL", "http://127.0.0.1:8001/mcp"),
            "headers": {},
        }

        # ==========================================
        # 3. CANVA MCP (Cloud URL)
        # ==========================================
        self.servers["canva"] = {
            "type": "http",
            "url": "https://mcp.canva.com/mcp",
            "headers": {},
            "auth_factory": self._canva_auth,
        }

        # # ==========================================
        # # 4. EXA MCP (Cloud URL with API Key)
        # # ==========================================
        # EXA_API_KEY = os.getenv("EXA_API_KEY", "")
        # self.servers["exa"] = {
        #     "type": "http",
        #     "url": (f"https://mcp.exa.ai/mcp?exaApiKey={EXA_API_KEY}"
        #         if EXA_API_KEY
        #         else "https://mcp.exa.ai/mcp"),
        #     "headers": {}
        # }

        # # ==========================================
        # # 5. JINA MCP (Cloud URL with Bearer Token Header)
        # # ==========================================
        # jina_key = os.getenv("JINA_API_KEY", "")
        # self.servers["jina"] = {
        #     "type": "http",
        #     "url": "https://mcp.jina.ai/v1",
        #     "headers": {
        #         "Authorization": f"Bearer {jina_key}"
        #     }
        # }

        print("   -> All 3 MCP servers successfully mapped.")

    @asynccontextmanager
    async def _open_session(self, config):
        if config["type"] == "http":
            factory = config.get("auth_factory")
            async with httpx2.AsyncClient(
                auth=factory() if factory else None,
                headers=config.get("headers") or None,
                follow_redirects=True,
                timeout=30.0,
            ) as http_client:
                async with streamable_http_client(
                    config["url"], http_client=http_client
                ) as streams:
                    async with ClientSession(streams[0], streams[1]) as session:
                        await session.initialize()
                        yield session
            return

        if config["type"] == "stdio":
            cm = stdio_client(config["params"])
        elif config["type"] == "sse":
            cm = sse_client(config["url"], headers=config.get("headers") or None)
        else:
            raise ValueError(f"Unknown transport: {config['type']}")

        async with cm as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                yield session

    async def fetch_tools_for_selected(self, selected_server_names, allowed_tools=None):
        combined = []
        for name in selected_server_names:
            config = self.servers.get(name)
            if not config:
                continue
            try:
                async with self._open_session(config) as session:
                    response = await session.list_tools()
                    for tool in response.tools:
                        ns_name = f"{name}__{tool.name}"
                        if (
                            allowed_tools is not None
                            and ns_name not in allowed_tools
                            and tool.name not in allowed_tools
                        ):
                            continue

                        schema = (
                            getattr(tool, "inputSchema", None)
                            or getattr(tool, "input_schema", None)
                            or {"type": "object", "properties": {}}
                        )

                        combined.append(
                            {
                                "type": "function",
                                "function": {
                                    "name": ns_name,
                                    "description": tool.description or "",
                                    "parameters": schema,
                                },
                            }
                        )
            except Exception as e:
                target = config.get("url", "stdio")
                for leaf in _leaf_exceptions(e):
                    print(
                        f"❌ Failed to fetch tools from {name} ({target}): {type(leaf).__name__}: {leaf}"
                    )
        return combined

    async def execute_tool(
        self, server_name: str, namespaced_tool: str, args: dict
    ) -> str:
        config = self.servers[server_name]
        tool_name = namespaced_tool.removeprefix(f"{server_name}__")

        async with self._open_session(config) as session:
            result = await session.call_tool(tool_name, args)

        is_error = getattr(result, "isError", None)
        if is_error is None:
            is_error = getattr(result, "is_error", False)

        parts = []
        for c in getattr(result, "content", None) or []:
            text = getattr(c, "text", None)
            parts.append(text if text is not None else str(c))
        out = "\n".join(parts)

        return f"Tool error: {out}" if is_error else out
