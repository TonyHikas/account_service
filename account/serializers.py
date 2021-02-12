from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.db.models import F
from django.utils import timezone
from django.utils.crypto import get_random_string
from rest_framework import serializers, status
from rest_framework.authtoken.models import Token

from .models import Confirm, CustomUser, ResetEmail, ResetPassword


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор пользователя
    """

    class Meta:
        model = CustomUser
        fields = ['id', 'confirmed', 'is_superuser', 'date_joined', 'email']


class RegisterSerializer(serializers.Serializer):
    """
    Сериализация регстриции
    """
    email = serializers.EmailField()
    password = serializers.RegexField(
        regex=r'^(?=.*[0-9].*)(?=.*[a-z].*)(?=.*[A-Z].*)[0-9a-zA-Z]{8,}$',
        error_messages={"invalid": [
            "Пароль должен состоять из 8 латинских символов, содержать как мининум 1 заглавную букву и 1 цифру"]}
    )

    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']
        return CustomUser.objects.create_user(email, password)

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
        return value


class AuthSerializer(serializers.Serializer):
    """
    Сериализация авторизации
    """
    email = serializers.EmailField()
    password = serializers.CharField()


class ResetPasswordGetSerializer(serializers.Serializer):
    """
    Сериализация запроса ключа для смены пароля
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        self.user = CustomUser.objects.filter(email=value)
        if not self.user.exists():
            raise serializers.ValidationError("Пользователь с таким email не найден")
        return value

    def create(self, validated_data):
        key = get_random_string(6)
        pass_reset = ResetPassword(
            user=self.user[0],
            key=key,
            prev_password=self.user[0].password,
            final_time=timezone.now() + timedelta(minutes=15),
            is_used=False
        )
        pass_reset.save()
        send_mail('Смена пароля', 'Ваш ключ для подтверждения: ' + pass_reset.key, settings.EMAIL_HOST_USER,
                  [validated_data['email']], fail_silently=False)
        return pass_reset.key


class ResetPasswordPostSerializer(serializers.Serializer):
    """
    Сериализация смены пароля
    """
    email = serializers.EmailField()
    key = serializers.CharField(max_length=20)
    new_password = serializers.RegexField(
        regex=r'^(?=.*[0-9].*)(?=.*[a-z].*)(?=.*[A-Z].*)[0-9a-zA-Z]{8,}$',
        error_messages={"invalid": [
            "Пароль должен состоять из 8 латинских символов, содержать как мининум 1 заглавную букву и 1 цифру"]}
    )

    def validate(self, data):
        # todo добавить проверку не использовался ли пароль до этого
        user = CustomUser.objects.filter(email=data["email"])
        if not user.exists():
            raise serializers.ValidationError({"key": "Неправильный ключ"})
        pass_resets = ResetPassword.objects.filter(user=user[0]).order_by('-created_at')
        if not pass_resets.exists():
            raise serializers.ValidationError({"key": "Неправильный ключ"})
        is_used = False
        for pass_reset in pass_resets:
            is_used = is_used or check_password(data["new_password"], pass_reset.prev_password)
        if is_used:
            raise serializers.ValidationError({"new_password": "Введите пароль, который не использовали ранее"})
        pass_resets = pass_resets[0]
        if pass_resets.final_time + timedelta(minutes=15) < timezone.now():
            raise serializers.ValidationError({"key": "Срок действия ключа истек"})
        if pass_resets.is_used:
            raise serializers.ValidationError({"key": "Срок действия ключа истек"})
        if pass_resets.key != data["key"]:
            raise serializers.ValidationError({"key": "Неправильный ключ"})

        pass_resets.is_used = True
        pass_resets.save()

        return data

    def create(self, validated_data):
        user = CustomUser.objects.get(email=validated_data["email"])
        user.password = make_password(validated_data["new_password"])
        user.save()
        return user


