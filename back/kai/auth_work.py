# python -m kai.auth_workspace                      -> lists tools
# python -m kai.auth_workspace <tool> '{"k":"v"}'   -> calls one
import asyncio, sys, json
from .mcp_server import UnifiedMCPManager

async def main():
    m = UnifiedMCPManager()
    await m.initialize_all_servers()
    tools = await m.fetch_tools_for_selected(["workspace"])
    names = [t["function"]["name"] for t in tools]

    if len(sys.argv) < 2:
        print("\n".join(names))
        return

    args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    print(await m.execute_tool("workspace", sys.argv[1], args))

asyncio.run(main())