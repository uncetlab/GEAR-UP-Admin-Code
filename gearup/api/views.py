"""
APIView class.

Provides an APIView class that is the base of all APT views in the gearapp.

"""

# from rest_framework.views import APIView
# from rest_framework.parsers import JSONParser

import base64
import hashlib
import hmac
import os
import time
import boto3
import botocore
from django.template.defaultfilters import slugify
from collections import OrderedDict
from django.conf import settings
from django.db.models import Q
from django.http import Http404
from django.contrib.gis.geos import Polygon

from rest_framework import status, authentication
from rest_framework.response import Response

from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination, _positive_int
from rest_framework.exceptions import APIException, PermissionDenied
from rest_framework_simplejwt.views import TokenObtainPairView

from core.models import School, Menu, UserType, CustomPage, File,\
    College, Major, UniversityProfile, Admin, Career
from api.serializers import SchoolSerializer, DeviceSerializer,\
    MenuSerializer, UserTypeSerializer, HomePageSerializer,\
    PageSerializer, CollegeListSerializer, CollegeSerializer,\
    MajorSerializer, CustomJWTSerializer, CareerListSerializer,\
    CareerSerializer


class ErrorBadParameters(APIException):
    """Custom exceptions."""

    status_code = 400
    default_detail = 'Filter Parameters are not in specified Format'


class Pagination(LimitOffsetPagination):
    """Override Pagination to add additional fields."""

    def get_paginated_response(self, data):
        """Modify paginated respnse."""
        return Response(OrderedDict([
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('offset', self.offset),
            ('results', data)
        ]))

    def get_limit(self, request):
        """Test."""
        if request._request.method == 'POST':
            if request.data.get('pagination'):
                pagination = request.data.get('pagination')
                return _positive_int(pagination.get('limit'))
        if self.limit_query_param:
            try:
                return _positive_int(
                    request.query_params[self.limit_query_param],
                    strict=True,
                    cutoff=self.max_limit
                )
            except (KeyError, ValueError):
                pass

        return self.default_limit

    def get_offset(self, request):
        """Test."""
        if request._request.method == 'POST':
            if request.data.get('pagination'):
                pagination = request.data.get('pagination')
                return _positive_int(pagination.get('offset'))
        try:
            return _positive_int(
                request.query_params[self.offset_query_param],
            )
        except (KeyError, ValueError):
            return 0


class BaseView(generics.GenericAPIView):
    """A APIView derivative Base Class for Authentication."""

    permission_classes = (IsAuthenticated,)
    queryset = ''
    pagination_class = Pagination
    university = None

    def initial(self, request, *args, **kwargs):
        """Check if the requesting user has authorization to view contents."""
        if request.user.is_superuser:
            university = request._request.session.get('university', None)
            if university and UniversityProfile.objects.filter(
                    uid=university).exists():
                self.university = UniversityProfile.objects.get(uid=university)

            return super(BaseView, self).initial(request, *args, **kwargs)
        admin = Admin.objects.filter(user=request.user).first()
        if not admin:
            raise PermissionDenied(
                {"message": "You don't have permission to access this api."})
        if admin.role == 'super_admin':
            university = request._request.session.get('university', None)
            if university and UniversityProfile.objects.filter(
                    uid=university).exists():
                self.university = UniversityProfile.objects.get(uid=university)

            return super(BaseView, self).initial(request, *args, **kwargs)
        if not admin.university:
            raise PermissionDenied(
                {"message": "You don't have permission to access this api."})
        if not admin.active:
            raise PermissionDenied(
                {"message": "You don't have permission to access this api."})
        if not admin.active or not admin.university.active:
            raise PermissionDenied(
                {"message": "You don't have permission to access this api."})
        if not admin.university.active:
            raise Http404
        self.university = admin.university
        return super(BaseView, self).initial(request, *args, **kwargs)

    def custom_paginator(self, queryset, paginate=False):
        """Paginator for all views."""
        queryset = queryset.filter(university=self.university)
        if paginate:
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.serializer_class(page, many=True)
                return self.get_paginated_response(serializer.data)
            else:
                serializer = self.serializer_class(queryset, many=True)
        else:
            serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class JWTTokenObtainPairSerializer(TokenObtainPairView):
    """Custom override."""

    serializer_class = CustomJWTSerializer


class UserTypeListView(BaseView):
    """
    User Types Listng View.

    A BaseView derivative class with token authentication,
    for listing user types. Values are predefined.

    """

    serializer_class = UserTypeSerializer

    def get(self, request, format=None):
        """Get the list of  user types defined in the system."""
        queryset = UserType.objects.all().order_by('order')
        return self.custom_paginator(queryset)


