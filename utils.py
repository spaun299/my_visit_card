import tornado.gen
import tornado.ioloop
import time
from concurrent.futures import ThreadPoolExecutor
import smtplib
import os
from geoip2.database import Reader
from geoip2.errors import AddressNotFoundError
from pytz import timezone, country_timezones, utc
import datetime


thread_pool = ThreadPoolExecutor(4)


def async_sleep(self, seconds):
    return tornado.gen.Task(tornado.ioloop.IOLoop.instance().add_timeout,
                            time.time() + seconds)


@tornado.gen.coroutine
def call_blocking_func_async(func, *args, **kwargs):
    yield thread_pool.submit(func, *args, **kwargs)


@tornado.gen.coroutine
def call_blocking_func_async_returning(func, *args, **kwargs):
    ret = yield thread_pool.submit(func, *args, **kwargs)
    return ret


@tornado.gen.coroutine
def send_email_async(message, password):
    tornado.ioloop.IOLoop.current().spawn_callback(call_blocking_func_async,
                                                   send_email,
                                                   message, password)


def send_email(message, password):
    fromaddr = 'spaun1002@gmail.com'
    toaddrs = 'spaun1002@gmail.com'
    message = 'Subject: New email from my PORTFOLIO\n\n' + message
    username = 'spaun1002@gmail.com'
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username, password)
    server.sendmail(fromaddr, toaddrs, message)
    server.quit()


def get_location_by_ip(ip):
    try:
        geo_obj = Reader(os.path.dirname(__file__) + '/geoip/geo_lite.mmdb').city(ip)
        return '%s/%s' % (geo_obj.country.name, geo_obj.city.name, )
    except AddressNotFoundError:
        return 'Address not found in db.'


def get_date_and_time_with_timezone(country='UA', date=True, time=False):
    country = timezone(country_timezones[country][0])
    date_time_str = ''
    if date:
        date_time_str += '%Y-%m-%d'
    if time:
        date_time_str += ' %H:%M:%S'
    date = utc.localize(datetime.datetime.utcnow(), is_dst=None).astimezone(
        country).strftime(date_time_str)
    return date


def date_formatting(date, format='%B %Y'):
    try:
        return datetime.datetime.strftime(date, format)
    except Exception:
        return
