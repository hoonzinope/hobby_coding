from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError
import time

def job():
    print("hello")

sched = BackgroundScheduler(timezone='Asia/Seoul')
sched.start()

sched.add_job(job, 'interval', seconds=1, id="hello")

count = 0
while True:
    time.sleep(3)
    print("count :",count)
    count += 1
    if count > 10:
        break