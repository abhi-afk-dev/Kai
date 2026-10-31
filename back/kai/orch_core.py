import os
import time
import json
import httpx
import asyncio
import datetime
from .kodo import kodo
from .conv import kai_chat, kai_chat_stream, kai_non_web_stream
from mcp import ClientSession
from openai import AsyncOpenAI
from dotenv import load_dotenv
from .router import get_decision
from .master import run_master_agentic_loop
from .mcp_server import UnifiedMCPManager
from .instructions import KAI_CANVA_INSTRUCTION, KAI_GITHUB_INSTRUCTION, KAI_WORKSPACE_INSTRUCTION, KAI_CONVERSATIONAL_INSTRUCTION, KAI_NON_WEB_INSTRUCTION
from .loop_utils import llm, run_tool, llm_stream

load_dotenv()

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPEN_API_KEY"),
)

EXA_API_KEY = os.getenv("EXA")
EXA_MCP_URL = (
    f"https://mcp.exa.ai/mcp?exaApiKey={EXA_API_KEY}"
    if EXA_API_KEY
    else "https://mcp.exa.ai/mcp"
)
mcp_manager = UnifiedMCPManager()
# _mcp_initialized = False
# 
# async def ensure_mcp_initialized():
    # global _mcp_initialized
    # if not _mcp_initialized:
        # await mcp_manager.initialize_all_servers()
        # _mcp_initialized = True
# 

criteria_hands = {
    "web": "Searching the live internet for real-time information, news, or general facts. or Reading, scraping, or extracting text content from a specific URL provided by the user.",
    "research": "Deep technical analysis or multi-model research using Kodo.",
    "github": "Interacting with GitHub repositories, issues, pull requests, commits, or code.",
    "workspace": "Managing Google Drive files, Google Docs, Sheets, Gmail, or Calendar events.",
    "canva": "Creating, editing, searching, or managing Canva designs, templates, brand kits, and graphics.",
}

criteria_orchestrator = {
    "conversational": "Casual chat, greetings, general questions, or direct answers that require no tool calls, external APIs, or deep research.",
    "single_tasked": "A focused task restricted to a single domain or tool (e.g., checking GitHub issues, creating a Canva design, reading a Google Doc, running deep research with Kodo or even need something from the web).",
    "master_loop": "A complex, multi-step, or multi-domain compound task that requires combining multiple tools/domains sequentially (e.g., researching a topic then building a Canva presentation, or fetching code from GitHub and pushing docs to Workspace)."
}

async def single_agent(prompt: str, agent):

    if agent == "web":
        async for chunk in kai_chat_stream(prompt, system_instruction=KAI_CONVERSATIONAL_INSTRUCTION):
            yield chunk
        return

    elif agent == "research":
        async for chunk in kodo(prompt):
            yield chunk
        return

    tools = await mcp_manager.fetch_tools_for_selected(selected_server_names=[agent])
    if not tools:
        yield f"Sorry, I couldn't connect to the {agent} integration right now."
        return

    instruction_name = f"KAI_{agent.upper()}_INSTRUCTION"
    instruction = globals().get(instruction_name, KAI_CONVERSATIONAL_INSTRUCTION)

    messages = [
        {"role": "system", "content": instruction},
        {"role": "user", "content": prompt},
    ]

    MAX_STEPS = 5
    for step in range(MAX_STEPS):
        try:
            message = await llm(messages, tools)
        except Exception as e:
            yield f"⚠️ The model is unavailable right now ({e}). Please try again."
            return

        if not message.tool_calls:
            async for chunk in llm_stream(messages, fallback=message.content or ""):
                yield chunk
            return

        messages.append(message)

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            yield f"🔧 {tool_name.split('__')[-1]}...\n"
            try:
                tool_args = json.loads(tool_call.function.arguments or "{}")
                print(f"🛠️ [{agent}] step {step}: {tool_name} {tool_args}")

                async def call(n=tool_name, a=tool_args):
                    return await mcp_manager.execute_tool(agent, n, a)

                tool_result = await run_tool(call, tool_name)
            except Exception as e:
                tool_result = f"Error executing tool {tool_name}: {e}"

            messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": str(tool_result)})

    yield "Sorry buddy, I couldn't finish that within the step limit."

async def main(prompt):
    await mcp_manager.initialize_all_servers()
    mode = await get_decision(criteria_orchestrator, prompt)
    
    if mode == "master_loop":
        message = ""
        async for chunk in run_master_agentic_loop(prompt, mcp_manager):
            yield chunk
            message += chunk
        print(f"\n--- THIS WILL BE THE MASTER ---\n{message}\n-------------------------------\n")

    elif mode == "single_tasked":
        agent = await get_decision(criteria_hands, prompt)

        if agent:
            message = ""
            async for chunk in single_agent(prompt, agent):
                yield chunk
                message += chunk
            print(f"\n--- THIS WILL BE THE SINGLE ONE ---\n{message}\n-------------------------------\n")

        else:
            async for chunk in kai_chat_stream(prompt, system_instruction=KAI_CONVERSATIONAL_INSTRUCTION):
                yield chunk
                
    else:
        async for chunk in kai_non_web_stream(prompt, system_instruction=KAI_NON_WEB_INSTRUCTION):
            yield chunk

# debugging code
# async def main(prompt):
#     t0, first, message = time.time(), None, ""
#     try:
#         await mcp_manager.initialize_all_servers()
#         mode = await get_decision(criteria_orchestrator, prompt)
#         print(f"MODE: {mode}")

#         if mode == "master_loop":
#             gen = run_master_agentic_loop(prompt, mcp_manager)
#         elif mode == "single_tasked":
#             agent = await get_decision(criteria_hands, prompt)
#             print(f"AGENT: {agent}")
#             gen = (single_agent(prompt, agent) if agent else
#                    kai_chat_stream(prompt, system_instruction=KAI_CONVERSATIONAL_INSTRUCTION))
#         else:
#             gen = kai_non_web_stream(prompt, system_instruction=KAI_NON_WEB_INSTRUCTION)

#         async for chunk in gen:
#             if first is None:
#                 first = time.time() - t0
#                 print(f"FIRST CHUNK after {first:.1f}s")
#             message += chunk
#             yield chunk
#     except asyncio.CancelledError:
#         print("CLIENT DISCONNECTED (proxy or browser closed the stream)")
#         raise
#     except Exception as e:
#         import traceback; traceback.print_exc()
#         yield f"\n⚠️ Error: {type(e).__name__}: {e}"
#     finally:
#         print(f"DONE in {time.time()-t0:.1f}s, {len(message)} chars\n{message[-300:]}")