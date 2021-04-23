"""Urls defined."""
from django.urls import path, include
from django.views.generic import TemplateView
from core.views import LoginView, DashBoard, LogoutView, ManageSchoolView,\
    ManageMenuView, ManageHomePageView, FileView, ManageCustomView,\
    ManageMajorsView, ManageCollegesView, CollegeDetailView,\
    AdminDashBoard, EditProfileView, ManageUniversityView,\
    ManageAPICredentialView, ManageAdminView, ManageLogView,\
    ManageCareersView, CareerDetailView

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('dashboard/', DashBoard.as_view(), name='university-home-page'),
    path('admin/', AdminDashBoard.as_view(), name="admin-dashboard"),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('manage_schools/', ManageSchoolView.as_view(), name='manage-schools'),
    path('manage_menu/', ManageMenuView.as_view(), name='manage-menu'),
    path('manage_home_page/', ManageHomePageView.as_view(),
         name='manage-home-page'),
    path('manage_file/', FileView.as_view(),
         name='manage-file'),
    path('manage_custom_pages/', ManageCustomView.as_view(),
         name='manage-custom-page'),
    path('manage_majors/', ManageMajorsView.as_view(),
         name='manage-majors'),
    path('manage-colleges/', ManageCollegesView.as_view(),
         name='manage-colleges'),
    path('college/', CollegeDetailView.as_view(),
         name='college-create'),
    path('college/<uuid:college_uid>/', CollegeDetailView.as_view(),
         name='college-detail'),
    path('404/', TemplateView.as_view(template_name='404.html'), name='404'),
    path('profile/', EditProfileView.as_view(), name='edit-profile'),
    path('manage_university/',
         ManageUniversityView.as_view(), name='manage-university'),
    path('manage_credentials/',
         ManageAPICredentialView.as_view(), name='manage-credentials'),
    path('manage_admin/',
         ManageAdminView.as_view(), name='manage-admin'),
    path('manage_logs/',
         ManageLogView.as_view(), name='manage-logs'),
    path('manage-careers/', ManageCareersView.as_view(),
         name='manage-careers'),
    path('career/', CareerDetailView.as_view(),
         name='career-create'),
    path('career/<uuid:career_uid>/', CareerDetailView.as_view(),
         name='career-detail'),
    path('', include('django.contrib.auth.urls')),
]
