from django.forms import Form, CharField, DecimalField
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .config import MONEY_MAX_DIGITS, MONEY_DECIMAL_PLACES

class RegistrationForm(UserCreationForm):
    first_name = CharField(max_length=100, required=True)
    last_name = CharField(max_length=100, required=True)
    email = CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class AddFundsForm(Form):
    money = DecimalField(
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES
    )

    def is_valid(self) -> bool:
        is_valid = super().is_valid()
        if not is_valid:
            return False
        money = self.cleaned_data.get('money', None)
        if not money:
            self.add_error('money', ValidationError('an error occured, money field was not specified!'))
            return False
        if money <= 0:
            self.add_error('money', ValidationError('you can only add positive amount of money!'))
            return False
        return True
