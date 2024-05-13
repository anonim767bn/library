from typing import Any, Iterable
from django.db import models
from uuid import uuid4
from datetime import datetime, timezone, date
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf.global_settings import AUTH_USER_MODEL

def get_datetime() -> datetime:
    return datetime.now(timezone.utc)

class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True

def check_positive(number) -> None:
    if number < 0:
        raise ValidationError(
            'value has to be greater than zero',
        )

def check_modified(dt: datetime) -> None:
    if dt > get_datetime():
        raise ValidationError(
            _('Date and time is bigger than current!'),
            params={'modified': dt}
        )

def check_created(dt: datetime) -> None:
    if dt > get_datetime():
        raise ValidationError(
            _('Date and time is bigger than current!'),
            params={'created': dt}
        )

class CreatedMixin(models.Model):
    created = models.DateTimeField(
        _('created'), null=True, blank=True,
        default=get_datetime, validators=[check_created],
    )

    class Meta:
        abstract = True

class ModifiedMixin(models.Model):
    modified = models.DateTimeField(
        _('modified'), null=True, blank=True,
        default=get_datetime, validators=[check_modified],
    )

    class Meta:
        abstract = True

class Author(UUIDMixin, CreatedMixin, ModifiedMixin):
    full_name = models.TextField(_('full name'), null=False, blank=False)

    books = models.ManyToManyField('Book', verbose_name=_('books'), through='BookAuthor')

    def __str__(self) -> str:
        return self.full_name

    class Meta:
        db_table = '"library"."author"'
        ordering = ['full_name']
        verbose_name = _('author')
        verbose_name_plural = _('authors')

class Genre(UUIDMixin, CreatedMixin, ModifiedMixin):
    name = models.TextField(_('name'), null=False, blank=False)
    description = models.TextField(_('description'), null=True, blank=True)

    books = models.ManyToManyField('Book', verbose_name=_('books'), through='BookGenre')

    def __str__(self) -> str:
        return self.name
    
    class Meta:
        db_table = '"library"."genre"'
        ordering = ['name']
        verbose_name = _('genre')
        verbose_name_plural = _('genres')

def check_year(year: int) -> None:
    if year > date.today().year:
        raise ValidationError(
            _('Year is bigger than current year!'),
            params={'year': year},
        )

book_types = (
    ('book', _('book')),
    ('magazine', _('magazine')),
)

class BookManager(models.Manager):
    def create(self, **kwargs: Any) -> Any:
        if 'volume' not in kwargs:
            raise ValidationError('volume field is required')
        else:
            check_positive(kwargs['volume'])

        if 'year' in kwargs.keys():
            check_year(kwargs['year'])

        if 'price' in kwargs.keys():
            check_positive(kwargs['price'])
        
        available_types = [book_type for book_type, _ in book_types]
        if 'type' in kwargs.keys() and kwargs['type'] not in available_types:
            raise ValidationError(f'available book types are: {available_types}')
        
        return super().create(**kwargs)

    def filter_book_by_author(self, author_name: str):
        return self.filter(authors__full_name=author_name).filter(type='book')

class Book(UUIDMixin, CreatedMixin, ModifiedMixin):
    title = models.TextField(_('title'), null=False, blank=False)
    description = models.TextField(_('description'), null=True, blank=True)
    volume = models.PositiveIntegerField(_('volume'), null=False, blank=False)
    type = models.TextField(_('type'), null=True, blank=True, choices=book_types)
    year = models.IntegerField(_('year'), null=True, blank=True, validators=[check_year])
    price = models.DecimalField(
        verbose_name=_('price'),
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[check_positive],
    )

    authors = models.ManyToManyField(Author, verbose_name=_('authors'), through='BookAuthor')
    genres = models.ManyToManyField(Genre, verbose_name=_('genres'), through='BookGenre')
    objects = BookManager()

    def save(self, *args, **kwargs):
        check_created(self.created)
        check_modified(self.modified)
        check_positive(self.price)
        if self.year:
            check_year(self.year)
        if self.type:
            available_types = [book_type for book_type, _ in book_types]
            if self.type not in available_types:
                raise ValidationError(f'available book types are: {available_types}')

        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'"{self.title}", {self.type}, {self.volume} pages'

    class Meta:
        db_table = '"library"."book"'
        ordering = ['title', 'type', 'year']
        verbose_name = _('book')
        verbose_name_plural = _('books')

class BookGenre(UUIDMixin, CreatedMixin):
    book = models.ForeignKey(Book, verbose_name=_('book'), on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, verbose_name=_('genre'), on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.book} - {self.genre}'

    class Meta:
        db_table = '"library"."book_genre"'
        unique_together = (
            ('book', 'genre'),
        )
        verbose_name = _('relationship book genre')
        verbose_name_plural = _('relationships book genre')

class BookAuthor(UUIDMixin, CreatedMixin):
    book = models.ForeignKey(Book, verbose_name=_('book'), on_delete=models.CASCADE)
    author = models.ForeignKey(Author, verbose_name=_('author'), on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.book} - {self.author}'

    class Meta:
        db_table = '"library"."book_author"'
        unique_together = (
            ('book', 'author'),
        )
        verbose_name = _('relationship book author')
        verbose_name_plural = _('relationships book author')

class ClientManager(models.Manager):
    def create(self, **kwargs: Any) -> Any:
        if 'money' in kwargs.keys():
            check_positive(kwargs['money'])
        return super().create(**kwargs)

class Client(UUIDMixin, CreatedMixin, ModifiedMixin):
    money = models.DecimalField(
        verbose_name=_('money'),
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[check_positive],
    )
    user = models.OneToOneField(
        AUTH_USER_MODEL, verbose_name=_('user'),
        null=False, blank=False, 
        unique=True, on_delete=models.CASCADE
    )
    books = models.ManyToManyField(Book, verbose_name=_('books'), through='BookClient')
    objects = ClientManager()

    def save(self, *args, **kwargs) -> None:
        check_positive(self.money)
        return super().save(*args, **kwargs)

    class Meta:
        db_table = '"library"."client"'
        verbose_name = _('client')
        verbose_name_plural = _('clients')

    @property
    def username(self) -> str:
        return self.user.username
    
    @property
    def first_name(self) -> str:
        return self.user.first_name
    
    @property
    def last_name(self) -> str:
        return self.user.last_name
    
    @property
    def email(self) -> str:
        return self.user.email
    
    def __str__(self) -> str:
        return f'{self.username} {self.first_name} {self.last_name}'

class BookClient(UUIDMixin, CreatedMixin):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name=_('book'))
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name=_('client'))

    class Meta:
        db_table = '"library"."book_client"'
        verbose_name = _('relationship book client')
        verbose_name_plural = _('relationships book client')
        unique_together = (
            ('book', 'client'),
        )
