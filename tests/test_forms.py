from django.test import TestCase
from django.contrib.auth.models import User

from library_app.forms import AddFundsForm, RegistrationForm
from library_app.config import MONEY_MAX_DIGITS, MONEY_DECIMAL_PLACES


class AddFundsFormTest(TestCase):
    def test_long_field(self):
        form = AddFundsForm(data={'money': int('9' * (MONEY_MAX_DIGITS + 1))})
        self.assertFalse(form.is_valid())

    def test_too_much_dp(self):
        dp = '9' * (MONEY_DECIMAL_PLACES + 1)
        form = AddFundsForm(data={'money': float(f'1.{dp}')})
        self.assertFalse(form.is_valid())

    def test_negative_money(self):
        self.assertFalse(AddFundsForm(data={'money': -1}).is_valid())

    def test_zero_money(self):
        self.assertFalse(AddFundsForm(data={'money': 0}).is_valid())

    def test_valid(self):
        self.assertTrue(AddFundsForm(data={'money': 100}).is_valid())


class RegistrationFormTest(TestCase):
    _valid_data = {
        'username': 'username',
        'first_name': 'first_name',
        'last_name': 'last_name',
        'email': 'email@email.com',
        'password1': 'Azpm1029!',
        'password2': 'Azpm1029!',
    }

    def test_valid(self):
        self.assertTrue(RegistrationForm(data=self._valid_data).is_valid())

    def invalid(self, invalid_data):
        data = self._valid_data.copy()
        for field, value in invalid_data:
            data[field] = value
        self.assertFalse(RegistrationForm(data=data).is_valid())

    def test_short_password(self):
        self.invalid(
            (
                ('password1', 'abc'),
                ('password2', 'abc'),
            )
        )

    def test_common_password(self):
        self.invalid(
            (
                ('password1', 'abcdef123'),
                ('password2', 'abcdef123'),
            )
        )

    def test_different_passwords(self):
        self.invalid(
            (
                ('password1', 'ASDksdjn9734'),
                ('password2', 'LKKJdfnalnd234329'),
            )
        )
    
    def test_invalid_email(self):
        self.invalid(
            (
                ('email', 'abc'),
            )
        )

    def test_existing_user(self):
        username, password = 'username', 'password'
        User.objects.create(username=username, password=password)
        self.invalid(
            (
                ('username', username),
                ('password', password),
            )
        )
