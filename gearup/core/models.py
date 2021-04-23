"""Database model definitions."""

import uuid
import boto3
import reversion
from django.template.defaultfilters import slugify
from datetime import timedelta

from django.contrib.gis.db import models
from django.db.models.signals import pre_save
from django.conf import settings
from django.db.models.functions import Cast
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.template.loader import select_template
from reversion.models import Version
from core.compare import CompareMixin
# from ckeditor_uploader.fields import RichTextUploadingField


@reversion.register()
class UniversityProfile(models.Model):
    """Model for defining User Types."""

    uid = models.UUIDField(primary_key=True, default=uuid.uuid4,
                           editable=False)
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=250, null=True, blank=True)
    logo = models.FileField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    location = models.PointField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        """Model name representation."""
        return self.name or ""

    @property
    def to_json(self):
        """Property to serialize fields for jquery."""
        return {
            'name': self.name,
            'uid': str(self.uid),
            'address': self.address if self.address else '',
            'email': self.email if self.email else '',
            'logo_url': self.logo.url if self.logo else '',
            'phone_number': self.phone_number if self.phone_number else '',
            'active': 'true' if self.active else 'false',
        }

    @property
    def logo_url(self):
        """College logo or default place holder."""
        return self.logo.url if self.logo\
            else "/static/images/college-tile-default-img.jpg"


@reversion.register()
class Admin(models.Model):
    """Model for defining User Types."""

    ROLES = (('super_admin', 'Super Admin'),
             ('admin', 'Admin'),
             ('silent_login', 'Silent Login'),)

    uid = models.UUIDField(primary_key=True, default=uuid.uuid4,
                           editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='admin')
    image = models.FileField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)
    invited_date = models.DateTimeField(auto_now=True)
    universities = models.ManyToManyField(
        UniversityProfile, related_name="universities")
    active = models.BooleanField(default=True)
    role = models.CharField(choices=ROLES, default='admin',
                            max_length=100)
    silent_login_password = models.CharField(
        null=True, blank=True, max_length=16)

    def __str__(self):
        """Model name representation."""
        return self.user.get_full_name() or ""

    @property
    def university(self):
        """Return the default university."""
        return self.universities.all().first()

    @property
    def to_json(self):
        """Property to serialize fields for jquery."""
        return {
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'uid': str(self.uid),
            'verified': 'true' if self.verified else 'false',
            'email': self.user.email if self.user.email else '',
            'universities': list(self.universities.annotate(
                str_id=Cast('uid',
                            output_field=models.TextField())).values_list(
                'str_id', flat=True)),
            'super_admin': 'true' if self.role == 'super_admin' else 'false',
            'active': 'true' if self.active else 'false',
        }

    @property
    def formatted_universities(self):
        """Return university names."""
        if self.universities.all():
            return ', '.join(
                self.universities.all().values_list('name', flat=True))
        return ''


# @reversion.register()
class UserType(models.Model):
    """Model for defining User Types."""

    uid = models.UUIDField(primary_key=True, default=uuid.uuid4,
                           editable=False)
    title = models.CharField(max_length=100)
    order = models.PositiveSmallIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    university = models.ForeignKey(UniversityProfile, on_delete=models.CASCADE)

    def __str__(self):
        """Model name representation."""
        return self.title or ""


