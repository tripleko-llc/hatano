from hatano.util import Conf
from hatano.iam import IamRole
from hatano.lmbda import Lambda
from hatano.apigateway import RestApi
from hatano.acm import Cert
from hatano.route53 import Route53
from hatano.s3 import S3

import os


class Conductor:
    def __init__(self, args):
        self.conf = Conf().read()
        self.stage = args.stage
        self.project = self.conf["project"]
        stages = self.conf.get("stage", {})
        self.stg_conf = stages.get(self.stage, {})

        self.functions = []
        if args.function:
            self.functions = [args.function]
        else:
            self.functions = self.conf.get("function", {}).keys()

        self.api = None
        self.s3_path = self.stg_conf.get("bucket")
        self.s3 = None
        self.certified = False
        self.domain = ""
        if self.s3_path:
            self.s3 = S3(self.s3_path, self.project, self.stage)

        if not self.stg_conf:
            raise Exception(f"Stage {stage} not defined")

    def update_funcs(self):
        for fname in self.functions:
            print(f"Updating function {fname}")
            self.update_func(fname)

    def update_func(self, name):
        fn = self.conf["function"][name]
        fn["name"] = name
        lmb = Lambda(self.stage, fn)
        lmb.update_function()

    def deploy_all(self):
        self.deploy_s3()
        self.create_api()
        self.deploy_funcs()
        self.deploy_api()
        self.deploy_domain()
        self.finish()

    def deploy_s3(self):
        if self.s3:
            try:
                print(f"Creating s3 bucket {s3.name()}")
                self.s3.create()
            except Exception as e:
                print(f"Failed: {e}")
            
            try:
                print(f"Uploading contents of {self.s3_path} to s3 bucket {s3.name()}")
                self.s3.upload_all()
            except Exception as e:
                print(f"Failed: {e}")

    def create_api(self):
        # Create REST API
        print(f"Creating REST API for {self.project}")
        self.api = RestApi(self.project)

    def deploy_api(self):
        # Deploy the API
        print(f"Deploying API stage {self.stage}")
        self.api.deploy(self.stage)

    def deploy_funcs(self):
        # Create each function and link to and endpoint
        for fname in self.functions:
            print(f"Deploying function {fname}")
            self.deploy_func(fname)

    def deploy_func(self, name):
        if not self.api:
            self.api = RestApi(self.stage)

        fn = self.conf["function"][name]
        fn["name"] = name
        fn["runtime"] = self.conf["runtime"]
        env = fn.get("env", {})
        if self.s3:
            env["S3_BUCKET"] = self.s3.name()

        fullname = f"{self.project}-{name}-{self.stage}"
    
        http_method = fn.get("method", "")
        http_path = fn.get("path")
    
        # Create iam role
        print("  - Creating IAM role")
        iam = IamRole(self.stage, fn)
        role = iam.lambda_role()
        iam.put_custom_policy()
        role_arn = role['Role']['Arn']
    
        # Create lambda
        print("  - Creating lambda")
        lmb = Lambda(self.stage, fn, role_arn=role_arn, env=env)
        func = lmb.create_function()
        func_arn = func['FunctionArn']
        lmb.add_permission("apigateway", "InvokeFunction")
    
        # Create resource and endpoint
        print("  - Linking endpoint to lambda")
        resource = self.api.create_resource(http_path)
        resource.link_endpoint(http_method, func_arn)

    def deploy_domain(self):
        domain = self.stg_conf.get("domain")
        cert = self.stg_conf.get("cert")
        self.domain = domain

        # Create domain name
        if domain and cert:
            print(f"Creating custom domain name {domain}")
            cert = Cert(cert)
            r = self.api.create_domain(domain, cert.arn)
            cloudfront = r['distributionDomainName']
            r53 = Route53()

            print("Creating cname record")
            r53.add_cname_record(domain, cloudfront)
            self.api.create_base_path_mapping(domain, "", stage)
            self.certified = True

    def finish(self):
        # Output
        print("-"*20)
        print("Project:", self.project)
        print("Stage:", self.stage)
        perm_url = f"{self.api.url}/{self.stage}"
        if self.certified:
            print(f"https://{self.domain} ({perm_url})")
        else:
            print(perm_url)
