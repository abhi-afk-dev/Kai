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


import asyncio
from laya import Router

router = Router()

async def get_decision(criteria, state):    
    questions = {
        "routing_choice": {
            "type": "choice",
            "instructions": "Which route should this take?",
            "criteria": criteria,
        },
    }

    result = await asyncio.to_thread(router.predict, state, questions)
    
    return result["answers"]["routing_choice"]["choice"]