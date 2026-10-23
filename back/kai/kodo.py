import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv
from .conv import kai_chat

load_dotenv()

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPEN_API_KEY"),
)


def get_model_config():
    return {
        "model1": "liquid/lfm-2.5-2.6b:free",
        "model2": "dots-studio/dots-3-note-preview:free",
        "model3": "cohere/north-mini-code:free",
    }


workers = "You are an expert research assistant. Your goal is to provide a detailed, objective, and well-structured analysis of the user's prompt. Be thorough, cover multiple facets of the topic, and format your response clearly using markdown."
judge = f"""You are an expert senior editor and chief research judge. You will be given multiple draft responses from different research agents to the same prompt. Your job is to:
1. Compare the responses for accuracy, depth, and unique insights.
2. Resolve any contradictions by taking the most logical and well-reasoned stance.
3. Synthesize everything into a single, comprehensive, highly polished final response for the user. Do not mention the individual models or agents—present the final answer as your own unified work."""
web_instruction = "You are a web research agent. Extract precise facts and data from live search results. Provide clear, objective, and well-structured answers using bold key points and bullet points. Avoid filler or commentary—deliver raw, synthesized answers directly."


async def brain_plug(model, web_research, prompt: str):
    messages = [
        {"role": "system", "content": workers},
        {
            "role": "user",
            "content": f"[LIVE WEB RESEARCH CONTEXT]:\n{web_research}\n\n[USER PROMPT]:\n{prompt}",
        },
    ]

    try:
        response = await client.chat.completions.create(
                    model=model, 
                    messages=messages,
                    max_tokens=8000,
                    timeout=120.0 
                )
        return model, response.choices[0].message.content

    except Exception as e:
        return model, f"❌ Brain ({model}) encountered an error: {e}"

async def kodo(user_prompt):
    web_research = await kai_chat(user_prompt, system_instruction=web_instruction)
    valid_models = [m for m in get_model_config().values() if m is not None]
    tasks = [brain_plug(model, web_research, user_prompt) for model in valid_models]
    results = await asyncio.gather(*tasks)

    worker_compilations = ""
    for model_name, content in results:
        worker_compilations += f"\n\n--- RESPONSE FROM {model_name} ---\n{content}"

    messages = [
        {"role": "system", "content": judge},
        {
            "role": "user",
            "content": f"[ORIGINAL PROMPT]:\n{user_prompt}\n\n[DRAFT RESPONSES TO EVALUATE]:{worker_compilations}",
        },
    ]

    
    stream = await client.chat.completions.create(
        model="recursive/flint-v1.0:free",
        messages=messages,
        stream=True,
        max_tokens=8000,
        timeout=120.0,
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


