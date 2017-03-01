#!/usr/bin/python

from distutils.core import setup

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
        'dnspython==1.15.0',
        'requests==2.13.0',
        'pytz==2016.10',
        'psycopg2==2.7',
        'jsonschema==2.6.0',
        'python-dateutil==2.6.0',
        'netifaces==0.10.5',
        'ipaddr==2.1.11',
    ],
    include_package_data=True,
    package_data={'pscheduler.limitprocessor': ['*.json']},
)
