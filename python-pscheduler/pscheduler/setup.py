#!/usr/bin/python3

from setuptools import setup

setup(
    name='pscheduler',
    version='0.1.1',
    description='pScheduler functions',
    url='http://www.perfsonar.net',
    author='The perfSONAR Development Team',
    author_email='perfsonar-developer@perfsonar.net',
    license='Apache 2.0',
    packages=[
        'pscheduler',
        'pscheduler.limitprocessor',
        'pscheduler.limitprocessor.identifier',
        'pscheduler.limitprocessor.limit',
    ],
    install_requires=[
        'dnspython >= 1.12.0',
        'requests >= 2.6.0',
        'pytz >= 2016.6',
        'psycopg2 >= 2.6.2',
        'jsonschema >= 2.5.1',
        'pyjq >= 2.2.0',
        'python-dateutil >= 2.5.3',
        'netifaces >= 0.5',
        'ipaddr >= 2.1.9',
    ],
    include_package_data=True,
    package_data={'pscheduler.limitprocessor': ['*.json']},

    tests_require=['nose'],
    test_suite='nose.collector',
)
