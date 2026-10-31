import os
import re
import json
import asyncio
from .kodo import kodo_non_stream
from .conv import kai_chat
from openai import AsyncOpenAI
from dotenv import load_dotenv
from .mcp_server import UnifiedMCPManager
from .instructions import KAI_MASTER_AGENT_INSTRUCTION
from .loop_utils import llm, run_tool, llm_stream
load_dotenv()

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPEN_API_KEY"),
)

INTERNAL_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_deep_research",
            "description": "Run deep multi-model research (Kodo) on complex technical topics, APIs, or libraries.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The detailed research query."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the live web or read a URL for real-time facts using Saku.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "What to search or extract from the web."}
                },
                "required": ["prompt"]
            }
        }
    }
]


def fill(o, store):
    if isinstance(o, str):
        return re.sub(
            r"\{\{?\s*research\s*\}?\}",
            lambda m: store.get("research", m.group(0)),
            o,
        )
    if isinstance(o, dict):
        return {k: fill(v, store) for k, v in o.items()}
    if isinstance(o, list):
        return [fill(v, store) for v in o]
    return o
async def run_master_agentic_loop(prompt, mpm_manager):
    store = {}
    servers = ["workspace"]
    p = prompt.lower()
    if "canva" in p or "design" in p: servers.append("canva")
    if "github" in p or "repo" in p: servers.append("github")

    mcp_tools = await mpm_manager.fetch_tools_for_selected(selected_server_names=servers)
    combined_tools = mcp_tools + INTERNAL_TOOLS
    system = KAI_MASTER_AGENT_INSTRUCTION

    if "research" in p:
        yield "🔎 Researching...\n"
        try:
            text = await kodo_non_stream(prompt)
        except Exception as e:
            yield f"⚠️ Research failed ({e}). Please try again."
            return
        store["research"] = text
        combined_tools = [t for t in combined_tools if t["function"]["name"] != "run_deep_research"]
        system += (
            f"\n\nResearch is finished and saved ({len(text)} chars). Preview:\n{text[:800]}\n\n"
            "Do NOT research again. To put the full text in a document, set its content to "
            "{{research}} exactly and always give the document a short title. "
            "Never retype the research. After creating the doc, reply with the link."
        )

    messages = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]

    for step in range(10):
        try:
            message = await llm(messages, combined_tools)
        except Exception as e:
            yield f"⚠️ The model is unavailable right now ({e}). Please try again."
            return

        if not message.tool_calls:
            yield "\n"
            async for chunk in llm_stream(messages, fallback=message.content or ""):
                yield chunk
            return

        messages.append(message)

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            yield f"🔧 {tool_name.split('__')[-1]}...\n"

            tool_args = fill(json.loads(tool_call.function.arguments or "{}"), store)
            if not isinstance(tool_args, dict):
                tool_args = {}
            print(f"🛠️ {tool_name} | {str(tool_args)[:500]}")

            async def call(tool_name=tool_name, tool_args=tool_args):
                if tool_name == "run_deep_research":
                    text = await kodo_non_stream(tool_args.get("query", ""))
                    store["research"] = text
                    return (f"Research complete ({len(text)} chars) and saved. To use the FULL text in any "
                            f"tool argument, write {{{{research}}}} exactly.\n\nPreview:\n{text[:800]}")
                if tool_name == "web_search":
                    return await kai_chat(tool_args.get("prompt", ""))
                return await mpm_manager.execute_tool(tool_name.split("__")[0], tool_name, tool_args)

            tool_result = await run_tool(call, tool_name)
            messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": str(tool_result)})

    yield "⚠️ Master agentic loop reached maximum iteration limit (10 steps) without finishing."