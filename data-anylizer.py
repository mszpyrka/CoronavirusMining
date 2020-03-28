import json
import time
import os
import pandas as pd
import pycountry as pc
import ast
import re
import sys

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


class CountryLookup:
    def __init__(self, translation_file):
        translation_df = pd.read_csv(translation_file, keep_default_na=False, na_values=[''])
        clean_df = translation_df[translation_df['alpha_2'].isnull().values == False]
        translation_dict = {}

        for _, row in clean_df.iterrows():
            alpha_2 = row['alpha_2']
            translation_dict[row['english_name']] = alpha_2

            native_names = ast.literal_eval(row['native_names'])
            for native in native_names:
                translation_dict[native] = alpha_2

            pc_record = pc.countries.lookup(alpha_2)
            translation_dict[pc_record.name.lower()] = alpha_2

            try:
                translation_dict[pc_record.official_name.lower()] = alpha_2
            except AttributeError:
                continue

        self.translation_dict = translation_dict

    def __getitem__(self, key):
        if key is None:
            return None
        key = key.lower()
        key_parts = re.split(r'[?.,-]', key)
        key_parts = [k for k in key_parts if len(k) > 0]
        for k in key_parts:
            k = ' '.join(k.split())
            lookup = self.translation_dict.get(k)
            if lookup is not None:
                return lookup

        return None


def prepare_data(tweet, cc):
    return {
        'id': tweet['id'],
        'time': time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')),
        'lang': tweet['lang'],
        'followers_count': tweet['user']['followers_count'],
        'country': cc
    }


class ChunkAnalizer:
    def __init__(self, output_dir_path):
        self.output_dir_path = output_dir_path
        self.date = -1
        self.records = []
        self.len = 0
        self.all = 0
        self.max_size = 200000
        self.countrylookup = CountryLookup('./analysis/countries-translation/global_names.csv')

    def save_data(self):
        print("Save %s tweet from %s - %s" % (self.len, self.all, self.date))
        output_file_path = "%s/%s.json" % (self.output_dir_path, self.date)
        if os.path.exists(output_file_path):
            with open(output_file_path, "r") as f:
                self.records = json.load(f)['records'] + self.records

        with open(output_file_path, "w") as f:
            data_json = {
                "records": self.records
            }
            json.dump(data_json, f)

        self.records = []
        self.len = 0
        self.all = 0

    def store_data(self, data):
        if (self.date != data['time'].split(' ')[0] and self.date != -1) or self.len >= self.max_size:
            self.save_data()

        self.records.append(data)
        self.date = data['time'].split(' ')[0]
        self.len += 1

    def process_tweet(self, tweet):
        cc = self.countrylookup[tweet['user']['location']]
        if cc is not None:
            self.store_data(prepare_data(tweet, cc))

    def process_chunk(self, chunk):
        chunk.GetContentFile('chunk.json')
        with open('chunk.json', 'r') as chunk_json:
            tweets_data = json.load(chunk_json)
            for tweet in tweets_data['records']:
                self.all += 1
                self.process_tweet(tweet)


def check_main_catalog():
    fileList = drive.ListFile({'q': "'1gCy3UlgGHDPA1CW5-mNh8zr5SO7-_gI3' in parents and trashed=false"}).GetList()
    for file in fileList:
        print("%s %s" % (file['title'], file['id']))


if __name__ == "__main__":
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    catalog_title = 'serwer-07.03-14.03'
    catalog_id = '1AmXEexUm_LC_52jRZZXUwqnDc34hd4cQ'

    if len(sys.argv) > 2:
        catalog_title = sys.argv[1]
        catalog_id = sys.argv[2]

    fileList = drive.ListFile({'q': "'%s' in parents and trashed=false" % catalog_id}).GetList()
    fileList.reverse()

    output_dir_path = os.path.join(os.getcwd(), r"output/%s" % catalog_title)
    if not os.path.exists(output_dir_path):
        os.makedirs(output_dir_path)

    chunkanalizer = ChunkAnalizer(output_dir_path)

    for chunk in fileList:
        print("Processing: %s %s" % (chunk['title'], chunk['id']))
        chunkanalizer.process_chunk(chunk)

    chunkanalizer.save_data()
