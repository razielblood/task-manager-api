from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from tasks.models import Task
from tasks.serializers import TaskSerializer
from permissions import IsManagerOrReadOnlyPermission


# Create your views here.
class ListCreateTasksView(ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsManagerOrReadOnlyPermission]


class RetrieveUpdateDestroyTasksView(RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsManagerOrReadOnlyPermission]
