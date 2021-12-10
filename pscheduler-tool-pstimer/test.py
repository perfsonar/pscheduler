import pscheduler 
import datetime 

start_time = datetime.date.now()
source = input['test']['spec']['url']
timeout_iso = input['test']['spec'].get('timeout', 'PT10S')
timeout = pscheduler.timedelta_as_seconds(pscheduler.iso8601_as_timedelta(timeout_iso))

try:
    pscheduler.api(source, timeout)

except:
# it is an error 

finally:
    end_time = datetime.datetime.now()

time = pscheduler.timedelta_as_iso8601(end_time - start_time)
print(time)
