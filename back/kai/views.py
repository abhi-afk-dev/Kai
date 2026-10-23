import os
import json
from .conv import kai_non_web_stream
from django.http import StreamingHttpResponse
from .orch_core import main as run_kai_orchestrator
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
async def chat_stream_view(request):
    data = json.loads(request.body)
    prompt = data.get("prompt", "")

    async def response_generator():
        async for chunk in run_kai_orchestrator(prompt):
            yield chunk

    return StreamingHttpResponse(response_generator(), content_type="text/plain; charset=utf-8")