import os
import json

import boto3

DATA_DIR = '/local/DATA/itp/networked_media/google_quickdraw'

TABLE_NAME = 'GoogleQuickdraw'
INPUT_DIR = 'filtered2'
INPUT_FILENAME = 'data_50_None.json'

dynamodb = boto3.resource(
    'dynamodb',
    region_name='us-east-1',
    # endpoint_url="http://localhost:8000"
)

table = dynamodb.Table(TABLE_NAME)

with open(os.path.join(DATA_DIR, INPUT_DIR, INPUT_FILENAME)) as json_file:
    sketches = json.load(json_file)
    with table.batch_writer() as batch:
        for i, sketch in enumerate(sketches):
            print("Adding sketch:", i, sketch['p_id'], sketch['s_id'])

            batch.put_item(Item=sketch)

print("Loaded", table.item_count, "sketches into table")
