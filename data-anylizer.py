import json
import datetime

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

import geopy.geocoders
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

geopy.geocoders.options.default_timeout = 10


def process_chunk(chunk_id, geolocator):
    with open('tweets.json') as json_file:
        tweets_data = json.load(json_file)
        f = open('resutls_geocode.txt', 'w+')
        for tweet in tweets_data['records']:
            if tweet['user']['location'] is not None:
                f.write("%s -> %s \n" % (tweet['user']['location'], geolocator.geocode(tweet['user']['location'])))


if __name__ == "__main__":
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    geolocator = Nominatim(user_agent="data-analizer2")
    #geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1, error_wait_seconds=1, max_retries=5)

    fileList = drive.ListFile({'q': "'1gCy3UlgGHDPA1CW5-mNh8zr5SO7-_gI3' in parents and trashed=false"}).GetList()
    for file in fileList:
        innerFileList = drive.ListFile({'q': "'%s' in parents and trashed=false" % file['id']}).GetList()
        for f in innerFileList:
            if f['title'] == 'COVIDtweets-0000.json':
                f.GetContentFile('tweets.json')
                start = datetime.datetime.now()
                process_chunk(f['title'], geolocator)
                duration = datetime.datetime.now() - start
                print(duration)