# @reversion.register()
class Device(models.Model):
    """Device model, to store user details when app is first used."""

    uid = models.UUIDField(primary_key=True, default=uuid.uuid4,
                           editable=False)
    device_id = models.CharField(max_length=100)
    app_info = models.CharField(max_length=500, null=True, blank=True)
    user_type = models.ForeignKey(UserType, null=True, blank=True,
                                  on_delete=models.CASCADE)
    school = models.ForeignKey('School', null=True, blank=True,
                               on_delete=models.CASCADE)
    custom_school = models.CharField(max_length=200, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    university = models.ForeignKey(UniversityProfile, on_delete=models.CASCADE)

    def __str__(self):
        """Model name representation."""
        return '%s-%s' % (self.user_type, self.school or self.custom_school)


@reversion.register()
class Menu(models.Model):
    """Model to manage menu records."""

    TYPES = (('native', 'Custom Pages'),
             ('external', 'External'),
             ('pre_defined', 'Pre Defined Pages'),)

    uid = models.UUIDField(primary_key=True, default=uuid.uuid4,
                           editable=False)
    title = models.CharField(max_length=100)
    icon = models.FileField(null=True, blank=True)
    url_type = models.CharField(choices=TYPES, default='native',
                                max_length=100)
    url = models.CharField(max_length=500, null=True, blank=True)
    active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)
    page = models.ForeignKey('CustomPage', null=True, blank=True,
                             on_delete=models.CASCADE,
                             related_name='menu_page')
    key_name = models.CharField(max_length=20, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    university = models.ForeignKey(UniversityProfile, on_delete=models.CASCADE)

    def __str__(self):
        """Model name representation."""
        return self.title or ""

    @property
    def to_json(self):
        """Property to serialize fields for jquery."""
        return {
            'title': self.title,
            'uid': str(self.uid),
            'page': str(self.page.uid) if self.page else '',
            'state': 'true' if self.active else 'false',
            'url_type': self.url_type,
            'url': self.url if self.url else '',
            'icon_url': self.icon.url if self.icon else '',
            'pre_defined_key': self.key_name if self.key_name else ''
        }


@reversion.register()
class School(models.Model):
    """Model to manage High School details when user first logs in."""

    uid = models.UUIDField(primary_key=True, default=uuid.uuid4,
                           editable=False)
    name = models.CharField(max_length=250)
    lea_name = models.CharField(max_length=250, null=True, blank=True)
    address_line1 = models.CharField(max_length=200, blank=True)
    address_line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=200, blank=True)
    state = models.CharField(max_length=200, blank=True)
    zip_code = models.CharField(max_length=200, blank=True)
    point = models.PointField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    university = models.ForeignKey(UniversityProfile, on_delete=models.CASCADE)

    def __str__(self):
        """Model name representation."""
        return self.name or ""

    @property
    def address_formatted(self):
        """Format address lane 1 & 2 to readable form."""
        return ', '.join(filter(None, [self.address_line1,
                                       self.address_line2]))

    @property
    def formatted_name(self):
        """Formated name with address in readable form."""
        name = "%(name)s, %(address)s".rstrip(', ') % {
            'name': self.name, 'address': self.address_formatted}
        return name.rstrip(', ')


@reversion.register()
class Tile(models.Model):
    """Model to manage Custom tiles for Home Page and other custom pages."""

    TYPES = [('native', 'Native'),
             ('external', 'External')]
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4,
                           editable=False)
    title = models.CharField(max_length=100)
    url = models.CharField(max_length=500, null=True, blank=True)
    active = models.BooleanField(default=True)
    url_type = models.CharField(choices=TYPES, default='native',
                                max_length=100)
    description = models.CharField(max_length=250, null=True, blank=True)
    image = models.FileField(blank=True, null=True)
    order = models.PositiveSmallIntegerField(default=0)
    page = models.ForeignKey('CustomPage', null=True, blank=True,
                             on_delete=models.CASCADE,
                             related_name='tile_page')
    created = models.DateTimeField(auto_now_add=True)
    university = models.ForeignKey(UniversityProfile, on_delete=models.CASCADE)
    modified_by_page = models.CharField(null=True, blank=True, max_length=10)

    def __str__(self):
        """Model name representation."""
        return self.title or ""

    class Meta:
        """Object meta definitions."""

        ordering = ['order']

    @property
    def image_url(self):
        """Image url."""
        return self.image.url if self.image else ''

    @property
    def to_json(self):
        """Property to serialize fields for jquery."""
        return {
            'title': self.title,
            'uid': str(self.uid),
            'page': str(self.page.uid) if self.page else '',
            'state': 'true' if self.active else 'false',
            'url_type': self.url_type,
            'url': self.url if self.url else '',
            'description': self.description or '',
            'image_url': self.image.url if self.image else '',
        }


