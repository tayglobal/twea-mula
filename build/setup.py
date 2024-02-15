from aws_setup.create_role import create_role, create_policy
from aws_setup.create_table import create_table
from aws_setup.create_lambda import create_lambda_func
from aws_setup.create_kms import create_kms, kms_key_id, put_kms_key_policy, describe_key
from aws_setup.create_api_gateway import create_all as create_all_api_gateway

if __name__ == '__main__':
    # TODO: Use cloud formation
    stage = 'dev'
    # create_kms()
    # print(f"KMS key = {kms_key_id()}")
    # put_kms_key_policy()
    # describe_key()
    # create_policy(stage)
    # create_role()
    # create_table(stage)
    create_lambda_func(stage)
    # create_all_api_gateway(stage)

