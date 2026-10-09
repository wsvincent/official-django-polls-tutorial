from django.http import JsonResponse
from django.views.decorators.http import require_safe


@require_safe
def health(request):
    """Report process liveness without depending on the database."""
    response = JsonResponse({"status": "ok"})
    response["Cache-Control"] = "no-store"
    return response
