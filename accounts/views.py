"""
Authentication views for the Cattle Disease Prediction System.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .forms import FarmerRegistrationForm, LoginForm


def login_view(request):
    """
    User login view.
    Redirects users to their respective dashboards based on role.
    """
    if request.user.is_authenticated:
        return redirect('accounts:redirect_after_login')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # Debug: Print authentication attempt
            print(f"\n[DEBUG LOGIN] Attempting login:")
            print(f"  Username: {username}")
            print(f"  Password length: {len(password)}")
            
            # Check if user exists
            from accounts.models import User
            try:
                user_obj = User.objects.get(username=username)
                print(f"  User exists: YES")
                print(f"  User role: {user_obj.role}")
                print(f"  User active: {user_obj.is_active}")
                print(f"  Has usable password: {user_obj.has_usable_password()}")
            except User.DoesNotExist:
                print(f"  User exists: NO")
                messages.error(request, 'Invalid username. This username does not exist.')
                return render(request, 'accounts/login.html', {'form': form})
            
            # Authenticate user
            user = authenticate(request, username=username, password=password)
            print(f"  Authentication result: {user}")
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    print(f"  Login successful! Role: {user.role}")
                    
                    # Get user's display name
                    try:
                        if hasattr(user, 'farmer_profile'):
                            display_name = user.farmer_profile.full_name
                        else:
                            display_name = user.username
                    except:
                        display_name = user.username
                    
                    messages.success(request, f'Welcome back, {display_name}!')
                    # Redirect based on role
                    print(f"  Redirecting to: accounts:redirect_after_login")
                    return redirect('accounts:redirect_after_login')
                else:
                    print(f"  User is inactive!")
                    messages.error(request, 'Your account is inactive. Please contact administrator.')
            else:
                print(f"  Authentication FAILED - incorrect password")
                messages.error(request, 'Invalid password. Please check your password and try again.')
        else:
            print(f"\n[DEBUG LOGIN] Form validation failed:")
            print(f"  Errors: {form.errors}")
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def redirect_after_login(request):
    """
    Redirect users to their respective dashboards based on role.
    """
    print(f"\n[DEBUG REDIRECT] Redirecting user:")
    print(f"  Username: {request.user.username}")
    print(f"  Role: {request.user.role}")
    print(f"  Is farmer: {request.user.is_farmer()}")
    print(f"  Is vet: {request.user.is_vet()}")
    print(f"  Is ministry: {request.user.is_ministry()}")
    
    if request.user.is_farmer():
        print(f"  Redirecting to: farmers:dashboard")
        return redirect('farmers:dashboard')
    elif request.user.is_vet():
        print(f"  Redirecting to: vets:dashboard")
        return redirect('vets:dashboard')
    elif request.user.is_ministry():
        print(f"  Redirecting to: ministry:dashboard")
        return redirect('ministry:dashboard')
    else:
        print(f"  No role match - redirecting to: landing:home")
        return redirect('landing:home')


def logout_view(request):
    """
    Custom logout view with confirmation page.
    Supports both GET (show confirmation) and POST (actually logout).
    """
    if request.method == 'POST':
        # Get user info before logging out
        user_name = None
        if request.user.is_authenticated:
            try:
                if hasattr(request.user, 'farmer_profile'):
                    user_name = request.user.farmer_profile.full_name
                elif hasattr(request.user, 'vet_profile'):
                    user_name = request.user.vet_profile.full_name
                else:
                    user_name = request.user.username
            except:
                user_name = request.user.username
        
        # Perform logout
        logout(request)
        
        # Show success message
        if user_name:
            messages.success(request, f'Goodbye {user_name}! You have been logged out successfully.')
        else:
            messages.success(request, 'You have been logged out successfully.')
        
        # Redirect to home page
        return redirect('landing:home')
    
    # GET request - show logout confirmation page
    return render(request, 'accounts/logout.html')
