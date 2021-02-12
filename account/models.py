from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from .managers import CustomUserManager


class CustomUser(AbstractUser):
    """
    Кастомный пользователь с уникальным полем email и без username
    """
    username = None
    email = models.EmailField(_('email address'), unique=True)

    confirmed = models.BooleanField(default=False)
    # подтверждён ли email

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'Users'


class ResetPassword(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    # пользователь к который меняет пароль
    key = models.CharField(max_length=255)
    # ключ для смены пароля
    prev_password = models.CharField(max_length=255)
    # текущий пароль, который пользователь хочет заменить на новый
    final_time = models.DateTimeField()
    # время до которого действует код сброса
    is_used = models.BooleanField()
    # был ли использован код

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ResetEmail(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    # пользователь к который меняет email
    key = models.CharField(max_length=255)
    # ключ для смены email
    prev_email = models.CharField(max_length=255)
    # текущий email, который пользователь хочет заменить на новый
    final_time = models.DateTimeField()
    # время до которого действует код сброса
    is_used = models.BooleanField()
    # был ли использован код

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Confirm(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    # пользователь который подтверждает email
    key = models.CharField(max_length=255)
    # ключ для подтверждения
    final_time = models.DateTimeField()
    # время до которого действует код
    is_used = models.BooleanField()
    # был ли использован код

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
