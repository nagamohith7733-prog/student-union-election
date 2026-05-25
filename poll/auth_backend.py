from django.contrib.auth.backends import ModelBackend
from .models import StudentProfile

class RegNoAuthBackend(ModelBackend):
    def authenticate(self, request, registration_number=None, password=None, **kwargs):
        try:
            profile = StudentProfile.objects.get(registration_number=registration_number)
            return super().authenticate(
                request,
                username=profile.user.username,
                password=password
            )
        except StudentProfile.DoesNotExist:
            return None