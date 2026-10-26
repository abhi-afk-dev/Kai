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
    # all_servers = ["github", "canva", "workspace"]
    servers = ["workspace"]
    p = prompt.lower()
    if "canva" in p or "design" in p: servers.append("canva")
    if "github" in p or "repo" in p: servers.append("github")

    mcp_tools = await mpm_manager.fetch_tools_for_selected(selected_server_names=servers)
    combined_tools = mcp_tools + INTERNAL_TOOLS

    system = KAI_MASTER_AGENT_INSTRUCTION

    if "research" in p:
        text = await kodo_non_stream(prompt)
        store["research"] = text
        combined_tools = [t for t in combined_tools if t["function"]["name"] != "run_deep_research"]
        system += (
            f"\n\nResearch is finished and saved ({len(text)} chars). Preview:\n{text[:800]}\n\n"
            "Do NOT research again. To put the full text in a document, set its content to "
            "{{research}} exactly and always give the document a short title. "
            "Never retype the research. After creating the doc, reply with the link."
        )

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt},
    ]

    for step in range(10):
        print(f"🔄 Master Loop Iteration [{step + 1}/10]")
        
        response = await client.chat.completions.create(
            model="dots-studio/dots-3-note-preview:free",
            messages=messages,
            tools=combined_tools,
            tool_choice="auto",
            timeout=120.0,
        )
        
        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            return message.content

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name


            tool_result = ""
            try:
                tool_args = fill(json.loads(tool_call.function.arguments or "{}"), store)
                print(f"🛠️ Master Agent invoking tool: {tool_name} | Args: {str(tool_args)[:500]}")

                if tool_name == "run_deep_research":
                    text = await kodo_non_stream(tool_args.get("query"))
                    store["research"] = text      
                    tool_result = (
                        f"Research complete ({len(text)} chars) and saved. To use the FULL text in any "
                        f"tool argument, such as a document's content, write {{{{research}}}} exactly. "
                        f"Do not retype it.\n\nPreview:\n{text[:800]}"
                    )
                
                elif tool_name == "web_search":
                    tool_result = await kai_chat(tool_args.get("prompt"))
                
                else:
                    server_name = tool_name.split("__")[0] if "__" in tool_name else None
                    
                    if server_name:
                        tool_result = await mpm_manager.execute_tool(server_name, tool_name, tool_args)
                    else:
                        tool_result = f"Error: Unknown tool namespace for {tool_name}"

            except Exception as e:
                tool_result = f"❌ Error executing tool {tool_name}: {e}"

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(tool_result)
            })

    return "⚠️ Master agentic loop reached maximum iteration limit (10 steps) without finishing."