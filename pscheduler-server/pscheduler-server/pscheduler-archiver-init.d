#!/bin/sh
#
# pscheduler-archiver        Start/Stop the pScheduler Archiver
#
# chkconfig: 2345 99 10
# description: Archiver for pScheduler database


### BEGIN INIT INFO
# Provides: pscheduler-archiver
# Default-Start:  2345
# Default-Stop: 10
# Short-Description: Run pscheduler archiver
# Description: Archiver for pscheduler database
### END INIT INFO


RETVAL=0
prog="pscheduler-archiver"
exec=/usr/bin/$prog
# TODO: This should come from the RPM macros
config=/etc/pscheduler/database-dsn
pidfile=/var/run/$proc.pid
lockfile=/var/lock/subsys/$proc

# Source function library.
. /etc/rc.d/init.d/functions

[ $UID -eq 0 ]


start() {
    if [ $UID -ne 0 ] ; then
        echo "User has insufficient privilege."
        exit 4
    fi
    [ -x $exec ] || exit 5
    [ -f $config ] || exit 6
    echo -n $"Starting $prog: "
    # TODO: This user need to be resolved from RPM macros
    # TODO: Find a cleaner way to do this.
    su - pscheduler -c "exec /usr/bin/$prog --dsn '@$config'" &
    echo $! > $pidfile
    retval=$?
    success
    echo
}


stop() {
    if [ $UID -ne 0 ] ; then
        echo "User has insufficient privilege."
        exit 4
    fi
    echo -n $"Stopping $prog: "
        if [ -s "$pidfile" ]; then
	    kill $(cat $pidfile) || failure "Stopping $prog"
	    rm -f $pidfile
	fi
    retval=$?
    success
    echo
}

restart() {
    rh_status_q && stop
    start
}

reload() {
	echo -n $"Reloading $prog: "
	if [ -n "`pidfileofproc $exec`" ]; then
		killproc $exec -HUP
	else
		failure $"Reloading $prog"
	fi
	retval=$?
	echo
}

force_reload() {
	# new configuration takes effect after restart
    restart
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

