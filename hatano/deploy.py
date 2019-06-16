from hatano.util import Conf
from hatano.iam import IamRole
from hatano.lmbda import Lambda
from hatano.apigateway import RestApi

import os


def deploy(args):
    # Extract stage
    stage = args.stage

    # Get project configuration
    c = Conf()
    project, stg_conf = c.get_stage(stage)

    # Create REST API
    api = RestApi(project, create=True)

    # Create each function and link to and endpoint
    for fname in stg_conf.get("functions", {}):
        fn = stg_conf["functions"][fname]
        fn["name"] = fname

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

    http_method = fn.get("method", "")
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

