# Copy this file to setting.py

# TODO: Put this in a yaml config
import os

APP_NAME = 'twea-mula'
AWS_REGION = 'ap-northeast-1'

POLICY_NAME = APP_NAME + '-policy'
ROLE_NAME = APP_NAME + '-role'

TABLE_MAP = {
    'dev': 'twea-mula-dev',
    'prod': 'twea-mula-prod'
}

LAMBDA_FUNCTION_MAP = {
    'dev': 'twea-mula-dev',
    'prod': 'twea-mula-prod'
}

# Discord related settings
APPLICATION_ID = "<Application ID Goes here>"
DISCORD_PUBLIC_KEY = '<Disocrd Public Key goes here>'

# Insert the channel ids
CHANNEL_IDS = {
    "test": 1234,
    "general": 4567
}

AWS_ACCOUNT=1234
GUILD_ID=1234

API_GATEWAY_MAP = {
    'dev': 'twea-mula-dev',
    'prod': 'twea-mula-prod'
}

KMS_KEY_NAME = APP_NAME + '-kms'

KMS_ID_KEY = '<Insert the KMS ID Key>'
