from datetime import timedelta

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import Choice, Question


class VotingSecurityTests(TestCase):
    def setUp(self):
        self.question = Question.objects.create(
            question_text="A published poll",
            pub_date=timezone.now() - timedelta(days=1),
        )
        self.choice = Choice.objects.create(
            question=self.question, choice_text="My choice", votes=0
        )
        self.future_question = Question.objects.create(
            question_text="A scheduled poll",
            pub_date=timezone.now() + timedelta(days=1),
        )
        self.future_choice = Choice.objects.create(
            question=self.future_question, choice_text="A future choice", votes=0
        )

    def test_future_results_are_not_public(self):
        response = self.client.get(
            reverse("polls:results", args=[self.future_question.pk])
        )

        self.assertEqual(response.status_code, 404)

    def test_future_polls_cannot_receive_votes(self):
        response = self.client.post(
            reverse("polls:vote", args=[self.future_question.pk]),
            {"choice": self.future_choice.pk},
        )

        self.assertEqual(response.status_code, 404)
        self.future_choice.refresh_from_db()
        self.assertEqual(self.future_choice.votes, 0)

    def test_voting_requires_post(self):
        response = self.client.get(reverse("polls:vote", args=[self.question.pk]))

        self.assertEqual(response.status_code, 405)
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.votes, 0)

    @override_settings(CSRF_COOKIE_SECURE=True)
    def test_https_voting_enforces_csrf_and_origin(self):
        client = Client(enforce_csrf_checks=True)
        url = reverse("polls:vote", args=[self.question.pk])
        client.get(reverse("polls:detail", args=[self.question.pk]), secure=True)
        csrf_token = client.cookies["csrftoken"].value

        rejected = client.post(
            url,
            {"choice": self.choice.pk, "csrfmiddlewaretoken": csrf_token},
            secure=True,
            HTTP_ORIGIN="https://untrusted.example.com",
        )
        self.assertEqual(rejected.status_code, 403)
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.votes, 0)

        accepted = client.post(
            url,
            {"choice": self.choice.pk, "csrfmiddlewaretoken": csrf_token},
            secure=True,
            HTTP_ORIGIN="https://testserver",
        )
        self.assertEqual(accepted.status_code, 302)
        self.assertEqual(
            accepted["Location"], reverse("polls:results", args=[self.question.pk])
        )
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.votes, 1)
