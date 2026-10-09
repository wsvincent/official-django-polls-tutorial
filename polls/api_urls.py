from rest_framework.routers import SimpleRouter

from .api import QuestionViewSet

app_name = "polls-api"

router = SimpleRouter()
router.register("polls", QuestionViewSet, basename="poll")

urlpatterns = router.urls
