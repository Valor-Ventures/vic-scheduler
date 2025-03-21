from apscheduler.schedulers.background import BackgroundScheduler # runs tasks in the background
import os
import requests
from datetime import datetime, timedelta
import time
from dotenv import load_dotenv
import sentry_sdk
load_dotenv()

# allows us to specify a recurring time for execution
scheduler = BackgroundScheduler()

def callvicapi(url,vic_instance :str = "vicbot"):
    if vic_instance == "vicbot":
        base_url = os.getenv("VICBOT_DJANGO_URL")
    elif vic_instance == "vic20":
        base_url = os.getenv("VIC20")
    headers = { "Authorization": f"Bearer {os.getenv('VIC_API_BEARER_TOKEN')}" }
    response = requests.get(base_url + url, headers=headers)
    return response.json()

@scheduler.scheduled_job('interval', minutes=1)
def check_email():
    print(f"checking email")
    return callvicapi("/api/checkemail")

@scheduler.scheduled_job('interval', hour=1)
def vic20_sfapi_ping():
    print(f"vic20 sfapi ping")
    return callvicapi("/api/startuprunway/ping",vic_instance="vic20")

#sunday - thursday
@scheduler.scheduled_job('cron', hour=21, minute=0)
def vic_daily_tasks():
    print(f"running vic daily tasks")
    response = callvicapi("/api/daily")
@scheduler.scheduled_job('cron', day_of_week='sun,mon,tue,wed,thu', hour=20, minute=0)
def vic_calendar_tasks():
    tomorrow = datetime.now() + timedelta(days=1)
    response = callvicapi("/api/calendar?date="+tomorrow.strftime("%Y-%m-%d"))

if __name__ == "__main__":
    print("Starting scheduler")
    sentry_sdk.init(
    dsn="https://ab479c2adc8863d82d53ab75150015db@o4508767931793409.ingest.us.sentry.io/4508998594461696",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)
    scheduler.start()
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()