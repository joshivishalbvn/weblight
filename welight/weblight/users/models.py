# users/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import datetime

class UserManager(BaseUserManager):
    def create_user(self, email, **extra_fields):
        if not email:
            raise ValueError("User must have an email")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        if not email:
            raise ValueError("User must have an email")

        if not username:
            raise ValueError("User must have an username")

        if not password:
            raise ValueError("User must have a password")

        user = self.model(email=self.normalize_email(email))
        user.username = username
        user.set_password(password)
        user.is_superuser = True
        user.is_admin = True
        user.is_staff = True
        user.is_active = True
        user.save(using=self._db)
        return user
    
ADMIN = "admin"
MANAGER = "manager"
EMPLOYEE = "employee"

ROLE_CHOICES = (
    (ADMIN, ADMIN),
    (MANAGER, MANAGER),
    (EMPLOYEE, EMPLOYEE),
)

class User(AbstractUser):
    """
    User Detail Model
    """

    phone_number = models.CharField(max_length=15)
    role = models.CharField(choices=ROLE_CHOICES,null=True, blank=True)
    reset_password_token = models.CharField(max_length=255, blank=True, null=True)

    USERNAME_FIELD = 'email' 
    REQUIRED_FIELDS = ['phone_number']

    objects = UserManager()


    def __str__(self):
        return self.email
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['email'], name='unique_email')
        ]


class SmsOtp(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True,related_name="user_sms_otp")
    otp = models.IntegerField(default=0)
    expired_time = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.expired_time = datetime.datetime.now() + datetime.timedelta(minutes=15)
        super().save(*args, **kwargs)

    def delete_by_sms(user):
        obj = SmsOtp.objects.filter(user=user).last()
        if obj:
            obj.delete()