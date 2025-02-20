from hatano.util import Conf
from hatano.route53 import Route53
from hatano.iam import IamRole
from hatano.s3 import S3

import boto3
import os

def clean(args):
    stage = args.stage
    c = Conf()
    conf = c.read()
    project = conf["project"]
    stg_conf = conf["stage"][stage]
    domain = stg_conf.get("domain")

    lda = boto3.client('lambda')
    agw = boto3.client('apigateway')
    r53 = Route53()
    s3_path = stg_conf.get("bucket")

    if s3_path:
        s3 = S3(s3_path, project, stage)
        try:
            print(f"Emptying s3 bucket {s3.name()}")
            s3.empty()
        except Exception as e:
            print(f"Failed: {e}")

        try:
            print(f"Deleting s3 bucket {s3.name()}")
            s3.delete()
        except Exception as e:
            print(f"Failed: {e}")

    if domain:
        try:
            print(f"Cleaning up custom domain {domain}")
            agw.delete_domain_name(domainName=domain)
        except Exception as e:
            print(f"Failed: {e}")

        try:
            print(f"Cleaning up cname record for {domain}")
            r53.delete_cname_record(domain)
        except Exception as e:
            print(f"Failed: {e}")

    all_apis = agw.get_rest_apis()
    for api in all_apis['items']:
        if api['name'] == project:
            try:
                print(f"Cleaning up REST API {project}")
                agw.delete_rest_api(restApiId=api['id'])
            except Exception as e:
                print(f"Failed: {e}")


    for name in conf.get("function", {}):
        fn = conf["function"][name]
        fn["name"] = name
        iam = IamRole(stage, fn)

        fullname = f"{project}-{name}-{stage}"

        try:
            print(f"Cleaning up function {name}")
            lda.delete_function(FunctionName=fullname)
        except Exception as e:
            print(f"Failed: {e}")

        try:
            print("Cleaning up custom role policy")
            iam.delete_custom_policy()
        except Exception as e:
            print(f"Failed: {e}")

        try:
            print(f"Cleaning up IAM role {fullname}")
            iam.delete_role()
        except Exception as e:
            print(f"Failed: {e}")

        try:
            print(f"Cleaning up CloudWatch logs {fullname}")
            logs = boto3.client('logs')
            groupname = f"/aws/lambda/{fullname}"
            logs.delete_log_group(logGroupName=groupname)
        except Exception as e:
            print(f"Failed: {e}")
