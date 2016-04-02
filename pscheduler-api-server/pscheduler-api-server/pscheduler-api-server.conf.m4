#
# Configuration for pScheduler REST API service
#

WSGIDaemonProcess __USER_NAME__ user=__USER_NAME__ group=__GROUP_NAME__ threads=10
WSGIScriptAlias __API_ROOT__ __API_DIR__/__NAME__.wsgi

<Directory __API_DIR__>

    WSGIProcessGroup __USER_NAME__
    WSGIApplicationGroup %{GLOBAL}

    Order deny,allow
    Allow from all

</Directory>
