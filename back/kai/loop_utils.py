import os, json, asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
client = AsyncOpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPEN_API_KEY"))

MODELS = ["nvidia/nemotron-3.5-super-vl:free", "recursive/flint-v1.0:free"]  # add more live ones
WRITE_WORDS = ("create", "send", "delete", "update", "write", "move", "comment", "commit", "publish", "push", "upload")


def _ok(msg):
    """Reject empty replies and tool calls with cut-off JSON."""
    if msg is None:
        return False
    for tc in msg.tool_calls or []:
        try:
            json.loads(tc.function.arguments or "{}")
        except Exception:
            return False
    return bool(msg.tool_calls or msg.content)

kw = {"max_tokens": 8000, "timeout": 60.0}
async def llm(messages, tools=None, retries=3):
    kw = {"max_tokens": 8000, "timeout": 120.0}
    if tools:
        kw.update(tools=tools, tool_choice="auto")
    for attempt in range(retries):
        for m in MODELS:
            try:
                r = await client.chat.completions.create(model=m, messages=messages, **kw)
                if r and r.choices and _ok(r.choices[0].message):
                    return r.choices[0].message
                print(f"⚠️ {m}: empty or truncated response")
            except Exception as e:
                print(f"⚠️ {m} failed: {type(e).__name__}: {e}")
        await asyncio.sleep(2 * (attempt + 1))
    raise RuntimeError("all models failed after retries")


READ_PREFIXES = ("get", "list", "search", "read", "find", "query", "resolve")

async def run_tool(call, name):
    short = name.split("__")[-1].lower().replace("-", "_")
    is_read = short.startswith(READ_PREFIXES) or name in ("web_search", "run_deep_research")
    tries = 3 if is_read else 1
    result = ""
    for i in range(tries):
        try:
            result = str(await call())
            if not result.startswith("Tool error"):
                break
        except Exception as e:
            result = f"Error executing {name}: {e}"
        await asyncio.sleep(2 * (i + 1))
    return result[:12000]

async def llm_stream(messages, fallback=""):
    """Streams the final answer. Tries each model until one produces output."""
    for m in MODELS:
        got = False
        try:
            stream = await client.chat.completions.create(
                model=m, messages=messages, stream=True, max_tokens=8000, timeout=60.0
            )
            async for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta.content
                if delta:
                    got = True
                    yield delta
            if got:
                return
        except Exception as e:
            print(f"⚠️ stream {m} failed: {type(e).__name__}: {e}")
            if got:          # already sent partial text, don't start over
                return
    if fallback:             # every stream failed, use the non-streamed reply
        yield fallback