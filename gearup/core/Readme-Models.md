
# Django Models Documentation

This `README.md` file provides documentation for the Django models defined in your Django project. These models represent various aspects of your application's data structure and functionality.

## Table of Contents
- [Gender](#gender)
- [UniversityProfile](#universityprofile)
- [Admin](#admin)
- [UserType](#usertype)
- [Device](#device)
- [Menu](#menu)
- [School](#school)
- [Tile](#tile)
- [PersonalInfo](#personalinfo)
- [About](#about)
- [CustomPage](#custompage)
- [Major](#major)
- [College](#college)
- [File](#file)
- [user_updated Function](#user_updated-function)
- [AuditVersion Model](#auditversion-model)


## Gender

### Fields
- `uid`: UUIDField (Primary Key)
- `options`: CharField (Max Length: 250)
- `order`: PositiveSmallIntegerField (Default: 0)
- `content`: TextField
- `created`: DateTimeField (Auto-Generated)

This model represents gender details when a user first logs in.

## UniversityProfile

### Fields
- `uid`: UUIDField (Primary Key)
- `created`: DateTimeField (Auto-Generated)
- `name`: CharField (Max Length: 250, Nullable)
- `logo`: FileField (Nullable)
- `address`: TextField (Nullable)
- `location`: PointField (Nullable)
- `email`: EmailField (Nullable)
- `phone_number`: CharField (Max Length: 20, Nullable)
- `active`: BooleanField (Default: True)

This model defines user profiles for universities.

## Admin

### Fields
- `uid`: UUIDField (Primary Key)
- `user`: OneToOneField (User, Related Name: 'admin', on_delete: CASCADE)
- `image`: FileField (Nullable)
- `created`: DateTimeField (Auto-Generated)
- `verified`: BooleanField (Default: False)
- `invited_date`: DateTimeField (Auto-Generated)
- `universities`: ManyToManyField (UniversityProfile, Related Name: 'universities')
- `active`: BooleanField (Default: True)
- `role`: CharField (Choices: 'super_admin', 'admin', 'silent_login', Default: 'admin', Max Length: 100)
- `silent_login_password`: CharField (Max Length: 16, Nullable)

This model defines administrators with various roles and related university profiles.

## UserType

### Fields
- `uid`: UUIDField (Primary Key)
- `title`: CharField (Max Length: 100)
- `order`: PositiveSmallIntegerField (Default: 0)
- `created`: DateTimeField (Auto-Generated)
- `university`: ForeignKey (UniversityProfile, on_delete: CASCADE)

This model defines user types associated with universities.

## Device

### Fields
- `uid`: UUIDField (Primary Key)
- `device_id`: CharField (Max Length: 100)
- `app_info`: CharField (Max Length: 500, Nullable)
- `user_type`: ForeignKey (UserType, Nullable, on_delete: CASCADE)
- `school`: ForeignKey ('School', Nullable, on_delete: CASCADE)
- `custom_school`: CharField (Max Length: 200, Blank)
- `gender`: ForeignKey (Gender, Nullable, on_delete: CASCADE)
- `created`: DateTimeField (Auto-Generated)
- `modified`: DateTimeField (Auto-Generated)
- `university`: ForeignKey (UniversityProfile, on_delete: CASCADE)

This model stores device details, including user type, school, and gender, when the app is first used.


## Menu

### Fields
- `uid`: UUIDField (Primary Key)
- `title`: CharField (Max Length: 100)
- `icon`: FileField (Nullable)
- `url_type`: CharField (Choices: 'native', 'external', 'pre_defined', Default: 'native', Max Length: 100)
- `url`: CharField (Max Length: 500, Nullable)
- `active`: BooleanField (Default: True)
- `order`: PositiveSmallIntegerField (Default: 0)
- `page`: ForeignKey ('CustomPage', Nullable, on_delete: CASCADE, Related Name: 'menu_page')
- `key_name`: CharField (Max Length: 20, Nullable)
- `created`: DateTimeField (Auto-Generated)
- `university`: ForeignKey (UniversityProfile, on_delete: CASCADE)

This model is used to manage menu records in your application.

## School

### Fields
- `uid`: UUIDField (Primary Key)
- `name`: CharField (Max Length: 250)
- `lea_name`: CharField (Max Length: 250, Nullable)
- `address_line1`: CharField (Max Length: 200, Blank)
- `address_line2`: CharField (Max Length: 200, Blank)
- `city`: CharField (Max Length: 200, Blank)
- `state`: CharField (Max Length: 200, Blank)
- `zip_code`: CharField (Max Length: 200, Blank)
- `point`: PointField (Nullable)
- `created`: DateTimeField (Auto-Generated)
- `university`: ForeignKey (UniversityProfile, on_delete: CASCADE)

This model is used to manage high school details when a user first logs in.

## Tile

### Fields
- `uid`: UUIDField (Primary Key)
- `title`: CharField (Max Length: 100)
- `url`: CharField (Max Length: 500, Nullable)
- `active`: BooleanField (Default: True)
- `url_type`: CharField (Choices: 'native', 'external', Default: 'native', Max Length: 100)
- `description`: CharField (Max Length: 250, Nullable)
- `image`: FileField (Nullable)
- `order`: PositiveSmallIntegerField (Default: 0)
- `page`: ForeignKey ('CustomPage', Nullable, on_delete: CASCADE, Related Name: 'tile_page')
- `created`: DateTimeField (Auto-Generated)
- `university`: ForeignKey (UniversityProfile, on_delete: CASCADE)
- `modified_by_page`: CharField (Max Length: 10, Nullable)

This model is used to manage custom tiles for the home page and other custom pages in your application.

## PersonalInfo

### Fields
- `uid`: UUIDField (Primary Key)
- `first_name`: CharField (Max Length: 20, Nullable)
- `last_name`: CharField (Max Length: 20, Nullable)
- `dob`: CharField (Max Length: 20, Nullable)
- `device_id`: CharField (Max Length: 100, Nullable)

This model stores personal information, including first name, last name, date of birth, and device ID.

## About

### Fields
- `uid`: UUIDField (Primary Key)
- `about_value`: CharField (Max Length: 20, Nullable)

This model represents an "about" value.

## CustomPage

### Fields
- `uid`: UUIDField (Primary Key)
- `title`: CharField (Max Length: 250)
- `created`: DateTimeField (Auto-Generated)
- `modified`: DateTimeField (Auto-Generated)
- `video`: ForeignKey ('File', Nullable, on_delete: SET_NULL, Related Name: 'page')
- `youtube_url`: ForeignKey ('File', Nullable, on_delete: SET_NULL, Related Name: 'custompage_url')
- `content`: TextField
- `mobile_page`: TextField
- `active`: BooleanField (Default: True)
- `tiles`: ManyToManyField (Tile, Blank)
- `home_page`: BooleanField (Default: False)
- `university`: ForeignKey (UniversityProfile, on_delete: CASCADE)

This model is used to manage custom pages within your application.



## Major

### Fields
- `uid`: UUIDField (Primary Key)
- `title`: CharField (Max Length: 250)
- `description`: TextField
- `active`: BooleanField (Default: True)
- `created`: DateTimeField (Auto-Generated)
- `university`: ForeignKey (UniversityProfile, on_delete=models.CASCADE)

This model is used to manage majors offered by universities.

## College

### Fields
- `uid`: UUIDField (Primary Key)
- `active`: BooleanField (Default: True)
- `name`: CharField (Max Length: 250)
- `short_name`: CharField (Max Length: 50, Nullable)
- `email`: EmailField (Nullable)
- `student_capacity`: PositiveIntegerField (Default: 0)
- `phone_number`: CharField (Max Length: 20, Nullable)
- `facebook_url`: URLField (Nullable)
- `twitter_url`: URLField (Nullable)
- `linkedin_url`: URLField (Nullable)
- `website`: URLField (Nullable)
- `content`: TextField (Nullable)
- `mobile_content`: TextField (Nullable)
- `mobile_url`: TextField (Nullable)
- `tags`: TextField (Nullable)
- `created`: DateTimeField (Auto-Generated)
- `modified`: DateTimeField (Auto-Generated)
- `in_state_sat_score`: PositiveIntegerField (Default: 0)
- `in_state_act_score`: PositiveIntegerField (Default: 0)
- `in_state_cost_per_year`: PositiveIntegerField (Default: 0)
- `out_state_sat_score`: PositiveIntegerField (Default: 0)
- `out_state_act_score`: PositiveIntegerField (Default: 0)
- `out_state_cost_per_year`: PositiveIntegerField (Default: 0)
- `majors`: ManyToManyField ('Major', Blank)
- `disability_access`: BooleanField (Default: False)
- `disability_access_url`: URLField (Nullable)
- `video`: ForeignKey ('File', Nullable, on_delete: SET_NULL, Related Name: 'college')
- `youtube_url`: ForeignKey ('File', Nullable, on_delete: SET_NULL, Related Name: 'college_url')
- `logo`: FileField (Nullable)
- `tiles`: ManyToManyField ('Tile', Blank)
- `address`: TextField (Nullable)
- `location`: PointField (Nullable)
- `university`: ForeignKey (UniversityProfile, on_delete=models.CASCADE)

This model is used to manage information about colleges affiliated with universities.

## File

### Fields
- `uid`: UUIDField (Primary Key)
- `name`: CharField (Max Length: 120, Nullable)
- `path`: TextField (Nullable)
- `size`: BigIntegerField (Default: 0)
- `file_type`: CharField (Max Length: 120, Nullable)
- `created`: DateTimeField (Auto-Generated)
- `thumbnail`: FileField (Nullable)
- `updated`: DateTimeField (Auto-Generated)
- `uploaded`: BooleanField (Default: False)
- `active`: BooleanField (Default: True)
- `file_key`: CharField (Max Length: 250)
- `university`: ForeignKey (UniversityProfile, on_delete=models.CASCADE)
- `external_url`: CharField (Max Length: 120, Nullable)
- `subtitle`: FileField (Nullable)

This model represents files and their metadata, including S3 upload details.

### Properties
- `secure_s3_url`: Generates an S3 download URL for the file.
- `cdn_url`: Generates a CDN URL for the file.
- `external_video_url`: Returns the external video URL if available.
- `delete_from_s3`: Deletes the file from S3.
- `delete`: Deletes the file from S3 and the database.

## user_updated Function

This function is a signal receiver that verifies an admin when a user changes their password.

## AuditVersion Model

### Fields
- Inherits from `Version` model

This model customizes the `Version` model for auditing purposes.

### Properties
- `user`: Returns the user associated with the audit.
- `status`: Returns the status of the version (created, modified, deleted).
- `changes`: Gets version comparison changes.
- `prev`: Gets the previous version.
- `next`: Gets the next version.


# Career Model Documentation

The `Career` model in this Django project represents careers and their associated information.

## Fields
- `uid`: UUIDField (Primary Key)
- `active`: BooleanField (Default: True)
- `career`: CharField (Max Length: 250)
- `email`: EmailField (Nullable, Blank)
- `phone_number`: CharField (Max Length: 20, Nullable, Blank)
- `facebook_url`: URLField (Nullable, Blank)
- `twitter_url`: URLField (Nullable, Blank)
- `linkedin_url`: URLField (Nullable, Blank)
- `instagram_url`: URLField (Nullable, Blank)
- `website`: URLField (Nullable, Blank)
- `content`: TextField (Nullable, Blank)
- `mobile_content`: TextField (Nullable, Blank)
- `created`: DateTimeField (Auto-Generated)
- `modified`: DateTimeField (Auto-Generated)
- `video`: ForeignKey to 'File' (Nullable, Blank)
- `tile_log_1`: FileField (Nullable, Blank)
- `tile_log_2`: FileField (Nullable, Blank)
- `tile_log_3`: FileField (Nullable, Blank)
- `tile_title_1`: CharField (Max Length: 250, Nullable, Blank)
- `tile_title_2`: CharField (Max Length: 250, Nullable, Blank)
- `tile_title_3`: CharField (Max Length: 250, Nullable, Blank)
- `tile_url_1`: URLField (Nullable, Blank)
- `tile_url_2`: URLField (Nullable, Blank)
- `tile_url_3`: URLField (Nullable, Blank)
- `logo`: FileField (Nullable, Blank)
- `tiles`: ManyToManyField to 'Tile' (Blank)
- `university`: ForeignKey to 'UniversityProfile' (on_delete=models.CASCADE)

## Properties
- `tile_log_url_1`: Career tile logo URL or default placeholder.
- `tile_log_url_2`: Career tile logo URL or default placeholder.
- `tile_log_url_3`: Career tile logo URL or default placeholder.
- `logo_url`: Career logo URL or default placeholder.
- `html_content(base_url='')`: Generates HTML content for mobile.
- `dark_mode_content(base_url='')`: Generates dark mode HTML content.
- `light_mode_content(base_url='')`: Generates light mode HTML content.
- `active_tiles`: Returns active tiles associated with the career.

The `Career` model stores information about careers and their associated data, such as contact details, content, and related tiles.

