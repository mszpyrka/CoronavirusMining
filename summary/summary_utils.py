import numpy as np
import pandas as pd
import pycountry as pc
import ast
import re

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
        key = key.lower()
        key_parts = re.split(r'[?.,-]', key)
        key_parts = [k for k in key_parts if len(k) > 0]
        for k in key_parts:
            k = ' '.join(k.split())
            lookup = self.translation_dict.get(k)
            if lookup is not None:
                return lookup
            
        return None