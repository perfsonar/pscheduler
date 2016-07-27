"""
Functions for interacting with HTTP servers
"""

from psjson import *

import requests


# TODO: Decide what to do about these.  They're necessary for the time
# being because perfSONAR generates a self-signed key that's used by
# default.  Consider a global configuration item that turns this on
# and off so sites that want to do verification can.

# SECURITY: This disables key verification when using HTTPS.
verify_keys = False


# SECURITY: This suppressses warnings about not verifying keys when
# using HTTPS.

if not verify_keys:
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)






class URLException(Exception):
    pass



def url_get( url,          # GET URL
             params={},    # GET parameters
             json=True,    # Interpret result as JSON
             throw=True    # Throw if status isn't 200
             ):
    """
    Fetch a URL using GET with parameters, returning whatever came back.
    """

    try:
        request = requests.get(url, params=params, verify=verify_keys)
        status = request.status_code
        text = request.text
    except Exception as ex:
        status = 400
        # TODO: This doesn't come out looking as nice as it should.
        text = "Error: " + str(ex)

    if status != 200:
        if throw:
            raise URLException(url + ": " + str(status)
                               + ": " + text)
        else:
            return (status, text)

    if json:
        return (status, pscheduler.json_load(text))
    else:
        return (status, text)


def url_post( url,          # GET URL
              params={},    # GET parameters
              data=None,    # Data to post
              json=True,    # Interpret result as JSON
              throw=True    # Throw if status isn't 200
              ):
    """
    Post to a URL, returning whatever came back.
    """

    request = requests.post(url, params=params, data=data, verify=verify_keys)
    status = request.status_code

    if status != 200 and status != 201:
        if throw:
            raise URLException("POST " + url + " returned " + str(status)
                               + ": " + request.text)
        else:
            return (status, request.text)

    if json:
        return (status, pscheduler.json_load(request.text))
    else:
        return (status, request.text)


def url_put( url,          # GET URL
             params={},    # GET parameters
             data=None,    # Data for body
             json=True,    # Interpret result as JSON
             throw=True    # Throw if status isn't 200
             ):
    """
    PUT to a URL, returning whatever came back.
    """

    request = requests.put(url, params=params, data=data, verify=verify_keys)
    status = request.status_code

    if status != 200 and status != 201:
        if throw:
            raise URLException("PUT " + url + " returned " + str(status)
                               + ": " + request.text)
        else:
            return (status, request.text)

    if json:
        return (status, pscheduler.json_load(request.text))
    else:
        return (status, request.text)




def url_delete( url,          # DELETE URL
                throw=True    # Throw if status isn't 200
             ):
    """
    Delete a URL.
    """

    request = requests.delete(url, verify=verify_keys)
    status = request.status_code

    if status != 200:
        if throw:
            raise URLException("DELETE " + url + " returned " + str(status)
                               + ": " + request.text)
        else:
            return (status, request.text)


def url_delete_list( urls ):
    """
    Delete a list of URLs and return tuples of the status and error
    for each.
    """
    return [ url_delete(url, throw=False) for url in urls ]
