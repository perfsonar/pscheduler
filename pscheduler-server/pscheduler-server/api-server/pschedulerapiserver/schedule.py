#
# Schedule-Related Pages
#

import pscheduler
import tempfile
import time

from pschedulerapiserver import application

from flask import request
from flask import send_file

from .dbcursor import dbcursor_query
from .json import *
from .limitproc import *
from .log import log
from .response import *
from .tasks import task_exists
from .util import server_netloc


# These are used by schedule()

CLASS_LEVELS = {
    "exclusive": 1,
    "normal": 2,
    "background": 3,
    "background-multi": 4,
    "nonstart": 5,
    "preempted": 6
}

CHART_COLUMNS = [
    "\\n",
    "\\nExclusive",
    "\\nNormal",
    "Background\\nSingle-Result",
    "Background\\nMulti-Result",
    "Non\\nStarting",
    "\\nPreempted"
    ]

CHART_COLUMNS_COUNT = len(CHART_COLUMNS) - 1

CHART_SCRIPT = """
reset
set terminal {term}
set output "{image_file}"
set timefmt "%Y-%m-%dT%H:%M:%S"

unset xtics
set x2range [0.5:{columns_count}.5]
set x2tics out scale 0 ( {x2tics} )

set ydata time
set ytics out nomirror
set format y "%Y-%m-%d\\n%H:%M:%S"
set yrange [{start}:{end}] reverse

set title "pScheduler Schedule for {host} at {time} / {runs} Runs"
set key off
set grid front noxtics ytics mytics linetype 0
set boxwidth 0.9

set style fill solid border lc rgb "#00e000"

plot "{data_file}" using 1:2:3:2:3 \\
  with candlesticks \\
  linewidth 1 \\
  linecolor rgb "#00e000" \\
  axes x2y1
"""

CHART_TERM = {
    "png": "png notransparent truecolor size 800,1200 background rgb \"#ffffff\"",
    "svg": "svg size 800,1200 dynamic",
    # This doesn't get used and is there so the format is considered valid.
    "json": "",
    # These are for debug and should revert to SVG by default.
    "data": "svg size 800,1200 dynamic",
    "script": "svg size 800,1200 dynamic",
}

CHART_SCRIPT_X2TICS = ", ".join(
    [ '"{0}" {1}'.format(pair[1], pair[0])
      for pair in enumerate(CHART_COLUMNS, start=0) ]
)



# Schedule
@application.route("/schedule", methods=['GET'])
def schedule():

    try:
        range_start = arg_datetime('start')
        range_end   = arg_datetime('end')
    except ValueError:
        return bad_request('Invalid start or end time')

    try:
        task = arg_uuid("task")
    except ValueError:
        return bad_request('Invalid task UUID')

    out_format = arg_string("format") or "json"

    if out_format not in CHART_TERM:
        return bad_request("Invalid format '%s'" % (out_format))

    query = ["""
            SELECT
                lower(times),
                upper(times),
                upper(times) - lower(times) AS run_duration,
                task,
                run,
                state_enum,
                state_display,
                task_json,
                task_cli,
                test_json,
                tool_json,
                errors,
                priority
            FROM schedule
            WHERE times && tstzrange(%s, %s, '[)')
    """]
    args = [range_start, range_end]

    if task is not None:
        query.append("AND task = %s")
        args.append(task)

    if out_format != "json":
        query.append("ORDER BY run_duration DESC")

    cursor = dbcursor_query(" ".join(query), args)

    runs = cursor.rowcount

    if out_format == "json":

        result = []

        base_url = pscheduler.api_url_hostport(server_netloc(), "tasks/")
        for row in cursor:

            task_href = base_url +  row[3]
            run_href = "%s/runs/%s" % (task_href, row[4])

            run = {
                "start-time": pscheduler.datetime_as_iso8601(row[0]),
                "end-time": pscheduler.datetime_as_iso8601(row[1]),
                "href": run_href,
                "result-href": "%s/result" % run_href,
                "state": row[5],
                "state-display": row[6],
                "task": row[7],
                "cli": row[8],
                "test": row[9],
                "tool": row[10],
                "errors": row[11],
                "priority": row[12]
            }

            run["task"]["href"] = task_href

            result.append(run)

        # This is sanitized because it contains data from multiple tasks
        return ok_json(result)

    else:

        try:
            data_path = None
            image_path = None
            (_, data_path) = tempfile.mkstemp()
            (_, image_path) = tempfile.mkstemp()

            # Data
            with open(data_path, "w") as data:
                for row in cursor:
                    sched_class = row[5] if row[5] in [ "nonstart" ] \
                                  else row[9]["scheduling-class"]
                    line = "%d %s %s\n" % (
                        CLASS_LEVELS[sched_class],
                        row[0].isoformat(),
                        row[1].isoformat()
                    )
                    data.write(line)
                    log.debug("LINE %s", line)
                data.close()
            if out_format == "data":
                return send_file(data_path)

            # Script
            script = CHART_SCRIPT.format(
                term=CHART_TERM[out_format],
                image_file=image_path,
                columns_count=CHART_COLUMNS_COUNT,
                x2tics=CHART_SCRIPT_X2TICS,
                start='"{}"'.format(range_start.isoformat()) if range_start is not None else "",
                end='"{}"'.format(range_end.isoformat()) if range_end is not None else "",
                host=server_hostname(),
                time=pscheduler.time_now().strftime("%Y-%m-%d %T %Z"),
                runs=runs,
                data_file=data_path
            )
            if out_format == "script":
                return ok(script)

            status, out, err = pscheduler.run_program(["gnuplot"], stdin=script)
            if status != 0:
                log.error("GNUPlot failed: %s" % (err))
                return error("Failed to plot schedule; see system logs. %s" % (err))

            filetype = "image/" + out_format
            return send_file(image_path, mimetype=filetype, cache_timeout=1)


        except Exception as ex:
            log.exception()        
            return error("Unable to plot schedule; see system logs. %s" % (ex))

        finally:
            for target in [ data_path, image_path ]:
                if target is not None:
                    os.unlink(target)


        raise RuntimeError("Reached code that should not be reached.")




