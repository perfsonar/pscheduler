changequote(<!,!>)dnl
changecom()dnl
#!/bin/sh
#
# pscheduler-__PROG__  Start/Stop the pScheduler __PROG__
#
# chkconfig: 2345 99 10
# description: pScheduler __PROG__ daemon


### BEGIN INIT INFO
# Provides: pscheduler-__PROG__
# Default-Start:  2345
# Default-Stop: 10
# Short-Description: Run pscheduler __PROG__
# Description: pScheduler __PROG__ daemon
### END INIT INFO



prog=__PROG__
exec=__DAEMONDIR__/$prog

config=__DSN__
proguser=__PSUSER__

pidfile=__VAR__/run/pscheduler-$prog.pid
lockfile=__VAR__/lock/subsys/$proc

# TODO: Should probably rotate this, but should almost always be empty.
logfile=__LOGDIR__/$prog.log

# Source function library.
. /etc/rc.d/init.d/functions

retval=0

[ $UID -eq 0 ]

start() {
    if [ $UID -ne 0 ] ; then
        echo "User has insufficient privilege."
        exit 4
    fi
    [ -x $exec ] || exit 5
    [ -f $config ] || exit 6
    echo -n $"Starting pScheduler $prog: "
    touch "$pidfile"
    chown "$proguser.$proguser" "$pidfile"
    if [ ! -s "$logfile" ] ; then
        echo "(This file should be empty unless there's a catastrophic failure.)" >> "$logfile"
    fi
    su $proguser \
       -c "$exec --daemon --pid-file '$pidfile' --dsn '@$config'" \
	>> "$logfile" 2>&1 &
    retval=$?
    success
    echo
}


stop() {
    if [ $UID -ne 0 ] ; then
        echo "User has insufficient privilege."
        exit 4
    fi
    echo -n $"Stopping pScheduler $prog: "
        if [ -s "$pidfile" ]; then
	    kill $(cat $pidfile) || failure "Stopping pScheduler $prog"
	    rm -f $pidfile
	fi
    retval=$?
    success
    echo
}

restart()
{
    stop
    start
}



case "$1" in
    start)
        $1
        ;;
    stop)
        $1
        ;;
    restart)
        $1
        ;;
    *)
        echo $"Usage: $0 {start|stop|restart}"
        exit 2
esac
exit $?
