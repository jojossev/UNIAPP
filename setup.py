from setuptools import setup, find_packages

setup(
    name="uniapp",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "Django==4.2.10",
        "psycopg2-binary==2.9.9",
        "Pillow==9.5.0",
        "gunicorn==21.2.0",
        "whitenoise==6.6.0",
        "dj-database-url==2.1.0",
        "python-decouple==3.8",
        "python-dotenv==1.0.0",
        "crispy-bootstrap5==2024.2",
        "django-crispy-forms==2.1",
        "django-allauth==0.61.1"
    ],
)
