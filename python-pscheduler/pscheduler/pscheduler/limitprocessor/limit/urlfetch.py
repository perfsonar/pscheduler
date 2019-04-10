"""
Limit Class for url-fetch
"""

import pscheduler


DATA_VALIDATOR = {
    "type": "object",
    "properties": {
        "url": { "$ref": "#/pScheduler/URL" },
        "url-transform": { "$ref": "#/pScheduler/JQTransformSpecification" },
        "bind": { "$ref": "#/pScheduler/Host" },
        "verify-keys": { "$ref": "#/pScheduler/Boolean" },
        "follow-redirects": { "$ref": "#/pScheduler/Boolean" },
        "timeout": { "$ref": "#/pScheduler/Duration" },
        "headers": { "type": "object" },
        "headers-transform": { "$ref": "#/pScheduler/JQTransformSpecification" },
        "params": { "type": "object" },
        "params-transform": { "$ref": "#/pScheduler/JQTransformSpecification" },

        "success-only": { "$ref": "#/pScheduler/Boolean" },
        "fail-result": { "$ref": "#/pScheduler/Boolean" }
    },
    "additionalProperties": False,
    "required": [ "url" ]
}


PRIVATE_KEY = "__URLFETCH_PRIVATE__"


def _jq_filter(transform):

    if transform is None:
        return None

    script = transform["script"]
    if isinstance(script, list):
        script = "\n".join(script)
    full_script = "def hint($name): ." + PRIVATE_KEY + ".hints[$name];" \
                  + script

    return pscheduler.JQFilter(
        full_script,
        args=transform.get("args", {})
        # Don't care about raw output.  Not doing that.
    )





def urlfetch_data_is_valid(data):
    """Check to see if data is valid for this class.  Returns a tuple of
    (bool, string) indicating valididty and any error message.
    """
    return pscheduler.json_validate(data, DATA_VALIDATOR)



class LimitURLFetch():

    """
    Limit that passes or fails depending on the result of a URL Fetch

    URLs fetched by this class should return a status of 200 and JSON
    that looks like this:

    {
      "result": false,                   Whether or not approval is given
      "message": "We don't like you."    Optional explanatory message
    }
    """

    def __init__(self,
                 data   # Data suitable for this class
                 ):

        
        valid, message = urlfetch_data_is_valid(data)
        if not valid:
            raise ValueError("Invalid data: %s" % message)

        self.url = data["url"]
        self.url_transform = _jq_filter(data.get("url-transform", None))
        self.bind = data.get("bind", None)
        self.follow = data.get("follow-redirects", True)
        self.timeout = pscheduler.timedelta_as_seconds(
            pscheduler.iso8601_as_timedelta(data.get("timeout", "PT3S")) )
        self.verify = data.get("verify-keys", True)
        self.fail_result = data.get("fail-result", False)

        self.headers = data.get("headers", {})
        self.headers_transform = _jq_filter(data.get("headers-transform", None))

        self.params = data.get("params", {})
        self.params_transform = _jq_filter(data.get("params-transform", None))

        self.success_only = data.get("success-only", False)


    def checks_schedule(self):
        return False


    def evaluate(self,
                 proposal  # Task and hints
                 ):

        private = { "hints": proposal["hints"] }

        # Generate the URL
        url = self.url
        if self.url_transform is not None:
            try:
                url = self.url_transform({
                    "url": self.url,
                    "run": proposal["task"],
                    PRIVATE_KEY: private
                })[0]
                if not isinstance(url, basestring):
                    raise ValueError("Transform did not return a string")
            except Exception as ex:
                return {
                    "passed": self.fail_result,
                    "reasons": [ "URL transform failed: %s" % (str(ex)) ]
                }


        # Generate the headers
        if self.headers_transform is not None:
            try:
                headers = self.headers_transform({
                    "headers": self.headers,
                    "run": proposal["task"],
                    PRIVATE_KEY: private
                })[0].get("headers", {})
            except Exception as ex:
                return {
                    "passed": self.fail_result,
                    "reasons": [ "Header transform failed: %s" % (str(ex)) ]
                }
        else:
            headers = {}

        # Generate the parameters
        if self.params_transform is not None:
            try:
                params = self.params_transform({
                    "params": self.params,
                    "run": proposal["task"],
                    PRIVATE_KEY: private
                })[0].get("params", {})
            except Exception as ex:
                return {
                    "passed": self.fail_result,
                    "reasons": [ "Parameter transform failed: %s" % (str(ex)) ]
                }
        else:
            params = {}

        # Fetch the result
        status, text = pscheduler.url_get(url,
                                          bind=self.bind,
                                          headers=headers,
                                          params=params,
                                          json=False,
                                          throw=False,
                                          timeout=self.timeout,
                                          allow_redirects=self.follow,
                                          verify_keys=self.verify
        )

        if self.success_only:
            if status == 200:
                return { "passed": True }
            elif status == 404:
                return { "passed": False, "reasons": [ "Resource not found" ] }
            # For anything else, fall through and let the error
            # handler below deal with it.

        # Take errors at face value
        if status != 200:
            return {
                "passed": self.fail_result,
                "reasons": [
                    "Fetch %s failed: %d: %s" % (url, status, text)
                ]
            }

        try:
            json = pscheduler.json_load(text)
        except ValueError:
            return {
                "passed": self.fail_result,
                "reasons": [ "Server returned invalid JSON '%s'" % (text) ]
            }

        try:
            passed = json["result"]
            if not isinstance(passed, bool):
                raise KeyError
        except KeyError:
            return {
                "passed": self.fail_result,
                "reasons": [ "Server returned an invalid result '%s'" % (text) ]
            }


        result = { "passed": passed }
        try:
            result["reasons"] = [ json["message"] ]
        except KeyError:
            pass  # Not there?  Don't care.

        return result



# A short test program

if __name__ == "__main__":

    for url in [
            #"https://some-host.org/returns-true",
            #"https://some-host.org/returns-false",
            "https://bad.example.net/not-valid",
            ]:
        limit = LimitURLFetch({
            "url": url,
#            "url-transform": {
#                "script": "\"https://www.notonthe.net/hole/true/\\(hint(\"requester\"))\""
#            },
            "timeout": "PT3S",
            "params": { "foo": 123, "bar": 456 },
            "params-transform": {
                "script": ".params.baz = 789 | .params.test = 9999 | .params.hinted = hint(\"requester\")"
            },
            "headers": { "Content-Type": "application/json" },
            "headers-transform": {
                "script": [
                    "  .headers.\"X-Argument\" = $foobar",
                    "| .headers.\"X-Hinted\" = hint(\"requester\")"
                ],
                "args": {
                    "foobar": "Arg-U-Ment"
                }
            }
        })
        print url, "->", limit.evaluate({
            "task": { "test": "xxx yyy: Z" },
            "hints": { "requester": "10.9.8.7" }
            })


    print
    print "Succeed-only:"

    for url in [
            "https://www.google.com",
            "https://www.amazon.com/bad-url",
            "https://www.not-a-valid-domain/bad-url",
    ]:

        limit = LimitURLFetch({
            "url": url,
            "success-only": True
        })
        print url, "->", limit.evaluate({
        "task": { "test": "xxx yyy: Z" },
        "hints": { "requester": "10.9.8.7" }
    })
