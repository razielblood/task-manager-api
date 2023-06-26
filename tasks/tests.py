from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User, Group
from rest_framework.reverse import reverse
from rest_framework import status
from tasks.models import Task
from datetime import datetime
from tasks.serializers import TaskSerializer


# Create your tests here.
class ListCreateTasksViewTestCase(TestCase):
    def setUp(self) -> None:
        # Create manager group
        self.manager_group = Group.objects.create(name="manager")

        # Create the users
        self.normal_user = User.objects.create(username="test_user", password="password")
        self.manager_user = User.objects.create(username="manager_user", password="password")
        self.manager_user.groups.add(self.manager_group)

        self.client = APIClient()
        self.url = reverse("task-list-create")

        self.valid_payload = {
            "title": "Valid task",
            "description": "Valid Description",
            "due_date": "2023-07-01",
            "state_code": "C",
        }

        self.invalid_payload_title = {
            "title": "",
            "description": "Invalid title",
            "due_date": "2023-07-01",
            "state_code": "C",
        }

        self.invalid_payload_description = {
            "title": "Invalid description",
            "description": "",
            "due_date": "2023-07-01",
            "state_code": "C",
        }

        self.invalid_payload_due_date = {
            "title": "Invalid due date",
            "description": "Invalid due date description",
            "due_date": "2023-25-99",
            "state_code": "C",
        }

        self.invalid_payload_state = {
            "title": "Invalid state",
            "description": "Invalid state description",
            "due_date": "2023-07-01",
            "state_code": "H",
        }

    def test_create_task(self):
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.post(self.url, self.valid_payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Check that the post returns 201")

        created_task = Task.objects.get(pk=response.data["id"])
        self.assertEqual(created_task.title, self.valid_payload.get("title"), "Check that the title is correct")
        self.assertEqual(
            created_task.description, self.valid_payload.get("description"), "Check that the description is correct"
        )
        self.assertEqual(
            created_task.due_date,
            datetime.strptime(self.valid_payload.get("due_date"), "%Y-%m-%d").date(),
            "Check that the due date is correct",
        )
        self.assertEqual(created_task.state, self.valid_payload.get("state_code"), "Check that the state is correct")

    def test_create_task_unauthorized(self):
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.post(self.url, self.valid_payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, "Check that the post returns 403")

    def test_list_tasks(self):
        task_1 = {
            "title": "Valid task 1",
            "description": "Valid Description 1",
            "due_date": "2023-07-01",
            "state": "C",
        }

        task_2 = {
            "title": "Valid task 2",
            "description": "Valid Description 2",
            "due_date": "2023-08-01",
            "state": "D",
        }

        Task.objects.create(**task_1)
        Task.objects.create(**task_2)

        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)

        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get(self.url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = [task for task in response.data["results"]]

        self.assertEqual(response_data, serializer.data, "Check that the returned data is correct")

    def test_invalid_payload_title(self):
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.post(self.url, self.invalid_payload_title)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, "Check that the post returns 400")

    def test_invalid_payload_description(self):
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.post(self.url, self.invalid_payload_description)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, "Check that the post returns 400")

    def test_invalid_payload_due_date(self):
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.post(self.url, self.invalid_payload_due_date)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, "Check that the post returns 400")

    def test_invalid_payload_state(self):
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.post(self.url, self.invalid_payload_state)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, "Check that the post returns 400")


