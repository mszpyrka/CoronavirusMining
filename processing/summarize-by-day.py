import os
import json
import pandas as pd

directory = './input'
directory_out = './output'


class CountryDict:
    def __init__(self):
        translation_file = '../analysis/countries-translation/global_names.csv'
        self.translation_df = pd.read_csv(translation_file, keep_default_na=False, na_values=[''])
        self.country_dict = {}
        for country in self.translation_df['alpha_2'].tolist():
            if country:
                self.country_dict[country] = 0

    def clear(self):
        self.country_dict = self.country_dict.fromkeys(self.country_dict, 0)

    def append(self, key):
        self.country_dict[key] += 1

    def store(self, filename):
        with open(directory_out + '/' + filename, 'w') as fp:
            json.dump(self.country_dict, fp)


def process_json(filename, country_dict):
    with open(directory + '/' + filename) as json_file:
        data = json.load(json_file)
        country_dict.clear()
        for record in data['records']:
            country_dict.append(record['country'])

        country_dict.store(filename)


if __name__ == "__main__":
    country_dict = CountryDict()
    for filename in os.listdir(directory):
        process_json(filename, country_dict)