# Schedule, tuned for use with the monitor
@application.route("/monitor", methods=['GET'])
def monitor():

    try:
        window_size = arg_cardinal('window')
    except ValueError as ex:
        return bad_request(str(ex))

    try:
        cursor = dbcursor_query("""SELECT ppf, lower(times), upper(times), task, run,
                                          state_enum, state_display, task_json,
                                          task_cli, priority FROM schedule_monitor(%s)""",
                                [window_size])

    except Exception as ex:
        log.exception()
        return error(str(ex))

    result = []

    base_url = pscheduler.api_url_hostport(server_netloc())
    for row in cursor:

        task_href = "%s/tasks/%s" % (base_url, row[2])
        run_href = "%s/runs/%s" % (task_href, row[3])

        run = {
            "ppf": row[0],
            "start-time": pscheduler.datetime_as_iso8601(row[1]),
            "end-time": pscheduler.datetime_as_iso8601(row[2]),
            "href": run_href,
            "result-href": "%s/result" % run_href,
            "state": row[5],
            "state-display": row[6],
            "task": row[7],
            "cli": row[8],
            "priority": row[9]
            }

        run["task"]["href"] = task_href

        result.append(run)

    # This is sanitized because it contains data from multiple tasks
    return ok_json(result)


@application.route('/schedule/availability', methods=['GET'])
def schedule_availability():
    """
        Returns the fraction of the given time range that the server is
        free from exclusive tasks.

        The time range is specified either by:
        - 'start' and 'end' - ISO 8601 timestamp
        or
        - 'next' - ISO 8601 duration (from now)

        Returns:
        - {
            'availability': <float>,
            'start': <ISO 8601 timestamp>,
            'end': <ISO 8601 timestamp>
        }
    """
    start, end, next = None, None, None

    try:
        start = arg_datetime('start')
        end = arg_datetime('end')
        next = arg_duration('next')
    except ValueError as e:
        return bad_request(f'Invalid argument [start, end or next] provided. Error: {e}')
    
    # start, end and next are mutually exclusive
    if (start or end) and next:
        return bad_request('Start and end are mutually exclusive with next')
    
    if (start or end) and not (start and end):
        return bad_request('Both start and end are required')
    
    if not (start or end or next):
        return bad_request('Start and end or next is required')

    if next:
        start = pscheduler.time_now()
        end = start + next

    # sanity check
    if start >= end:
        return bad_request('start must be before end')

    try:
        cursor = dbcursor_query("""
            WITH params AS (
                SELECT tstzrange(%s, %s, '[]') AS period
            ),
            overlap_runs AS (
                SELECT r.times * p.period AS overlap_period
                FROM run_conflictable r, params p
                WHERE r.exclusive AND r.times && p.period
            ),
            agg_periods AS (
                SELECT unnest(range_agg(overlap_period)) AS period
                FROM overlap_runs
            ),
            overlap_seconds AS (
                SELECT COALESCE(SUM(EXTRACT(EPOCH FROM upper(period) - lower(period))), 0) AS o_sec
                FROM agg_periods
            ),
            total_seconds AS (
                SELECT EXTRACT(EPOCH FROM upper(period) - lower(period)) AS t_sec
                FROM params
            )
            SELECT 1.0 - (o_sec / t_sec) AS availability
            FROM overlap_seconds, total_seconds;
        """, [start, end], onerow=True)

        availability = cursor.fetchone()[0]

        return ok_json({
            'availability': float(availability),
            'start': f'{start.isoformat()}',
            'end': f'{end.isoformat()}'
        })
    except Exception as e:
        log.exception()
        return error(f'Error: {e}')
