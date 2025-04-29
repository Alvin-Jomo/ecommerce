from django.shortcuts import redirect, render
from userauths.forms import UserRegisterForm, ProfileForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from userauths.models import Profile, User
import re
from django.core.mail import send_mail
from django.conf import settings
from .backends import ApprovedUserBackend
from django.contrib.auth import get_user_model


def login_view(request):
    """
    Handles user login, allowing login via username, email, or phone number.
    """
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in.")
        return redirect("core:index")  # Redirect to home if already logged in

    if request.method == "POST":
        identifier = request.POST.get("identifier")
        password = request.POST.get("password")

        # Match identifier to username, email, or phone number
        if re.match(r'^[\w\.-]+@[\w\.-]+$', identifier):  # Email
            user = User.objects.filter(email=identifier).first()
        elif re.match(r'^(07|01)\d{8}$', identifier):  # Phone number
            user = User.objects.filter(profile__phone=identifier).first()
        else:  # Username
            user = User.objects.filter(username=identifier).first()

        # Authenticate user
        if user is not None:
            auth_backend = ApprovedUserBackend()
            authenticated_user = auth_backend.authenticate(request, username=user.username, password=password)

            if authenticated_user:
                login(request, authenticated_user)
                messages.success(request, "You are logged in.")
                next_url = request.GET.get("next", 'core:index')  # Default to 'home' inst ead of 'index'
                return redirect(next_url)
            else:
                if not user.is_active:
                    messages.error(request, "Your account is inactive. Contact admin for assistance.")
                elif not user.is_approved:
                    messages.error(request, "Your account is not approved yet. Please wait for admin approval.")
                else:
                    messages.error(request, "Invalid credentials. Please try again.")
        else:
            messages.error(request, "Invalid credentials. Please try again.")

    return render(request, "userauths/sign-in.html")

def register_view(request):
    """
    Handles user registration.
    """
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            username = form.cleaned_data.get("username")

            # Success message for user
            messages.success(
                request,
                f"Hey {username}, your account was created successfully. Please wait for admin approval."
            )

            # Notify the admin about the new user
            try:
                send_mail(
                    'New Customer Registered',
                    f'A new customer has registered.\n\nUsername: {username}\nEmail: {new_user.email}',
                    settings.DEFAULT_FROM_EMAIL,
                    ['alvotheboss@gmail.com', settings.DEFAULT_FROM_EMAIL],
                    fail_silently=False,
                )
            except Exception as e:
                messages.error(request, f"Failed to notify admin: {str(e)}")

            return redirect('userauths:sign-in')
    else:
        form = UserRegisterForm()

    return render(request, "userauths/sign-up.html", {'form': form})


def logout_view(request):
    """
    Logs out the user and redirects to the sign-in page.
    """
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "You logged out successfully.")
    return redirect("userauths:sign-in")


def profile_update(request):
    """
    Handles updating of user profile.
    """
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("core:dashboard")
    else:
        form = ProfileForm(instance=profile)

    context = {
        "form": form,
        "profile": profile,
    }
    return render(request, "userauths/profile-edit.html", context)
