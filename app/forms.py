# --- file: payapp/app/forms.py ---
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import CreatorProfile
import re
from PIL import Image


class UserSignupForm(forms.Form):
    """
    A form for user registration.
    """
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter a username'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'you@example.com'})
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'})
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'})
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError('This username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email address is already in use.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')
        if password and password2 and password != password2:
            self.add_error('password2', "Passwords do not match.")
        return cleaned_data


class UserLoginForm(forms.Form):
    """
    A form for user authentication.
    """
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your username'})
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'})
    )


class CreatorProfileForm(forms.ModelForm):
    """
    A form for editing a creator's profile information.
    """
    class Meta:
        model = CreatorProfile
        fields = ['upi_id', 'bio', 'profile_image']
        widgets = {
            'upi_id': forms.TextInput(attrs={'placeholder': 'yourname@bank'}),
            'bio': forms.Textarea(attrs={'placeholder': 'Tell your supporters about yourself...', 'rows': 4}),
            'profile_image': forms.FileInput(attrs={'accept': 'image/*'}),
        }

    def clean_profile_image(self):
        profile_image = self.cleaned_data.get('profile_image')
        if profile_image:
            # Size check
            if profile_image.size > 5 * 1024 * 1024:  # 5MB
                raise ValidationError("Image file too large (max 5MB).")

            # Type check using Pillow
            try:
                img = Image.open(profile_image)
                img.verify()  # verifies image integrity
            except Exception:
                raise ValidationError("File must be a valid image.")
        return profile_image

    def clean_upi_id(self):
        """
        Custom validation for the UPI ID.
        Ensures the format is correct and matches the client-side pattern.
        """
        upi_id = self.cleaned_data.get('upi_id')
        if upi_id:
            if not re.match(r'^[a-zA-Z0-9.\-_]{3,}@[a-zA-Z0-9]{3,}$', upi_id):
                raise ValidationError(
                    "Please enter a valid UPI ID in the format 'username@bank' with at least 3 characters before and after '@'."
                )
        return upi_id
