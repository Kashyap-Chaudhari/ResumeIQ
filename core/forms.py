from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label="First Name")
    last_name = forms.CharField(max_length=30, required=True, label="Last Name")
    email = forms.EmailField(required=True, help_text='Required. A valid email address.')
    accept_terms = forms.BooleanField(required=True, label="I agree to the Terms of Service and Privacy Policy")

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email")
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'accept_terms':
                field.widget.attrs.update({'class': 'form-control form-control-saas w-100'})
            else:
                field.widget.attrs.update({'class': 'form-check-input mt-0'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="Email or Username", widget=forms.TextInput(attrs={'class': 'form-control form-control-saas w-100', 'placeholder': 'e.g. demo@student.com'}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class': 'form-control form-control-saas w-100', 'placeholder': '••••••••', 'id': 'passwordInput'}))
    remember_me = forms.BooleanField(required=False, label="Remember me for 30 days", widget=forms.CheckboxInput(attrs={'class': 'form-check-input mt-0'}))
