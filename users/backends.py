from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class UserBackend(BaseBackend):

    def authenticate(self, request, display_name=None, password=None):
        try:
            user = User.objects.get(display_name=display_name)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
        
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
