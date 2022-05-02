from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError
import random
from yackhu import crawler
import time

crawler = crawler()

def job1():
    try:
        crawler.ygosu_url_return()
    except Exception as e:
        print("ygosu error",e)

def job2():
    try:
        crawler.today_humor_url_return()
    except Exception as e:
        print("today_humor error",e)

def job3():
    try:
        crawler.fmkorean_url_return()
    except Exception as e:
        print("fmkorean error",e)

def job4():
    try:
        crawler.etorent_url_return()
    except Exception as e:
        print("etorent error",e)

def job5():
    try:
        crawler.dogdrip_url_return()
    except Exception as e:
        print("dogdrip error",e)

def job6():
    try:
        crawler.dc_mom_url_return()
    except Exception as e:
        print("dc_mom error",e)

def job7():
    try:
        crawler.bobadream_url_return()
    except Exception as e:
        print("bobadream error",e)

sched = BackgroundScheduler(timezone='Asia/Seoul')
sched.start()

#
second = 15 # random.randint(300,600)
sched.add_job(job1, 'interval', seconds=second, id="ygosu_url_return")
sched.add_job(job2, 'interval', seconds=second, id="today_humor_url_return")
sched.add_job(job3, 'interval', seconds=second, id="fmkorean_url_return")
sched.add_job(job4, 'interval', seconds=second, id="etorent_url_return")
sched.add_job(job5, 'interval', seconds=second, id="dogdrip_url_return")
sched.add_job(job6, 'interval', seconds=second, id="dc_mom_url_return")
sched.add_job(job7, 'interval', seconds=second, id="bobadream_return")


while True:
    print("crawling start...")
    time.sleep(3600)