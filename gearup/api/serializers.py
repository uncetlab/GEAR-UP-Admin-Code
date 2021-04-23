"""Defines all the serializers needed for the api."""

from django.http import Http404
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import PermissionDenied

from core.models import Device, Menu, Tile, CustomPage, File,\
    College, Major, Admin, UniversityProfile, Career


class UserTypeSerializer(serializers.Serializer):
    """Serializes the user type data for api."""

    uid = serializers.UUIDField(read_only=True)
    title = serializers.CharField(required=True, allow_blank=False,
                                  max_length=250)


class SchoolSerializer(serializers.Serializer):
    """Serializes the high school data for api."""

    uid = serializers.UUIDField(read_only=True)
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        """Generate formatted icon url."""
        return obj.formatted_name


class DeviceSerializer(serializers.ModelSerializer):
    """Serializer of Device data, entered when a device first registered."""

    class Meta:
        """Defining serializer meta data."""

        model = Device
        fields = ('device_id', 'user_type', 'school',
                  'custom_school', 'university')

    # def validate(self, data):
    #     """"Validator to check if school or custom school data is present."""
    #     school = data.get('school', None)
    #     custom_school = data.get('custom_school', None)
    #     if not (school or custom_school):
    #         raise serializers.ValidationError(
    #             "Need to provide school details")
    #     return data


class MenuSerializer(serializers.ModelSerializer):
    """Serializer of Menu, added from backend."""

    icon = serializers.SerializerMethodField()

    class Meta:
        """Defining serializer meta data."""

        model = Menu
        fields = '__all__'

    def get_icon(self, obj):
        """Generate formatted icon url."""
        return obj.icon.url.lstrip('/') if obj.icon else None


class TileSerializer(serializers.ModelSerializer):
    """Serializer for model Tile."""

    image = serializers.SerializerMethodField()
    page = serializers.SerializerMethodField()

    class Meta:
        """Defining serializer meta data."""

        model = Tile
        fields = ['title', 'image', 'url', 'url_type',
                  'image', 'description', 'order', 'page']

    def get_image(self, obj):
        """Generate formatted icon url."""
        return obj.image.url.lstrip('/') if obj.image else None

    def get_page(self, obj):
        """Convert uid to string."""
        return str(obj.page_id) if obj.page else None


class FileSerializer(serializers.ModelSerializer):
    """Serializer for model File."""

    url = serializers.SerializerMethodField()
    uid = serializers.UUIDField(read_only=True)
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        """Defining serializer meta data."""

        model = File
        fields = ['uid', 'name', 'url', 'thumbnail']

    def get_url(self, obj):
        """Generate cdn secure url."""
        return obj.cdn_url

    def get_thumbnail(self, obj):
        """Generate thumbnail url."""
        return obj.thumbnail.url.lstrip('/') if obj.thumbnail else None


class HomePageSerializer(serializers.ModelSerializer):
    """Serializer for homepage."""

    active_tiles = TileSerializer(many=True, read_only=True)
    video = FileSerializer(read_only=True)
    uid = serializers.UUIDField(read_only=True)

    class Meta:
        """Defining serializer meta data."""

        model = CustomPage
        fields = ['uid', 'title', 'video', 'active_tiles']


class PageSerializer(serializers.ModelSerializer):
    """Serializer for Custompage."""

    video = FileSerializer(read_only=True)
    uid = serializers.UUIDField(read_only=True)
    content = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        """Constructor."""
        html_content = kwargs.pop('html_content', True)
        self.html_content = html_content
        self.web_view = kwargs.pop('web_view', False)
        if self.html_content:
            if not self.web_view:
                self.fields.pop('content')
            self.fields.pop('active')
        super(PageSerializer, self).__init__(*args, **kwargs)

    class Meta:
        """Defining serializer meta data."""

        model = CustomPage
        fields = ['uid', 'title', 'video', 'content',
                  'dark_mode_content', 'light_mode_content', 'active']

    def get_content(self, obj):
        """Send html content to api and normal content to admin."""
        if self.html_content:
            return obj.html_content
        return obj.content


class CoordinateField(serializers.Field):
    """Serialize latitude and longitude of point field."""

    def to_representation(self, value):
        """Parse point to latitude and longitude."""
        ret = {
            "longitude": value.location.x if value.location else 0,
            "latitude": value.location.y if value.location else 0
        }
        return ret


class CollegeListSerializer(serializers.ModelSerializer):
    """Serializer for College."""

    uid = serializers.UUIDField(read_only=True)
    logo = serializers.SerializerMethodField()
    location = CoordinateField(source='*')

    def get_logo(self, obj):
        """Generate formatted icon url."""
        return obj.logo.url.lstrip('/') if obj.logo else None

    class Meta:
        """Defining serializer meta data."""

        model = College
        fields = ['name', 'uid', 'location', 'logo',
                  'tags', 'disability_access_url']


