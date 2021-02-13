from rest_framework import status
from rest_framework.test import APITestCase
from .models import CustomUser, ResetPassword, ResetEmail, Confirm


class AccountTests(APITestCase):

    def register(self, *, email='someMail@mail.ru', password='SomeStrongPassword1'):
        url = '/account/register/'
        data = {
            'email': email,
            'password': password
        }
        return self.client.post(url, data, format='json')

    def auth(self, *, email='someMail@mail.ru', password='SomeStrongPassword1'):
        login_url = '/account/auth/'
        data = {
            'email': email,
            'password': password
        }

        return self.client.post(login_url, data, format='json')

    def test_create_account(self):

        url = '/account/register/'
        data = {
            'email': 'someMail@mail.ru',
            'password': 'SomeStrongPassword1'
        }
        response = self.register()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.filter(email=data['email']).count(), 1)

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_auth(self):
        login_url = '/account/auth/'
        fake_data = {
            'email': 'someMail@mail.ru',
            'password': 'SomeStrongPassword'
        }
        self.register()

        response = self.auth()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(login_url, fake_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def get_reset_key(self, *, reset_key_url, reset_model):
        """ Получение ключа для смены пароля/email/подтверждения """

        reset_key_data = {
            'email': 'someMail@mail.ru',
        }
        response = self.client.post(reset_key_url, reset_key_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = CustomUser.objects.get(email='someMail@mail.ru')
        reset_items = reset_model.objects.filter(user=user)

        self.assertEqual(reset_items.count(), 1)
        reset_item = reset_items[0]
        return reset_item.key

    def test_reset_password(self):
        self.register()
        key = self.get_reset_key(reset_key_url='/account/reset_password_key/', reset_model=ResetPassword)
        reset_url = '/account/reset_password/'
        reset_data = {
            'email': 'someMail@mail.ru',
            'key': key,
            'new_password': 'SomeStrongPassword2'
        }
        response = self.client.post(reset_url, reset_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.auth(password='SomeStrongPassword2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reset_email(self):
        self.register()
        key = self.get_reset_key(reset_key_url='/account/reset_email_key/', reset_model=ResetEmail)
        reset_url = '/account/reset_email/'
        reset_data = {
            'email': 'someMail@mail.ru',
            'key': key,
            'new_email': 'someMail2@mail.ru'
        }
        response = self.client.post(reset_url, reset_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.auth(email='someMail2@mail.ru')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_confirm(self):
        self.register()
        key = self.get_reset_key(reset_key_url='/account/confirm_key/', reset_model=Confirm)
        reset_url = '/account/confirm/'
        reset_data = {
            'email': 'someMail@mail.ru',
            'key': key,
        }
        response = self.client.post(reset_url, reset_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user = CustomUser.objects.get(email='someMail@mail.ru')
        self.assertEqual(user.confirmed, True)
