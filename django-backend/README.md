## Create Django backend

In venv, install django and djangorestframework:

     pip install Django
     pip install Djangorestframework

Create project:

     django-admin startproject toppixbackend .

Create API:

     django-admin startapp toppixapi

Check server runs properly:

     python manage.py runserver

Apply migrations:

     python manage.py migrate

Create superuser:

    python manage.py createsuperuser

(For local use, password is 'test'.)

Add application to installed apps in toppixbackend/settings.py. Then, create class in toppixapi/models.py.

Apply migrations:

     python manage.py makemigrations
     python manage.py migrate     

Register model in toppixapi/admin.py.
