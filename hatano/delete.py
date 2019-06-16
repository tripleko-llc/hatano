from hatano.util import get_stage

import boto3

def delete(args):
    stage = args.stage
    project, stg_conf = get_stage(stage)

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

    for fn in stg_conf.get("functions", []):
        name = fn.get("name", "")
        fullname = f"{project}-{name}-{stage}"

        try:
            lda.delete_function(FunctionName=fullname)
        except:
            pass

        try:
            iam.delete_role(RoleName=fullname)
        except:
            pass
   



