#
# URL-Related Functions
#

import urlparse

from flask import request

def internal_url(path):
    return request.url_root + path

def root_url(path = None):
    return request.url_root + ("" if path is None else path)

def base_url(path = None):
    return request.base_url + ("" if path is None else "/" + path)

def url_last_in_path(url):
    result = urlparse.urlparse(url)
    return result.path.split('/')[-1]
