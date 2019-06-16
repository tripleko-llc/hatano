from hatano.util import Conf
from hatano.route53 import Route53

import boto3

def clean(args):
    stage = args.stage
    c = Conf()
    project, stg_conf = c.get_stage(stage)
    domain = stg_conf.get("domain")

    lda = boto3.client('lambda')
    iam = boto3.client('iam')
    agw = boto3.client('apigateway')
    r53 = Route53()

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


    for name in stg_conf.get("functions", {}):
        fullname = f"{project}-{name}-{stage}"

        try:
            print(f"Cleaning up function {name}")
            lda.delete_function(FunctionName=fullname)
        except Exception as e:
            print(f"Failed: {e}")

        try:
            print(f"Cleaning up IAM role {fullname}")
            iam.delete_role(RoleName=fullname)
        except Exception as e:
            print(f"Failed: {e}")
   



