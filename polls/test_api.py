import datetime

from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from .models import Choice, Question


class PollAPITests(APITestCase):
    def setUp(self):
        self.question = Question.objects.create(
            question_text="What's new?",
            pub_date=timezone.now() - datetime.timedelta(days=1),
        )
        self.choice = Choice.objects.create(
            question=self.question, choice_text="Django REST Framework", votes=2
        )
        self.future_question = Question.objects.create(
            question_text="Future poll",
            pub_date=timezone.now() + datetime.timedelta(days=1),
        )

    def test_list_returns_published_polls_with_choices(self):
        response = self.client.get(reverse("polls-api:poll-list"))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], self.question.pk)
        self.assertEqual(data[0]["question_text"], self.question.question_text)
        self.assertIn("pub_date", data[0])
        self.assertEqual(
            data[0]["choices"],
            [
                {
                    "id": self.choice.pk,
                    "choice_text": self.choice.choice_text,
                    "votes": 2,
                }
            ],
        )

    def test_detail_returns_published_poll(self):
        response = self.client.get(
            reverse("polls-api:poll-detail", args=[self.question.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], self.question.pk)
        self.assertEqual(response.json()["choices"][0]["id"], self.choice.pk)

    def test_future_poll_is_not_available(self):
        response = self.client.get(
            reverse("polls-api:poll-detail", args=[self.future_question.pk])
        )

        self.assertEqual(response.status_code, 404)

    def test_missing_poll_returns_404(self):
        response = self.client.get(reverse("polls-api:poll-detail", args=[99999]))

        self.assertEqual(response.status_code, 404)

    def test_api_is_read_only(self):
        response = self.client.post(
            reverse("polls-api:poll-list"),
            {"question_text": "New poll", "pub_date": timezone.now().isoformat()},
            format="json",
        )

        self.assertEqual(response.status_code, 405)
        self.assertEqual(Question.objects.count(), 2)