class ResetEmailGetSerializer(serializers.Serializer):
    """
    Сериализация запроса ключа для смены email
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        self.user = CustomUser.objects.filter(email=value)
        if not self.user.exists():
            raise serializers.ValidationError("Пользователь с таким email не найден")
        return value

    def create(self, validated_data):
        key = get_random_string(6)
        email_reset = ResetEmail(
            user=self.user[0],
            key=key,
            prev_email=self.user[0].email,
            final_time=timezone.now() + timedelta(minutes=15),
            is_used=False
        )
        email_reset.save()
        send_mail('Смена email', 'Ваш ключ для подтверждения: ' + email_reset.key, settings.EMAIL_HOST_USER,
                  [validated_data['email']], fail_silently=False)
        return email_reset.key


class ResetEmailPostSerializer(serializers.Serializer):
    """
    Сериализация смены email
    """
    email = serializers.EmailField()
    key = serializers.CharField(max_length=20)
    new_email = serializers.EmailField()

    def validate(self, data):
        user = CustomUser.objects.filter(email=data["email"])
        if not user.exists():
            raise serializers.ValidationError({"key": "Неправильный ключ"})
        email_reset = ResetEmail.objects.filter(user=user[0]).order_by('-created_at')[:1]
        if not email_reset.exists():
            raise serializers.ValidationError({"key": "Неправильный ключ"})
        email_reset = email_reset[0]
        if email_reset.final_time + timedelta(minutes=15) < timezone.now():
            raise serializers.ValidationError({"key": "Срок действия ключа истек"})
        if email_reset.is_used:
            raise serializers.ValidationError({"key": "Срок действия ключа истек"})
        if email_reset.key != data["key"]:
            raise serializers.ValidationError({"key": "Неправильный ключ"})

        other_users = CustomUser.objects.filter(email=data["new_email"])
        if other_users.exists():
            raise serializers.ValidationError({"new_email": "Пользователь с таким email уже существует"})

        email_reset.is_used = True
        email_reset.save()
        return data

    def create(self, validated_data):

        user = CustomUser.objects.get(email=validated_data["email"])
        user.email = validated_data["new_email"]
        user.save()
        return user


class ConfirmGetSerializer(serializers.Serializer):
    """
    Сериализация запроса ключа для подтверждения
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        self.user = CustomUser.objects.filter(email=value)
        if not self.user.exists():
            raise serializers.ValidationError("Пользователь с таким email не найден")
        if self.user[0].confirmed == True:
            raise serializers.ValidationError("Пользователь уже подтверждён")
        return value

    def create(self, validated_data):
        key = get_random_string(6)
        conf = Confirm(
            user=self.user[0],
            key=key,
            final_time=timezone.now() + timedelta(minutes=15),
            is_used=False
        )
        conf.save()
        send_mail('Подтверждение email',
                  'Ссылка для подтверждения email http://cryptorobots.ru/#/confirm/' + validated_data[
                      'email'] + '/' + conf.key, settings.EMAIL_HOST_USER, [validated_data['email']],
                  fail_silently=False)
        return conf.key


class ConfirmPostSerializer(serializers.Serializer):
    """
    Сериализация подтверждения
    """
    email = serializers.EmailField()
    key = serializers.CharField(max_length=20)

    def validate(self, data):
        user = CustomUser.objects.filter(email=data["email"])
        if not user.exists():
            raise serializers.ValidationError({"key": "Неправильный ключ"})
        conf = Confirm.objects.filter(user=user[0]).order_by('-created_at')[:1]
        if not conf.exists():
            raise serializers.ValidationError({"key": "Неправильный ключ"})
        conf = conf[0]
        if conf.final_time + timedelta(minutes=15) < timezone.now():
            raise serializers.ValidationError({"key": "Срок действия ключа истек"})
        if conf.is_used:
            raise serializers.ValidationError({"key": "Срок действия ключа истек"})
        if conf.key != data["key"]:
            raise serializers.ValidationError({"key": "Неправильный ключ"})

        conf.is_used = True
        conf.save()
        return data

    def create(self, validated_data):
        user = CustomUser.objects.get(email=validated_data["email"])
        user.confirmed = True
        user.save()
        return user
