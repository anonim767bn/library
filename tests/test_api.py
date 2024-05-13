from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

from library_app.models import Book, Author, Genre

def create_apitest(model_class, model_url, creation_attrs):
    class APITest(TestCase):
        _user_creds = {'username': 'abc', 'password': 'abc'}
        _superuser_creds = {
            'username': 'def',
            'password': 'def',
            'is_superuser': True
        }

        def setUp(self):
            self.client = APIClient()
            self.user = User.objects.create(**self._user_creds)
            self.user_token = Token(user=self.user)
            self.superuser = User.objects.create(**self._superuser_creds)
            self.superuser_token = Token(user=self.superuser)

        def get(self, user: User, token: Token):
            self.client.force_authenticate(user=user, token=token)
            response = self.client.get(model_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        def test_get_user(self):
            self.get(self.user, self.user_token)

        def test_get_superuser(self):
            self.get(self.superuser, self.superuser_token)

        def manage(
                self, user: User, token: Token,
                post_status: int,
                put_status: int,
                delete_status: int
            ):
            self.client.force_authenticate(user=user, token=token)

            # POST
            response = self.client.post(model_url, creation_attrs)
            self.assertEqual(response.status_code, post_status)

            # creating object for changes
            created = model_class.objects.create(**creation_attrs)
            url = f'{model_url}{created.id}/'

            # PUT
            response = self.client.put(url, creation_attrs)
            self.assertEqual(response.status_code, put_status)

            # DELETE
            response = self.client.delete(url)
            self.assertEqual(response.status_code, delete_status)

        def test_manage_user(self):
            self.manage(
                self.user, self.user_token,
                status.HTTP_403_FORBIDDEN, status.HTTP_403_FORBIDDEN, status.HTTP_403_FORBIDDEN
            )

        def test_manage_superuser(self):
            self.manage(
                self.superuser, self.superuser_token,
                status.HTTP_201_CREATED, status.HTTP_200_OK, status.HTTP_204_NO_CONTENT
            )

    return APITest

BookApiTest = create_apitest(Book, '/api/books/', {'title': 'a', 'volume': 1})
GenreApiTest = create_apitest(Genre, '/api/genres/', {'name': 'abc'})
AuthorApiTest = create_apitest(Author, '/api/authors/', {'full_name': 'a b c'})