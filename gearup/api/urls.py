"""Defines all the api urls."""

from django.urls import path

from api.views import (
    CareerDetailView,
    CareerListView,
    CollegeDetailView,
    CollegeListView,
    CustomPageDetailView,
    FilePolicyAPI,
    FileUploadCompleteHandler,
    HomePageView,
    JWTTokenObtainPairSerializer,
    MajorListView,
    MenuListView,
    SchoolListView,
    UserTypeListView,
)

urlpatterns = [
    path("token/", JWTTokenObtainPairSerializer.as_view(), name="token_obtain_pair"),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("user_types/", UserTypeListView.as_view(), name="user_type_list"),
    path("schools/", SchoolListView.as_view(), name="school_list"),
    path("menus/", MenuListView.as_view(), name="menu_list"),
    path("home_page/", HomePageView.as_view(), name="home_page"),
    path("files/policy/", FilePolicyAPI.as_view(), name="upload-policy"),
    path(
        "files/complete/", FileUploadCompleteHandler.as_view(), name="upload-complete"
    ),
    path("pages/<uuid:page_uid>", CustomPageDetailView.as_view(), name="custom_page"),
    path("colleges/", CollegeListView.as_view(), name="college_list"),
    path(
        "colleges/<uuid:college_uid>",
        CollegeDetailView.as_view(),
        name="college_detail",
    ),
    path("majors/", MajorListView.as_view(), name="major_list"),
    path("careers/", CareerListView.as_view(), name="careers_list"),
    path("careers/<uuid:career_uid>", CareerDetailView.as_view(), name="career_detail"),
]