class RetrieveUpdateDestroyTasksViewTestCase(TestCase):
    def setUp(self) -> None:
        # Create manager group
        self.manager_group = Group.objects.create(name="manager")

        # Create the users
        self.normal_user = User.objects.create(username="test_user", password="password")
        self.manager_user = User.objects.create(username="manager_user", password="password")
        self.manager_user.groups.add(self.manager_group)

        base_task = {
            "title": "Valid task",
            "description": "Valid Description",
            "due_date": "2023-07-01",
            "state": "C",
        }

        self.test_task = Task.objects.create(**base_task)

        self.client = APIClient()

        self.url = reverse("task-retrieve-update-destroy", args=[self.test_task.id])

        self.valid_payload = {
            "title": "Updated task",
            "description": "Updated Description",
            "due_date": "2024-03-24",
            "state_code": "P",
        }

        self.patch_payload_title = {"title": "Patched task"}

        self.patch_payload_description = {"description": "Patched description"}

        self.patch_payload_due_date = {"due_date": "2030-01-01"}

        self.patch_payload_state = {"state_code": "D"}

        self.invalid_payload_title = {
            "title": "",
            "description": "Invalid title",
            "due_date": "2023-07-01",
            "state_code": "C",
        }

        self.invalid_payload_description = {
            "title": "Invalid description",
            "description": "",
            "due_date": "2023-07-01",
            "state_code": "C",
        }

        self.invalid_payload_due_date = {
            "title": "Invalid due date",
            "description": "Invalid due date description",
            "due_date": "2023-25-99",
            "state_code": "C",
        }

        self.invalid_payload_state = {
            "title": "Invalid state",
            "description": "Invalid state description",
            "due_date": "2023-07-01",
            "state_code": "H",
        }

    def test_get_task(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Check that the get returns 200")

        serializer = TaskSerializer(self.test_task)

        self.assertEqual(response.data, serializer.data, "Check that te retrieved data is correct")

    def test_patch_task_unauthorized(self):
        self.client.force_authenticate(self.normal_user)
        response = self.client.patch(self.url, self.patch_payload_title)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, "Check that the patch returns 403")

    def test_patch_task_title(self):
        self.client.force_authenticate(self.manager_user)
        response = self.client.patch(self.url, self.patch_payload_title)
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Check that the patch returns 200")

        modified_task = Task.objects.get(pk=self.test_task.pk)
        serializer = TaskSerializer(modified_task)
        self.assertEqual(self.patch_payload_title.get("title"), serializer.data.get("title"))

    def test_patch_task_description(self):
        self.client.force_authenticate(self.manager_user)
        response = self.client.patch(self.url, self.patch_payload_description)
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Check that the patch returns 200")

        modified_task = Task.objects.get(pk=self.test_task.pk)
        serializer = TaskSerializer(modified_task)
        self.assertEqual(self.patch_payload_description.get("description"), serializer.data.get("description"))

    def test_patch_task_due_date(self):
        self.client.force_authenticate(self.manager_user)
        response = self.client.patch(self.url, self.patch_payload_due_date)
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Check that the patch returns 200")

        modified_task = Task.objects.get(pk=self.test_task.pk)
        serializer = TaskSerializer(modified_task)
        self.assertEqual(self.patch_payload_due_date.get("due_date"), serializer.data.get("due_date"))

    def test_patch_task_state(self):
        self.client.force_authenticate(self.manager_user)
        response = self.client.patch(self.url, self.patch_payload_state)
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Check that the patch returns 200")

        modified_task = Task.objects.get(pk=self.test_task.pk)
        self.assertEqual(self.patch_payload_state.get("state_code"), modified_task.state)

    def test_put_task_unauthorized(self):
        self.client.force_authenticate(self.normal_user)
        response = self.client.put(self.url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, "Check that the patch returns 403")

    def test_put_task(self):
        self.client.force_authenticate(self.manager_user)
        response = self.client.put(self.url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Check that the patch returns 200")

        updated_task = Task.objects.get(pk=self.test_task.pk)
        serializer = TaskSerializer(updated_task)
        self.assertEqual(response.data, serializer.data, "Check that the task is updated correctly")

    def test_put_task_invalid_title(self):
        self.client.force_authenticate(self.manager_user)
        response = self.client.put(self.url, self.invalid_payload_title)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, "Check that the put returns 400")

    def test_put_task_invalid_description(self):
        self.client.force_authenticate(self.manager_user)
        response = self.client.put(self.url, self.invalid_payload_description)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, "Check that the put returns 400")

    def test_put_task_invalid_due_date(self):
        self.client.force_authenticate(self.manager_user)
        response = self.client.put(self.url, self.invalid_payload_due_date)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, "Check that the put returns 400")

    def test_put_task_invalid_state(self):
        self.client.force_authenticate(self.manager_user)
        response = self.client.put(self.url, self.invalid_payload_state)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, "Check that the put returns 400")

    def test_delete_task_unauthorized(self):
        self.client.force_authenticate(self.normal_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, "Check that the delete returns 403")

    def test_delete_task(self):
        self.client.force_authenticate(self.manager_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, "Check that the delete returns 204")
        self.assertFalse(Task.objects.filter(pk=self.test_task.pk).exists(), "Check that the task is deleted")
