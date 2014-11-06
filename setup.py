#!/usr/bin/env python
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys


setup_requires = []

if 'test' in sys.argv:
    setup_requires.append('pytest')

dev_requires = []

tests_require = [
    'pytest',
    'pytest-cov',
    'pytest-django',
    'pytest-timeout',
    'unittest2',
]

install_requires = [
    'Django==1.7.1',
    'psycopg2==2.5.1',
    'django-vanilla-views==1.0.2',
    'django-crispy-forms==1.4.0',
    'django-admin-bootstrapped==1.6.3',
    'django-codemirror-widget==0.4.0',
    'PyYAML==3.11',
    'gevent==1.0.1',
    'gevent-psycopg2==0.0.3',
    'django-annoying==0.8.0',
]


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['cloudy']
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name='cloudy',
    version='0.1',
    author='Luper Rouch',
    author_email='luper.rouch@gmail.com',
    url='https://github.com/flupke/cloudy-release',
    description='A flexible deployment system',
    long_description=open('README.rst').read(),
    packages=find_packages('src'),
    package_dir={'':'src'},
    zip_safe=False,
    install_requires=install_requires,
    extras_require={
        'tests': tests_require,
        'dev': dev_requires,
    },
    tests_require=tests_require,
    cmdclass={'test': PyTest},
    license='MPL 2.0',
    include_package_data=True,
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
