from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import datetime, timezone

from library_app import models

def create_test(attr, value):
    def new_test(self):
        data = self._creation_attrs.copy()
        data[attr] = value
        with self.assertRaises(ValidationError):
            self._model_class.objects.create(**data)
    return new_test

def add_tests(tests):
    def decorator(class_):
        for num, values in enumerate(tests):
            attr, value = values
            method = create_test(attr, value)
            setattr(class_, f'test_{attr}_{num}', method)
        return class_
    return decorator

def create_model_test(model_class, creation_attrs, tests):
    @add_tests(tests)
    class ModelTest(TestCase):
        _model_class = model_class
        _creation_attrs = creation_attrs

        def test_successful_creation(self):
            self._model_class.objects.create(**self._creation_attrs)
    return ModelTest

book_attrs = {'title': 'ABC', 'type': 'book', 'volume': 123}
genre_attrs = {'name': 'ABC'}
author_attrs = {'full_name': 'Muxeem Nudga'}

book_tests = (
    ('volume', -1),
    ('year', 3000),
    ('price', -10),
    ('type', 'Vadim'),
)

BookModelTest = create_model_test(models.Book, book_attrs, book_tests)
AuthorModelTest = create_model_test(models.Author, author_attrs, [])
GenreModelTest = create_model_test(models.Genre, genre_attrs, [])

PAST_YEAR = 2007
FUTURE_YEAR = 3000

valid_tests = (
    (models.check_created, datetime(PAST_YEAR, 1, 1, 1, 1, 1, 1, tzinfo=timezone.utc)),
    (models.check_modified, datetime(PAST_YEAR, 1, 1, 1, 1, 1, 1, tzinfo=timezone.utc)),
    (models.check_positive, 1),
    (models.check_year, PAST_YEAR),
)
invalid_tests = (
    (models.check_created, datetime(FUTURE_YEAR, 1, 1, 1, 1, 1, 1, tzinfo=timezone.utc)),
    (models.check_modified, datetime(FUTURE_YEAR, 1, 1, 1, 1, 1, 1, tzinfo=timezone.utc)),
    (models.check_positive, -1),
    (models.check_year, FUTURE_YEAR),
)

def create_validation_test(validator, value, valid=True):
    if valid:
        return lambda _: validator(value)
    def test(self):
        with self.assertRaises(ValidationError):
            validator(value)
    return test

valid_methods = {
    f'test_valid_{args[0].__name__}': create_validation_test(*args) for args in valid_tests
}
invalid_methods = {
    f'test_invalid_{args[0].__name__}': create_validation_test(*args, valid=False) for args in invalid_tests
}

TestValidators = type('TestValidators', (TestCase,), valid_methods | invalid_methods)
