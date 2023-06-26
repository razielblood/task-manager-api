from rest_framework.urls import path
from tasks.views import ListCreateTasksView, RetrieveUpdateDestroyTasksView

urlpatterns = [
    path("tasks/", ListCreateTasksView.as_view(), name="task-list-create"),
    path("tasks/<int:pk>", RetrieveUpdateDestroyTasksView.as_view(), name="task-retrieve-update-destroy"),
]
