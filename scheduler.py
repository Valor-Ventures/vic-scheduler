from apscheduler.schedulers.background import BackgroundScheduler # runs tasks in the background
import os
import requests
from datetime import datetime, timedelta
import time
# allows us to specify a recurring time for execution
scheduler = BackgroundScheduler()

def callvicapi(url):
    base_url = os.getenv("VIC_DJANGO_URL")
    headers = { "Authorization": f"Bearer {os.getenv('VIC_API_BEARER_TOKEN')}" }
    response = requests.get(base_url + url, headers=headers)
    return response.json()

@scheduler.scheduled_job('interval', minutes=1)
def check_email():
    print(f"checking email")
    return callvicapi("/api/checkemail")

#sunday - thursday
@scheduler.scheduled_job('cron', hour=21, minute=0)
def vic_daily_tasks():
    print(f"running vic daily tasks")
    response = callvicapi("/api/daily")
@scheduler.scheduled_job('cron', day_of_week='sun,mon,tue,wed,thu', hour=20, minute=0)
def vic_calendar_tasks():
    tomorrow = datetime.now() + timedelta(days=1)
    response = callvicapi("/api/calendar/?date="+tomorrow.strftime("%Y-%m-%d"))

if __name__ == "__main__":
    scheduler.start()
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()