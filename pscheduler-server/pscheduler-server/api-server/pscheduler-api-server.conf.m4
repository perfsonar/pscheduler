#
# Configuration for pScheduler REST API service
#

WSGIDaemonProcess __USER_NAME__ user=__USER_NAME__ group=__GROUP_NAME__ maximum-requests=5000
WSGIScriptAlias __API_ROOT__ __API_DIR__/__NAME__.wsgi

# Keep's python interpreter from being initialized in the apache
# server worker processes
WSGIRestrictEmbedded On 

<Directory __API_DIR__>

    WSGIProcessGroup __USER_NAME__
    WSGIApplicationGroup __USER_NAME__

    Order deny,allow
    Allow from all

</Directory>

# Not something we need.
KeepAlive Off