class MajorSerializer(serializers.ModelSerializer):
    """Serializer for Majors."""

    uid = serializers.UUIDField(read_only=True)

    class Meta:
        """Defining serializer meta data."""

        model = Major
        fields = ['uid', 'title', 'description']


class CollegeSerializer(serializers.ModelSerializer):
    """Serializer for College."""

    uid = serializers.UUIDField(read_only=True)
    video = FileSerializer(read_only=True)
    logo = serializers.SerializerMethodField()
    location = CoordinateField(source='*')
    majors = MajorSerializer(many=True, read_only=True)
    content = serializers.SerializerMethodField()
    active_tiles = TileSerializer(many=True, read_only=True)
    dark_mode_content = serializers.SerializerMethodField()
    light_mode_content = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        """Constructor."""
        html_content = kwargs.pop('html_content', True)
        self.html_content = html_content
        self.base_url = kwargs.pop('base_url', None)
        self.web_view = kwargs.pop('web_view', False)

        self.add_tile = kwargs.pop('add_tile', None)
        if not self.add_tile:
            self.fields.pop('active_tiles')
        if self.html_content:
            if not self.web_view:
                self.fields.pop('content')
        super(CollegeSerializer, self).__init__(*args, **kwargs)

    def get_logo(self, obj):
        """Generate formatted icon url."""
        return obj.logo.url.lstrip('/') if obj.logo else None

    def get_dark_mode_content(self, obj):
        return obj.dark_mode_content(base_url=self.base_url)

    def get_light_mode_content(self, obj):
        return obj.light_mode_content(base_url=self.base_url)

    class Meta:
        """Defining serializer meta data."""

        model = College
        exclude = ['created', 'modified', 'tiles', 'university', 'active']

    def get_content(self, obj):
        """Send html content to api and normal content to admin."""
        if self.html_content:
            return obj.html_content(base_url=self.base_url)
        return obj.content


class CustomJWTSerializer(TokenObtainPairSerializer):
    """Serializer for JWT."""

    def validate(self, attrs):
        """Override validation."""
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        admin = Admin.objects.filter(user=self.user).first()
        if not admin:
            raise PermissionDenied(
                {"message": "You don't have permission to access this api."})
        if not admin.university:
            raise PermissionDenied(
                {"message": "You don't have permission to access this api."})
        if not admin.university.active:
            raise Http404
        if not admin.active:
            raise PermissionDenied(
                {"message": "You don't have permission to access this api."})
        return data


class UniversityListSerializer(serializers.ModelSerializer):
    """Serializer for College."""

    uid = serializers.UUIDField(read_only=True)

    class Meta:
        """Defining serializer meta data."""

        model = UniversityProfile
        fields = ['name', 'uid']


class CareerListSerializer(serializers.ModelSerializer):
    """Serializer for College."""

    uid = serializers.UUIDField(read_only=True)
    logo = serializers.SerializerMethodField()

    def get_logo(self, obj):
        """Generate formatted icon url."""
        return obj.logo.url.lstrip('/') if obj.logo else None

    class Meta:
        """Defining serializer meta data."""

        model = Career
        fields = ['career', 'uid', 'logo']


class CareerSerializer(serializers.ModelSerializer):
    """Serializer for Career."""

    uid = serializers.UUIDField(read_only=True)
    video = FileSerializer(read_only=True)
    logo = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()
    active_tiles = TileSerializer(many=True, read_only=True)
    dark_mode_content = serializers.SerializerMethodField()
    light_mode_content = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        """Constructor."""
        html_content = kwargs.pop('html_content', True)
        self.html_content = html_content
        self.base_url = kwargs.pop('base_url', None)
        self.web_view = kwargs.pop('web_view', False)
        self.add_tile = kwargs.pop('add_tile', None)
        if not self.add_tile:
            self.fields.pop('active_tiles')
        if self.html_content:
            if not self.web_view:
                self.fields.pop('content')
        super(CareerSerializer, self).__init__(*args, **kwargs)

    def get_logo(self, obj):
        """Generate formatted icon url."""
        return obj.logo.url.lstrip('/') if obj.logo else None

    def get_dark_mode_content(self, obj):
        return obj.dark_mode_content(base_url=self.base_url)

    def get_light_mode_content(self, obj):
        return obj.light_mode_content(base_url=self.base_url)

    class Meta:
        """Defining serializer meta data."""

        model = Career
        exclude = ['created', 'modified', 'tiles', 'university', 'active']

    def get_content(self, obj):
        """Send html content to api and normal content to admin."""
        if self.html_content:
            return obj.html_content(base_url=self.base_url)
        return obj.content
