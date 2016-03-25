"""
Internally-used functions for posting runs to the timelines on
multiple servers.
"""

# In-module things we use
from pstime import *
from psurl import *

import datetime
import pscheduler
import random
import re
import requests
import time
import urlparse


def run_post(
    task_url_text, # URL for task
    start_time     # Desired start time
):
    """
    Schedule a run of a task on all participating nodes.

    Returns a tuple containing a list of the posted run URLs (which
    will be None in the event of an error) and an error message (None
    if there was no error).
    """

    task_url = urlparse.urlparse(task_url_text)
    assert type(start_time) == datetime.datetime

    status, task = pscheduler.url_get(task_url_text, params={'detail': 1})

    # Generate a list of the task URLs

    task_urls =[]
    participants = task['detail']['participants']
    assert len(participants) >= 1

    parts = list(task_url)
    for participant in participants:
        parts[1] = re.sub( '^[^:]*',
                           'localhost' if participant is None else str(participant),
                           parts[1])
        task_urls.append( urlparse.urlunsplit(parts[:-1]) )


    #
    # Figure out the range of times in which the task can be run.
    #

    task_duration = pscheduler.iso8601_as_timedelta(task['detail']['duration'])
    try:
        task_slip = pscheduler.iso8601_as_timedelta(task['detail']['slip'])
    except KeyError:
        task_slip = datetime.timedelta()

    run_range_end = start_time + task_duration + task_slip

    range_params = {
        'start': pscheduler.datetime_as_iso8601(start_time),
        'end': pscheduler.datetime_as_iso8601(run_range_end)
        }

    #
    # Get a list of the time ranges each participant has available to
    # run the task that overlap with the range we want.
    #

    range_set = []

    for task_url in task_urls:

        status, json_ranges = pscheduler.url_get( task_url + '/runtimes',
                                       params = range_params )

        if status != 200 or len(json_ranges) == 0:
            return (None, None, None, "Host %s cannot schedule this run" % participant)
        
        range_set.append( [ (pscheduler.iso8601_as_datetime(item['lower']),
                             pscheduler.iso8601_as_datetime(item['upper']))
                            for item in json_ranges ] )

    #
    # Find the range that fits
    #

    schedule_range = pscheduler.coalesce_ranges( range_set, task_duration )
    if schedule_range is None:
        return (None, None, None, "No mutually-agreeable time to run this task.")

    (schedule_lower, schedule_upper) = schedule_range
    assert schedule_lower < schedule_upper

    # Apply random slip if one was specified

    try:
        randslip = task['schedule']['randslip']
        slip_available = schedule_upper - schedule_lower - task_duration
        slip_seconds = pscheduler.timedelta_as_seconds(slip_available) \
            * random.random()
        schedule_lower += pscheduler.seconds_as_timedelta(int(slip_seconds))
    except KeyError:
        pass  # No randon slip, no problem.

    # Make sure we haven't slipped further than allowed.
    assert schedule_upper - schedule_lower >= task_duration

    schedule_upper = schedule_lower + task_duration

    #
    # Post the runs to the participants
    #

    run_params = { 'start': schedule_lower.isoformat() }
    runs_posted = []

    # First one is the lead.  Post it and get the UUID.

    status, run_lead_url \
        = pscheduler.url_post(task_urls[0] + '/runs', run_params)
    assert type(run_lead_url) in [str, unicode]
    runs_posted.append(run_lead_url)

    # What to add to a task URL to make the run URL
    run_suffix = run_lead_url[len(task_urls[0]):]

    # Cover the rest of the participants if there are any.

    for task_url in task_urls[1:]:
        try:
            status, run_url = pscheduler.url_post(task_url + run_suffix, params=run_params)
            runs_posted.append(run_url)
        except Exception as ex:
            # Any error means we go no further.
            # TODO: Hold error message?
            break

    if len(runs_posted) != len(task_urls):
        pscheduler.url_delete_list(runs_posted)
        # TODO: Better error?
        return (None, None, None, "Failed to post runs to all participants.")

    #
    # Fetch all per-participant data, merge it and distribute the
    # result to all participants.
    #

    part_data = []

    for run in runs_posted:
        status, result = pscheduler.url_get(run, throw=False)
        if status != 200 or not 'participant-data' in result:
            pscheduler.url_delete_list(runs_posted)
            # TODO: Better error?
            return (None, None, None, "Failed to get run data from all participants")
        part_data.append(result['participant-data'])

    full_data = {
        'run': pscheduler.json_dump({ 'part-data-full': part_data })
        }

    for run in runs_posted:
        status, result = pscheduler.url_put(run, full_data, json=False)
        if status != 200:
            pscheduler.url_delete_list(runs_posted)
            # TODO: Better error?
            return (None, None, None, "Failed to post run data to all participants")


    # TODO: Probably also want to return the start and end times?
    return (runs_posted[0], schedule_lower, schedule_upper, None)



def run_fetch_result(
    url,
    tries=10,
    timeout=pscheduler.seconds_as_timedelta(10)
    ):
    """
    Fetch the results of a run, trying repeatedly until a timeout
    specified as a timedeltas been passed.
    """

    end_time = pscheduler.time_now() + timeout
    sleep_time = pscheduler.timedelta_as_seconds(timeout / tries)

    while pscheduler.time_now() < end_time:

        status, result = pscheduler.url_get(url, throw=False)
        if status == 200 and result['state'] == 'finished':
                return result
        time.sleep(sleep_time)

    # TODO: This or throw something?
    return None