@reversion.register()
class CustomPage(models.Model):
    """Model to manage custom pages."""

    uid = models.UUIDField(primary_key=True, default=uuid.uuid4,
                           editable=False)
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    video = models.ForeignKey('File', null=True, blank=True,
                              on_delete=models.SET_NULL, related_name='page')
    content = models.TextField()
    active = models.BooleanField(default=True)
    tiles = models.ManyToManyField(Tile, blank=True)
    home_page = models.BooleanField(default=False)
    university = models.ForeignKey(UniversityProfile, on_delete=models.CASCADE)

    def __str__(self):
        """Model name representation."""
        return self.title or ""

    @property
    def active_tiles(self):
        """Return active tiles."""
        return self.tiles.filter(active=True)

    @property
    def to_json(self):
        """Property to serialize fields for jquery."""
        return {
            'title': self.title,
            'uid': str(self.uid),
            'state': 'true' if self.active else 'false',
            'content': self.content or ''
        }

    @property
    def related_tiles(self):
        return True if Tile.objects.filter(
            page=self, active=True, university=self.university).exists() else False

    @property
    def html_content(self):
        """Create html content for mobile."""
        return '''<!DOCTYPE html>
            <html>
              <meta name="viewport"
                content="width=device-width,
                initial-scale=1, shrink-to-fit=no">
              <head>
                 <link
                  href="https://fonts.googleapis.com/css?family=Roboto:400,400i,700,700i&display=swap"
                   rel="stylesheet">
            <style>
                %(style_width)s
            </style>
            </head>
            <body style="font-family: 'Roboto',
             sans-serif; font-size:14px; line-height:24px; color: #212529;">
            %(content)s</body></html>''' % {
            'content': self.content,
            'style_width': 'img{max-width:100%;}'}

    @property
    def dark_mode_content(self):
        context = {
            'content': self.content
        }
        template_name = 'themes/%s/dark_mode.html' % slugify(self.university.name)

        default_template = template_name.replace(slugify(self.university.name), 'default')
        template = select_template([template_name, default_template])
        return template.render(context)

    @property
    def light_mode_content(self):
        context = {
            'content': self.content
        }
        template_name = 'themes/%s/light_mode.html' % slugify(self.university.name)
        default_template = template_name.replace(slugify(self.university.name), 'default')
        template = select_template([template_name, default_template])
        return template.render(context)


@reversion.register()
class Major(models.Model):
    """Model to manage Universities."""

    uid = models.UUIDField(primary_key=True, default=uuid.uuid4,
                           editable=False)
    title = models.CharField(max_length=250)
    description = models.TextField()
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    university = models.ForeignKey(UniversityProfile, on_delete=models.CASCADE)

    def __str__(self):
        """Model name representation."""
        return self.title or ""

    @property
    def college_names(self):
        """Get list of college names associated with major."""
        return ', '.join(
            list(self.college_set.all().values_list('name', flat=True)))

    @property
    def to_json(self):
        """Property to serialize fields for jquery."""
        return {
            'title': self.title,
            'uid': str(self.uid),
            'state': 'true' if self.active else 'false',
            'description': self.description or '',
            'colleges': list(self.college_set.annotate(
                str_id=Cast(
                    'uid', output_field=models.TextField())).values_list(
                'str_id', flat=True))
        }


