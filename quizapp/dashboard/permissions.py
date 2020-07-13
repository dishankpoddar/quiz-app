from rest_framework import permissions

class IsTeacher(permissions.BasePermission):
    def has_object_permission(self,request,view,obj):
        try:
            request.user.teacher
            return(True)
        except:
            return(False)

class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self,request,view,obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user.teacher