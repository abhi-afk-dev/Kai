# import os
# import httpx
# import asyncio
# from dotenv import load_dotenv

# load_dotenv()


# async def get_decision(criteria, instructions):
#     headers = {
#         "Authorization": f"Bearer {os.getenv('OPEN_API_KEY')}",
#         "Content-Type": "application/json",
#     }

#     payload = {
#         "model": "respan/span-01-lite",
#         "state": "",
#         "questions": {
#             "routing_choice": {
#                 "type": "choice",
#                 "instructions": instructions,
#                 "criteria": criteria,
#             }
#         },
#     }

#     async with httpx.AsyncClient() as client:
#         response = await client.post(
#             "https://openrouter.ai/api/alpha/decisions",
#             json=payload,
#             headers=headers,
#             timeout=120.0,
#         )
#         data = response.json()
#         if "error" in data:
#             raise RuntimeError(data["error"])
#         return data["answers"]["routing_choice"]["choice"]

# import asyncio
# import nanojev

# agent = nanojev.load("v0.1")

# async def get_decision(criteria, state):    
#     instructions = "Which route should this take?"

#     probs = await asyncio.to_thread(
#         agent.decide,
#         instructions,
#         criteria,
#         state
#     )
    
#     return max(probs, key=probs.get)

import os
import sys
import asyncio
import logging

# 1. Force unbuffered logging and disable PyTorch multi-threading deadlocks
os.environ["PYTHONUNBUFFERED"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import torch
torch.set_num_threads(1)

import nanojev

# Configure explicit logging that immediately flushes to Railway logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# 2. Eagerly load the model ON STARTUP (never inside the function call)
logging.info("Starting nano-jev model pre-load...")
try:
    agent = nanojev.load("v0.1")
    logging.info("nano-jev model successfully loaded into memory.")
except Exception as e:
    logging.critical(f"Failed to load nano-jev model: {e}", exc_info=True)
    raise e

# 3. Decision function with explicit timeouts
async def get_decision(criteria: list[str], state: str, timeout_sec: float = 5.0) -> str:
    instructions = "Which route should this take?"
    logging.info(f"Routing request received for state snippet: '{state[:40]}...'")

    try:
        # Wrap in wait_for so it raises an explicit TimeoutError instead of hanging silently
        probs = await asyncio.wait_for(
            asyncio.to_thread(agent.decide, instructions, criteria, state),
            timeout=timeout_sec
        )
        
        winning_choice = max(probs, key=probs.get)
        logging.info(f"Decision resolved -> '{winning_choice}' | Probs: {probs}")
        return winning_choice

    except asyncio.TimeoutError:
        logging.error(f"Inference timed out after {timeout_sec} seconds.")
        raise RuntimeError("Routing decision timed out.")
    except Exception as e:
        logging.error(f"Inference failed with error: {e}", exc_info=True)
        raise e
