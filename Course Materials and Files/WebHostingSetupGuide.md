This is a step-by-step guide on how to host a Django application named "ecomprj" on Heroku, alternatively Railway.

**Step 1: Prerequisites**

Before you start, make sure you have the following prerequisites in place:

- A working Django project (in this case, "ecomprj").
- Git installed on your local machine.
- A Heroku account. Sign up at https://signup.heroku.com/ if you don't have one.

**Step 2: Install Heroku CLI**

If you haven't already, install the Heroku Command Line Interface (CLI) on your machine. You can download it from https://devcenter.heroku.com/articles/heroku-cli.

**Step 3: Prepare Your Django Project**

Ensure your Django project is ready for deployment:

- Make sure your project is using a compatible database like PostgreSQL (Heroku's default).
- Include a `requirements.txt` file that lists all project dependencies. You can generate this file using `pip freeze > requirements.txt`.

**Step 4: Create a Procfile**

Create a `Procfile` (without any file extension) in your project's root directory. This file tells Heroku how to run your application. Add the following line to the `Procfile`:

```
web: gunicorn ecomprj.wsgi
```

Replace "ecomprj" with your Django project's name.

**Step 5: Initialize a Git Repository**

If your project is not already under version control with Git, initialize a Git repository in your project directory:

```bash
git init
git add .
git commit -m "Initial commit"
```

**Step 6: Log in to Heroku**

Log in to your Heroku account using the Heroku CLI:

```bash
heroku login
```

This will open a browser window where you can authenticate your Heroku account.

**Step 7: Create a Heroku App**

Create a new Heroku app using the Heroku CLI:

```bash
heroku create your-app-name
```

Replace "your-app-name" with a unique name for your Heroku app (it will be part of the app's URL).

**Step 8: Configure Environment Variables**

Set your Django project's secret key and any other environment variables your project requires. You can do this by running:

```bash
heroku config:set SECRET_KEY=your-secret-key
```

Replace "your-secret-key" with your actual Django secret key. Repeat this step for other environment variables your project needs.

**Step 9: Add Heroku Postgres Add-on**

Heroku provides a PostgreSQL database for your app. Add it to your app:

```bash
heroku addons:create heroku-postgresql:hobby-dev
# Or more better database
```

**Step 10: Push to Heroku**

Deploy your Django project to Heroku by pushing your Git repository to the Heroku remote:

```bash
git push heroku master
```

**Step 11: Migrate and Create Superuser**

Run the following commands on Heroku to set up your database and create a superuser:

```bash
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

**Step 12: Open the App**

Your app should now be deployed on Heroku. You can open it in your browser using:

```bash
heroku open
```

This will open the URL of your Heroku app in a new browser window.

Your Django application "ecomprj" should now be up and running on Heroku. You can continue to develop your project, push changes to the Heroku repository, and manage your application using the Heroku CLI and Heroku Dashboard.







<!-- Admin Login Credentials -->

```bash
email: admin@gmail.com
password: testing321
```




<!-- Required Packages -->
```bash
asgiref==3.5.0
boto3==1.20.26
botocore==1.23.54
Django==3.2.18
dj-database-url==0.5.0
django-auto-logout==0.5.0
django-ckeditor==6.0.0
django-ckeditor-5==0.1.6
crispy-bootstrap5==0.7
django-crispy-forms==2.0
django-dotenv==1.4.2
django-environ==0.9.0
django-filter==21.1
django-formset-js-improved==0.5.0.2
django-jazzmin==2.6.0
django-jquery-js==3.1.1
django-js-asset==1.2.2
django-mailgun-provider==0.2.3
django-plaintext-password==0.1.0
django-rest-auth==0.9.5
django-rest-framework==0.1.0
django-social-share==2.2.1
django-static-fontawesome==5.14.0.0
django-storages==1.12.3
django-taggit==3.0.0
django-import-export
django-templated-mail==1.1.1
django-tinymce==3.4.0
django-widget-tweaks==1.4.8
djangorestframework==3.13.1
djangorestframework-simplejwt==5.2.0
djoser==2.0.5
Pillow==9.1.0
psycopg2-binary
python-decouple==3.5
rjsmin==1.1.0
s3transfer==0.5.2
validate-email==1.3
whitenoise==5.2.0
shortuuid
django-mathfilters
django-dbbackup
django-admin-sortable2
stripe
django-simple-captcha
paypal-payouts-sdk==1.0.0
paypalhttp==1.0.1
django-paypal==2.0
django-mailgun-provider==0.2.3
django-anymail==9.1
geoip2==4.6.0
requests
s3transfer
django-user-agents
gunicorn

django-jet
django-grappelli
channels
daphne
django_heroku
channels_redis
django_daraja
django-cors-headers==4.2.0
'''





