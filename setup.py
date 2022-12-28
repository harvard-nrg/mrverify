import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

requires = [
    'yaxil',
    'pyaml',
    'jinja2',
    'natsort',
    'jsonpath-ng',
    'google-api-python-client',
    'google-auth-oauthlib'
]

test_requirements = [
    'pytest',
    'vcrpy'
]

about = dict()
with open(os.path.join(here, 'mrverify', '__version__.py'), 'r') as f:
    exec(f.read(), about)

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    packages=find_packages(),
    package_data={
        '': ['*.yaml', '*.html']
    },
    include_package_data=True,
    scripts=[
        'scripts/mrcheck.py'
    ],
    install_requires=requires,
    tests_require=test_requirements
)

