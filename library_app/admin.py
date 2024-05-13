from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from datetime import date
from django.utils.translation import gettext_lazy as _

from .models import Author, Genre, Book, BookAuthor, BookGenre, Client, BookClient

class BookAuthorInline(admin.TabularInline):
    model = BookAuthor
    extra = 1

class BookGenreInline(admin.TabularInline):
    model = BookGenre
    extra = 1

class BookClientInline(admin.TabularInline):
    model = BookClient
    extra = 1

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    model = Client
    inlines = (BookClientInline,)

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    model = Author
    inlines = (BookAuthorInline,)

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    model = Genre

class NewestBookFilter(admin.SimpleListFilter):
    title = _('recency')
    parameter_name = 'recency'

    def lookups(self, *args) -> list[tuple[str, str]]:
        return [
            ('10yo', _('Written in the last 10 years')),
            ('20yo', _('Written in the last 20 years')),
        ]
    
    def queryset(self, request: Any, queryset: QuerySet[Any]) -> QuerySet[Any]:
        decade = 10
        if self.value() == '10yo':
            return queryset.filter(year__gte=date.today().year-decade)
        elif self.value() == '20yo':
            return queryset.filter(year__gte=date.today().year-decade*2)
        return queryset
    

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    model = Book
    inlines = (BookGenreInline, BookAuthorInline)
    list_filter = (
        'type',
        'genres',
        NewestBookFilter,
    )

@admin.register(BookAuthor)
class BookAuthorAdmin(admin.ModelAdmin):
    model = BookAuthor

@admin.register(BookGenre)
class BookGenreAdmin(admin.ModelAdmin):
    model = BookGenre