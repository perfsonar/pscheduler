#!/usr/bin/python
#
# pScheduler REST API Server
#


# TODO: Need to add code to validate incoming UUIDs so the database
# doesn't barf on them and leave a cryptic error message.


from pschedulerapiserver import *

# TODO: For now, these are is hard-wired defaults.  At some point we
# should be pulling this from a config file.

dsn = "@/etc/pscheduler/database-dsn"
dbcursor_init(dsn)


opt_debug = True


# TODO: Need a catch-all to do 404s.


if __name__ == "__main__":
    # TODO: Not portable outside of Unix
    port = 80 if os.getuid() == 0 \
        else 29285 # Spell out "BWCTL" on a phone and this is what you get.
        
    application.run(
        host='0.0.0.0',
        port=port,  
        debug=opt_debug
        )
