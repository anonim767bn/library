from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'books', views.BookViewSet)
router.register(r'genres', views.GenreViewSet)
router.register(r'authors', views.AuthorViewSet)

urlpatterns = [
    path('', views.main, name='homepage'),
    path('books/', views.BookListView.as_view(), name='books'),
    path('book/', views.book_view, name='book'),
    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('author/', views.author_view, name='author'),
    path('genres/', views.GenreListView.as_view(), name='genres'),
    path('genre/', views.genre_view, name='genre'),
    path('api/', include(router.urls)),
    path('register/', views.register, name='register'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api-auth/', include('rest_framework.urls'), name='rest_framework'),
    path('profile/', views.profile, name='profile'),
    path('buy/', views.buy, name='buy'),
]