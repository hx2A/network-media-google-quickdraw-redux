import time
import boto3

TABLE_NAME = 'GoogleQuickdraw'

dynamodb = boto3.resource(
    'dynamodb',
    region_name='us-east-1',
    # endpoint_url="http://localhost:8000"
)


try:
    table = dynamodb.Table(TABLE_NAME)
    table.delete()
    time.sleep(5)  # wait for delete to finish
except Exception as e:
    pass


table = dynamodb.create_table(
    TableName=TABLE_NAME,
    KeySchema=[
        {
            'AttributeName': 'p_id',
            'KeyType': 'HASH'  # Partition key
        },
        {
            'AttributeName': 's_id',
            'KeyType': 'RANGE'  # Sort key
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'p_id',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 's_id',
            'AttributeType': 'N'
        },
        {
            'AttributeName': 'f',
            'AttributeType': 'N'
        },
        {
            'AttributeName': 'i',
            'AttributeType': 'N'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 2,
        'WriteCapacityUnits': 40
    },
    GlobalSecondaryIndexes=[
        {
            'IndexName': 'GoogleQuickdrawFlagged',
            'KeySchema': [
                {
                    'AttributeName': 'f',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 's_id',
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            'Projection': {
                'ProjectionType': 'ALL'
            },
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 2,
                'WriteCapacityUnits': 40
            }
        },
        {
            'IndexName': 'GoogleQuickdrawInappropriate',
            'KeySchema': [
                {
                    'AttributeName': 'i',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 's_id',
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            'Projection': {
                'ProjectionType': 'ALL'
            },
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 2,
                'WriteCapacityUnits': 40
            }
        },
    ]
)

print("Table status:", table.table_status)
