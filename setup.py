from setuptools import setup, find_packages

PACKAGE = 'ocdsapi'
DESCRIPTION = """
    Application for serving OCDS releases
"""
VERSION = '0.2.1'
INSTALL_REQUIRES = [
    'setuptools',
    'CouchDB',
    'requests',
    'Flask',
    'flask-restful',
    'arrow',
    'ocdsmerge',
    "gunicorn",
    'pastedeploy',
    'iso8601',
    'gevent',
]
TEST_REQUIRES = [
    'pytest',
    "pytest-flask",
    'pytest-cov'
]

EXTRA = INSTALL_REQUIRES + TEST_REQUIRES
ENTRY_POINTS = {
    'paste.app_factory': [
        'main = ocdsapi.app:create_app',
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
