"""
Functions for interacting with HTTP servers
"""

from psjson import *

import httplib
import pycurl
import StringIO
import urllib


# TODO: Decide what to do about this.  It's necessary for the time
# being because perfSONAR generates a self-signed key that's used by
# default.  Consider a global configuration item that turns this on
# and off so sites that want to do verification can.

# SECURITY: This disables key verification when using HTTPS.
verify_keys_default = False



class URLException(Exception):
    pass



class PycURLRunner(object):

    def __init__(self, url, params, bind, timeout, allow_redirects, headers, verify_keys):
        """Constructor"""

        self.curl = pycurl.Curl()

        full_url = url if params is None else "%s?%s" % (url, urllib.urlencode(params))
        self.curl.setopt(pycurl.URL, str(full_url))

        if bind is not None:
            self.curl.setopt(pycurl.INTERFACE, bind)

        self.curl.setopt(pycurl.FOLLOWLOCATION, allow_redirects)

        if headers is not None:            
            self.curl.setopt(pycurl.HTTPHEADER, [
                "%s: %s" % (str(key), str(value))
                for (key, value) in headers.items()
            ])

        if timeout is not None:
            self.curl.setopt(pycurl.TIMEOUT_MS, int(timeout * 1000.0))

        self.curl.setopt(pycurl.SSL_VERIFYPEER, verify_keys)

        self.buf = StringIO.StringIO()
        self.curl.setopt(pycurl.WRITEFUNCTION, self.buf.write)


    def __call__(self, json, throw):
        """Fetch the URL"""
        try:
            self.curl.perform()
            status = self.curl.getinfo(pycurl.HTTP_CODE)
            text = self.buf.getvalue()
        except pycurl.error as ex:
            (code, message) = ex
            status = 400
            text = message
        finally:
            self.curl.close()
            self.buf.close()
            
        #If status is outside the HTTP 2XX success  range
        if status < 200 or status > 299:
            if throw:
                raise URLException(text.strip())
            else:
                return (status, text)

        if json:
            return (status, json_load(text))
        else:
            return (status, text)




def url_get( url,          # GET URL
             params=None,  # GET parameters
             bind=None,    # Bind request to specified address
             json=True,    # Interpret result as JSON
             throw=True,   # Throw if status isn't 200
             timeout=None, # Seconds before giving up
             allow_redirects=True, # Allows URL to be redirected
             headers=None, # Hash of HTTP headers
             verify_keys=verify_keys_default  # Verify SSL keys
             ):
    """
    Fetch a URL using GET with parameters, returning whatever came back.
    """

    curl = PycURLRunner(url, params, bind, timeout, allow_redirects, headers, verify_keys)
    return curl(json, throw)




def __content_type_data(content_type, headers, data):

    """Figure out the Content-Type based on an incoming type and data and
    return that plus data in a type that PycURL can handle."""

    assert(content_type is None or isinstance(content_type, basestring))
    assert(isinstance(headers, dict))

    if content_type is None or "Content-Type" not in headers:

        # Dictionaries are JSON
        if isinstance(data, dict):
            content_type = "application/json"
            data = json_dump(data)

        # Anything else is plain text.
        else:
            content_type = "text/plain"
            data = str(data)

    return content_type, data





def url_post( url,          # GET URL
              params={},    # GET parameters
              data=None,    # Data to post
              content_type=None,  # Content type
              bind=None,    # Bind request to specified address
              json=True,    # Interpret result as JSON
              throw=True,   # Throw if status isn't 200
              timeout=None, # Seconds before giving up
              allow_redirects=True, #Allows URL to be redirected
              headers={},   # Hash of HTTP headers
              verify_keys=verify_keys_default  # Verify SSL keys
              ):
    """
    Post to a URL, returning whatever came back.
    """

    content_type, data = __content_type_data(content_type, headers, data)
    headers["Content-Type"] = content_type

    curl = PycURLRunner(url, params, bind, timeout, allow_redirects, headers, verify_keys)

    curl.curl.setopt(pycurl.POSTFIELDS, data)

    return curl(json, throw)



def url_put( url,          # GET URL
             params={},    # GET parameters
             data=None,    # Data for body
             content_type=None,  # Content type
             bind=None,    # Bind request to specified address
             json=True,    # Interpret result as JSON
             throw=True,   # Throw if status isn't 200
             timeout=None, # Seconds before giving up
             allow_redirects=True, #Allows URL to be redirected
             headers={},   # Hash of HTTP headers
             verify_keys=verify_keys_default  # Verify SSL keys
             ):
    """
    PUT to a URL, returning whatever came back.
    """

    content_type, data = __content_type_data(content_type, headers, data)
    headers["Content-Type"] = content_type

    curl = PycURLRunner(url, params, bind, timeout, allow_redirects, headers, verify_keys)

    curl.curl.setopt(pycurl.CUSTOMREQUEST, "PUT")
    curl.curl.setopt(pycurl.POSTFIELDS, data)

    return curl(json, throw)



def url_delete( url,          # DELETE URL
                params={},    # DELETE parameters
                bind=None,    # Bind request to specified address
                throw=True,   # Throw if status isn't 200
                timeout=None, # Seconds before giving up
                allow_redirects=True, #Allows URL to be redirected
                headers=None, # Hash of HTTP headers
                verify_keys=verify_keys_default  # Verify SSL keys
             ):
    """
    Delete a URL.
    """

    curl = PycURLRunner(url, params, bind, timeout, allow_redirects, headers, verify_keys)

    curl.curl.setopt(pycurl.CUSTOMREQUEST, "DELETE")

    return curl(False, throw)



def url_delete_list(
        urls,
        params=None,
        bind=None,
        timeout=None, # Seconds before giving up
        allow_redirects=True, #Allows URL to be redirected
        headers=None, # Hash of HTTP headers
        verify_keys=verify_keys_default  # Verify SSL keys
        ):
    """
    Delete a list of URLs and return tuples of the status and error for
    each.  Note that the timeout is per delete, not for the aggregated
    operation.
    """
    return [ url_delete(url, throw=False, timeout=timeout, params=params,
                        bind=bind, headers=headers, verify_keys=verify_keys, 
                        allow_redirects=allow_redirects)
             for url in urls ]
