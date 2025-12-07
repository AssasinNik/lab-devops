from django.test import TestCase, Client

class BasicTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_health_endpoint(self):
        response = self.client.get("/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_api_endpoint(self):
        response = self.client.get("/api/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("hostname", data)
        self.assertIn("database", data)
        self.assertEqual(data["service"], "django-task-manager")

    def test_create_and_get_tasks(self):
        response = self.client.post(
            "/tasks/",
            data='{"title":"Test Task","description":"Test description","status":"pending"}',
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        task_data = response.json()
        self.assertEqual(task_data["title"], "Test Task")
        self.assertEqual(task_data["status"], "pending")
        task_id = task_data["id"]

        response = self.client.get("/tasks/")
        self.assertEqual(response.status_code, 200)
        tasks = response.json()["tasks"]
        ids = [t["id"] for t in tasks]
        self.assertIn(task_id, ids)

    def test_create_task_without_title(self):
        response = self.client.post(
            "/tasks/",
            data='{"description":"No title"}',
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_create_task_with_invalid_status(self):
        response = self.client.post(
            "/tasks/",
            data='{"title":"Task","status":"invalid_status"}',
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

