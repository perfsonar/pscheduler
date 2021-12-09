"""
pScheduler BatchProcessor
"""

import copy
import datetime
import multiprocessing
import time

from ..psjson import *
from ..api import *
from ..psurl import *
from ..iso8601 import *
from ..pstime import *
from ..jqfilter import *
from ..jsonval import *


class BatchProcessor():

    __INTERNAL = "__internal__"

    __INPUT_SCHEMA = {

        "local": {

            "global": {
                "type": "object",
                "properties": {
                    "data": { "$ref": "#/pScheduler/AnyJSON" },
                    "transform-post": { "$ref": "#/pScheduler/JQTransformSpecification" },
                    "transform-pre": { "$ref": "#/pScheduler/JQTransformSpecification" }
                },
                "additionalProperties": False
            },

            "job": {
                "type": "object",
                "properties": {
                    "label": { "$ref": "#/pScheduler/String" },
                    "enabled": { "$ref": "#/pScheduler/Boolean" },
                    "iterations": { "$ref": "#/pScheduler/Cardinal" },
                    "parallel": { "$ref": "#/pScheduler/Boolean" },
                    "backoff": { "$ref": "#/pScheduler/Duration" },
                    "sync-start": { "$ref": "#/pScheduler/Boolean" },
                    "task": { "$ref": "#/pScheduler/AnyJSON" },  # Validated later.
                    "task-transform": { "$ref": "#/pScheduler/JQTransformSpecification" }
                },
                "additionalProperties": False,
                "required": [
                    "task"
                ]
            }
        },

        "type": "object",
        "properties": {
            "schema": { "type": "integer" },
            "global": { "$ref": "#/local/global" },
            "jobs": { 
                "type": "array",
                "items": { "$ref": "#/local/job" }
            },
        },
        "additionalProperties": False,
        "required": [
            "jobs",
        ]
    }


    def __fail(self, message):
        """
        Construct a failure for run_task
        """
        return {
            "succeeded": False,
            "error": message
        }


    def __run_task(self, task_args):
        """
        Run a single task and return the result.
        """

        label, delay, spec, debug, dry_run = task_args

        debug("%s: Spec is %s" % (label, json_dump(spec, pretty=True)))

        # TODO: This needs to be passed in or processed elsewhere
        if dry_run:
            debug("%s: Dry run; skipping task" % label)
            return {}


        # Find the lead participant.

        parts_url = api_url_hostport(self.assist,
                                     '/tests/%s/participants' % (spec['test']['type']))
        debug("%s: Fetching participant list from %s" % (label, parts_url))

        participants_params = {'spec': json_dump(spec['test']['spec'])}
        status, participants = url_get(parts_url,
                                       params=participants_params,
                                       bind=self.assist_bind,
                                       throw=False )

        if status != 200:
            debug("%s: Failed: %s" % (label, participants))
            return self.__fail("Unable to determine the lead participant: %s" % participants)

        debug("%s: Got participants: %s" % (label, participants))

        # Substitute the lead if one was provided and the returned
        # lead is local.
        if participants["participants"][0] is None:
            debug("%s: Using directed lead of %s" % (label, self.lead))
        lead = participants["participants"][0] or self.lead

        if delay:
            debug("%s: Sleeping %ss before start" % (label, delay))
            time.sleep(delay)

        tasks_url = api_url(host=lead, path="/tasks")
        debug("%s: Posting to %s" % (label, tasks_url))

        try:
            status, task_url = url_post(tasks_url, data=json_dump(spec), bind=self.bind)
        except Exception as ex:
            debug("Failed: %s" % (str(ex)))
            return self.__fail("Failed to post task: %s" % (str(ex)))

        debug("%s: New task is %s" % (label, task_url))


        # Fetch the posted task with extra details.

        try:
            status, task_data = url_get(task_url, params={"detail": True}, throw=False, bind=self.bind)
            if status != 200:
                return self.__fail("Failed to get task data: %s" % (task_data))
        except Exception as ex:
            return self.__fail("Failed to get task data: %s" % (str(ex)))

        try:
            first_run_url = task_data["detail"]["first-run-href"]
        except KeyError:
            return self.__fail("Server returned incomplete data.")

        debug("%s: First run is at %s" % (label, first_run_url))


        # Get the first run

        status, run_data = url_get(first_run_url, throw=False, bind=self.bind)

        if status == 404:
            return self.__fail("The server never scheduled a run for the task.")
        if status != 200:
            return self.__fail("Error %d: %s" % (status, run_data))

        for key in ["start-time", "end-time", "result-href"]:
            if key not in run_data:
                return self.__fail("Server did not return %s with run data" % (key))

        debug("%s: First run is %s" % (label, run_data["href"]))

        # Wait for the end time to pass.

        try:
            end_time = iso8601_as_datetime(run_data["end-time"])
        except ValueError as ex:
            return self.__fail("Server did not return a valid end time for the task: %s" % (str(ex)))

        now = time_now()
        sleep_time = end_time - now if end_time > now else datetime.timedelta()
        sleep_seconds = sleep_time.total_seconds()

        debug("%s: Waiting %s seconds for run to finish" % (label, sleep_seconds))
        time.sleep(sleep_seconds)

        # Wait for the result to come available and fetch it.

        # TODO: If everything stops all at once, there will be a run on
        # the server.  Use a mutex to serialize this.

        debug("%s: Waiting for result at %s" % (label, run_data["result-href"]))

        status, result_data = url_get(run_data["result-href"],
                                      params={"wait-merged": True},
                                      throw=False, bind=self.bind)

        # TODO: 404 is only semi-kosher becasue bgmulti doesn't generate a
        # result.  Need a fix in the server for this.
        if status not in [200, 404]:
            return self.__fail("Did not get a result: %s" % (result_data))


        # Get all runs and return them in all three formats

        status, runs = url_get(task_data["detail"]["runs-href"], throw=False, bind=self.bind)
        if status != 200:
            return self.__fail("Error %d getting runs: %s" % (status, runs))

        run_data = []

        for run in runs:

            debug("%s: Fetching run %s" % (label, run))

            status, run_json = url_get(run, bind=self.bind)
            if status != 200:
                # TODO: Probably not what we want.
                return [ { "application/json": self.__fail("Error %d getting runs: %s" % (status, runs)) } ]

            result_href = run_json["result-href"]

            run_set = { "application/json": run_json }

            if "result-merged" in run_json:
                for text_format in [ "application/json", "text/plain", "text/html" ]:
                    is_json = text_format == "application/json"
                    status, text = url_get(result_href,
                                           params={"format": text_format},
                                           json=is_json,
                                           throw=False, bind=self.bind)
                    if status == 200:
                        debug("%s: Got %s result" % (label, text_format))
                        run_set[text_format] = text
                    else:
                        debug("%s: Failed to get %s: %d: %s" % (label, text_format, status, text))
                        run_set[text_format] = self.__fail("%d: %s" % (status, text))


            run_data.append(run_set)


        return {
            "task": spec,
            "runs": run_data
        }






    def __prep_job(self, job_number, job, debug, dry_run):

            if not job.get("enabled", True):
                return

            iterations = job.get("iterations", 1)

            backoff = iso8601_as_timedelta(job.get("backoff", "P0D"))
            backoff_secs = timedelta_as_seconds(backoff)

            run_task_args = []


            def __apply_transform(data,
                                  transform,
                                  args,
                                  transform_location,
                                  runtime_location
                              ):
                """
                Apply a transform and return the results, exiting if compilation
                or runtime fails.
                """

                if transform is None:
                    return data
        
                try:
                    script = "\n".join(transform["script"])
                    filterer = JQFilter(script, args=args)
                    return filterer(data)[0]
                except ValueError as ex:
                    raise ValueError("At %s: %s" % (transform_location, ex))
                except jqfilter.JQRuntimeError as ex:
                    raise ValueError("At %s: %s" % (runtime_location, ex))

                assert False, "Should not be reached."


            for iteration in range(0, iterations):

                transform_args = {
                    "global": self.global_data,
                    "iteration": iteration
                }


                # Global Pre Transform
                global_pre_transformed = __apply_transform(job["task"],
                                                           self.global_transform_pre,
                                                           transform_args,
                                                           "/global/transform-pre",
                                                           "/jobs/%d, iteration %d, global pre-transform" % (job_number,
                                                                                                                  iteration)
                )

                # Job Task Transform
                job_task_transformed = __apply_transform(global_pre_transformed,
                                                         job.get("task-transform"),
                                                         transform_args,
                                                         "/jobs/%d/task-transform" % (job_number),
                                                         "/jobs/%d/task-transform, iteration %d" % (job_number, iteration)
                )

                # Global Post Transform
                transformed = __apply_transform(job_task_transformed,
                                                self.global_transform_post,
                                                transform_args,
                                                "/global/transform-post",
                                                "/jobs/%d, iteration %d, global post-transform" % (job_number, iteration)
                )



                # Make sure the task back up structurally-valid

                valid, message = json_validate(transformed,
                                               { "$ref": "#/pScheduler/TaskSpecification" })

                if not valid:
                    raise ValueError("At /jobs/%d/task iteration %d: %s" % (job_number, iteration, message))

                if "schedule" in transformed:

                    schedule = transformed["schedule"]

                    # Scrub out anything that shouldn't be there.
                    for parameter in [ "start", "repeat", "repeat-cron", "until", "max-runs" ]:
                        try:
                            del schedule[parameter]
                        except KeyError:
                            pass  # Not there?  Don't care.

                else:

                    transformed["schedule"] = {}

                # Hold it for run time.
                run_task_args.append((
                    "%s/%d" % (job.get("label", "unlabeled"), iteration),
                    backoff_secs * iteration,
                    transformed,
                    debug,
                    dry_run
                ))

            job[self.__INTERNAL] = run_task_args




    def __init__(self, spec, assist=None, assist_bind=None, lead=None, bind=None):
        """
        Create a batch processor.
        """

        valid, message = json_validate(spec, self.__INPUT_SCHEMA,
                                       max_schema=1)
        if not valid:
            raise ValueError(message)

        self.spec = copy.deepcopy(spec)


        # Make sure whoever we're using for assistance is running pScheduler
        if assist is None:
            assist = os.environ.get("PSCHEDULER_ASSIST", api_local_host())
        if assist_bind is None:
            assist_bind = os.environ.get("PSCHEDULER_ASSIST_BIND", api_local_host())
        (has, error) = api_has_pscheduler(assist, bind=assist_bind)
        if not has:
            raise ValueError("Unable to find pScheduler on %s: %s" % (assist, error))

        self.assist = assist
        self.assist_bind = assist_bind
        self.lead = lead
        self.bind = bind

        try:
            self.global_data = spec["global"]["data"]
        except KeyError:
            self.global_data = None

        try:
            self.global_transform_pre = spec["global"]["transform-pre"]
        except KeyError:
            self.global_transform_pre = { "script": "." }

        try:
            self.global_transform_post = spec["global"]["transform-post"]
        except KeyError:
            self.global_transform_post = { "script": "." }





    def __call__(self,
                 dry_run=False,               # Don't actually run tasks
                 debug=lambda message: None   # Call to make for debug output
    ):
        """
        Run the jobs and return the result.
        """

        result = copy.deepcopy(self.spec)

        for job_number, job in enumerate(result["jobs"]):
            self.__prep_job(job_number, job, debug, dry_run)


        for job in result["jobs"]:

            label = job.get("label", "unlabeled")

            # Grab the internal stuff first and delete it so we can debug in peace.

            run_task_args = job.get(self.__INTERNAL, [])
            iterations = len(run_task_args)

            try:
                del job[self.__INTERNAL]
            except KeyError:
                pass

            debug("Job %s: %s" % (label, json_dump(job, pretty=True)))

            if not job.get("enabled", True):
                debug("%s: Disabled" % label)
                job["results"] = []
                continue


            # TODO: It might be better to use a mutex to serialize access to
            # the server instead of backoff.

            backoff = iso8601_as_timedelta(job.get("backoff", "P0D"))
            backoff_secs = timedelta_as_seconds(backoff)

            parallel = job.get("parallel", False)


            if parallel and job.get("sync-start", True):

                # Make everything past all backoffs and setup time.
                start_delay = (backoff * iterations) \
                              + iso8601_as_timedelta(job.get("setup-time", "PT15S"))
                start = datetime_as_iso8601(time_now() + start_delay)

                debug("%s: Pushing start out %s to %s" % (label, start_delay, start))

                # Inject the schedule into all runs.
                for run in run_task_args:
                    label, backoff, spec, debug, dry_run = run
                    spec["schedule"]["start"] = start


            if parallel and iterations > 1:

                debug("%s: Parallel run of %d tasks" % (label, iterations))

                with multiprocessing.dummy.Pool(processes=iterations) as pool:
                    job["results"] = list(pool.imap(self.__run_task, run_task_args, chunksize=1))

            else:

                # TODO: REMOVE THIS.  TODO: Why?
                job["results"] = [ self.__run_task(arg) for arg in run_task_args ]


        return result
