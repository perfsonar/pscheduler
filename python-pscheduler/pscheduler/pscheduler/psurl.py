"""
Functions for interacting with HTTP servers
"""

from psjson import *

import requests
import urlparse

from requests.packages.urllib3.poolmanager import PoolManager


# TODO: Decide what to do about these.  They're necessary for the time
# being because perfSONAR generates a self-signed key that's used by
# default.  Consider a global configuration item that turns this on
# and off so sites that want to do verification can.

# SECURITY: This disables key verification when using HTTPS.
verify_keys_default = False


# SECURITY: This suppressses warnings about not verifying keys when
# using HTTPS.

if not verify_keys_default:
    # NOTE: This used to do a separate import of
    # InsercureRequestWarning but can't because of the way Debian
    # de-vendorizes the requests package.
    requests.packages.urllib3.disable_warnings(
        requests.packages.urllib3.exceptions.InsecureRequestWarning)



class _SourceAddressAdapter(requests.adapters.HTTPAdapter):
    """
    Adapter for requests that binds the requesting socket to a source
    address
    """
    def __init__(self, source_address, **kwargs):
        self.source_address = source_address

        super(_SourceAddressAdapter, self).__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       source_address=self.source_address)


def _mount_url(session, url, bind):
    """
    Bind the protocol for a URL to an address
    """
    if bind is None:
        return

    session.mount("%s://" % (urlparse.urlparse(url).scheme),
                  _SourceAddressAdapter((bind, 0)))



class URLException(Exception):
    pass


def __formatted_connection_error(ex):
    """
    Format a requests.exceptions.ConnectionError into a nice string
    """
    assert type(ex) == requests.exceptions.ConnectionError
    fate = "Unspecified connection error occurred" #this should not happen
    message = ""
    if len(ex.args) > 0:
        exargs_tuple = tuple(ex.args[0])
        fate = exargs_tuple[0]
        if len(exargs_tuple) > 1 and hasattr(exargs_tuple[1], '__len__') and len(exargs_tuple[1]) > 1:
            message = exargs_tuple[1][1]
    return "Error: %s %s." % (fate, message)



def url_get( url,          # GET URL
             params={},    # GET parameters
             bind=None,    # Bind request to specified address
             json=True,    # Interpret result as JSON
             throw=True,   # Throw if status isn't 200
             timeout=None, # Seconds before giving up
             headers=None, # Hash of HTTP headers
             verify_keys=verify_keys_default  # Verify SSL keys
             ):
    """
    Fetch a URL using GET with parameters, returning whatever came back.
    """

    with requests.Session() as session:
        _mount_url(session, url, bind)

        try:
            request = session.get(url, params=params, verify=verify_keys,
                                  headers=headers, timeout=timeout)
            status = request.status_code
            text = request.text
        except requests.exceptions.Timeout:
            status = 400
            text = "Request timed out"
        except requests.exceptions.ConnectionError as ex:
            status = 400
            text = __formatted_connection_error(ex)
        except Exception as ex:
            status = 400
            text = "Error: %s" % (str(ex))

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
              bind=None,    # Bind request to specified address
              json=True,    # Interpret result as JSON
              throw=True,   # Throw if status isn't 200
              timeout=None,  # Seconds before giving up
              headers=None, # Hash of HTTP headers
              verify_keys=verify_keys_default  # Verify SSL keys
              ):
    """
    Post to a URL, returning whatever came back.
    """

    with requests.Session() as session:
        _mount_url(session, url, bind)

        try:
            request = session.post(url, params=params, data=data,
                                   verify=verify_keys, headers=headers,
                                   timeout=timeout)
            status = request.status_code
            text = request.text
        except requests.exceptions.Timeout:
            status = 400
            text = "Request timed out"
        except requests.exceptions.ConnectionError as ex:
            status = 400
            text = __formatted_connection_error(ex)
        except Exception as ex:
            status = 500
            text = str(ex)


    if status != 200 and status != 201:
        if throw:
            raise URLException("POST " + url + " returned " + str(status)
                               + ": " + text)
        else:
            return (status, text)

    if json:
        return (status, pscheduler.json_load(text))
    else:
        return (status, text)



def url_put( url,          # GET URL
             params={},    # GET parameters
             data=None,    # Data for body
             bind=None,    # Bind request to specified address
             json=True,    # Interpret result as JSON
             throw=True,   # Throw if status isn't 200
             timeout=None, # Seconds before giving up
             headers=None, # Hash of HTTP headers
             verify_keys=verify_keys_default  # Verify SSL keys
             ):
    """
    PUT to a URL, returning whatever came back.
    """

    with requests.Session() as session:
        _mount_url(session, url, bind)

        try:
            request = session.put(url, params=params, data=data,
                                  verify=verify_keys, headers=headers,
                                  timeout=timeout)
            status = request.status_code
            text = request.text
        except requests.exceptions.Timeout:
            status = 400
            text = "Request timed out"
        except requests.exceptions.ConnectionError as ex:
            status = 400
            text = __formatted_connection_error(ex)
        except Exception as ex:
            status = 500
            text = str(ex)

    if status != 200 and status != 201:
        if throw:
            raise URLException("PUT " + url + " returned " + str(status)
                               + ": " + text)
        else:
            return (status, text)

    if json:
        return (status, pscheduler.json_load(text))
    else:
        return (status, text)




def url_delete( url,          # DELETE URL
                bind=None,    # Bind request to specified address
                throw=True,   # Throw if status isn't 200
                timeout=None, # Seconds before giving up
                headers=None, # Hash of HTTP headers
                verify_keys=verify_keys_default  # Verify SSL keys
             ):
    """
    Delete a URL.
    """

    with requests.Session() as session:
        _mount_url(session, url, bind)

        try:
            request = session.delete(url, verify=verify_keys,
                                     headers=headers, timeout=timeout)
            status = request.status_code
            text = request.text
        except requests.exceptions.Timeout:
            status = 400
            text = "Request timed out"
        except requests.exceptions.ConnectionError as ex:
            status = 400
            text = __formatted_connection_error(ex)
        except Exception as ex:
            status = 500
            text = str(ex)


    if status != 200 and throw:
        raise URLException("DELETE " + url + " returned " + str(status)
                           + ": " + text)

    return (status, text)



def url_delete_list(
        urls,
        bind=None,
        timeout=None, # Seconds before giving up
        headers=None, # Hash of HTTP headers
        verify_keys=verify_keys_default  # Verify SSL keys
        ):
    """
    Delete a list of URLs and return tuples of the status and error for
    each.  Note that the timeout is per delete, not for the aggregated
    operation.
    """
    return [ url_delete(url, throw=False, timeout=timeout, bind=bind,
                        headers=headers, verify_keys=verify_keys)
             for url in urls ]
