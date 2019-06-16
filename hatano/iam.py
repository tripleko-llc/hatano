from hatano.util import get_stage

import boto3
import json


trust = {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": [
            "lambda.amazonaws.com",
            "apigateway.amazonaws.com"
            ]
      },
      "Action": "sts:AssumeRole"
    }
  ]
}

class IamRole:
    def __init__(self, stage, fnargs):
        self.stage = stage
        self.name = fnargs.get("name")
        self.project, stg_conf = get_stage(stage)
        self.iam = boto3.client('iam')

    def lambda_role(self):
        fullname = f"{self.project}-{self.name}-{self.stage}"
        role = self.iam.create_role(
                Path=f"/{self.project}/",
                RoleName=fullname,
                AssumeRolePolicyDocument=json.dumps(trust)
                )
        return role

