check_process()
{
  is_process_started=0

  [ "$1" = "" ]  && return $is_process_started # return 0
  [ `pgrep -n $1` ] && is_process_started=1 || is_process_started=0
}

date_time=$(date '+%d/%m/%Y %H:%M:%S')

check_process "httpd"

if [ $is_process_started -ne 1 ]; then
  #httpd needs to be started
  echo -e "$date_time | httpd was stopped, starting it ..." >> /root/httpd_start.log
  { /root/homework/materials/class03/src/tinyhttpd/tinyhttpd/httpd & } \
                                        1>>/root/httpd_messages.log    \
                                        2>>/root/httpd_error.log
  echo -e "$date_time | ... httpd started succesfully\n" >> /root/httpd_start.log
else
  echo "httpd already started"
fi
