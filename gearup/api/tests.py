"""Test cases for api."""

from django.contrib.auth.models import User
from django.contrib.gis.geos.point import Point
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Admin, College, CustomPage, School, UniversityProfile, UserType


class TokenGenerationTests(APITestCase):
    """Test case to check jwt authentication."""

    def setUp(self):
        """Define intial Values."""
        self.username = "sherlock"
        self.password = "holmes"
        self.data = {"username": self.username, "password": self.password}

    def test_current_user(self):
        """Testing creation of user and generation of token."""
        # URL using path name
        url = reverse("token_obtain_pair")

        # Create a user is a workaround in order to authentication works
        user = User.objects.create_user(
            username="sherlock",
            email="sherlock@holmes.com",
            password="holmes",
            is_active=True,
        )
        self.assertEqual(user.is_active, 1, "Active User")

        university = UniversityProfile.objects.get_or_create(
            name="NC University", active=True
        )[0]
        admin = Admin(user=user, role="silent_login", active=True)
        admin.save()
        admin.universities.set([university])
        admin.save()

        # First post to get token
        response = self.client.post(url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)
        token = response.data["access"]

        # Next post/get's will require the token to connect
        self.client.credentials(HTTP_AUTHORIZATION="Bearer {0}".format(token))
        response = self.client.get(reverse("user_type_list"), data={"format": "json"})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)


class ObtainTokenBase(APITestCase):
    """Base Class to obtain token after creating user."""

    def setUp(self):
        """Initialise Values."""
        self.username = "sherlock"
        self.password = "holmes"
        self.email = "sherlock@holmes.com"
        self.data = {"username": self.username, "password": self.password}

    def obtain_token(self):
        """Obtain JWT token."""
        if User.objects.filter(username=self.username).exists():
            user = User.objects.filter(username=self.username).first()
        else:
            user = User.objects.create_user(
                username="sherlock",
                email="sherlock@holmes.com",
                password="holmes",
                is_active=True,
            )
        university = UniversityProfile.objects.get_or_create(
            name="NC University", active=True
        )[0]
        admin = Admin.objects.get_or_create(
            user=user, role="silent_login", active=True
        )[0]
        admin.save()
        admin.universities.set([university])
        admin.save()
        self.assertEqual(user.is_active, 1, "Active User")

        response = self.client.post(
            reverse("token_obtain_pair"), self.data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)
        token = response.data["access"]
        return token, university


class CreateNewDeviceTest(ObtainTokenBase):
    """Test module for inserting a new device."""

    def setUp(self):
        """Initialise Values."""
        super().setUp()
        token, university = self.obtain_token()
        user_type = UserType.objects.get_or_create(
            title="Student", university=university
        )[0]
        school = School.objects.get_or_create(name="RajaGiri", university=university)[0]
        self.valid_payload = {
            "device_id": "d9a8bd8f-8371-4d45-816c-c01517daf2c8",
            "user_type": user_type.uid,
            "custom_school": school.uid,
            "app_info": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6)",
        }
        self.invalid_payload = {
            "device_id": "",
            "user_type": "techer",
            "custom_school": "Pamerion",
            "app_info": "",
        }

    def test_create_valid_device(self):
        """Sample create."""
        token, university = self.obtain_token()
        self.client.credentials(HTTP_AUTHORIZATION="Bearer {0}".format(token))
        response = self.client.post(
            reverse("school_list"), self.valid_payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_device(self):
        """Sample create."""
        token, university = self.obtain_token()
        self.client.credentials(HTTP_AUTHORIZATION="Bearer {0}".format(token))
        response = self.client.post(
            reverse("school_list"), self.invalid_payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SchoolList(ObtainTokenBase):
    """Test for School list api."""

    def test_school_list(self):
        """Test for School list api."""
        token, university = self.obtain_token()

        self.client.credentials(HTTP_AUTHORIZATION="Bearer {0}".format(token))
        response = self.client.get(reverse("school_list"), data={"format": "json"})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)


class MenuList(ObtainTokenBase):
    """Test for Menu Listing api."""

    def test_menu_list(self):
        """Test for Menu Listing api."""
        token, university = self.obtain_token()

        self.client.credentials(HTTP_AUTHORIZATION="Bearer {0}".format(token))
        response = self.client.get(reverse("menu_list"), data={"format": "json"})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)


class UserTypeList(ObtainTokenBase):
    """Test for user list endpoint."""

    def test_user_type_list(self):
        """Test for user list endpoint."""
        token, university = self.obtain_token()

        self.client.credentials(HTTP_AUTHORIZATION="Bearer {0}".format(token))
        response = self.client.get(reverse("user_type_list"), data={"format": "json"})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)


class HomePage(ObtainTokenBase):
    """Test for homepage."""

    def test_home_page(self):
        """Test for user list endpoint."""
        token, university = self.obtain_token()

        self.client.credentials(HTTP_AUTHORIZATION="Bearer {0}".format(token))
        response = self.client.get(reverse("home_page"), data={"format": "json"})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)


class CustomPageTest(ObtainTokenBase):
    """Test for Custom page."""

    def test_custom_page(self):
        """Test for user list endpoint."""
        token, university = self.obtain_token()
        page = CustomPage.objects.get_or_create(title="Sample", university=university)[
            0
        ]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer {0}".format(token))
        response = self.client.get(
            reverse("custom_page", kwargs={"page_uid": page.uid}),
            data={"format": "json"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)


class CollegeList(ObtainTokenBase):
    """Test for college list endpoint."""

    def test_college_list(self):
        """Test for user list endpoint."""
        token, university = self.obtain_token()

        self.client.credentials(HTTP_AUTHORIZATION="Bearer {0}".format(token))
        response = self.client.get(reverse("college_list"), data={"format": "json"})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)


class CollegeDetailTest(ObtainTokenBase):
    """Test for Custom page."""

    def test_user_type_list(self):
        """Test for user list endpoint."""
        token, university = self.obtain_token()
        college = College(
            name="Emory College",
            in_state_cost_per_year=47954,
            student_capacity=6867,
            address="Atlanta, GA",
            location=Point(float("-90.3084017323959"), float("38.64724015"), srid=4326),
            university=university,
        )
        college.save()
        self.client.credentials(HTTP_AUTHORIZATION="Bearer {0}".format(token))
        response = self.client.get(
            reverse("college_detail", kwargs={"college_uid": college.uid}),
            data={"format": "json"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)
