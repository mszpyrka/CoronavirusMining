import json
import datetime
import os

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


def process_chunk(chunk):
    chunk.GetContentFile('chunk.json')
    with open('chunk.json', 'r') as chunk_json:
        tweets_data = json.load(chunk_json)
        for tweet in tweets_data['records']:
            print(tweet)


def check_main_catalog():
    fileList = drive.ListFile({'q': "'1gCy3UlgGHDPA1CW5-mNh8zr5SO7-_gI3' in parents and trashed=false"}).GetList()
    for file in fileList:
        print("%s %s" % (file['title'], file['id']))


if __name__ == "__main__":
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    #check_main_catalog()
    catalog_title = 'serwer-07.03-14.03'
    catalog_id = '1AmXEexUm_LC_52jRZZXUwqnDc34hd4cQ'
    fileList = drive.ListFile({'q': "'%s' in parents and trashed=false" % catalog_id}).GetList()
    fileList.reverse()

    output_dir_path = os.path.join(os.getcwd(), r"output/%s" % catalog_title)
    if not os.path.exists(output_dir_path):
        os.makedirs(output_dir_path)

    for chunk in fileList:
        print("Processing: %s %s" % (chunk['title'], chunk['id']))
        process_chunk(chunk)
