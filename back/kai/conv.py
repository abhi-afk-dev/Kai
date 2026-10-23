import os
import json
import httpx
import datetime
from mcp import ClientSession
from openai import AsyncOpenAI
from dotenv import load_dotenv
from contextlib import AsyncExitStack
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamable_http_client

load_dotenv()

EXA_API_KEY = os.getenv("EXA")
EXA_MCP_URL = (
    f"https://mcp.exa.ai/mcp?exaApiKey={EXA_API_KEY}"
    if EXA_API_KEY
    else "https://mcp.exa.ai/mcp"
)
JINA_API_KEY = os.getenv("JINA")

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPEN_API_KEY"),
)

def extract_text(result) -> str:
    return "\n".join(block.text for block in result.content if hasattr(block, "text"))

async def exa_search(session: ClientSession, query: str, num_results: int = 5) -> str:
    result = await session.call_tool(
        "web_search_exa", {"query": query, "numResults": num_results}
    )
    return extract_text(result)

async def jina_read(url: str) -> str:
    headers = {}
    if JINA_API_KEY:
        headers["Authorization"] = f"Bearer {JINA_API_KEY}"

    async with httpx.AsyncClient(timeout=30.0) as http_client:
        response = await http_client.get(f"https://r.jina.ai/{url}", headers=headers)
        response.raise_for_status()
        return response.text

kai_tools = [
        {
        "type": "function",
        "function": {
            "name": "exa_search",
            "description": "Search the web for real-time information, news, or links.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query to look up."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "jina_read",
            "description": "Extract clean markdown text from a specific URL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The full URL of the webpage to read."}
                },
                "required": ["url"]
            }
        }
    }
]

async def kai_chat(
    prompt: str, 
    context_data: str = "", 
    system_instruction: str = ""
):
    full_system_prompt = system_instruction
    if context_data:
        full_system_prompt += f"\n\n[USER PERSONAL CONTEXT Memory]:\n{context_data}"

    try:
        async with AsyncExitStack() as stack:
            read_stream, write_stream = await stack.enter_async_context(sse_client(EXA_MCP_URL))
            session = await stack.enter_async_context(ClientSession(read_stream, write_stream))
            await session.initialize()

            messages = [
                {"role": "system", "content": full_system_prompt},
                {"role": "user", "content": prompt}
            ]   
    
            while True:
                response = await client.chat.completions.create(
                    model="nvidia/nemotron-3.5-super-vl:free", 
                    messages=messages,
                    tools=kai_tools,
                    tool_choice="auto",
                    max_tokens=2000,
                    timeout=60.0 
                )
                message = response.choices[0].message
                
                messages.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": message.tool_calls
                }) 
                
                if not message.tool_calls:
                    return message.content or "Task completed."
                    
                for tool_call in message.tool_calls:
                    func_name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)
                    
                    result = f"Error: Unknown tool '{func_name}' called."
                    
                    if func_name == "exa_search":
                        print(f"  [exa search] → {args.get('query')}")
                        result = await exa_search(session, args.get("query"))
                    elif func_name == "jina_read":
                        print(f"  [jina read]  → {args.get('url')}")
                        result = await jina_read(args.get("url"))
                        
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result)
                    })
                
    except Exception as e:
        return f"❌ Kai encountered an error: {e}"
    
async def kai_chat_stream(
    prompt: str, 
    context_data: str = "", 
    system_instruction: str = ""
):
    full_system_prompt = system_instruction
    if context_data:
        full_system_prompt += f"\n\n[USER PERSONAL CONTEXT Memory]:\n{context_data}"

    messages = [
        {"role": "system", "content": full_system_prompt},
        {"role": "user", "content": prompt}
    ]   

    try:
        async with streamable_http_client(EXA_MCP_URL) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                while True:
                    response = await client.chat.completions.create(
                        model="nvidia/nemotron-3.5-super-vl:free", 
                        messages=messages,
                        tools=kai_tools,
                        tool_choice="auto",
                        max_tokens=2000,
                        timeout=60.0 
                    )
                    message = response.choices[0].message
                    
                    messages.append({
                        "role": "assistant",
                        "content": message.content,
                        "tool_calls": message.tool_calls
                    })
                    
                    if not message.tool_calls:
                        if message.content:
                            yield message.content
                        return
                
                    for tool_call in message.tool_calls:
                        func_name = tool_call.function.name
                        args = json.loads(tool_call.function.arguments)

                        if func_name == "exa_search":
                            print(f"  [exa]  → {args.get('query')}")
                            result = await exa_search(session, args.get("query"))

                        elif func_name == "jina_read":
                            print(f"  [jina] → {args.get('url')}")
                            result = await jina_read(args.get("url"))

                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": str(result)
                        })
                
    except Exception as e:
        yield f"❌ Kai encountered an error: {e}"

async def kai_non_web_stream(
    prompt: str, 
    context_data: str = "", 
    system_instruction: str=""
):
    full_system_prompt = system_instruction
    if context_data:
        full_system_prompt += f"\n\n[USER PERSONAL CONTEXT Memory]:\n{context_data}"

    messages = [
        {"role": "system", "content": full_system_prompt},
        {"role": "user", "content": prompt}
    ]   
    
    stream_response = await client.chat.completions.create(
        model="nvidia/nemotron-3.5-super-vl:free", 
        messages=messages,
        stream=True,
        max_tokens=2000,
        timeout=60.0 
    )
    
    async for chunk in stream_response:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta