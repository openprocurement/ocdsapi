from setuptools import setup, find_packages

DESCRIPTION = """
    Application for serving OCDS releases
"""


install_requires = [
    'setuptools',
    'CouchDB',
    'requests',
    'Flask',
    'flask-restful',
    'arrow',
    'ocdsmerge==0.2',
    "gunicorn",
    'pastedeploy',
    'iso8601',
    'gevent',
    'repoze.lru'
]

test_requires = [
    'pytest',
    "pytest-flask",
    'pytest-cov'
]

extra = install_requires + test_requires

entry_points = {
    'paste.app_factory': [
        'main = ocdsapi.app:create_app',
    ],
    'ocdsapi.resources': [
        'releases = ocdsapi.resources:include',
    ]
}

setup(name='ocdsapi',
      version='0.1.1',
      description=DESCRIPTION,
      author='Quintagroup, Ltd.',
      author_email='info@quintagroup.com',
      license='Apache License 2.0',
      include_package_data=True,
      packages=find_packages(),
      zip_safe=False,
      install_requires=install_requires,
      extras_require={"test": extra},
      tests_require=test_requires,
      entry_points=entry_points
      )
