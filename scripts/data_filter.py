import os
import glob
import json

import numpy as np
import pandas as pd
from pandas import Series


DATA_DIR = '/local/DATA/itp/networked_media/google_quickdraw'

SIZE_LIMIT = 50
FILE_LIMIT = None
INPUT_DIR = 'clean'
OUTPUT_DIR = 'filtered2'

with open(os.path.join(DATA_DIR, 'lookups', 'iso_codes.json'), 'r') as f:
    iso_codes = json.load(f)

files = glob.glob(os.path.join(DATA_DIR, INPUT_DIR, '*.p'))
if FILE_LIMIT:
    files = sorted(np.random.choice(files, size=FILE_LIMIT, replace=False))
else:
    files = sorted(files)

all_data = []

for i, filename in enumerate(files):
    print("{0}/{1}: {2}".format(files.index(filename) + 1,
                                len(files), filename))

    rs = np.random.RandomState(i)
    data = pd.read_pickle(filename)

    def data_filtering(df):
        if df.shape[0] <= SIZE_LIMIT:
            return df
        else:
            return df.sample(n=SIZE_LIMIT, replace=False, random_state=rs)

    all_data.append(
        data.groupby('c').apply(data_filtering).reset_index(drop=True))

data_filtered = pd.concat(all_data).reset_index()

# make the country and category codes all lowercase
data_filtered['c'] = data_filtered['c'].str.lower()
data_filtered['w'] = data_filtered['w'].apply(
    lambda cc: cc.replace(' ', '_').lower())
data_filtered['p_id'] = (data_filtered['c'] + '|' + data_filtered['w'])
# discard countries we have no iso code for
data_filtered = data_filtered[data_filtered['c'].isin(iso_codes.keys())]

# get the category codes to save for the dropdown
category_codes = (
    {cc: ' '.join([w.capitalize() for w in cc.split('_')])
     for cc in data_filtered['w'].unique()}
)

# get the country counts so we know which to remove from dropdown
country_counts = data_filtered['c'].value_counts().to_frame()

# drop unneeded columns
data_filtered.drop(['c', 'w'], axis=1, inplace=True)

data_file = 'data_{0}_{1}.p'.format(SIZE_LIMIT, FILE_LIMIT)
data_filtered.to_pickle(os.path.join(DATA_DIR, OUTPUT_DIR, data_file))


def remove_index(r):
    del r['index']
    return r


records = [remove_index(r) for r in data_filtered.to_dict(orient='records')]

json_file = 'data_{0}_{1}.json'.format(SIZE_LIMIT, FILE_LIMIT)
with open(os.path.join(DATA_DIR, OUTPUT_DIR, json_file), 'w') as f:
    json.dump(records, f)
    print("Wrote {0} records".format(len(records)))

json_file = 'category_codes_{0}.json'.format(FILE_LIMIT)
with open(os.path.join(DATA_DIR, 'lookups', json_file), 'w') as f:
    f.write(json.dumps(category_codes))

# Fix country dropdown. want to make sure countries in dropdown have at least
# a few pictures. Also, want the country dropdown to be sorted by country name,
# not country code.
with open(os.path.join(DATA_DIR, 'lookups', 'iso_codes.json'), 'r') as f:
    iso_codes = json.load(f)

country_counts = country_counts.query('c >= 100')
country_counts['name'] = Series(iso_codes)
country_counts.sort_values('name', inplace=True)

with open(os.path.join(DATA_DIR, 'lookups', 'iso_codes_filtered.json'),
          'w') as f:
    f.write(country_counts['name'].to_json())
