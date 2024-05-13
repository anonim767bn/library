from typing import Any
from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.core import paginator as django_paginator, exceptions
from rest_framework import viewsets, permissions
from django.contrib.auth import mixins, decorators

from .serializers import BookSerializer, GenreSerializer, AuthorSerializer
from .models import Book, Author, Genre, Client
from .forms import RegistrationForm, AddFundsForm

def main(request):
    return render(
        request,
        'index.html',
        context={
            'books': Book.objects.count(),
            'authors': Author.objects.count(),
            'genres': Genre.objects.count(),
        }
    )

def create_listview(model_class, plural_name, template):
    class CustomListView(mixins.LoginRequiredMixin, ListView):
        model = model_class
        template_name = template
        paginate_by = 10
        context_object_name = plural_name

        def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
            context = super().get_context_data(**kwargs)
            instances = model_class.objects.all()
            paginator = django_paginator.Paginator(instances, 10)
            page = self.request.GET.get('page')
            page_obj = paginator.get_page(page)
            context[f'{plural_name}_list'] = page_obj
            return context
    return CustomListView

BookListView = create_listview(Book, 'books', 'catalog/books.html')
GenreListView = create_listview(Genre, 'genres', 'catalog/genres.html')
AuthorListView = create_listview(Author, 'authors', 'catalog/authors.html')
    
def create_view(model, model_name, template, redirect_page):
    @decorators.login_required
    def view(request):
        id_ = request.GET.get('id', None)
        if not id_:
            return redirect(redirect_page)
        try:
            target = model.objects.get(id=id_) if id_ else None
        except exceptions.ValidationError:
            return redirect(redirect_page)
        if not target:
            return redirect(redirect_page)
        context={model_name: target}
        if model == Book:
            client = Client.objects.get(user=request.user)
            context['client_has_book'] = target in client.books.all()
        return render(
            request,
            template,
            context,
        )
    return view

book_view = create_view(Book, 'book', 'entities/book.html', 'books')
author_view = create_view(Author, 'author', 'entities/author.html', 'authors')
genre_view = create_view(Genre, 'genre', 'entities/genre.html', 'genres')

class APIPermission(permissions.BasePermission):
    _safe_methods = ['GET', 'HEAD', 'OPTIONS']
    _unsafe_methods = ['POST', 'PUT', 'DELETE']

    def has_permission(self, request, _):
        if request.method in self._safe_methods and (request.user and request.user.is_authenticated):
            return True
        if request.method in self._unsafe_methods and (request.user and request.user.is_superuser):
            return True
        return False

def create_viewset(model_class, serializer):
    class CustomViewSet(viewsets.ModelViewSet):
        queryset = model_class.objects.all()
        serializer_class = serializer
        permission_classes = [APIPermission]

    return CustomViewSet

BookViewSet = create_viewset(Book, BookSerializer)
AuthorViewSet = create_viewset(Author, AuthorSerializer)
GenreViewSet = create_viewset(Genre, GenreSerializer)

def register(request):
    errors = ''
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Client.objects.create(user=user)
        else:
            errors = form.errors
    else:
        form = RegistrationForm()

    return render(
        request,
        'registration/register.html',
        {
            'form': form,
            'errors': errors,
        }
    )

@decorators.login_required
def profile(request):
    client = Client.objects.get(user=request.user)
    attrs = 'username', 'first_name', 'last_name', 'email', 'money'

    if request.method == 'POST':
        form = AddFundsForm(request.POST)
        if form.is_valid():
            money = form.cleaned_data.get('money', None)
            client.money += money
            client.save()
    else:
        form = AddFundsForm()
    
    client_data = {attr: getattr(client, attr) for attr in attrs}

    return render(
        request,
        'pages/profile.html',
        {
            'form': form,
            'client_data': client_data,
            'client_books': client.books.all(),
        }
    )

@decorators.login_required
def buy(request):
    book_id = request.GET.get('id', None)
    if not book_id:
        return redirect('books')
    try:
        book = Book.objects.get(id=book_id) if book_id else None
    except exceptions.ValidationError:
        return redirect('books')
    if not book:
        return redirect('books')
    client = Client.objects.get(user=request.user)
    client_has_book = book in client.books.all()
    if request.method == 'POST' and book and client.money >= book.price:
        client.books.add(book)
        client.money -= book.price
        client.save()
        return redirect('profile')

    return render(
        request,
        'pages/buy.html',
        {
            'money': client.money,
            'book': book,
            'client_has_book': client_has_book,
        }
    )