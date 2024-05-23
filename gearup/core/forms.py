"""Module for forms."""

from django import forms
from django.contrib.auth.models import User

from core.models import Career, College, CustomPage, Menu, Tile, UniversityProfile


class LoginForm(forms.Form):
    """Login rorm for the admin user."""

    email = forms.CharField(max_length=100, required=True)
    password = forms.CharField(max_length=100, required=True)

    def clean(self):
        """Form Validations."""
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        if not User.objects.filter(email__iexact=email).exists():
            self.add_error("email", "Invalid Username")
        else:
            user = User.objects.get(email__iexact=email)
            if not user.check_password(password):
                self.add_error("password", "Invalid credentials")


class MenuForm(forms.ModelForm):
    """Form for adding and editting Menu."""

    class Meta:
        """Field details."""

        model = Menu
        fields = ("title", "url_type", "active", "icon", "url", "page", "key_name")


class TileForm(forms.ModelForm):
    """Form for adding and editting Tile."""

    image_url = forms.CharField(required=False)

    class Meta:
        """Field details."""

        model = Tile
        fields = ("title", "url_type", "active", "image", "url", "page", "description")


class PageForm(forms.ModelForm):
    """Form for adding and editting Page."""

    banner_video_tile = forms.CharField(required=False)

    class Meta:
        """Field details."""

        model = CustomPage
        fields = ("title", "content", "active")


class CollegeForm(forms.ModelForm):
    """Form for managing a College."""

    class Meta:
        """Form meta class."""

        model = College
        exclude = ("tiles",)


class UniversityForm(forms.ModelForm):
    """Form for adding and editting University."""

    class Meta:
        """Field details."""

        model = UniversityProfile
        fields = ("name", "address", "email", "logo", "phone_number")


class CareerForm(forms.ModelForm):
    """Form for managing a Career."""

    class Meta:
        """Form meta class."""

        model = Career
        exclude = ("tiles",)
