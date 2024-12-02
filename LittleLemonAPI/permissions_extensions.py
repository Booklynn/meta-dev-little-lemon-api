from rest_framework.permissions import BasePermission

class IsManager(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return 'Manager' in request.user.groups.values_list('name', flat=True) or \
               'Admin' in request.user.groups.values_list('name', flat=True)
    
class IsDeliveryCrew(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return 'Delivery crew' in request.user.groups.values_list('name', flat=True)
