from datetime import datetime
import pytz

est_timezone = pytz.timezone('America/New_York')


def current_date():
    utc_time = datetime.utcnow().replace(tzinfo=pytz.utc)
    est_time = utc_time.astimezone(est_timezone)
    return est_time.strftime("%m-%d-%Y")


def current_date_time():
    utc_time = datetime.utcnow().replace(tzinfo=pytz.utc)
    est_time = utc_time.astimezone(est_timezone)
    return est_time.strftime("%m-%d-%Y %H:%M:%S")


def current_month():
    utc_time = datetime.utcnow().replace(tzinfo=pytz.utc)
    est_time = utc_time.astimezone(est_timezone)
    return est_time.strftime("%m-%y")
