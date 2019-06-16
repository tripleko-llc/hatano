from hatano.util import Conf

import boto3

def clean(args):
    stage = args.stage
    c = Conf()
    project, stg_conf = c.get_stage(stage)

    lda = boto3.client('lambda')
    iam = boto3.client('iam')
    agw = boto3.client('apigateway')

    all_apis = agw.get_rest_apis()
    for api in all_apis['items']:
        if api['name'] == project:
            try:
                agw.delete_rest_api(restApiId=api['id'])
            except:
                pass

    for name in stg_conf.get("functions", {}):
        fullname = f"{project}-{name}-{stage}"

        try:
            lda.delete_function(FunctionName=fullname)
        except:
            pass

        try:
            iam.delete_role(RoleName=fullname)
        except:
            pass
   



