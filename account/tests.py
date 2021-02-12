from rest_framework import status
from rest_framework.test import APITestCase
from .models import CustomUser


class AccountTests(APITestCase):
    def test_create_account(self):

        url = '/account/register/'
        data = {
            'email': 'someMail@mail.ru',
            'password': 'SomeStrongPassword1'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.filter(email=data['email']).count(), 1)

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_auth(self):
        register_url = '/account/register/'
        login_url = '/account/auth/'
        data = {
            'email': 'someMail@mail.ru',
            'password': 'SomeStrongPassword1'
        }
        fake_data = {
            'email': 'someMail@mail.ru',
            'password': 'SomeStrongPassword'
        }
        self.client.post(register_url, data, format='json')

        response = self.client.post(login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(login_url, fake_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
