from rest_framework import serializers
from .models import Group, Exam, Assignment, ExamAttempt
from apps.accounts.models import User, Organization


class GroupSerializer(serializers.ModelSerializer):
    student_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'organization', 'name', 'level', 'student_count', 'created_at']

    def get_student_count(self, obj):
        return User.objects.filter(group=obj, role='student').count()


class ExamSerializer(serializers.ModelSerializer):
    assigned_group_ids = serializers.SerializerMethodField()
    enabled_sections = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = ['id', 'organization', 'title', 'exam_type', 'status', 'assigned_groups',
                  'assigned_group_ids', 'sections_data', 'enabled_sections', 'created_at',
                  'reopened_at', 'notif_seen_by']

    def get_assigned_group_ids(self, obj):
        return list(obj.assigned_groups.values_list('id', flat=True))

    def get_enabled_sections(self, obj):
        sections = obj.sections_data or {}
        return [k for k, v in sections.items() if v.get('enabled')]


class AssignmentSerializer(serializers.ModelSerializer):
    group_ids = serializers.SerializerMethodField()
    target_student_ids = serializers.SerializerMethodField()
    viewed_by_ids = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = ['id', 'organization', 'title', 'content', 'file_url', 'file_name',
                  'file_mime', 'groups', 'group_ids', 'target_students', 'target_student_ids',
                  'viewed_by', 'viewed_by_ids', 'created_at']

    def get_group_ids(self, obj):
        return list(obj.groups.values_list('id', flat=True))

    def get_target_student_ids(self, obj):
        return list(obj.target_students.values_list('id', flat=True))

    def get_viewed_by_ids(self, obj):
        return list(obj.viewed_by.values_list('id', flat=True))


class ExamAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamAttempt
        fields = ['id', 'student', 'exam', 'status', 'started_at', 'submitted_at',
                  'current_section_index', 'answers', 'writing_text', 'flagged',
                  'notepad_text', 'font_level', 'section_deadlines', 'progress_data']