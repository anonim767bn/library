from rest_framework.serializers import HyperlinkedModelSerializer

from .models import Book, Genre, Author

class BookSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'description',
            'type', 'year', 'volume',
            'created', 'modified',
        ]

class GenreSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Genre
        fields = [
            'id', 'name', 'description', 'created', 'modified',
        ]

class AuthorSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Author
        fields = [
            'id', 'full_name', 'created', 'modified',
        ]