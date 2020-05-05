#
# Run a HTTP test with cURL
#

import io
import datetime
import pycurl

import pscheduler

def run(input):

    # TODO: Check the spec schema

    try:
        assert input["test"]["type"] == "http"
        source = input['test']['spec']['url']
        always_succeed = input['test']['spec'].get('always-succeed', False)
        keep_content = input['test']['spec'].get('keep-content', None)
        timeout_iso = input['test']['spec'].get('timeout', 'PT10S')
        timeout = pscheduler.timedelta_as_seconds(pscheduler.iso8601_as_timedelta(timeout_iso))
    except KeyError as ex:
        return({
            "succeeded": False,
            "error": "Missing data in input"
        })


    # Can-run should weed these out, but backstop it with a check just in case.
    if source[0:5] == "file:" and keep_content is not None:
        return({
            "succeeded": False,
            "error": "Cannot keep content from file:// URLs"
        })


    succeeded = False
    error = None
    diags = []

    STDERR = ""

    # TODO: Implement this with libcurl

    curl = pycurl.Curl()

    curl.setopt(pycurl.URL, str(source))

    # TODO: This test doesn't have bind but needs one.
    # curl.setopt(pycurl.INTERFACE, str(bind))

    # TODO: Redirects as an option?
    # curl.setopt(pycurl.FOLLOWLOCATION, allow_redirects)

    if timeout is not None:
        curl.setopt(pycurl.TIMEOUT_MS, int(timeout * 1000.0))

    curl.setopt(pycurl.SSL_VERIFYHOST, False)
    curl.setopt(pycurl.SSL_VERIFYPEER, False)

    buf = io.BytesIO()
    curl.setopt(pycurl.WRITEFUNCTION, buf.write)

    text = ""

    try:
        start_time = datetime.datetime.now()
        curl.perform()
        status = curl.getinfo(pycurl.HTTP_CODE)
        # PycURL returns a zero for non-HTTP URLs
        if status == 0:
            status = 200
        text = buf.getvalue().decode()
    except pycurl.error as ex:
        code, message = ex.args
        status = 400
        text = message
    finally:
        end_time = datetime.datetime.now()
        curl.close()
        buf.close()


    # 200-299 is success; anything else is an error.
    fetch_succeeded = (status >= 200 and status < 300)
    succeeded = always_succeed or fetch_succeeded

    if succeeded:

        schema = pscheduler.HighInteger(1)

        result = {
            "succeeded": True,
            "time": pscheduler.timedelta_as_iso8601(end_time - start_time)
        }

        if always_succeed:
            result["status"] = status
            schema.set(2)

        try:
            result["found"] = text.find(input['test']['spec']["parse"]) >= 0
        except KeyError:
            pass

        if keep_content is not None or (always_succeed and not fetch_succeeded):
            result["content"] = text if keep_content is None or keep_content == 0 else text[:keep_content]
            schema.set(2)

            # headers?

        result["schema"] = schema.value()

    else:
        result = {
            "succeeded": False,
            "error": text
        }

    return result




if __name__ == "__main__":
    print(run({
        "test": {
            "type": "http",
            "spec": {
                "url": "file:///etc/issue",
                "parse": "perfSONAR",
                "keep-content": 100,
                "always-succeed": True
            }
        }
    }))

    print(run({
        "test": {
            "type": "http",
            "spec": {
                "url": "https://www.perfsonar.net",
                "parse": "perfSONAR",
                "keep-content": 100,
                "always-succeed": True
            }
        }
    }))
