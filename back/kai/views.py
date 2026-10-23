from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .orch_core import main as run_kai_orchestrator
from .conv import kai_non_web_stream

@csrf_exempt
async def chat_stream_view(request):
    if request.method != "POST":
        return StreamingHttpResponse("Only POST allowed", status=405)

    data = json.loads(request.body)
    prompt = data.get("prompt", "")

    async def response_generator():
        async for chunk in run_kai_orchestrator(prompt):
            yield chunk

    return StreamingHttpResponse(response_generator(), content_type="text/plain; charset=utf-8")