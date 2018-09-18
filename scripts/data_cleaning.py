import os
import glob
import json
import multiprocessing as mp

import numpy as np
from pandas import DataFrame

DATA_DIR = '/local/DATA/itp/networked_media/google_quickdraw'

files = sorted(glob.glob(os.path.join(DATA_DIR, 'raw', '*.ndjson')))


def clean_file(filename):
    print("{0}/{1}: {2}".format(files.index(filename) + 1,
                                len(files), filename))

    with open(filename, 'r') as f:
        lines = f.readlines()

    all_data = []

    for line in lines:
        data = json.loads(line)
        data_clean = {}
        data_clean['c'] = data['countrycode']
        data_clean['w'] = data['word']
        data_clean['s_id'] = int(data['key_id'])
        data_clean['r'] = data['recognized']
        data_clean['d'] = []
        for drawing in data['drawing']:
            drawing = np.array(drawing)
            drawing[:, 1:] = drawing[:, 1:] - drawing[:, :-1]
            data_clean['d'].append(drawing.tolist())

        all_data.append(data_clean)

    df = DataFrame(all_data)
    new_filename = (os.path.split(filename)[1].split('.')[0] + '.p')
    new_filename = new_filename.replace(' ', '_').lower()
    df.to_pickle(os.path.join(DATA_DIR, 'clean', new_filename))


p = mp.Pool(10)
_ = p.map(clean_file, files)
p.close()
