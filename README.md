# 📚Library_Management_System


## 🎯 Overview
MyApp is a Django-based library management system designed to streamline book and member management. It provides a user-friendly interface for administrators to handle authentication, manage book records, and track student or member details efficiently.

##  🌐 Core features

- Secure admin authentication
- Comprehensive CRUD operations for books
- Efficient student/member record management
- Powerful search and filter capabilities
- Details information of user
- Add, update, delete 

##  ⚙️ Installation
```bash
pip install django
pip install pillow
python -m venv venv
cd myapp
python manage.py migrate
python makemigrations
python management.py runserver

```
## 🛠​​ Technical Requirements
- Backend  using Python and Django Framework
- Using SQLite for store data
- Frontend using HTML, CSS, and JavaScript
- Responsive design implemented using Bootstrap
- CRUD operations for managing books and members
- User-friendly dashboard and clean interface


## 📂 Folder Structure of project
```bash
myapp/
├── myproject/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── myapp/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   |└── migrations/
│   |    └── __init__.py
├   templates/
│   ├── author_confirm_delete.html
│   ├── author_form.html
│   ├── author.html
│   ├── book_confirm_delete.html
│   ├── book_form.html
│   ├── book.html
│   ├── category_confirm_delete.html
│   ├── category_form.html
│   ├── category.html
│   ├── home.html
│   ├── login.html
│   ├── nav.html
│   ├── register.html
│   ├── search_results.html
│   ├── user_form.html
│   ├── user_profile.html
│   └── user_login.html
├   | static/
│   └── css/
├── __pycache__/
├── manage.py
├── db.sqlite3
├── requirements.txt
└── README.md
```
## 💻 Link of Using 
- Django:  https://docs.djangoproject.com/
- Bootstrap:  https://getbootstrap.com/docs/



