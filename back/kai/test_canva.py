import asyncio, logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("httpcore").setLevel(logging.WARNING)
from .mcp_server import UnifiedMCPManager

async def main():
    m = UnifiedMCPManager()
    await m.initialize_all_servers()
    tools = await m.fetch_tools_for_selected(["canva"])
    print("TOOLS:", len(tools))

asyncio.run(main())