# Django Admin Classes Documentation

This README.md document provides documentation for the Django admin classes defined in the `admin.py` file of our Django project. These admin classes are used to customize the admin interface for various models in our project.

## Table of Contents

- [UniversityProfileAdmin (Admin for University Profiles)](#universityprofileadmin-admin-for-university-profiles)
- [AdminProfileAdmin (Admin for Admin Profiles)](#adminprofileadmin-admin-for-admin-profiles)
- [UserTypeAdmin (Admin for User Types)](#usertypeadmin-admin-for-user-types)
- [DeviceAdmin (Admin for Devices)](#deviceadmin-admin-for-devices)
- [MenuAdmin (Admin for Menu Items)](#menuadmin-admin-for-menu-items)
- [PersonalAdmin (Admin for Personal Information)](#personaladmin-admin-for-personal-information)
- [SchoolAdmin (Admin for Schools)](#schooladmin-admin-for-schools)
- [CustomPageAdmin (Admin for Custom Pages)](#custompageadmin-admin-for-custom-pages)
- [CollegeAdmin (Admin for Colleges)](#collegeadmin-admin-for-colleges)
- [TileAdmin (Admin for Tiles)](#tileadmin-admin-for-tiles)
- [CareerAdmin (Admin for Careers)](#careeradmin-admin-for-careers)

## UniversityProfileAdmin (Admin for University Profiles)

The `UniversityProfileAdmin` class is used to customize the admin interface for UniversityProfile model.

### No Customization

This admin class does not have any customizations and inherits the default behavior of the admin interface.

## AdminProfileAdmin (Admin for Admin Profiles)

The `AdminProfileAdmin` class is used to customize the admin interface for AdminProfile model.

### No Customization

This admin class does not have any customizations and inherits the default behavior of the admin interface.

## UserTypeAdmin (Admin for User Types)

The `UserTypeAdmin` class is used to customize the admin interface for UserType model.

### List Filter

- `university`: Allows filtering UserType objects by associated university.

## DeviceAdmin (Admin for Devices)

The `DeviceAdmin` class is used to customize the admin interface for Device model.

### List Filter

- `university`: Allows filtering Device objects by associated university.

## MenuAdmin (Admin for Menu Items)

The `MenuAdmin` class is used to customize the admin interface for Menu model.

### List Filter

- `university`: Allows filtering Menu objects by associated university.

## PersonalAdmin (Admin for Personal Information)

The `PersonalAdmin` class is used to customize the admin interface for PersonalInfo model.

### List Filter

- `first_name`: Allows filtering PersonalInfo objects by first name.

## SchoolAdmin (Admin for Schools)

The `SchoolAdmin` class is used to customize the admin interface for School model.

### List Filter

- `university`: Allows filtering School objects by associated university.

### List Display

- `name`: Display the 'name' field in the list view.

## CustomPageAdmin (Admin for Custom Pages)

The `CustomPageAdmin` class is used to customize the admin interface for CustomPage model.

### List Filter

- `university`: Allows filtering CustomPage objects by associated university.

## CollegeAdmin (Admin for Colleges)

The `CollegeAdmin` class is used to customize the admin interface for College model.

### List Filter

- `university`: Allows filtering College objects by associated university.

## TileAdmin (Admin for Tiles)

The `TileAdmin` class is used to customize the admin interface for Tile model.

### List Filter

- `university`: Allows filtering Tile objects by associated university.

## CareerAdmin (Admin for Careers)

The `CareerAdmin` class is used to customize the admin interface for Career model.

### List Filter

- `university`: Allows filtering Career objects by associated university.
