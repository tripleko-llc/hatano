from hatano.util import get_stage
from hatano.iam import IamRole
from hatano.lmbda import Lambda
from hatano.apigateway import RestApi

import os


def deploy(args):
    # Extract stage
    stage = args.stage

    # Get project configuration
    project, stg_conf = get_stage(stage)

    # Create REST API
    api = RestApi(project, create=True)

    # Create each function and link to and endpoint
    for fn in stg_conf.get("functions", []):
        deploy_func(stage, fn, api=api)

    # Deploy the API
    api.deploy(stage)

    # Output
    print("Project:", project)
    print("Stage:", stage)
    print(f"{api.url}/{stage}")


def deploy_func(stage, fn, api=None):
    if not api:
        api = RestApi(stage, create=True)

    http_method = fn.get("http", "")
    http_path = fn.get("path")

    # Create iam role
    iam = IamRole(stage, fn)
    role = iam.lambda_role()
    role_arn = role['Role']['Arn']

    # Create lambda
    lmb = Lambda(stage, fn, role_arn)
    func = lmb.create_function()
    func_arn = func['FunctionArn']
    lmb.add_permission("apigateway")

    # Create resource and endpoint
    resource = api.create_resource(http_path)
    resource.link_endpoint(http_method, func_arn)

