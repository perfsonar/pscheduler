#!/bin/sh
#
# pscheduler-runner        Start/Stop the pScheduler Runner
#
# chkconfig: 2345 99 10
# description: Runner for pScheduler database


### BEGIN INIT INFO
# Provides: pscheduler-runner
# Default-Start:  2345
# Default-Stop: 10
# Short-Description: Run pscheduler runner
# Description: Runner for pscheduler database
### END INIT INFO


prog="pscheduler-runner"
exec=/usr/bin/$prog

# TODO: These should come from the RPM macros
config=/etc/pscheduler/database-dsn
proguser=pscheduler

pidfile=/var/run/$prog.pid
lockfile=/var/lock/subsys/$proc

# TODO: Need to rotate this.
logfile=/var/log/$prog.log

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
    echo -n $"Starting $prog: "
    touch "$pidfile"
    chown "$proguser.$proguser" "$pidfile"
    nohup su pscheduler \
	-s /bin/sh \
	-c "echo \$\$ > '$pidfile' && exec $exec --dsn '@$config'" \
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