@reversion.register()
class College(models.Model):
    """Model to manage Universities."""

    uid = models.UUIDField(primary_key=True, default=uuid.uuid4,
                           editable=False)
    active = models.BooleanField(default=True)
    name = models.CharField(max_length=250)
    short_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    student_capacity = models.PositiveIntegerField(default=0)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    facebook_url = models.URLField(null=True, blank=True)
    twitter_url = models.URLField(null=True, blank=True)
    linkedin_url = models.URLField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    tags = models.TextField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    in_state_sat_score = models.PositiveIntegerField(default=0)
    in_state_act_score = models.PositiveIntegerField(default=0)
    in_state_cost_per_year = models.PositiveIntegerField(default=0)

    out_state_sat_score = models.PositiveIntegerField(default=0)
    out_state_act_score = models.PositiveIntegerField(default=0)
    out_state_cost_per_year = models.PositiveIntegerField(default=0)
    majors = models.ManyToManyField('Major', blank=True)

    disability_access = models.BooleanField(default=False)
    disability_access_url = models.URLField(null=True, blank=True)

    video = models.ForeignKey('File', null=True, blank=True,
                              on_delete=models.SET_NULL,
                              related_name='college')
    logo = models.FileField(null=True, blank=True)

    tiles = models.ManyToManyField(Tile, blank=True)

    address = models.TextField(null=True, blank=True)
    location = models.PointField(null=True, blank=True)
    university = models.ForeignKey(UniversityProfile, on_delete=models.CASCADE)

    def __str__(self):
        """Model name representation."""
        return self.name or ""

    @property
    def logo_url(self):
        """College logo or default place holder."""
        return self.logo.url if self.logo\
            else "/static/images/college-tile-default-img.jpg"

    def html_content(self, base_url=''):
        """Create html content for mobile."""
        tile_html = ''

        for tile in self.tiles.filter(active=True):
            tile_html += '''<div style="padding:8px; margin-top: 10px;
            background-color: #FFFFFF; border-radius:7px;
            box-shadow:2px 2px 4px #e2e2e2;
            border:1px #f8f8f8 solid;">
            <a  %(target)s  href="%(tile_url)s" style="text-decoration: none;
            color:#141933;">
            <div style="width:40px; height: 40px;
                display: inline-block; margin-left: 10px;
                margin-right: 10px;  vertical-align: middle;">
                <img style="%(img_style)s" src="%(tile_icon)s" alt=""/>
            </div>
            <div style="display: inline-block;
                font-size:13px; color:#141933;
                font-family: 'Roboto', sans-serif; ">
            %(tile_title)s
            </div></a></div>''' % {
                'target': 'target="_blank"' if tile.url else None,
                'tile_url': tile.url,
                'tile_icon': base_url + tile.image.url
                if tile.image else base_url + "/static/images/default_tile_img-s.png",
                'tile_title': tile.title,
                'img_style': 'max-width: 100%; max-height:100%; vertical-align: -webkit-baseline-middle'
            }

        return '''<!DOCTYPE html>
            <html>
              <meta name="viewport"
                content="width=device-width,
                initial-scale=1, shrink-to-fit=no">
              <head>
                 <link
                  href="https://fonts.googleapis.com/css?family=Roboto:400,400i,700,700i&display=swap"
                   rel="stylesheet">
            <style>
                %(style_width)s
            </style>
            </head>
            <body style="font-family: 'Roboto',
             sans-serif; font-size:14px; line-height:24px; color: #212529;">
            %(content)s%(tile_html)s</body></html>''' % {
            'content': self.content,
            'tile_html': tile_html,
            'style_width': 'img{max-width:100%;}'}

    def dark_mode_content(self, base_url=''):
        tile_html = ''

        for tile in self.tiles.filter(active=True):
            tile_html += '''<div style="padding:8px;
            margin-top: 10px; background-color:#333; border-radius:7px;
            box-shadow:2px 2px 4px #000000; border: 1px #737373 solid;color:#2ac5f9;">
            <a href="%(tile_url)s" style="text-decoration: none;
            color:#2ac5f9;font-size:13px; font-family: 'Roboto', sans-serif; ">
            <div style="width:40px; height: 40px;
                display: inline-block; margin-left: 10px;
                margin-right: 10px;  vertical-align: middle;">
                <img style="%(img_style)s" src="%(tile_icon)s" alt=""/>
            </div>
            <div style="display: inline-block;">
            %(tile_title)s
            </div></a></div>''' % {
                'tile_url': tile.url,
                'tile_icon': base_url + tile.image.url
                if tile.image else "/static/images/default_tile_img-s.png",
                'tile_title': tile.title,
                'img_style': 'max-width: 100%; max-height:100%; vertical-align: -webkit-baseline-middle'
            }
        context = {
            'content': self.content,
            'tile_html': tile_html
        }
        template_name = 'themes/%s/dark_mode.html' % slugify(self.university.name)
        default_template = template_name.replace(slugify(self.university.name), 'default')
        template = select_template([template_name, default_template])
        return template.render(context)

    def light_mode_content(self, base_url=''):
        tile_html = ''

        for tile in self.tiles.filter(active=True):
            tile_html += '''<div style="padding:8px; margin-top: 10px;
            background-color: #FFFFFF; border-radius:7px;
            box-shadow:2px 2px 4px #e2e2e2; border:1px #f8f8f8 solid;">
            <a href="%(tile_url)s" style="text-decoration: none;
            font-size:13px; color:#2D3256;font-family: 'Roboto', sans-serif; ">
            <div style="width:40px; height: 40px; display: inline-block; margin-left: 10px;
            margin-right: 10px;  vertical-align: middle;">
                <img style="%(img_style)s" src="%(tile_icon)s" alt=""/>
            </div>
            <div style="display: inline-block;">
            %(tile_title)s
            </div></a></div>''' % {
                'tile_url': tile.url,
                'tile_icon': base_url + tile.image.url
                if tile.image else "/static/images/default_tile_img-s.png",
                'tile_title': tile.title,
                'img_style': 'max-width: 100%; max-height:100%; vertical-align: -webkit-baseline-middle'
            }
        context = {
            'content': self.content,
            'tile_html': tile_html
        }
        template_name = 'themes/%s/light_mode.html' % slugify(self.university.name)
        default_template = template_name.replace(slugify(self.university.name), 'default')
        template = select_template([template_name, default_template])
        return template.render(context)

    @property
    def active_tiles(self):
        """Return active tiles."""
        return self.tiles.filter(active=True)


