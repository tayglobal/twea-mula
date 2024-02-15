import boto3
import json
from settings import POLICY_NAME, ROLE_NAME, AWS_ACCOUNT, AWS_REGION, LAMBDA_FUNCTION_MAP, KMS_ID_KEY


iam = boto3.client('iam')

def create_policy(stage: str):
    lambda_name = LAMBDA_FUNCTION_MAP[stage]
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "dynamodb:BatchGet*",
                    "dynamodb:DescribeStream",
                    "dynamodb:DescribeTable",
                    "dynamodb:Get*",
                    "dynamodb:Query",
                    "dynamodb:Scan",
                    "dynamodb:BatchWrite*",
                    "dynamodb:CreateTable",
                    "dynamodb:Delete*",
                    "dynamodb:Update*",
                    "dynamodb:PutItem"
                ],
                "Resource": "arn:aws:dynamodb:*:*:table/twea-mula-*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": "arn:aws:logs:*:*:*"
            },
            {
                "Effect": "Allow",
                "Action": "lambda:InvokeFunction",
                "Resource": f"arn:aws:lambda:{AWS_REGION}:{AWS_ACCOUNT}:function:{lambda_name}"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "kms:Encrypt",
                    "kms:Decrypt",
                    "kms:ReEncrypt*",
                    "kms:GenerateDataKey*",
                    "kms:DescribeKey"
                ],
                "Resource": f"arn:aws:kms:{AWS_REGION}:{AWS_ACCOUNT}:key/{KMS_ID_KEY}"
            }
        ]
    }

    response = iam.create_policy(
        PolicyName=POLICY_NAME,
        PolicyDocument=json.dumps(policy_document)
    )

    # response = iam.create_policy_version(
    #     PolicyArn=f'arn:aws:iam::{AWS_ACCOUNT}:policy/{POLICY_NAME}',
    #     PolicyDocument=json.dumps(policy_document),
    #     SetAsDefault=True
    # )

    print(response)

def create_role(update: bool = False):
    assume_role_policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            },
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "apigateway.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }

    # response = iam.create_role(
    #     RoleName=ROLE_NAME,
    #     AssumeRolePolicyDocument=json.dumps(assume_role_policy_document)
    # )
    # print(response)

    response = iam.update_assume_role_policy(
        RoleName=ROLE_NAME,
        PolicyDocument=json.dumps(assume_role_policy_document),
    )
    print(response)

    # response = iam.attach_role_policy(
    #     RoleName=ROLE_NAME,
    #     PolicyArn=f'arn:aws:iam::{AWS_ACCOUNT}:policy/{POLICY_NAME}'
    # )

    # print(response)

    # response = iam.attach_role_policy(
    #     RoleName=ROLE_NAME,
    #     PolicyArn='arn:aws:iam::aws:policy/AWSLambdaExecute'
    # )

    # print(response)
