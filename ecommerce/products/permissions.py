from rest_framework import permissions

class IsOwnerOrStaffOrReadOnly(permissions.BasePermission):
    """
    SAFE methods allowed for anyone.
    Create: authenticated users.
    Update / Delete: owner OR staff users only.
    """

    def has_permission(self, request, view):
        # list and retrieve are allowed to anyone (or use IsAuthenticatedOrReadOnly in settings)
        if request.method in permissions.SAFE_METHODS:
            return True
        # POST requires authentication
        if request.method == 'POST':
            return request.user and request.user.is_authenticated
        # For PUT/PATCH/DELETE defer to object-level permission
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # staff allowed
        if request.user and request.user.is_staff:
            return True
        # owner allowed
        return obj.owner == request.user
