from rest_framework.permissions import BasePermission

class IsBusinessUser(BasePermission):
    """Permission to allow only BusinessProfile users access"""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return hasattr(request.user, 'business_profile')