from rest_framework.permissions import BasePermission

class IsCustomerUser(BasePermission):
    """Permission: Only users with CustomerProfile can create reviews"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return hasattr(request.user, 'customer_profile')
    
class IsReviewOwner(BasePermission):
    """Permission: Only the reviewer can update/delete their review"""
    
    def has_object_permission(self, request, view, obj):
        return obj.reviewer == request.user