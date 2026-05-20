from rest_framework.permissions import BasePermission

class IsCustomerUser(BasePermission):
    """Permission: Only users with CustomerProfile can create orders"""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return hasattr(request.user, 'customer_profile')
    
class IsOrderBusinessUser(BasePermission):
    """Permission: Only business user of order can update it"""
    
    def has_object_permission(self, request, view, obj):
        return obj.business_user == request.user