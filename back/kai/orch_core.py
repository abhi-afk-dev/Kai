import os
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

load_dotenv()

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

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPEN_API_KEY"),
)

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
        response = await client.chat.completions.create(
            model="nvidia/nemotron-3.5-super-vl:free",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            max_tokens=4000,
            timeout=120.0,
        )
        message = response.choices[0].message

        if not message.tool_calls:
            if message.content:
                yield message.content
            return

        messages.append(message)

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            try:
                tool_args = json.loads(tool_call.function.arguments or "{}")
                print(f"🛠️ [{agent}] step {step}: {tool_name} {tool_args}")
                tool_result = await mcp_manager.execute_tool(agent, tool_name, tool_args)
            except Exception as e:
                tool_result = f"Error executing tool {tool_name}: {e}"

            print(f"   ↳ result: {str(tool_result)[:300]}")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(tool_result),
            })

    yield "Sorry, I couldn't finish that within the step limit."

async def main(prompt):
    await mcp_manager.initialize_all_servers()
    mode = await get_decision(criteria_orchestrator, prompt)

    if mode == "master_loop":
        response = await run_master_agentic_loop(prompt, mcp_manager)
        yield response

    elif mode == "single_tasked":
        agent = await get_decision(criteria_hands, prompt)

        if agent:
            async for chunk in single_agent(prompt, agent):
                yield chunk
        else:
            async for chunk in kai_chat_stream(prompt, system_instruction=KAI_CONVERSATIONAL_INSTRUCTION):
                yield chunk
                
    else:
        async for chunk in kai_non_web_stream(prompt, system_instruction=KAI_NON_WEB_INSTRUCTION):
            yield chunk