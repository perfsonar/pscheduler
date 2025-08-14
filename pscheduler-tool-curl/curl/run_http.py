#
# Run a HTTP test with cURL
#

import io
import datetime
import os
import pscheduler
import pycurl

from urllib.parse import urlparse, urlunparse

from utilities import file_ok


def run(input):

    # TODO: Check the spec schema

    try:
        assert input["test"]["type"] == "http"
        source = input['test']['spec']['url']
        headers = input['test']['spec'].get('headers', {})
        always_succeed = input['test']['spec'].get('always-succeed', False)
        keep_content = input['test']['spec'].get('keep-content', None)
        timeout_iso = input['test']['spec'].get('timeout', 'PT10S')
        ip_version = input['test']['spec'].get('ip-version', None)
        timeout = pscheduler.timedelta_as_seconds(pscheduler.iso8601_as_timedelta(timeout_iso))
    except KeyError as ex:
        return({
            "succeeded": False,
            "error": "Missing data in input"
        })


    # Choke on anything that would allow insight into the contents of
    # local files.

    parsed_url = urlparse(source)

    if parsed_url.scheme == 'file':
        real_path = os.path.realpath(parsed_url.path)
        reasons = file_ok(real_path)
        if reasons:
            return({
                'succeeded': False,
                'error': '\n'.join(reasons)
            })

        # Make cURL use the canonical path because it doesn't deal
        # well with symlinks.  This looks like a private API but
        # isn't.
        parsed_url = parsed_url._replace(path=real_path)
        source = urlunparse(parsed_url)

    succeeded = False
    error = None
    diags = [
        f'Fetching {source}'
    ]

    STDERR = ""

    curl = pycurl.Curl()

    curl.setopt(pycurl.USERAGENT, "Mozilla/5.0 (pScheduler) HTTP response measurement tool")
    curl.setopt(pycurl.URL, str(source))
    curl.setopt(pycurl.HTTPHEADER, [header + ': ' + value for header, value in headers.items()])

    # TODO: This test doesn't have bind but needs one.
    # curl.setopt(pycurl.INTERFACE, str(bind))

    # The origianl psurl tool followed redirects, this one should,
    # too.
    # TODO: This should be a test parameter.
    curl.setopt(pycurl.FOLLOWLOCATION, True)

    if timeout is not None:
        curl.setopt(pycurl.TIMEOUT_MS, int(timeout * 1000.0))

    curl.setopt(pycurl.SSL_VERIFYHOST, False)
    curl.setopt(pycurl.SSL_VERIFYPEER, False)

    if ip_version is not None:
        curl.setopt(pycurl.IPRESOLVE,
                    pycurl.IPRESOLVE_V4 if ip_version == 4 else pycurl.IPRESOLVE_V6
        )

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
        try:
            text = buf.getvalue().decode()
        except ValueError:
            if keep_content:
                status = 415
                text = "Data returned from the server could not be decoded as a string."
            else:
                # Note that if the content isn't being kept, the
                # 'parse' parameter still needs something to chew on,
                # so we leave the empty string in place.
                pass

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
            "diags": '\n'.join(diags) if diags else None,
            "error": None,
            "result": run_result
        }

    else:

        diags.append(f'Fetch returned non-success status {status}')
        return {
            "succeeded": False,
            "diags": '\n'.join(diags) if diags else None,
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