class SchoolListView(BaseView):
    """
    A BaseView derivative class that lists the High schools added in backend.

    There is  option to query the schools.

    """

    serializer_class = DeviceSerializer

    def get(self, request, format=None):
        """Get the list of highschools defined in the system."""
        query = request.GET.get('query', None)
        if query:
            queries = [i.strip() for i in query.split(",")]
            name = queries[0]
            address_1 = queries[1] if len(queries) >= 2 else None
            address_2 = queries[2] if len(queries) >= 3 else None
            if name and address_1:
                queryset = School.objects.filter(
                    Q(name__icontains=name) |
                    Q(address_line1__icontains=address_1)).order_by('name')
            elif address_2:
                queryset = School.objects.filter(
                    Q(name__icontains=name) |
                    Q(address_line1__icontains=address_1) |
                    Q(address_line2__icontains=address_2) |
                    Q(address_line2__icontains=address_1) |
                    Q(address_line2__icontains=address_2)).order_by('name')
            else:
                queryset = School.objects.filter(
                    Q(name__icontains=name) |
                    Q(address_line1__icontains=name)).order_by('name')
        else:
            queryset = School.objects.all().order_by('name')
        self.serializer_class = SchoolSerializer
        return self.custom_paginator(queryset)

    def post(self, request):
        """Do some stuff here."""
        data = request.data.copy()
        data['app_info'] = request.META.get('HTTP_USER_AGENT') or\
            data.get('app_info')
        data['university'] = self.university.uid
        serializer = DeviceSerializer(data=data)
        if serializer.is_valid(self):
            serializer.save()
            output_serializer = SchoolSerializer()
            return Response(output_serializer.data, 201)
        else:
            return Response(serializer.errors, 400)


class MenuListView(BaseView):
    """A BaseView derivative class that lists the Menu added in backend."""

    serializer_class = MenuSerializer

    def get(self, request, format=None):
        """Get the list of menu items defined in the system."""
        queryset = Menu.objects.filter(active=True).order_by('order')
        return self.custom_paginator(queryset)


class HomePageView(BaseView):
    """A BaseView derivative class that shows details of home page."""

    serializer_class = HomePageSerializer

    def get(self, request, format=None):
        """Get the details of home page."""
        admin = request.user.admin
        home_page = CustomPage.objects.filter(
            home_page=True, university=admin.university).first()
        serializer = HomePageSerializer(instance=home_page)
        return Response(serializer.data)


