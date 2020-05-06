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
            "error": "Cannot keep content from file:// URLs",
            "diags": None
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

        run_result = {
            "succeeded": True,
            "time": pscheduler.timedelta_as_iso8601(end_time - start_time)
        }

        if always_succeed:
            run_result["status"] = status
            schema.set(2)

        try:
            run_result["found"] = text.find(input['test']['spec']["parse"]) >= 0
        except KeyError:
            pass

        # If the fetch failed or we've been told to keep 0 content, plaster it all in.
        if (not fetch_succeeded) or (keep_content is not None and keep_content == 0):
            run_result["content"] = text
            schema.set(2)
        elif keep_content is not None:
            run_result["content"] = text[:keep_content]

            schema.set(2)

        run_result["schema"] = schema.value()

        return {
            "succeeded": True,
            "diags": None,
            "error": None,
            "result": run_result
        }

    else:

        return {
            "succeeded": False,
            "diags": "Fetch returned non-success status %d" % (status),
            "error": text
        }

    assert False, "Should not be reached."





if __name__ == "__main__":

    for data in [
            {
                "test": {
                    "type": "http",
                    "spec": {
                        "url": "file:///etc/issue",
                        "parse": "perfSONAR",
                        "keep-content": 100,
                        "always-succeed": True
                    }
                }
            },
            {
                "test": {
                    "type": "http",
                    "spec": {
                        "url": "https://www.not-a-real-domain.foo/",
                        "parse": "perfSONAR",
                        "keep-content": 100,
                        "always-succeed": False
                    }
                }
            },
            {
                "test": {
                    "type": "http",
                    "spec": {
                        "url": "https://www.not-a-real-domain.foo/",
                        "parse": "perfSONAR",
                        "keep-content": 100,
                        "always-succeed": True
                    }
                }
            },
            {
                "test": {
                    "type": "http",
                    "spec": {
                        "url": "https://www.perfsonar.net",
                        "parse": "perfSONAR",
                        "keep-content": 100,
                        "always-succeed": True
                    }
                }
            }
    ]:
        print(pscheduler.json_dump(run(data), pretty=True))

