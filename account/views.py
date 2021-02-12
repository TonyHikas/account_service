import datetime
from datetime import timedelta
from django.contrib.auth import authenticate

from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from account.permitions import IsAdmin

from .models import Confirm, CustomUser, ResetEmail, ResetPassword
from .serializers import (AuthSerializer, ConfirmGetSerializer,
                          ConfirmPostSerializer, RegisterSerializer,
                          ResetEmailGetSerializer, ResetEmailPostSerializer,
                          ResetPasswordGetSerializer,
                          ResetPasswordPostSerializer, UserSerializer)


class UserViewSet(viewsets.ModelViewSet):
    """
    Сет для работы с пользователем
    """
    permission_classes = [IsAdminUser]
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['get'], permission_classes=[IsAdmin])
    def admin_stat(self, request):

        count = CustomUser.objects.count()
        today = CustomUser.objects.filter(date_joined__date=datetime.date.today()).count()

        return Response({"count": count, "today": today}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """ Регистрация """
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = Token.objects.create(user=user)
            
            return Response({"token": token.key}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def auth(self, request):
        serializer = AuthSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(username=serializer.data["email"], password=serializer.data["password"])
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        return Response({"error": ["Неправильный email или пароль"]}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def reset_password_key(self, request):
        serializer = ResetPasswordGetSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        pass_resets = ResetPassword.objects.filter(user=serializer.user[0], is_used=False).order_by('-created_at')
        if pass_resets.exists():
            pass_resets = pass_resets[0]
            if pass_resets.created_at + timedelta(minutes=1) > timezone.now():
                return Response(status=status.HTTP_429_TOO_MANY_REQUESTS)
        serializer.save()
        return Response(status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def reset_password(self, request):
        serializer = ResetPasswordPostSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def reset_email_key(self, request):
        serializer = ResetEmailGetSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        email_resets = ResetEmail.objects.filter(user=serializer.user[0], is_used=False).order_by('-created_at')
        if email_resets.exists():
            email_resets = email_resets[0]
            if email_resets.created_at + timedelta(minutes=1) > timezone.now():
                return Response(status=status.HTTP_429_TOO_MANY_REQUESTS)
        serializer.save()
        return Response(status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def reset_email(self, request):
        serializer = ResetEmailPostSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def confirm_key(self, request):
        serializer = ConfirmGetSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        conf = Confirm.objects.filter(user=serializer.user[0], is_used=False).order_by('-created_at')
        if conf.exists():
            conf = conf[0]
            if conf.created_at + timedelta(minutes=1) > timezone.now():
                return Response(status=status.HTTP_429_TOO_MANY_REQUESTS)
        serializer.save()
        return Response(status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def confirm(self, request):
        serializer = ConfirmPostSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def info(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