class FilePolicyAPI(APIView):
    """
    This view is to get the AWS Upload Policy for our s3 bucket.

    What we do here is first create a File object instance in our
    Django backend. This is to include the File instance in the path
    we will use within our bucket as you'll see below.
    """

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.SessionAuthentication]

    def check_s3_key_exists(self, filename, file_extension, uuid_string):
        """Check if file with same key already exists in s3 bucket.

        If file with same key already exists on s3 bucket, append
        uuid to file name. uuid is the uid of the file object we created.
        """
        filename = "%(filename)s%(extension)s" % {
            'filename': slugify(filename), 'extension': file_extension}
        file_key = "{upload_env}/{filename}".format(
            upload_env=settings.AWS_UPLOAD_ENV, filename=filename)
        s3 = boto3.resource(
            's3', region_name=settings.AWS_UPLOAD_REGION,
            aws_access_key_id=settings.AWS_UPLOAD_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_UPLOAD_SECRET_KEY)

        try:
            s3.Object(settings.AWS_UPLOAD_BUCKET, file_key).load()
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                pass
            else:
                return None
        else:
            file_key = "%(existing_key)s-%(replaced_uid)s" %\
                {'existing_key': file_key.split(file_extension)[0],
                 'replaced_uid': uuid_string + file_extension}
        return file_key

    def post(self, request, *args, **kwargs):
        """
        The initial post request includes the filename.

        and auth credientails. we will generate file key,
        signature and policy.
        """
        filename_req = request.data.get('filename')
        university_id = request.data.get('university')
        replace_video_id = request.data.get('replace_video_id')
        if not filename_req:
            return Response({"message": "A filename is required"},
                            status=status.HTTP_400_BAD_REQUEST)
        if not (university_id and UniversityProfile.objects.filter(
                uid=university_id).exists()):
            return Response({"message": "University needs to be specified"},
                            status=status.HTTP_400_BAD_REQUEST)
        if replace_video_id and File.objects.filter(
                uid=replace_video_id).exists():
            file = File.objects.get(uid=replace_video_id)
            file.delete()
        policy_expires = int(time.time() + 5000)

        username_str = str(request.user.username)
        """
        Below we create the Django object. We'll use this
        in our upload path to AWS.

        Example:
        To-be-uploaded file's name: Some Random File.mp4
        Eventual Path on S3: <bucket>/<uploaded_env>/Some-Random-File.mp4
        """

        fname, file_extension = os.path.splitext(filename_req)
        university = UniversityProfile.objects.get(uid=university_id)
        file_obj = File.objects.create(
            name=fname,
            university=university)
        file_obj_id = file_obj.uid
        upload_start_path = self.check_s3_key_exists(fname, file_extension,
                                                     str(file_obj_id))
        if not upload_start_path:
            return Response(
                {"message": "Something error happened, please try again"},
                status=status.HTTP_400_BAD_REQUEST)

        file_key = upload_start_path.replace(settings.AWS_UPLOAD_ENV, '')
        filename_final = "{file_obj_id}{file_extension}".format(
            file_obj_id=file_obj_id,
            file_extension=file_extension)

        final_upload_path = "{upload_start_path}{filename_final}".format(
            upload_start_path=upload_start_path, filename_final=filename_final)
        if filename_req and file_extension:
            """
            Save the eventual path and key to the Django-stored File instance
            """
            file_obj.path = final_upload_path
            file_obj.file_key = file_key
            file_obj.save()

        policy_document_context = {
            "expire": policy_expires,
            "bucket_name": settings.AWS_UPLOAD_BUCKET,
            "key_name": "",
            "acl_name": "public-read",
            "content_name": "",
            "content_length": 524288000,
            "upload_start_path": "",

        }
        policy_document = """
        {"expiration": "2020-01-01T00:00:00Z",
          "conditions": [
            {"bucket": "%(bucket_name)s"},
            ["starts-with", "$key", "%(upload_start_path)s"],
            {"acl": "%(acl_name)s"},

            ["starts-with", "$Content-Type", "%(content_name)s"],
            ["starts-with", "$filename", ""],
            {'success_action_status':'201'},
            ["content-length-range", 0, %(content_length)d]
          ]
        }
        """ % policy_document_context

        aws_secret = str.encode(settings.AWS_UPLOAD_SECRET_KEY)
        policy_document_str_encoded = str.encode(
            policy_document.replace(" ", ""))

        url = 'https://s3.amazonaws.com/{bucket}'.format(
            bucket=settings.AWS_UPLOAD_BUCKET
        )
        policy = base64.b64encode(policy_document_str_encoded)
        signature = base64.b64encode(
            hmac.new(aws_secret, policy, hashlib.sha1).digest())
        data = {
            "policy": policy,
            "signature": signature,
            "key": settings.AWS_UPLOAD_ACCESS_KEY_ID,
            "file_bucket_path": upload_start_path,
            "file_id": file_obj_id,
            "filename": filename_req,
            "url": url,
            "username": username_str,
            "bucket": settings.AWS_UPLOAD_BUCKET,
            "accessKey": settings.AWS_UPLOAD_ACCESS_KEY_ID,
            "secretKey": settings.AWS_UPLOAD_SECRET_KEY
        }
        return Response(data, status=status.HTTP_200_OK)


class FileUploadCompleteHandler(APIView):
    """Update the Django File Model.

    Once Upload is completed, update the File details.
    """

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.SessionAuthentication]

    def post(self, request, *args, **kwargs):
        """Update the file object on call back function."""
        file_id = request.POST.get('file')
        size = request.POST.get('fileSize')
        obj_id = request.POST.get('obj_id')
        obj_type = request.POST.get('obj_type')
        data = {}
        type_ = request.POST.get('fileType')
        if file_id:
            obj = File.objects.get(uid=file_id)
            obj.size = int(size)
            obj.uploaded = True
            obj.type = type_
            obj.save()
            data['id'] = obj.uid
            data['saved'] = True
        if obj_type and obj_id:
            if obj_type == 'custom_page' and\
                    CustomPage.objects.filter(uid=obj_id).exists():
                page = CustomPage.objects.get(uid=obj_id)
                page.video = obj
                page.save()
            elif obj_type == 'college' and\
                    College.objects.filter(uid=obj_id).exists():
                college = College.objects.get(uid=obj_id)
                college.video = obj
                college.save()
        return Response(data, status=status.HTTP_200_OK)


