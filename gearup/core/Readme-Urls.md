# Django Project URL Configuration

This `README.md` file provides documentation for the `urls.py` file, which is located in the `core` folder of your Django project. The `urls.py` file is a crucial part of your Django project as it defines the URL patterns and routes for your web application.

## Table of Contents

- [Introduction](#introduction)
- [URL Patterns](#url-patterns)
  - [Home Page](#home-page)
  - [Dashboard](#dashboard)
  - [Admin Dashboard](#admin-dashboard)
  - [Login](#login)
  - [Logout](#logout)
  - [Manage Schools](#manage-schools)
  - [Manage Menu](#manage-menu)
  - [Manage Home Page](#manage-home-page)
  - [Manage Files](#manage-files)
  - [Manage Custom Pages](#manage-custom-pages)
  - [Manage Majors](#manage-majors)
  - [Manage Colleges](#manage-colleges)
  - [College Detail](#college-detail)
  - [404 Page](#404-page)
  - [Edit Profile](#edit-profile)
  - [Manage University](#manage-university)
  - [Manage API Credentials](#manage-api-credentials)
  - [Manage Admin](#manage-admin)
  - [Manage Logs](#manage-logs)
  - [Manage Careers](#manage-careers)
  - [Career Detail](#career-detail)
- [Conclusion](#conclusion)

## Introduction

The `urls.py` file in your Django project's `core` folder defines the URL patterns and their corresponding views for your web application. This file plays a pivotal role in routing incoming requests to the appropriate views, enabling users to access different parts of your web application.

## URL Patterns

### Home Page

- **URL**: `/`
- **View**: `TemplateView` with the template name 'index.html'
- **Name**: `index`

This URL pattern maps the root URL of your application to the home page template, which is usually the landing page for your site.

### Dashboard

- **URL**: `/dashboard/`
- **View**: `DashBoard` view class
- **Name**: `university-home-page`

This URL pattern maps the `/dashboard/` URL to the `DashBoard` view, which presumably displays a dashboard for your university-related content.

### Admin Dashboard

- **URL**: `/admin/`
- **View**: `AdminDashBoard` view class
- **Name**: `admin-dashboard`

This URL pattern is for accessing the admin dashboard of your application, typically for administrative tasks.

### Login

- **URL**: `/login/`
- **View**: `LoginView` view class
- **Name**: `login`

This URL pattern is for accessing the login page, allowing users to log into your application.

### Logout

- **URL**: `/logout/`
- **View**: `LogoutView` view class
- **Name**: `logout`

This URL pattern is for logging users out of your application.

### Manage Schools

- **URL**: `/manage_schools/`
- **View**: `ManageSchoolView` view class
- **Name**: `manage-schools`

This URL pattern is used for managing schools within your application.

### Manage Menu

- **URL**: `/manage_menu/`
- **View**: `ManageMenuView` view class
- **Name**: `manage-menu`

This URL pattern is used for managing the menu of your application.

### Manage Home Page

- **URL**: `/manage_home_page/`
- **View**: `ManageHomePageView` view class
- **Name**: `manage-home-page`

This URL pattern is used for managing the home page content of your application.

### Manage Files

- **URL**: `/manage_file/`
- **View**: `FileView` view class
- **Name**: `manage-file`

This URL pattern is used for managing files within your application.

### Manage Custom Pages

- **URL**: `/manage_custom_pages/`
- **View**: `ManageCustomView` view class
- **Name**: `manage-custom-page`

This URL pattern is used for managing custom pages in your application.

### Manage Majors

- **URL**: `/manage_majors/`
- **View**: `ManageMajorsView` view class
- **Name**: `manage-majors`

This URL pattern is used for managing majors within your application.

### Manage Colleges

- **URL**: `/manage-colleges/`
- **View**: `ManageCollegesView` view class
- **Name**: `manage-colleges`

This URL pattern is used for managing colleges within your application.

### College Detail

- **URL**: `/college/` and `/college/<uuid:college_uid>/`
- **View**: `CollegeDetailView` view class
- **Name**: `college-create` and `college-detail`

These URL patterns are used for creating and viewing college details, possibly using a unique identifier (`college_uid`).

### 404 Page

- **URL**: `/404/`
- **View**: `TemplateView` with the template name '404.html'
- **Name**: `404`

This URL pattern maps to a custom 404 error page.

### Edit Profile

- **URL**: `/profile/`
- **View**: `EditProfileView` view class
- **Name**: `edit-profile`

This URL pattern allows users to edit their profiles.

### Manage University

- **URL**: `/manage_university/`
- **View**: `ManageUniversityView` view class
- **Name**: `manage-university`

This URL pattern is used for managing university-related content.

### Manage API Credentials

- **URL**: `/manage_credentials/`
- **View**: `ManageAPICredentialView` view class
- **Name**: `manage-credentials`

This URL pattern is used for managing API credentials within your application.

### Manage Admin

- **URL**: `/manage_admin/`
- **View**: `ManageAdminView` view class
- **Name**: `manage-admin`

This URL pattern is used for managing administrative tasks within your application.

### Manage Logs

- **URL**: `/manage_logs/`
- **View**: `ManageLogView` view class
- **Name**: `manage-logs`

This URL pattern is used for managing logs within your application.

### Manage Careers

- **URL**: `/manage-careers/`
- **View**: `ManageCareersView` view class
- **Name**: `manage-careers`

This URL pattern is used for managing careers within your application.

### Career Detail

- **URL**: `/career/` and `/career/<uuid:career_uid>/`
- **View**: `CareerDetailView` view class
- **Name**: `career-create` and `career-detail`

These URL patterns are used for creating and viewing career details, possibly using a unique identifier (`career_uid`).

## Conclusion

This `urls.py` file defines the URL patterns and their corresponding views for various parts of your Django web application. By following these URL patterns, users can access different pages and functionalities within your application, making it a crucial component of your project's routing system.
