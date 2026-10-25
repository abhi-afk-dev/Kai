import asyncio, threading, webbrowser
from contextlib import asynccontextmanager
import httpx2
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pydantic import AnyUrl
from mcp import ClientSession
from mcp.client.auth import OAuthClientProvider
from mcp.client.streamable_http import streamable_http_client
from mcp.shared.auth import OAuthClientMetadata
from .oauth_store import FileTokenStorage

URL = "https://mcp.canva.com/mcp"
PORT = 3030
REDIRECT = f"http://localhost:{PORT}/callback"


async def main():
    loop = asyncio.get_running_loop()
    fut = loop.create_future()

    class OAuthResult:
        def __init__(self, code, state, iss):
            self.code = code
            self.state = state
            self.iss = iss

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            q = parse_qs(urlparse(self.path).query)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Authorized. You can close this tab.")

            code = q["code"][0]
            state = q.get("state", [None])[0]
            iss = q.get("iss", [None])[0]

            loop.call_soon_threadsafe(fut.set_result, OAuthResult(code, state, iss))

        def log_message(self, *a):
            pass

    server = HTTPServer(("localhost", PORT), Handler)
    threading.Thread(target=server.handle_request, daemon=True).start()

    async def redirect_handler(url: str):
        print("Open this URL if the browser doesn't launch:\n", url)
        webbrowser.open(url)

    async def callback_handler():
        return await fut

    provider = OAuthClientProvider(
        server_url=URL,
        client_metadata=OAuthClientMetadata(
            client_name="Kai",
            redirect_uris=[AnyUrl(REDIRECT)],
            grant_types=["authorization_code", "refresh_token"],
            response_types=["code"],
            token_endpoint_auth_method="none",
        ),
        storage=FileTokenStorage("canva"),
        redirect_handler=redirect_handler,
        callback_handler=callback_handler,
    )

    async with httpx2.AsyncClient(auth=provider) as http_client:
        async with streamable_http_client(URL, http_client=http_client) as (r, w):
            async with ClientSession(r, w) as s:
                await s.initialize()
                tools = await s.list_tools()
                print("✅ Authorized. Tools:", [t.name for t in tools.tools])


asyncio.run(main())
