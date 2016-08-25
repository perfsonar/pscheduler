#!/usr/bin/python
#
# 
#

import daemon
import datetime
import detach
import errno
import json
import optparse
import os
import pscheduler
import psycopg2
import psycopg2.extensions
import select
import signal
import socket
import sys
import time
import traceback

from dateutil.tz import tzlocal



# Gargle the arguments

opt_parser = optparse.OptionParser()

# Daemon-related options

opt_parser.add_option("--daemon",
                      help="Daemonize",
                      action="store_true",
                      dest="daemon", default=False)
opt_parser.add_option("--pid-file",
                      help="Location of PID file",
                      action="store", type="string", dest="pidfile",
                      default=None)

# Program options

opt_parser.add_option("-a", "--archive-defaults",
                      help="Directory containing default archivers",
                      action="store", type="string", dest="archive_defaults",
                      default="__DEFAULT_DIR__")
opt_parser.add_option("-c", "--channel",
                      help="Schedule notification channel",
                      action="store", type="string", dest="channel",
                      default="archiving_change")
# TODO: Do we want pscheduler as the default here?
opt_parser.add_option("-d", "--dsn",
                      help="Database connection string",
                      action="store", type="string", dest="dsn",
                      default="dbname=pscheduler")
opt_parser.add_option("-r", "--refresh",
                      help="Forced refresh interval (ISO8601)",
                      action="store", type="string", dest="refresh",
                      default="PT1M")
opt_parser.add_option("--verbose", action="store_true", dest="verbose")
opt_parser.add_option("--debug", action="store_true", dest="debug")


(options, args) = opt_parser.parse_args()

refresh = pscheduler.iso8601_as_timedelta(options.refresh)
if refresh is None:
    opt_parser.error('Invalid refresh interval "' + options.refresh + '"')
if pscheduler.timedelta_as_seconds(refresh) == 0:
    opt_parser.error("Refresh interval must be calculable as seconds.")

log = pscheduler.Log(verbose=options.verbose, debug=options.debug)

dsn = options.dsn


#
# Maintainer for default archives
#

class DefaultArchiveMaintainer:

    def __init__(self, path):

        self.path = path

        # Most recent file or directory change we saw
        self.most_recent = 0


    def __write_db(self, db, log, archives):

        log.debug("Writing the database")

        cursor = db.cursor()

        try:
            cursor.execute("DELETE FROM archive_default")
        except Exception as ex:
            log.error("Failed to delete defaults: %s", str(ex))

        for archive in archives:

            cursor.execute("SAVEPOINT archiver_insert")
            failed = True
            try:
                cursor.execute("INSERT INTO archive_default (archive) VALUES (%s)",
                               [ pscheduler.json_dump(archive["spec"]) ])
                log.debug("Inserted data from %s", archive["path"])
                failed = False
            except psycopg2.Error as ex:
                log.warning("Ignoring %s: %s", archive["path"], ex.diag.message_primary)
            except Exception as ex:
                log.error("%s: %s", archive["path"], str(ex))

            if failed:
                cursor.execute("ROLLBACK TO SAVEPOINT archiver_insert")

        # Finish up and get out

        db.commit()



    def refresh(self, db, log):

        log.debug("Refreshing default archivers")

        if not os.path.isdir(self.path):
            log.debug("%s is not a directory", self.path)
            return

        timestamps = [ os.path.getmtime(self.path) ]

        # Examine everything before tinkering with the database

        archives = []

        # Hold warnings until after we see something's changed so we
        # don't spew them repeatedly.
        warnings = []

        for path in [ os.path.join(self.path, f)
                      for f in os.listdir(self.path) ]:

            log.debug("Examining file %s", path)

            if os.path.isfile(path):

                # Append the timestamp whether the file is valid or
                # not, because we're looking for any kind of change.
                # Note that we check mtime *and* ctime to catch
                # permission changes and the like.
                timestamps.append( max(os.path.getctime(path),
                                       os.path.getmtime(path)) )
            else:
                log.debug("Not a file")
                continue

            try:
                with open(path, 'r') as content:
                    spec = pscheduler.json_load(content)
            except Exception as ex:
                warnings.append("Ignoring %s: %s" % (path, str(ex)))
                continue

            archives.append({
                    "path": path,
                    "spec": spec
                    })

        newest = sorted(timestamps, reverse=True)[0]
        if newest <= self.most_recent:
            log.debug("Nothing has changed; not updating.")
            return

        for warning in warnings:
            log.warning(warning)

        self.most_recent = newest

        # Commit to the database as safely as possible.

        autocommit_original = db.autocommit
        db.autocommit = False
        try:
            self.__write_db(db, log, archives)
        except Exception as ex:
            log.error("Unexpected exception: %s", str(ex))
        db.autocommit = autocommit_original



#
# Main Program
#

