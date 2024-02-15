import boto3
from settings import AWS_REGION, TABLE_MAP


dynamodb = boto3.client('dynamodb', region_name=AWS_REGION)

def create_table(stage):
    table_name = TABLE_MAP[stage]
    index_attr = 'path'
    folder_attr = 'folder'
    folder_index = folder_attr + '-index'
    
    table_params = {
        'TableName': table_name,
        'AttributeDefinitions': [
            {
                'AttributeName': index_attr,
                'AttributeType': 'S'
            },
            {
                'AttributeName': folder_attr,
                'AttributeType': 'S'
            }
        ],
        'KeySchema': [
            {
                'AttributeName': index_attr,
                'KeyType': 'HASH'
            }
        ],
        'BillingMode': 'PAY_PER_REQUEST',
        'GlobalSecondaryIndexes': [
            {
                'IndexName': folder_index,
                'KeySchema': [
                    {
                        'AttributeName': folder_attr,
                        'KeyType': 'HASH'
                    }
                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                }
            }
        ]
    }
    
    response = dynamodb.create_table(**table_params)
    print(response)

def delete_table(stage):
    response = dynamodb.delete_table(TableName=TABLE_MAP[stage])
    print(response)
