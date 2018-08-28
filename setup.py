from setuptools import setup, find_packages

PACKAGE = 'ocdsapi'
DESCRIPTION = """
    Application for serving OCDS releases
"""
VERSION = '0.2.2'
INSTALL_REQUIRES = [
    'setuptools',
    'CouchDB',
    'requests',
    'Flask',
    'flask-restful',
    'flask-cors',
    'flask-restful-swagger-2',
    'arrow',
    'ocdsmerge',
    "gunicorn",
    'pastedeploy',
    'iso8601',
    'gevent',
    'pyyaml'
]
TEST_REQUIRES = [
    'pytest',
    "pytest-flask",
    'pytest-cov',
    'munch',
]

EXTRA = INSTALL_REQUIRES + TEST_REQUIRES
ENTRY_POINTS = {
    'paste.app_factory': [
        'main = ocdsapi.application:make_paste_application',
    ],
    'ocdsapi.resources': [
        'releases = ocdsapi.releases:include',
        'records  = ocdsapi.records:include'
    ]
}

setup(name=PACKAGE,
      version=VERSION,
      description=DESCRIPTION,
      author='Quintagroup, Ltd.',
      author_email='info@quintagroup.com',
      license='Apache License 2.0',
      include_package_data=True,
      packages=find_packages(),
      zip_safe=False,
      install_requires=INSTALL_REQUIRES,
      extras_require={"test": EXTRA},
      entry_points=ENTRY_POINTS
      )
