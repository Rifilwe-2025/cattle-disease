"""
Forms for the Farmers app.
"""
from django import forms
from django.core.validators import RegexValidator
from .models import Farmer


class FarmerRegistrationForm(forms.Form):
    """
    Complete farmer registration form with user account creation.
    This form creates both User and Farmer profile.
    """
    # User account fields
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username',
            'required': True
        }),
        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password (min 8 characters)'
        }),
        min_length=8,
        help_text="Password must be at least 8 characters long."
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        }),
        label='Confirm Password'
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com'
        }),
        required=True,
        help_text="Required for password reset. We'll send reset links to this email."
    )
    
    # Farmer profile fields
    full_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Full Name'
        }),
        required=True
    )
    phone_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+263XXXXXXXXX'
        }),
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Enter a valid phone number.")],
        required=True
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
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    district = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'District'
        }),
        required=True
    )
    latitude = forms.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Latitude (optional)',
            'step': '0.000001'
        }),
        help_text="GPS Latitude (optional)"
    )
    longitude = forms.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Longitude (optional)',
            'step': '0.000001'
        }),
        help_text="GPS Longitude (optional)"
    )
    cattle_breed = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Brahman, Angus, Hereford'
        }),
        required=True,
        help_text="Primary cattle breed on your farm"
    )
    number_of_cattle = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Number of cattle',
            'min': 1
        }),
        required=True,
        help_text="Total number of cattle on your farm"
    )
    
    def clean(self):
        """Validate form data."""
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
                raise forms.ValidationError("A user with this username already exists.")
        
        return cleaned_data


class FarmerProfileForm(forms.ModelForm):
    """
    Form for farmer profile update (after registration).
    """
    PROVINCE_CHOICES = [('', 'Select Province')] + [
        ('Bulawayo', 'Bulawayo'), ('Harare', 'Harare'), ('Manicaland', 'Manicaland'),
        ('Mashonaland Central', 'Mashonaland Central'), ('Mashonaland East', 'Mashonaland East'),
        ('Mashonaland West', 'Mashonaland West'), ('Masvingo', 'Masvingo'),
        ('Matabeleland North', 'Matabeleland North'), ('Matabeleland South', 'Matabeleland South'),
        ('Midlands', 'Midlands'),
    ]
    province = forms.ChoiceField(choices=PROVINCE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Farmer
        fields = [
            'full_name', 'phone_number', 'email', 'province', 'district', 'latitude', 'longitude',
            'cattle_breed', 'number_of_cattle', 'farming_type'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+263XXXXXXXXX'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your.email@example.com'}),
            'district': forms.TextInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'cattle_breed': forms.TextInput(attrs={'class': 'form-control'}),
            'number_of_cattle': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'farming_type': forms.Select(attrs={'class': 'form-control'}),
        }


class CaseSubmissionForm(forms.Form):
    """
    Form for submitting a disease case with symptoms and contextual information.
    Collects all 102 features needed for ML prediction (93 symptoms + 9 contextual).
    """
    # Symptom selection (93 symptoms)
    symptoms = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True,
        help_text="Select all symptoms observed in your cattle."
    )
    
    # Contextual Feature 1: Age
    age_years = forms.IntegerField(
        min_value=1,
        max_value=15,
        initial=3,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Age in years (1-15)'
        }),
        required=True,
        help_text="Age of the affected cattle in years"
    )
    
    # Contextual Feature 2: Sex
    sex = forms.ChoiceField(
        choices=[('Male', 'Male'), ('Female', 'Female')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        help_text="Sex of the affected cattle"
    )
    
    # Contextual Feature 3: Breed
    breed = forms.ChoiceField(
        choices=[
            ('Brahman', 'Brahman'),
            ('Mashona', 'Mashona'),
            ('Tuli', 'Tuli'),
            ('Crossbreed', 'Crossbreed')
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        help_text="Breed of the affected cattle"
    )
    
    # Contextual Feature 4: Vaccination Status
    vaccinated = forms.ChoiceField(
        choices=[('Yes', 'Yes'), ('No', 'No')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        help_text="Is the cattle vaccinated?"
    )
    
    # Contextual Feature 5: Herd Size
    herd_size = forms.IntegerField(
        min_value=1,
        max_value=1000,
        initial=20,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Number of cattle in herd'
        }),
        required=True,
        help_text="Total number of cattle in your herd"
    )
    
    # Contextual Feature 6: Farming Type
    farming_type = forms.ChoiceField(
        choices=[
            ('Communal', 'Communal'),
            ('Small-scale', 'Small-scale'),
            ('Commercial', 'Commercial')
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        help_text="Type of farming operation"
    )
    
    # Contextual Feature 7: Recent Movement
    recent_movement = forms.ChoiceField(
        choices=[('Yes', 'Yes'), ('No', 'No')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        help_text="Has the cattle been moved recently (last 30 days)?"
    )
    
    # Contextual Feature 8: Season
    season = forms.ChoiceField(
        choices=[('Dry', 'Dry Season'), ('Rainy', 'Rainy Season')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        help_text="Current season"
    )
    
    # Contextual Feature 9: Province
    province = forms.ChoiceField(
        choices=[
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
        required=True,
        help_text="Province where the cattle is located"
    )
    
    # Additional notes
    notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Additional notes (optional)'
        }),
        required=False,
        help_text="Any additional information about the case."
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Load symptom choices from ML model (93 symptoms only, not contextual features)
        try:
            import joblib
            from django.conf import settings
            feature_names = joblib.load(settings.FEATURE_NAMES_PATH)
            
            # Filter out contextual features - only show symptoms
            contextual_features = ['age_years', 'sex', 'breed', 'vaccinated', 'herd_size',
                                   'farming_type', 'recent_movement', 'season', 'province']
            symptom_names = [f for f in feature_names if f not in contextual_features 
                             and not f.startswith('sex_') and not f.startswith('breed_')
                             and not f.startswith('vaccinated_') and not f.startswith('farming_type_')
                             and not f.startswith('recent_movement_') and not f.startswith('season_')
                             and not f.startswith('province_')]
            
            # Format symptom names for display
            symptom_choices = [(name, name.replace('_', ' ').title()) for name in symptom_names]
            self.fields['symptoms'].choices = symptom_choices
        except Exception as e:
            # Fallback if model files not available
            self.fields['symptoms'].choices = []
