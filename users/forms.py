from allauth.account.forms import SignupForm
from django import forms
from .models import UserSettings


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Введите ваше имя"}),
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Введите вашу фамилию"}),
    )
    phone_number = forms.CharField(
        max_length=12,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "XXX XX XX XX",
                "pattern": r"\d{3}\s\d{2}\s\d{2}\s\d{2}",
            }
        ),
    )
    company_name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Название компании"}),
    )
    owner_name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Имя владельца"}),
    )
    
    
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        # Удаляем все пробелы и нецифровые символы
        phone_digits = ''.join(filter(str.isdigit, phone))
        
        if len(phone_digits) != 9:
            raise forms.ValidationError('Номер телефона должен содержать 9 цифр')
            
        # Форматируем номер перед сохранением
        formatted_phone = f"{phone_digits[:3]} {phone_digits[3:5]} {phone_digits[5:7]} {phone_digits[7:9]}"
        return formatted_phone

    def save(self, request):
        # Сохраняем основного пользователя
        user = super().save(request)

        # Сохраняем основные поля пользователя
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.save()

        # Обновляем настройки пользователя
        user_settings = UserSettings.objects.get_or_create(user=user)[0]
        user_settings.phone_number = self.cleaned_data["phone_number"]
        user_settings.company_name = self.cleaned_data.get("company_name", "")
        user_settings.owner_name = self.cleaned_data.get("owner_name", "")
        user_settings.save()

        return user


# views.py (если нужно получить номер телефона в представлении)
def some_view(request):
    phone_number = (
        request.user.settings.phone_number
    )  # Так можно получить номер телефона


from django import forms
from .models import UserSettings


class ProfileSettingsForm(forms.Form):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Введите ваше имя"}),
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Введите вашу фамилию"}),
    )
    phone_number = forms.CharField(
        max_length=12,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "XXX XX XX XX",
                "pattern": r"\d{3}\s\d{2}\s\d{2}\s\d{2}",
            }
        ),
    )
    company_name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Название компании"}),
    )
    owner_name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Имя владельца"}),
    )

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number")
        phone_digits = "".join(filter(str.isdigit, phone))

        if len(phone_digits) != 9:
            raise forms.ValidationError("Номер телефона должен содержать 9 цифр")

        formatted_phone = f"{phone_digits[:3]} {phone_digits[3:5]} {phone_digits[5:7]} {phone_digits[7:9]}"
        return formatted_phone

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-input"
