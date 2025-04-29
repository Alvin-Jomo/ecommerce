from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class ApprovedUserBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            # Attempt to get the user by username
            user = UserModel.objects.get(username=username)
            # Check if the password is correct and the user is active and approved
            if user.check_password(password) and user.is_active and user.is_approved:
                return user
        except UserModel.DoesNotExist:
            return None
        return None