from setuptools import setup, find_packages

DESCRIPTION = """
    Library for generating building OCDS API
"""


install_requires = [
    'setuptools',
    'CouchDB',
    'requests',
    'Flask',
    'ocdsmerge==0.2',
    "gunicorn",
    'pyyaml',
    'iso8601'
]

test_requires = [
    'pytest',
    "pytest-flask"
]

extra = install_requires + test_requires

entry_points = {
    'paste.app_factory': [
        'api_server = ocdsapi.app:run',
    ],
}

setup(name='ocdsapi',
      version='0.1.0',
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
