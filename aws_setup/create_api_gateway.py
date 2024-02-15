import boto3
from settings import AWS_REGION, API_GATEWAY_MAP, LAMBDA_FUNCTION_MAP, ROLE_NAME

client = boto3.client("apigateway", region_name=AWS_REGION)


def get_rest_api_id(stage):
    response = client.get_rest_apis()
    name = API_GATEWAY_MAP[stage]
    return next(x["id"] for x in response["items"] if x["name"] == name)


def _get_resource_id(rest_api_id, path):
    response = client.get_resources(restApiId=rest_api_id)

    return next(x["id"] for x in response["items"] if x["path"] == path)


def create_resource(rest_api_id):
    root_id = _get_resource_id(rest_api_id, '/')

    response = client.create_resource(
        restApiId=rest_api_id,
        parentId=root_id,
        pathPart="interactions",
    )

    print(response)


def create_method(rest_api_id, resource_id):
    response = client.put_method(
        restApiId=rest_api_id,
        resourceId=resource_id,
        httpMethod="POST",
        authorizationType="NONE",
    )

    print(response)

def get_role_arn():
    iam = boto3.client('iam')

    response = iam.get_role(
        RoleName=ROLE_NAME
    )

    return response['Role']['Arn']

def create_integration(stage, rest_api_id, resource_id):
    lambda_uri = get_lambda_function_uri(LAMBDA_FUNCTION_MAP[stage])
    uri = f"arn:aws:apigateway:{AWS_REGION}:lambda:path/2015-03-31/functions/{lambda_uri}/invocations"
    print(uri)

    credentials = get_role_arn()

    # response = client.put_integration(
    #     restApiId=rest_api_id,
    #     resourceId=resource_id,
    #     httpMethod='POST',
    #     type='AWS_PROXY',
    #     integrationHttpMethod='POST',
    #     uri=uri,
    #     credentials=credentials
    # )

    response = client.update_integration(
        restApiId=rest_api_id,
        resourceId=resource_id,
        httpMethod='POST',
        patchOperations=[
            {
                'op': 'replace',
                'path': '/uri',
                'value': uri,
            },
        ]
    )

    print(response)

def get_lambda_function_uri(function_name):
    client = boto3.client("lambda", region_name=AWS_REGION)
    response = client.get_function(FunctionName=function_name)
    return response["Configuration"]["FunctionArn"]


def create_deploy(rest_api_id, stage):
    response = client.create_deployment(
        restApiId=rest_api_id,
        stageName=stage,  # replace with your stage name
        description=f"{stage} stage",
    )
    
    print(response)


def create_api_gateway(stage):
    response = client.create_rest_api(
        name=API_GATEWAY_MAP[stage],
        description="An API gateway to server twea-mula",
        endpointConfiguration={
            "types": [
                "REGIONAL",
            ]
        },
    )

    print(response)


def create_all(stage):
    # create_api_gateway(stage)
    rest_api_id = get_rest_api_id(stage)
    # create_resource(rest_api_id)

    resource_id = _get_resource_id(rest_api_id, '/interactions')
    # create_method(rest_api_id, resource_id)
    create_integration(stage, rest_api_id, resource_id)
    # create_deploy(rest_api_id, stage)