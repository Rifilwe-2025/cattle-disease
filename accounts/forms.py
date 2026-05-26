"""
Forms for authentication and user registration.
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.validators import RegexValidator
from .models import User


class LoginForm(forms.Form):
    """Custom login form - simplified to work with custom User model."""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'required': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'required': True
        })
    )


class FarmerRegistrationForm(forms.ModelForm):
    """
    Registration form for farmers.
    Farmers register directly with their details.
    """
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        min_length=8
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),
        label='Confirm Password'
    )
    full_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'})
    )
    phone_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+263XXXXXXXXX'}),
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Enter a valid phone number.")]
    )
    province = forms.ChoiceField(
        choices=[('', 'Select Province')] + [
            ('Bulawayo', 'Bulawayo'),
            ('Harare', 'Harare'),
            ('Manicaland', 'Manicaland'),
            ('Mashonaland Central', 'Mashonaland Central'),
            ('Mashonaland East', 'Mashonaland East'),
            ('Mashonaland West', 'Mashonaland West'),
            ('Masvingo', 'Masvingo'),
            ('Matabeleland North', 'Matabeleland North'),
            ('Matabeleland South', 'Matabeleland South'),
            ('Midlands', 'Midlands'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    district = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'District'})
    )
    latitude = forms.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Latitude (optional)'})
    )
    longitude = forms.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Longitude (optional)'})
    )
    cattle_breed = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Brahman, Angus'})
    )
    number_of_cattle = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Number of cattle'})
    )
    farming_type = forms.ChoiceField(
        choices=[
            ('', 'Select Farming Type'),
            ('Commercial', 'Commercial'),
            ('Subsistence', 'Subsistence'),
            ('Mixed', 'Mixed'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'password', 'password_confirm', 'full_name', 'phone_number']
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data
    
    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            role='FARMER',
            phone_number=self.cleaned_data['phone_number'],
        )
        return user
