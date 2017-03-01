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
    # NOTE: This used to do a separate import of
    # InsercureRequestWarning but can't because of the way Debian
    # de-vendorizes the requests package.
    requests.packages.urllib3.disable_warnings(
        requests.packages.urllib3.exceptions.InsecureRequestWarning)


class URLException(Exception):
    pass


def url_get(url,          # GET URL
            params={},    # GET parameters
            json=True,    # Interpret result as JSON
            throw=True,   # Throw if status isn't 200
            timeout=None  # Seconds before giving up
            ):
    """
    Fetch a URL using GET with parameters, returning whatever came back.
    """

    try:
        request = requests.get(url, params=params, verify=verify_keys,
                               timeout=timeout)
        status = request.status_code
        text = request.text
    except requests.exceptions.Timeout:
        status = 400
        text = "Request timed out"
    except Exception as ex:
        status = 400
        # TODO: This doesn't come out looking as nice as it should.
        text = "Error: " + str(ex)

    if status != 200:
        if throw:
            raise URLException(url + ": " + str(status) +
                               ": " + text)
        else:
            return (status, text)

    if json:
        return (status, pscheduler.json_load(text))
    else:
        return (status, text)


def url_post(url,          # GET URL
             params={},    # GET parameters
             data=None,    # Data to post
             json=True,    # Interpret result as JSON
             throw=True,   # Throw if status isn't 200
             timeout=None  # Seconds before giving up
             ):
    """
    Post to a URL, returning whatever came back.
    """

    try:
        request = requests.post(url, params=params, data=data, verify=verify_keys,
                                timeout=timeout)
        status = request.status_code
        text = request.text
    except requests.exceptions.Timeout:
        status = 400
        text = "Request timed out"
    except Exception as ex:
        status = 500
        text = str(ex)

    if status != 200 and status != 201:
        if throw:
            raise URLException("POST " + url + " returned " + str(status) +
                               ": " + text)
        else:
            return (status, text)

    if json:
        return (status, pscheduler.json_load(text))
    else:
        return (status, text)


def url_put(url,          # GET URL
            params={},    # GET parameters
            data=None,    # Data for body
            json=True,    # Interpret result as JSON
            throw=True,   # Throw if status isn't 200
            timeout=None  # Seconds before giving up
            ):
    """
    PUT to a URL, returning whatever came back.
    """

    try:
        request = requests.put(url, params=params, data=data, verify=verify_keys,
                               timeout=timeout)
        status = request.status_code
        text = request.text
    except requests.exceptions.Timeout:
        status = 400
        text = "Request timed out"
    except Exception as ex:
        status = 500
        text = str(ex)

    if status != 200 and status != 201:
        if throw:
            raise URLException("PUT " + url + " returned " + str(status) +
                               ": " + text)
        else:
            return (status, text)

    if json:
        return (status, pscheduler.json_load(text))
    else:
        return (status, text)


def url_delete(url,          # DELETE URL
               throw=True,   # Throw if status isn't 200
               timeout=None  # Seconds before giving up
               ):
    """
    Delete a URL.
    """
    try:
        request = requests.delete(url, verify=verify_keys, timeout=timeout)
        status = request.status_code
        text = request.text
    except requests.exceptions.Timeout:
        status = 400
        text = "Request timed out"
    except Exception as ex:
        status = 500
        text = str(ex)

    if status != 200 and throw:
        raise URLException("DELETE " + url + " returned " + str(status) +
                           ": " + text)

    return (status, text)


def url_delete_list(
        urls,
        timeout=None  # Seconds before giving up
):
    """
    Delete a list of URLs and return tuples of the status and error for
    each.  Note that the timeout is per delete, not for the aggregated
    operation.
    """
    return [url_delete(url, throw=False, timeout=timeout) for url in urls]