def main_program():

    # Exit nicely when certain signals arrive so running processes are
    # cleaned up.

    def exit_handler(signum, frame):
        log.info("Exiting on signal %d", signum)
        exit(0)

    for sig in [ signal.SIGHUP, signal.SIGINT, signal.SIGQUIT, signal.SIGTERM ]:
        signal.signal(sig, exit_handler)



    # TODO: All DB transactions need to be error checked

    pg = pscheduler.pg_connection(dsn)
    cursor = pg.cursor()
    cursor.execute("LISTEN " + options.channel)

    # This cursor is for doing updates inside the other's loop.
    update_cursor = pg.cursor()


    # Something to maintain the default archiver list
    default_maintainer = DefaultArchiveMaintainer(options.archive_defaults)
    default_maintainer.refresh(pg, log)



    next_refresh = None

    while True:

        # Wait for something to happen.

        if next_refresh is None:

            log.debug("Retrieving immediately.")

        else:

            log.debug("Waiting %s for change or notification", next_refresh)

            try:
                if select.select([pg],[],[],
                                 pscheduler.timedelta_as_seconds(next_refresh)) \
                                 != ([],[],[]):
                    pg.poll()
                    del pg.notifies[:]
                    log.debug("Notified.")

            except select.error as ex:

                err_no, message = ex
                if err_no != errno.EINTR:
                    log.exception()
                    raise ex

            # Only refresh after there's been a wait.
            default_maintainer.refresh(pg, log)


        # Until we hear otherwise...
        next_refresh = refresh

        cursor.execute("""SELECT id, uuid, archiver, archiver_data, start,
                      duration, test, tool, participants, result,
                      attempts, last_attempt
                      FROM archiving_eligible""")

        if cursor.rowcount == 0:
            log.debug("Nothing to archive.")
            continue



        for row in cursor.fetchall():

            run_id, uuid, archiver, archiver_data, start, duration, test, \
                tool, participants, result_merged, attempts, \
                last_attempt = row

            participants_merged = []
            for participant in participants:
                participants_merged.append(socket.gethostname() \
                                           if participant is None \
                                           else participant)

            json = {
                'data': archiver_data,
                'result': {
                    'id': uuid,
                    'schedule': {
                        'start': pscheduler.datetime_as_iso8601(start),
                        'duration': pscheduler.timedelta_as_iso8601(duration)
                        },
                    'test': test,
                    'tool': {
                        'name': tool['name'],
                        'version': tool['version'],
                        },
                    'participants': participants_merged,
                    'result': result_merged
                    },
                'attempts': attempts,
                'last-attempt': None if last_attempt is None \
                    else pscheduler.datetime_as_iso8601(last_attempt) 
                }


            archiver_in = pscheduler.json_dump(json)
            log.debug("Running archiver %s with input %s", archiver, archiver_in)

            returncode, stdout, stderr = pscheduler.run_program(
                [ "pscheduler", "internal", "invoke", "archiver", archiver, "archive" ],
                stdin = archiver_in,
                timeout = 10  # TODO: What's appropriate here?
                )

            log.debug("Archiver exited %d", returncode)
            log.debug("Returned JSON from archiver: %s", stdout)
            log.debug("Returned errors from archiver: %s", stderr)

            attempt = pscheduler.json_dump( [ {
                        "time": pscheduler.datetime_as_iso8601(datetime.datetime.now(tzlocal())),
                        "return-code": returncode,
                        "stdout": stdout,
                        "stderr": stderr
                        } ] )



            if returncode != 0:

                log.debug("Permanent Failure: %s", stderr)
                update_cursor.execute("""UPDATE archiving
                                     SET
                                       archived = TRUE,
                                       attempts = attempts + 1,
                                       last_attempt = now(),
                                       next_attempt = NULL,
                                       diags = diags || (%s::JSONB)
                                     WHERE id = %s""",
                                      [ attempt, run_id ])
                pass  # TODO: Update with diags

            else:


                try:
                    returned_json = pscheduler.json_load(stdout)
                except ValueError:
                    log.error("Archiver %s returned invalid JSON: %s", archiver, stdout)
                    continue

                if returned_json['succeeded']:
                    log.debug("Succeeded: %s to %s", uuid, archiver)
                    update_cursor.execute("""UPDATE archiving
                                         SET
                                             archived = TRUE,
                                             attempts = attempts + 1,
                                             last_attempt = now(),
                                             next_attempt = NULL,
                                             diags = diags || (%s::JSONB)
                                         WHERE id = %s""",
                                          [ attempt, run_id ])

                else:

                    log.debug("Failed: %s to %s: %s", uuid, archiver, stdout)

                    # If there's a retry, schedule the next one.

                    if "retry" in returned_json:

                        next_delta = pscheduler.iso8601_as_timedelta(
                            returned_json['retry'])

                        next = datetime.datetime.now(tzlocal()) \
                            + next_delta

                        log.debug("Rescheduling for %s", next)

                        update_cursor.execute("""UPDATE archiving
                                             SET
                                                 attempts = attempts + 1,
                                                 last_attempt = now(),
                                                 next_attempt = %s,
                                                 diags = diags || (%s::JSONB)
                                             WHERE id = %s""",
                                              [ next, attempt, run_id ])

                        if next_delta < next_refresh:
                            next_refresh = next_delta

                    else:

                        log.debug("No retry requested.  Giving up.")



if options.daemon:
    pidfile = pscheduler.PidFile(options.pidfile)
    with daemon.DaemonContext(pidfile=pidfile):
        pscheduler.safe_run(lambda: main_program())
else:
    pscheduler.safe_run(lambda: main_program())
