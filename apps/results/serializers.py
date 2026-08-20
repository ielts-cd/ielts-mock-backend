from rest_framework import serializers
from .models import ExamResult


class ExamResultSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    exam_title_display = serializers.SerializerMethodField()

    class Meta:
        model = ExamResult
        fields = ['id', 'attempt', 'student', 'student_name', 'exam', 'exam_title_display',
                  'organization', 'overall_band', 'section_scores', 'section_bands',
                  'section_raw', 'review_data', 'stats', 'writing_status', 'writing_band',
                  'task1_band', 'task2_band', 'task1_criteria', 'task2_criteria',
                  'exam_title', 'exam_type', 'submitted_at']

    def get_student_name(self, obj):
        return obj.student.name if obj.student else None

    def get_exam_title_display(self, obj):
        return obj.exam.title if obj.exam else obj.exam_title


class GradeWritingSerializer(serializers.Serializer):
    task1_criteria = serializers.DictField(required=False)
    task2_criteria = serializers.DictField(required=False)
    task1_band = serializers.FloatField(required=False, allow_null=True)
    task2_band = serializers.FloatField(required=False, allow_null=True)
    band = serializers.FloatField(required=False, allow_null=True)