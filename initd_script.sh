#! /bin/bash

APPNAME=spending
USER=ubuntu
APP_HOME=/usr/local/src/spending/
APP_PATH=80
ACTIVATE=/home/ubuntu/venv/bin/activate
APPMODULE=spending.wsgi
DAEMON=gunicorn
BIND=0.0.0.0
PIDFILE=/var/run/$DAEMON-$APPNAME.pid
LOGFILE=/var/log/$DAEMON-$APPNAME.log
LOGLEVEL=info
WORKERS=5
THREADS=2


. /lib/lsb/init-functions


if [ -e "/etc/default/$APPNAME" ]
then
    . /etc/default/$APPNAME
fi


case "$1" in
  start)
        echo "Starting deferred execution scheduler" "$APPNAME"
        source $ACTIVATE
	cd $APP_HOME
	$DAEMON --bind=$BIND:$APP_PATH --pid=$PIDFILE --workers=$WORKERS --user=$USER --log-file=$LOGFILE $APPMODULE --log-level=$LOGLEVEL -D --preload
	echo $?
    ;;
  stop)
        echo "Stopping deferred execution scheduler" $APPNAME
        local pid=$(/bin/cat "$PIDFILE" 2>/dev/null)
	echo pid
	kill -9 `cat $PIDFILE`
        echo $?
    ;;
  force-reload|restart)
    $0 stop
    $0 start
    ;;
  status)
    status_of_proc -p $PIDFILE $DAEMON && exit 0 || exit $?
    ;;
  *)
    echo "Usage: /etc/init.d/$APPNAME {start|stop|restart|force-reload|status}"
    exit 1
    ;;
esac

exit 0
