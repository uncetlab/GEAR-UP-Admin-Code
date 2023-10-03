# Django Forms

This README.md provides documentation for the Django forms defined in the `forms.py` file of your project.

## Table of Contents

1. [LoginForm](#loginform)
2. [MenuForm](#menuform)
3. [TileForm](#tileform)
4. [PageForm](#pageform)
5. [CollegeForm](#collegeform)
6. [UniversityForm](#universityform)
7. [CareerForm](#careerform)

---

## 1. LoginForm

The `LoginForm` class is used to create a form for admin users to log in.

**Fields:**
- `email`: CharField (Max Length: 100, Required)
- `password`: CharField (Max Length: 100, Required)

**Form Validations:**
- It validates the existence of the provided email in the database.
- It checks if the password matches the user's stored password.

---

## 2. MenuForm

The `MenuForm` class is used to create a form for adding and editing menu items.

**Fields:**
- `title`: CharField
- `url_type`: ChoiceField
- `active`: BooleanField
- `icon`: CharField
- `url`: URLField
- `page`: ForeignKey to 'Page'
- `key_name`: CharField

---

## 3. TileForm

The `TileForm` class is used to create a form for adding and editing tiles.

**Fields:**
- `title`: CharField
- `url_type`: ChoiceField
- `active`: BooleanField
- `image_url`: CharField (Optional)
- `image`: ImageField
- `url`: URLField
- `page`: ForeignKey to 'Page'
- `description`: CharField

---

## 4. PageForm

The `PageForm` class is used to create a form for adding and editing pages.

**Fields:**
- `title`: CharField
- `content`: TextField
- `active`: BooleanField
- `banner_video_tile`: CharField (Optional)

---

## 5. CollegeForm

The `CollegeForm` class is used to create a form for managing a College.

**Fields:**
- [All fields from the College model except 'tiles']

---

## 6. UniversityForm

The `UniversityForm` class is used to create a form for adding and editing University profiles.

**Fields:**
- `name`: CharField
- `address`: TextField
- `email`: EmailField
- `logo`: FileField
- `phone_number`: CharField

---

## 7. CareerForm

The `CareerForm` class is used to create a form for managing a Career.

**Fields:**
- [All fields from the Career model except 'tiles']

---

This README.md provides an overview of the forms in your Django project's `forms.py` file.
