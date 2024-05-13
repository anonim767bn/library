from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework import status

from library_app.models import Client, Book, Genre, Author

def create_test_with_auth(url, page_name, template, auth=True):
    def method(self):
        self.client = APIClient()
        if auth:
            self.user = User.objects.create(username='user', password='user')
            Client.objects.create(user=self.user)
            self.client.force_login(self.user)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTemplateUsed(response, template)

        response = self.client.get(reverse(page_name))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    return method

def create_test_no_auth(url):
    def method(self):
        self.client = APIClient()

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    return method

def create_test_instance(url, model, creation_attrs):
    def method(self):
        self.client = APIClient()
        self.user = User.objects.create(username='user', password='user')
        Client.objects.create(user=self.user)
        self.target_id = model.objects.create(**creation_attrs).id
        
        # GET with no auth
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        self.client.force_login(user=self.user)
        # GET WITH auth, but without query
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        # GET WITH auth, id in query is invalid
        response = self.client.get(f'{url}?id=123')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        # GET with auth and with valid id
        target_url = f'{url}?id={self.target_id}'
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    return method

# required order: url, page name, template
pages = (
    ('/books/', 'books', 'catalog/books.html'),
    ('/genres/', 'genres', 'catalog/genres.html'),
    ('/authors/', 'authors', 'catalog/authors.html'),
    ('/profile/', 'profile', 'pages/profile.html'),
)
base_pages = (
    ('', 'homepage', 'index.html'),
    ('/register/', 'register', 'registration/register.html'),
    ('/accounts/login/', 'login', 'registration/login.html'),
)
methods = {f'test_{page[1]}': create_test_with_auth(*page) for page in (list(pages) + list(base_pages))}
TestPagesAuth = type('TestPages', (TestCase,), methods)

methods_no_auth = {f'test_{url}': create_test_no_auth(url) for url, _, _ in pages}
base_pages_no_auth = {f'test_{page[1]}':create_test_with_auth(*page, auth=False) for page in base_pages}
methods_no_auth.update(base_pages_no_auth)
TestPagesNoAuth = type('TestPagesNoAuth', (TestCase,), methods_no_auth)

instance_pages = (
    ('/buy/', Book, {'title': 'A', 'volume': 1}),
    ('/book/', Book, {'title': 'A', 'volume': 1}),
    ('/genre/', Genre, {'name': 'A'}),
    ('/author/', Author, {'full_name': 'A'}),
)
methods_instance = {f'test_{page[1].__name__}': create_test_instance(*page) for page in instance_pages}
TestInstancePages = type('TestInstancePages', (TestCase,), methods_instance)

