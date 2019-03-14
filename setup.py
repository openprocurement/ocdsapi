import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'plaster_pastedeploy',
    'pyramid',
    'waitress',
    'alembic',
    'cornice',
    'cornice_swagger',
    'pyramid_retry',
    'pyramid_tm',
    'SQLAlchemy',
    'transaction',
    'psycopg2cffi',
    'zope.sqlalchemy',
    'ocdsmerge',
    'simplejson',
    'pyyaml',
    'fastjsonschema',
    'deep_merge',
    'elasticsearch>=6.0.0,<7.0.0',
    'gevent'
]

tests_require = [
    'WebTest >= 1.3.1',  # py3 compat
    'pytest >= 3.7.4',
    'pytest-cov',
]

setup(
    name='ocdsapi',
    version='0.0',
    description='ocdsapi',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Pyramid',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    author='',
    author_email='',
    url='',
    keywords='web pyramid pylons',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'testing': tests_require,
    },
    install_requires=requires,
    entry_points={
        'paste.app_factory': [
            'main = ocdsapi.app:main',
        ],
        'console_scripts': [
            'initialize_ocdsapi_db=ocdsapi.scripts.initialize_db:main',
            'rebuild_index=ocdsapi.scripts.index:main'
        ],
    },
)
