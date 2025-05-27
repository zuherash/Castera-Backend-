from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        # المستخدم يقدر يشوف أو يعدل فقط إذا كان صاحب الاجتماع أو مدير
        return obj.user == request.user or request.user.role == 'admin'