class CustomPageDetailView(BaseView):
    """A BaseView derivative class that shows details of page."""

    serializer_class = HomePageSerializer

    def get(self, request, page_uid, format=None):
        """Get the details of page."""
        page = CustomPage.objects.filter(uid=page_uid).first()
        web_view = bool(request.GET.get('web_view', False))
        if not page:
            raise Http404
        serializer = PageSerializer(instance=page, web_view=web_view)
        return Response(serializer.data)


class CollegeListView(BaseView):
    """A BaseView derivative class that lists all colleges."""

    serializer_class = CollegeListSerializer

    def get(self, request, format=None):
        """Get the list of  colleges."""
        queryset = College.objects.filter(active=True).distinct()

        # queryset = queryset.distinct()
        return self.custom_paginator(queryset.order_by('name'), paginate=True)

    def post(self, request):
        """Do some filtering here.

        ---
            {
                "filter": {
                    "majors": [
                        "f9a0905f-0dab-4802-b2b5-7278f1ecc093",
                        "d9c7cd13-0df5-49e2-87cb-f7bcec1b75d3",
                        "7d2f0a53-7976-4735-a69e-45e66c834b48"
                    ],
                    "state_type": "in_state",
                    "query": "Nc College",
                    "sat_score_range": {
                        "min": 400,
                        "max": 1600
                    },
                    "act_score_range": {
                        "min": 1,
                        "max": 36
                    },
                    "avg_cost_range": {
                        "min": 500,
                        "max": 2000
                    },
                    "student_capacity": {
                        "operator": "bt",
                        "value1": 5000,
                        "value2": 10000
                    },
                    "location_poly": {
                        "lat1": "-11.13301327",
                        "lng1": "-75.89342594",
                        "lat2": "-11.13151844",
                        "lng2": "-75.89605987"
                    }
                },
                "pagination": {
                    "offset": 41,
                    "limit": 20
                }
            }

            Note: state_type will be defaulted to in_state
        ---
        """
        data = request.data.copy()
        # import ipdb; ipdb.set_trace()
        filters = data.get('filter', '{}')
        queryset = College.objects.filter(active=True)
        if filters:
            query = filters.get('query')
            majors = filters.get('majors', [])
            state_type = filters.get(
                'state_type', 'in_state')
            sat_score_range = filters.get('sat_score_range', {})
            act_score_range = filters.get('act_score_range', {})
            avg_cost_range = filters.get('avg_cost_range', {})
            student_capacity = filters.get('student_capacity', {})
            location_poly = filters.get('location_poly', {})
            disability_access = filters.get(
                'disability_access', None)
            if bool(student_capacity) and 'operator' not in student_capacity:
                raise ErrorBadParameters(
                    'operator should be specified in student_capacity.')

            if query:
                queryset = queryset.filter(name__icontains=query)
            if majors:
                queryset = queryset.filter(majors__in=majors)
            if bool(sat_score_range):
                if "min" not in sat_score_range \
                        or "max" not in sat_score_range:
                    raise ErrorBadParameters(
                        'Please provide min & max in sat_score_range')

                if state_type == 'in_state':
                    queryset = queryset.filter(
                        in_state_sat_score__gte=sat_score_range["min"],
                        in_state_sat_score__lte=sat_score_range["max"])
                else:
                    queryset = queryset.filter(
                        out_state_sat_score__gte=sat_score_range["min"],
                        out_state_sat_score__lte=sat_score_range["max"])
            if bool(act_score_range):
                if "min" not in act_score_range \
                        or "max" not in act_score_range:
                    raise ErrorBadParameters(
                        'Please provide min & max in act_score_range')

                if state_type == 'in_state':
                    queryset = queryset.filter(
                        in_state_act_score__gte=act_score_range["min"],
                        in_state_act_score__lte=act_score_range["max"])
                else:
                    queryset = queryset.filter(
                        out_state_act_score__gte=act_score_range["min"],
                        out_state_act_score__lte=act_score_range["max"])
            if bool(avg_cost_range):
                if "min" not in avg_cost_range \
                        or "max" not in avg_cost_range:
                    raise ErrorBadParameters(
                        'Please provide min & max in avg_cost_range')
                if state_type == 'in_state':
                    queryset = queryset.filter(
                        in_state_cost_per_year__gte=avg_cost_range["min"],
                        in_state_cost_per_year__lte=avg_cost_range["max"])
                else:
                    queryset = queryset.filter(
                        out_state_cost_per_year__gte=avg_cost_range["min"],
                        out_state_cost_per_year__lte=avg_cost_range["max"])
            if bool(student_capacity):
                if student_capacity['operator'] == 'bt':
                    if 'value1' not in student_capacity \
                            or 'value2' not in student_capacity:
                        raise ErrorBadParameters('Specify `value1` and \
                            `value2` in student_capacity')
                    queryset = queryset.filter(
                        student_capacity__gte=student_capacity['value1'],
                        student_capacity__lte=student_capacity['value2'])
                elif student_capacity['operator'] == 'gt':
                    if 'value1' not in student_capacity:
                        raise ErrorBadParameters(
                            'Specify `value1` in student_capacity')
                    queryset = queryset.filter(
                        student_capacity__gt=student_capacity['value1'])
                elif student_capacity['operator'] == 'lt':
                    if 'value1' not in student_capacity:
                        raise ErrorBadParameters(
                            'Specify `value1` in student_capacity')
                    queryset = queryset.filter(
                        student_capacity__lt=student_capacity['value1'])
                elif student_capacity['operator'] == 'eq':
                    if 'value1' not in student_capacity:
                        raise ErrorBadParameters(
                            'Specify `value1` in student_capacity')
                    queryset = queryset.filter(
                        student_capacity=student_capacity['value1'])
                else:
                    raise ErrorBadParameters(
                        'Invalid operator specified in student_capacity.')

            if bool(location_poly):
                if 'lat1' not in location_poly or 'lng1' not in location_poly \
                        or 'lat2' not in location_poly \
                        or 'lng2' not in location_poly:
                    raise ErrorBadParameters(
                        'Send location parameters in specified format')

                try:
                    lat1 = location_poly.get('lat1')
                    lng1 = location_poly.get('lng1')
                    lat2 = location_poly.get('lat2')
                    lng2 = location_poly.get('lng2')
                    area_points = [(float(lng1), float(lat1)),
                                   (float(lng1), float(lat2)),
                                   (float(lng2), float(lat2)),
                                   (float(lng2), float(lat1)),
                                   (float(lng1), float(lat1))]
                except Exception as e:
                    print(e)
                    raise ErrorBadParameters("Invalid location coordinates")
                poly = Polygon(area_points)
                queryset = queryset.filter(location__contained=poly)
            if disability_access:
                queryset = queryset.filter(
                    disability_access=True,
                    disability_access_url__isnull=False)

        queryset = queryset.distinct()
        return self.custom_paginator(queryset.order_by('name'), paginate=True)


