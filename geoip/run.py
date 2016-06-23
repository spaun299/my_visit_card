from urllib.request import urlretrieve
import gzip
import os
import traceback
import sys
import time
import schedule
import argparse


def grab_db(url_to_parse, destination_path):
    download_from = url_to_parse
    zip_path = 'zipped_file.gz'
    print('Downloading file from: %s ...' % download_from)
    try:
        urlretrieve(download_from, zip_path)
        print('File downloaded successfully', 'Unzipping file...', sep='\n')
        with gzip.open(zip_path, 'r') as gz:
            with open(destination_path, 'wb') as mmdb:
                for line in gz:
                    mmdb.write(line)
        os.remove(zip_path)
        print('File unzipped as %s' % destination_path)
    except Exception as e:
        _, _, tb = sys.exc_info()
        traceback.print_tb(tb)
        tb_info = traceback.extract_tb(tb)
        filename_, line_, func_, text_ = tb_info[-1]
        message = 'An error occurred on File "{file}" line {line}\n {assert_message}'.format(
            line=line_, assert_message=e.args, file=filename_)
        print(message, "Can't download file", sep='\n')
        exit()


def run_scheduler(url, destination_path):
    schedule.every(5).days.at("15:00").do(grab_db, url_to_parse=url,
                                          destination_path=destination_path)
    while True:
        schedule.run_pending()
        time.sleep(2)

default_url = 'http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz'
parser = argparse.ArgumentParser(description='Script that grab gz file from http and '
                                             'unzip to your destination.'
                                             '(Default GeoLite2 database)')
parser.add_argument('-url', default=default_url,
                    help='Pass downloadable link. Default: %s' % default_url)
parser.add_argument('-destination', default='geo_lite.mmdb',
                    help='Path for downloaded file.Default: geo_lite.mmdb')
parser.add_argument('-schedule', default='y',
                    help='y or n. If "y" script will run on schedule')

if __name__ == '__main__':
    parser_args = parser.parse_args()
    if parser_args.schedule.lower() == 'y':
        run_scheduler(parser_args.url, parser_args.destination)
    elif parser_args.schedule.lower() == 'n':
        grab_db(parser_args.url, parser_args.destination)
    else:
        print('Unrecognized option for "schedule". Available y/n')
