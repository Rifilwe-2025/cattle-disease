"""
Forms for the Vets app.
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import VetApplication, Vet, VaccineRequest, VetAreaReport


class VetApplicationForm(forms.ModelForm):
    """
    Form for vet doctors to apply for registration.
    """
    provinces_served = forms.ChoiceField(
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
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
        help_text="Select the main province where you provide veterinary services"
    )
    
    class Meta:
        model = VetApplication
        fields = [
            'full_name', 'phone_number', 'email', 'license_number',
            'qualification', 'years_of_experience', 'provinces_served',
            'latitude', 'longitude'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'years_of_experience': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Convert provinces_served to JSON
        if 'provinces_served' in self.cleaned_data:
            instance.provinces_served = self.cleaned_data['provinces_served']
        if commit:
            instance.save()
        return instance


class VetRegistrationForm(forms.Form):
    """
    Form for approved vets to register their login credentials and complete their profile.
    """
    # Account credentials
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username'
        }),
        help_text="Username for logging in to the system"
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com'
        }),
        help_text="Your professional email address"
    )
    phone_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+263XXXXXXXXX'
        }),
        help_text="Your contact phone number"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password (min. 8 characters)'
        }),
        min_length=8,
        help_text="Choose a strong password"
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        }),
        label='Confirm Password',
        help_text="Re-enter your password"
    )
    
    # Location information
    province = forms.ChoiceField(
        choices=[('', 'Select Main Province')] + [
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
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Your primary practice location (province)"
    )
    district = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter district name'
        }),
        help_text="Your primary practice location (district)"
    )
    latitude = forms.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., -17.829289',
            'step': '0.000001'
        }),
        help_text="GPS Latitude (Optional - helps farmers find you)"
    )
    longitude = forms.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 31.052254',
            'step': '0.000001'
        }),
        help_text="GPS Longitude (Optional - helps farmers find you)"
    )
    
    # Availability
    is_available = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Available for New Cases',
        help_text="Check this if you're currently accepting new cases"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        username = cleaned_data.get('username')
        
        # Check password match
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")
        
        # Check username uniqueness
        if username:
            from accounts.models import User
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError("A user with this username already exists. Please choose another.")
        
        return cleaned_data


class VetProfileForm(forms.ModelForm):
    """Form for vet profile edit (phone, email, location, availability)."""
    class Meta:
        model = Vet
        fields = ['full_name', 'phone_number', 'email', 'latitude', 'longitude', 'is_available', 'profile_photo']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'profile_photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class VetConsultationForm(forms.Form):
    """
    Form for vets to submit diagnosis and recommendations for a case.
    """
    diagnosis = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Enter your diagnosis...'
        }),
        required=True,
        help_text="Your professional diagnosis of the case"
    )
    recommendations = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Enter treatment recommendations...'
        }),
        required=True,
        help_text="Treatment recommendations and next steps"
    )


class VaccineRequestForm(forms.ModelForm):
    """Form for vets to request vaccines / medical stock from Ministry."""

    class Meta:
        model = VaccineRequest
        fields = ['title', 'vaccine_name', 'quantity', 'priority', 'description']
        labels = {
            'title': _('Title'),
            'vaccine_name': _('Vaccine / product name'),
            'quantity': _('Estimated quantity (doses)'),
            'priority': _('Priority'),
            'description': _('Reason & justification'),
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Short title of request'),
            }),
            'vaccine_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('e.g. FMD vaccine'),
            }),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _(
                    'Explain why you need these vaccines, affected areas, herd sizes, etc.'
                ),
            }),
        }


class VetAreaReportForm(forms.ModelForm):
    """Form for vets to send narrative situation reports to Ministry."""

    class Meta:
        model = VetAreaReport
        fields = ['title', 'summary', 'province', 'district', 'period_start', 'period_end', 'body']
        labels = {
            'title': _('Title'),
            'summary': _('Short summary'),
            'province': _('Province'),
            'district': _('District / area'),
            'period_start': _('Period start'),
            'period_end': _('Period end'),
            'body': _('Detailed report'),
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('e.g. Monthly report – Midlands North'),
            }),
            'summary': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Short summary of main findings'),
            }),
            'province': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Province')}),
            'district': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('District / area (optional)'),
            }),
            'period_start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'period_end': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': _(
                    'Describe disease trends, challenges, vaccine gaps, and your recommendations...'
                ),
            }),
        }
