from setuptools import setup,find_packages

setup(
    name = "scrapedump",
    version = "0.1",
    url = "https://github.com/sweemeng/scrapedump",
    license = "BSD",
    description = "A raw data webapp for Data, a sinarproject",
    author = "sweemeng",
    packages = find_packages("scrapedump"),
    package_dir = {'':'scrapedump'},
    install_requires = [
        'setuptools',
        'pymongo',
        'flask',
        'flask-login',
        'flask-principal',
        'flask-wtf',
        'gunicorn',
        'ipython',
        'simplejson',
        'wsgiref',
        'nose',
        'py-bcrypt',
        'celery',
        ],
)
