import os, hmac, json
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .orch_core import main as run_kai_orchestrator


def _authorized(request):
    expected = os.getenv("KAI_PASSWORD", "")
    given = request.headers.get("X-Kai-Key", "")
    return bool(expected) and hmac.compare_digest(given.encode(), expected.encode())


@csrf_exempt
async def check_auth(request):
    if request.method != "POST":
        return JsonResponse({"ok": False}, status=405)
    ok = _authorized(request)
    return JsonResponse({"ok": ok}, status=200 if ok else 401)


@csrf_exempt
async def chat_stream_view(request):
    if request.method != "POST":
        return StreamingHttpResponse("Only POST allowed", status=405)
    if not _authorized(request):
        return StreamingHttpResponse("Unauthorized", status=401)

    data = json.loads(request.body)
    prompt = data.get("prompt", "")

    async def response_generator():
        async for chunk in run_kai_orchestrator(prompt):
            yield chunk

    # return StreamingHttpResponse(response_generator(), content_type="text/plain; charset=utf-8")
    resp = StreamingHttpResponse(response_generator(), content_type="text/plain; charset=utf-8")
    resp["Cache-Control"] = "no-cache"
    resp["X-Accel-Buffering"] = "no"
    return resp