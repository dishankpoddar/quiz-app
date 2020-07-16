from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings

def logout_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, logout_url=settings.LOGOUT_URL):
    """
    Decorator for views that checks that the user is logged OUT, redirecting
    to the log-out page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: not u.is_authenticated,
        login_url=logout_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def student_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='login'):
    '''
    Decorator for views that checks that the logged in user is a student,
    redirects to the log-in page if necessary.
    '''
    def is_student(user):
        try:
            user.student
            return(True)
        except:
            return(False)

    actual_decorator = user_passes_test(
        lambda u: is_student(u),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def teacher_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='login'):
    '''
    Decorator for views that checks that the logged in user is a teacher,
    redirects to the log-in page if necessary.
    '''
    def is_teacher(user):
        try:
            return(True)
        except:
            return(False)
            
    actual_decorator = user_passes_test(
        lambda u: is_teacher(u),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
