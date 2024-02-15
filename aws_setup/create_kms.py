import boto3
from settings import AWS_REGION, APP_NAME, KMS_KEY_NAME, AWS_ACCOUNT, ROLE_NAME, KMS_ID_KEY
import json

def create_kms():
    kms = boto3.client('kms', region_name=AWS_REGION)

    response = kms.create_key(
        Description='KMS for twea-mula',
        KeyUsage='ENCRYPT_DECRYPT',
        CustomerMasterKeySpec='SYMMETRIC_DEFAULT',
    )

    response = kms.create_key(
        Description='KMS for ' + APP_NAME,
        KeyUsage='ENCRYPT_DECRYPT',
        Origin='AWS_KMS',
    )
    print(response)

    key_id = response['KeyMetadata']['KeyId']

    # Create an alias for the new KMS key
    alias_name = 'alias/' +  KMS_KEY_NAME
    kms.create_alias(
        AliasName=alias_name,
        TargetKeyId=key_id,
    )

    print(response)

def put_kms_key_policy():
    kms = boto3.client('kms')

    policy = {
        "Version": "2012-10-17",
        "Id": "key-default-1",
        "Statement": [
            {
                "Sid": "Enable IAM User Permissions",
                "Effect": "Allow",
                "Principal": {
                    "AWS": f"arn:aws:iam::{AWS_ACCOUNT}:root"
                },
                "Action": "kms:*",
                "Resource": "*"
            },
            {
                "Sid": "Allow use of the key",
                "Effect": "Allow",
                "Principal": {
                    "AWS": f"arn:aws:iam::{AWS_ACCOUNT}:role/{ROLE_NAME}"
                },
                "Action": [
                    "kms:Encrypt",
                    "kms:Decrypt",
                    "kms:ReEncrypt*",
                    "kms:GenerateDataKey*",
                    "kms:DescribeKey"
                ],
                "Resource": "*"
            }
        ]
    }

    response = kms.put_key_policy(
        KeyId=f'arn:aws:kms:{AWS_REGION}:{AWS_ACCOUNT}:key/{KMS_ID_KEY}',
        PolicyName='default',
        Policy=json.dumps(policy),
    )
    
    print(response)

def kms_key_id():
    kms = boto3.client('kms', region_name=AWS_REGION)

    response = kms.list_aliases()

    for alias in response['Aliases']:
        if alias['AliasName'] == 'alias/' + KMS_KEY_NAME:
            key_id = alias['TargetKeyId']
            return key_id

    return None

def describe_key():
    kms = boto3.client('kms')

    response = kms.describe_key(
        KeyId=f'arn:aws:kms:{AWS_REGION}:{AWS_ACCOUNT}:key/{KMS_ID_KEY}',
    )

    print(response)