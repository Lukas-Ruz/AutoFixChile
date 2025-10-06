from django.contrib.auth import get_user_model

def user_context(request):

    User = get_user_model() 
    return {
        'user': request.user if request.user.is_authenticated else None,
    }
