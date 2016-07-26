#!/usr/bin/python

from distutils.core import setup

setup(name='pscheduler',
      version='0.1',
      description='pScheduler functions',
      url='http://www.perfsonar.net',
      author='The perfSONAR Development Team',
      author_email='perfsonar-developer@perfsonar.net',
      license='Apache 2.0',
      packages=['pscheduler',
                'pscheduler.limitprocessor',
                'pscheduler.limitprocessor.identifier',
                'pscheduler.limitprocessor.limit',
            ],
      include_package_data=True,
      package_data={'pscheduler.limitprocessor': ['*.json']},

      )
