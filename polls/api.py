from django.utils import timezone
from rest_framework import viewsets

from .models import Question
from .serializers import QuestionSerializer


class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        return (
            Question.objects.filter(pub_date__lte=timezone.now())
            .prefetch_related("choice_set")
            .order_by("-pub_date", "-pk")
        )