class CollegeDetailView(BaseView):
    """A BaseView derivative class that shows details of College."""

    serializer_class = CollegeSerializer

    def get(self, request, college_uid, format=None):
        """Get the details of home page."""
        college = College.objects.filter(uid=college_uid).first()
        if not college:
            raise Http404
        base_url = '%(scheme)s://%(http_host)s' % {
            'scheme': request._request.scheme,
            'http_host': request._request.META.get('HTTP_HOST')}

        add_tile = bool(request.GET.get('add_tile', False))
        web_view = bool(request.GET.get('web_view', False))
        serializer = CollegeSerializer(
            instance=college, base_url=base_url, add_tile=add_tile, web_view=web_view)
        return Response(serializer.data)


class MajorListView(BaseView):
    """A BaseView derivative class that lists the Majors added in backend."""

    serializer_class = MajorSerializer

    def get(self, request, format=None):
        """Get the list of majors defined in the system."""
        queryset = Major.objects.filter(active=True).order_by('title')
        query = request.GET.get('query', None)
        if query:
            queryset = queryset.filter(title__icontains=query)
        return self.custom_paginator(queryset)


class CareerListView(BaseView):
    """A BaseView derivative class that lists all colleges."""

    serializer_class = CareerListSerializer

    def get(self, request, format=None):
        """Get the list of  colleges."""
        queryset = Career.objects.filter(active=True).distinct()

        # queryset = queryset.distinct()
        return self.custom_paginator(queryset.order_by('career'), paginate=True)


class CareerDetailView(BaseView):
    """A BaseView derivative class that shows details of College."""

    serializer_class = CareerSerializer

    def get(self, request, career_uid, format=None):
        """Get the details of home page."""
        career = Career.objects.filter(uid=career_uid).first()
        if not career:
            raise Http404
        base_url = '%(scheme)s://%(http_host)s' % {
            'scheme': request._request.scheme,
            'http_host': request._request.META.get('HTTP_HOST')}

        add_tile = bool(request.GET.get('add_tile', False))
        web_view = bool(request.GET.get('web_view', False))
        serializer = CareerSerializer(
            instance=career, base_url=base_url, add_tile=add_tile, web_view=web_view)
        return Response(serializer.data)