@reversion.register()
class File(models.Model):
    """File Model to represent s3 Upload."""

    uid = models.UUIDField(primary_key=True, default=uuid.uuid4,
                           editable=False)
    name = models.CharField(max_length=120, null=True, blank=True)
    path = models.TextField(blank=True, null=True)
    size = models.BigIntegerField(default=0)
    file_type = models.CharField(max_length=120, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    thumbnail = models.FileField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    uploaded = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    file_key = models.CharField(max_length=250)
    university = models.ForeignKey(UniversityProfile, on_delete=models.CASCADE)

    def __str__(self):
        """Model name representation."""
        return self.name or ""

    @property
    def secure_s3_url(self):
        """Generate s3 download url for file."""
        return "https://%(bucket)s.s3.amazonaws.com/%(env)s%(file_key)s"\
            % {"bucket": settings.AWS_UPLOAD_BUCKET,
               "env": settings.AWS_UPLOAD_ENV,
               "file_key": self.file_key}

    @property
    def cdn_url(self):
        """Generate cdn url for file."""
        return "%(url)s/%(env)s%(file_key)s"\
            % {"url": settings.CLOUDFRONT_URL,
                "env": settings.AWS_UPLOAD_ENV,
               "file_key": self.file_key}

    @property
    def delete_from_s3(self):
        """Delete a file from s3."""
        s3 = boto3.resource(
            's3', region_name=settings.AWS_UPLOAD_REGION,
            aws_access_key_id=settings.AWS_UPLOAD_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_UPLOAD_SECRET_KEY)
        s3.Object(settings.AWS_UPLOAD_BUCKET, self.file_key).delete()
        return

    def delete(self, *args, **kwargs):
        """Delete file from s3 along with deleting from db."""
        self.delete_from_s3
        super().delete(*args, **kwargs)


@receiver(pre_save, sender=User)
def user_updated(sender, **kwargs):
    """Verify admin when user changes password."""
    user = kwargs.get('instance', None)
    if user:
        new_password = user.password
        try:
            old_password = User.objects.get(pk=user.pk).password
        except User.DoesNotExist:
            old_password = None
        if new_password != old_password:
            if Admin.objects.filter(user=user, verified=False).exists():
                Admin.objects.filter(
                    user=user, verified=False).update(verified=True)


class AuditVersion(Version):
    """Customise Version."""

    class Meta:
        """Proxy Model."""

        proxy = True

    @property
    def user(self):
        """User of audit."""
        return self.revision.user

    @property
    def status(self):
        """Return Status of Version."""
        if not self.object:
            return 'deleted'
        if (self.revision.date_created -
                self.object.created) < timedelta(seconds=10):
            return 'created'
        return 'modified'

    @property
    def changes(self):
        """Get version compared changes."""
        if self.prev:
            return CompareMixin.compare(
                CompareMixin(), self.object, self.prev, self)[0]
        return []

    @property
    def prev(self):
        """Get Previous version."""
        if self.object:
            return AuditVersion.objects.get_for_object(
                self.object).exclude(pk=self.pk).order_by(
                'revision__date_created').first()
        return None

    @property
    def next(self):
        """Get next version."""
        if self.object:
            return AuditVersion.objects.get_for_object(
                self.object).exclude(pk=self.pk).order_by(
                '-revision__date_created').first()
        return None


@reversion.register()
class Career(models.Model):
    """Model to manage Universities."""

    uid = models.UUIDField(primary_key=True, default=uuid.uuid4,
                           editable=False)
    active = models.BooleanField(default=True)
    career = models.CharField(max_length=250)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    facebook_url = models.URLField(null=True, blank=True)
    twitter_url = models.URLField(null=True, blank=True)
    linkedin_url = models.URLField(null=True, blank=True)
    instagram_url = models.URLField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    video = models.ForeignKey('File', null=True, blank=True,
                              on_delete=models.SET_NULL,
                              related_name='career')
    logo = models.FileField(null=True, blank=True)
    tiles = models.ManyToManyField(Tile, blank=True)
    university = models.ForeignKey(UniversityProfile, on_delete=models.CASCADE)

    def __str__(self):
        """Model name representation."""
        return self.career or "-"

    @property
    def logo_url(self):
        """College logo or default place holder."""
        return self.logo.url if self.logo\
            else "/static/images/college-tile-default-img.jpg"

    def html_content(self, base_url=''):
        """Create html content for mobile."""
        tile_html = ''

        for tile in self.tiles.filter(active=True):
            tile_html += '''<div style="padding:8px; margin-top: 10px;
            background-color: #FFFFFF; border-radius:7px;
            box-shadow:2px 2px 4px #e2e2e2;
            border:1px #f8f8f8 solid;">
            <a %(target)s href="%(tile_url)s" style="text-decoration: none;
            color:#141933;">
            <div style="width:40px; height: 40px;
                display: inline-block; margin-left: 10px;
                margin-right: 10px;  vertical-align: middle;">
                <img style="%(img_style)s" src="%(tile_icon)s" alt=""/>
            </div>
            <div style="display: inline-block;
                font-size:13px; color:#141933;
                font-family: 'Roboto', sans-serif; ">
            %(tile_title)s
            </div></a></div>''' % {
                'target': 'target="_blank"' if tile.url else None,
                'tile_url': tile.url,
                'tile_icon': base_url + tile.image.url
                if tile.image else base_url + "/static/images/default_tile_img-s.png",
                'tile_title': tile.title,
                'img_style': 'max-width: 100%; max-height:100%; vertical-align: -webkit-baseline-middle'
            }

        return '''<!DOCTYPE html>
            <html>
              <meta name="viewport"
                content="width=device-width,
                initial-scale=1, shrink-to-fit=no">
              <head>
                 <link
                  href="https://fonts.googleapis.com/css?family=Roboto:400,400i,700,700i&display=swap"
                   rel="stylesheet">
            <style>
                %(style_width)s
            </style>
            </head>
            <body style="font-family: 'Roboto',
             sans-serif; font-size:14px; line-height:24px; color: #212529;">
            %(content)s%(tile_html)s</body></html>''' % {
            'content': self.content,
            'tile_html': tile_html,
            'style_width': 'img{max-width:100%;}'}

    def dark_mode_content(self, base_url=''):
        tile_html = ''

        for tile in self.tiles.filter(active=True):
            tile_html += '''<div style="padding:8px;
            margin-top: 10px; background-color:#333; border-radius:7px;
            box-shadow:2px 2px 4px #000000; border: 1px #737373 solid;color:#2ac5f9;">
            <a href="%(tile_url)s" style="text-decoration: none;
            color:#2ac5f9;font-size:13px; font-family: 'Roboto', sans-serif; ">
            <div style="width:40px; height: 40px;
                display: inline-block; margin-left: 10px;
                margin-right: 10px;  vertical-align: middle;">
                <img style="%(img_style)s" src="%(tile_icon)s" alt=""/>
            </div>
            <div style="display: inline-block;">
            %(tile_title)s
            </div></a></div>''' % {
                'tile_url': tile.url,
                'tile_icon': base_url + tile.image.url
                if tile.image else "/static/images/default_tile_img-s.png",
                'tile_title': tile.title,
                'img_style': 'max-width: 100%; max-height:100%; vertical-align: -webkit-baseline-middle'
            }
        context = {
            'content': self.content,
            'tile_html': tile_html
        }
        template_name = 'themes/%s/dark_mode.html' % slugify(self.university.name)
        default_template = template_name.replace(slugify(self.university.name), 'default')
        template = select_template([template_name, default_template])
        return template.render(context)

    def light_mode_content(self, base_url=''):
        tile_html = ''

        for tile in self.tiles.filter(active=True):
            tile_html += '''<div style="padding:8px; margin-top: 10px;
            background-color: #FFFFFF; border-radius:7px;
            box-shadow:2px 2px 4px #e2e2e2; border:1px #f8f8f8 solid;">
            <a href="%(tile_url)s" style="text-decoration: none;
            font-size:13px; color:#2D3256;font-family: 'Roboto', sans-serif; ">
            <div style="width:40px; height: 40px; display: inline-block; margin-left: 10px;
            margin-right: 10px;  vertical-align: middle;">
                <img style="%(img_style)s" src="%(tile_icon)s" alt=""/>
            </div>
            <div style="display: inline-block;">
            %(tile_title)s
            </div></a></div>''' % {
                'tile_url': tile.url,
                'tile_icon': base_url + tile.image.url
                if tile.image else "/static/images/default_tile_img-s.png",
                'tile_title': tile.title,
                'img_style': 'max-width: 100%; max-height:100%; vertical-align: -webkit-baseline-middle'
            }
        context = {
            'content': self.content,
            'tile_html': tile_html
        }
        template_name = 'themes/%s/light_mode.html' % slugify(self.university.name)
        default_template = template_name.replace(slugify(self.university.name), 'default')
        template = select_template([template_name, default_template])
        return template.render(context)

    @property
    def active_tiles(self):
        """Return active tiles."""
        return self.tiles.filter(active=True)
