from django.contrib.auth.forms import AuthenticationForm


class CustomAuthenticationForm(AuthenticationForm):
    error_messages = {
        'invalid_login': "Невірний логін або пароль. Будь ласка, спробуйте ще раз.",
        'inactive': "Цей обліковий запис неактивний.",
    }