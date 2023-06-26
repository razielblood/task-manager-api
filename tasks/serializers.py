from rest_framework import serializers
from tasks.models import Task
from rest_framework.exceptions import ValidationError


class TaskSerializer(serializers.ModelSerializer):
    state = serializers.CharField(source="get_state_display", read_only=True)
    state_code = serializers.CharField(source="state", write_only=True)

    def validate_state_code(self, data):
        state_codes = [code for code, _ in Task.STATE_CHOICES]
        if data not in state_codes:
            raise ValidationError(f"Invalid state {data}")
        return data

    class Meta:
        model = Task
        fields = ("id", "title", "description", "due_date", "state", "state_code")
