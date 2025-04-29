from django import forms
from django.contrib.auth.forms import UserCreationForm
from userauths.models import User, Profile


class UserRegisterForm(UserCreationForm):
    phone = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={"placeholder": "Phone"}))
    location = forms.ChoiceField(
        choices=[('', 'Select Location')] + Profile.LOCATION_CHOICES,
        required=True,
        widget=forms.Select(attrs={"placeholder": "Location"})
    )
    manager = forms.ChoiceField(
        choices=[('', 'Select Manager')] + Profile.MANAGER_CHOICES,
        required=True,
        widget=forms.Select(attrs={"placeholder": "Manager"})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        """
        Override save to ensure both User and Profile are created properly.
        """
        user = super().save(commit=False)
        if commit:
            user.save()
            # Use get_or_create to prevent duplicate profiles
            profile, created = Profile.objects.get_or_create(
                user=user,
                defaults={
                    'phone': self.cleaned_data.get('phone'),
                    'location': self.cleaned_data.get('location'),
                    'manager': self.cleaned_data.get('manager'),
                }
            )
            if not created:  # Update existing profile if needed
                profile.phone = self.cleaned_data.get('phone')
                profile.location = self.cleaned_data.get('location')
                profile.manager = self.cleaned_data.get('manager')
                profile.save()
        return user


class ProfileForm(forms.ModelForm):
    full_name = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Full Name"}), required=False
    )
    bio = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Bio"}), required=False
    )
    phone = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Phone"}), required=False
    )

    class Meta:
        model = Profile
        fields = ['full_name', 'image', 'bio', 'phone']
