#
# WSGI File for pscheduler-api-server
#

import sys
sys.path.insert(0, '/var/www/pscheduler-api-server')

# TODO: Redirect stdout?
sys.stdout = sys.stderr

from pschedulerapiserver import application
