from rest_framework.permissions import BasePermission

class IsSupport(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'support'

class IsCEO(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'ceo'

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role in ['ceo', 'admin']

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role in ['ceo', 'admin', 'manager']

class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role in ['ceo', 'admin', 'manager', 'teacher']

class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role in ['ceo', 'admin', 'manager', 'teacher']

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'student'

class IsOwnerOrStaff(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'support':
            return True
        if request.user.role in ['ceo', 'admin', 'manager', 'teacher']:
            if hasattr(obj, 'organization'):
                return obj.organization_id == request.user.organization_id
            if hasattr(obj, 'exam') and hasattr(obj.exam, 'organization'):
                return obj.exam.organization_id == request.user.organization_id
        if hasattr(obj, 'student') and obj.student_id == request.user.id:
            return True
        if hasattr(obj, 'user') and obj.user_id == request.user.id:
            return True
        return False

class IsOrganizationMember(BasePermission):
    def has_permission(self, request, view):
        if request.user.role == 'support':
            return True
        if request.user.role in ['ceo', 'admin', 'manager', 'teacher']:
            return request.user.organization_id is not None
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'support':
            return True
        if hasattr(obj, 'organization'):
            return obj.organization_id == request.user.organization_id
        if hasattr(obj, 'org_id'):
            return obj.org_id == request.user.organization_id
        return False