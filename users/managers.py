from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):

    def create_user(self, display_name=None, password=None):

        if not display_name:
            raise ValueError('empty-display-name')
        #if not email:
            #raise ValueError('Email must be set!')
        if not password:
            raise ValueError('empty-password')
        #email = self.normalize_email(email)
        user = self.model(display_name=display_name)
        user.set_password(password)
        user.save()
        return user
        
    def create_superuser(self, display_name=None, email=None, password=None):

        if not email:
            raise ValueError('Email must be set!')
        if not display_name:
            raise ValueError('Display Name must be set!')
        if not password:
            raise ValueError('Password must be set!')
        email = self.normalize_email(email)
        user = self.model(display_name=display_name, email=email, is_admin=True, is_active=True, is_staff=True, is_superuser=True)
        user.set_password(password)
        user.save()
        return user

