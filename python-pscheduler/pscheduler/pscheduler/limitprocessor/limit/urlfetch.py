"""
Limit Class for url-fetch
"""

import pscheduler


DATA_VALIDATOR = {
    "type": "object",
    "properties": {
        "url": { "$ref": "#/pScheduler/URL" },
        "bind": { "$ref": "#/pScheduler/Host" },
        "follow-redirects": { "$ref": "#/pScheduler/Boolean" },
        "timeout": { "$ref": "#/pScheduler/Duration" },
        "verify-keys": { "$ref": "#/pScheduler/Boolean" },
        "headers": { "type": "object" },
        "headers-transform": { "$ref": "#/pScheduler/JQTransformSpecification" },
        "params": { "type": "object" },
        "params-transform": { "$ref": "#/pScheduler/JQTransformSpecification" },
        "fail-result": { "$ref": "#/pScheduler/Boolean" }
    },
    "additionalProperties": False,
    "required": [ "url" ]
}


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
        self.bind = data.get("bind", None)
        self.follow = data.get("follow-redirects", True)
        self.timeout = pscheduler.timedelta_as_seconds(
            pscheduler.iso8601_as_timedelta(data.get("timeout", "PT3S")) )
        self.verify = data.get("verify-keys", True)
        self.fail_result = data.get("fail-result", False)

        self.headers = data.get("headers", {})
        if "headers-transform" in data:
            self.headers_transform = pscheduler.JQFilter(
                data["headers-transform"],
                args=data.get("args", {})
                # Don't bother with raw output.  We don't care.
            )
        else:
            self.headers_transform = None

        self.params = data.get("params", {})
        if "params-transform" in data:
            self.params_transform = pscheduler.JQFilter(
                data["params-transform"],
                args=data.get("args", {})
                # Don't bother with raw output.  We don't care.
            )
        else:
            self.params_transform = None



    def checks_schedule(self):
        return False


    def evaluate(self,
                 run
                 ):

        # Generate the headers
        if self.headers_transform is not None:
            try:
                headers = self.headers_transform({
                    "headers": self.headers,
                    "run": run
                })[0].get("headers", {})
            except Exception as ex:
                return {
                    "passed": self.fail_result,
                    "reasons": [ "Transform failed: %s" % (str(ex)) ]
                }
        else:
            headers = {}

        # Generate the parameters
        if self.params_transform is not None:
            try:
                params = self.params_transform({
                    "params": self.params,
                    "run": run
                })[0].get("params", {})
            except Exception as ex:
                return {
                    "passed": self.fail_result,
                    "reasons": [ "Transform failed: %s" % (str(ex)) ]
                }
        else:
            params = {}

        # Fetch the result
        status, text = pscheduler.url_get(self.url,
                                          bind=self.bind,
                                          headers=headers,
                                          params=params,
                                          json=False,
                                          throw=False,
                                          timeout=self.timeout,
                                          allow_redirects=self.follow,
                                          verify_keys=self.verify
        )

        # Take errors at face value
        if status != 200:
            return {
                "passed": self.fail_result,
                "reasons": [
                    "Fetch failed: %d: %s" % (status, text)
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
            "#https://some-host.org/returns-true",
            "#https://some-host.org/returns-false",
            "https://bad.example.net/not-valid",
            ]:
        limit = LimitURLFetch({
            "url": url,
            "timeout": "PT3S",
            "params": { "foo": 123, "bar": 456 },
            "params-transform": {
                "script": ".params.baz = 789 | .params.test = 9999"
            }
        })
        print url, "->", limit.evaluate({ "test": "xxx yyy: Z" })
