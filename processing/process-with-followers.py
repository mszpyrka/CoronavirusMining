import os
import json
import pandas as pd
from collections import defaultdict
import shutil

directory = './input'
directory_out = './output'

parts = 4


class CountryDict:
    def __init__(self):
        translation_file = '../analysis-utils/countries-translation/global_names.csv'
        self.translation_df = pd.read_csv(translation_file, keep_default_na=False, na_values=[''])
        self.country_list = []
        for country in self.translation_df['alpha_2'].tolist():
            if country:
                self.country_list.append(country)

        self.country_dict = {k: [] for k in self.country_list}
        self.country_percent = {k: {} for k in self.country_list}
        self.thresholds = [50, 25, 10, 5, 2, 1, 0]

    def clear(self):
        self.country_dict = defaultdict(list)

    def append(self, key, value):
        self.country_dict[key].append(value)

    def store_percent(self):
        for key in self.country_dict:
            country_max = self.country_dict[key][0]
            self.country_percent[key]['max'] = country_max
            step = 0
            threshold = country_max * (self.thresholds[step] / 100)
            counter = 0
            #print("Start threshold %s" % threshold)
            for fol_count in self.country_dict[key]:
                processed = False
                #print("Actual threshold %s and part number %s and value %s" % (threshold, part_number, fol_count))
                while not processed:
                    if fol_count >= threshold:
                        counter += 1
                        processed = True
                    else:
                        #print("Stored " + key + " " + str(1 - part_number/parts) + " " + filename)
                        percent_step = self.thresholds[step]
                        self.country_percent[key][str(percent_step) + '%+'] = counter
                        counter = 0
                        step += 1
                        #print(part_number)
                        threshold = country_max * (self.thresholds[step] / 100)

            percent_step = self.thresholds[step]
            self.country_percent[key][str(percent_step) + '%+'] = counter

        with open(directory_out + '/' + filename[:-5] + '-percent.json', 'w') as fp:
            json.dump(self.country_percent, fp)

    def store(self, filename):
        for key in self.country_dict:
            self.country_dict[key].sort(reverse=True)

        with open(directory_out + '/' + filename, 'w') as fp:
            json.dump(self.country_dict, fp)

        self.store_percent()


def process_json(filename, country_dict):
    with open(directory + '/' + filename) as json_file:
        data = json.load(json_file)
        country_dict.clear()
        for record in data['records']:
            country_dict.append(record['country'], record['followers_count'])

        #country_dict.append(data['records'][0]['country'], data['records'][0]['followers_count'])
        country_dict.store(filename)


if __name__ == "__main__":
    shutil.rmtree('./output', ignore_errors=True)

    if not os.path.exists('./output'):
        os.makedirs('./output')

    country_dict = CountryDict()
    for filename in os.listdir(directory):
        print("Process %s" % filename)
        process_json(filename, country_dict)
