"""Default admin module."""

from django.contrib import admin
# from django.contrib.gis.admin import OSMGeoAdmin
from django.contrib.gis.admin.options import GISModelAdmin

# from django import forms
from core.models import (
    Admin,
    Career,
    College,
    CustomPage,
    Device,
    Menu,
    School,
    Tile,
    UniversityProfile,
    UserType,
)

# from ckeditor_uploader.widgets import CKEditorUploadingWidget


class UniversityProfileAdmin(admin.ModelAdmin):
    """Tile Admin."""

    pass


class AdminProfileAdmin(admin.ModelAdmin):
    """Tile Admin."""

    pass


class UserTypeAdmin(admin.ModelAdmin):
    """UserTypeAdmin."""

    list_filter = ("university",)


class DeviceAdmin(admin.ModelAdmin):
    """Device Admin."""

    list_filter = ("university",)


class MenuAdmin(admin.ModelAdmin):
    """Menu Admin."""

    list_filter = ("university",)


class SchoolAdmin(GISModelAdmin):
    """School Admin."""

    list_filter = ("university",)
    list_display = ("name",)


class CustomPageAdmin(admin.ModelAdmin):
    """Custompage Admin."""

    list_filter = ("university",)


class CollegeAdmin(GISModelAdmin):
    """College Admin."""

    list_filter = ("university",)


class TileAdmin(admin.ModelAdmin):
    """Tile Admin."""

    list_filter = ("university",)


class CareerAdmin(admin.ModelAdmin):
    """Career Admin."""

    list_filter = ("university",)


admin.site.register(UserType, UserTypeAdmin)
admin.site.register(Device, DeviceAdmin)
admin.site.register(Menu, MenuAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(CustomPage, CustomPageAdmin)
admin.site.register(College, CollegeAdmin)
admin.site.register(Tile, TileAdmin)
admin.site.register(UniversityProfile, UniversityProfileAdmin)
admin.site.register(Admin, AdminProfileAdmin)
admin.site.register(Career, CareerAdmin)
