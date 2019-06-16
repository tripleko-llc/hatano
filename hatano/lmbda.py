from hatano.errors import HatanoError
from hatano.util import ZipSrc
from hatano.util import Conf

import boto3

class Lambda:
    def __init__(self, stage, fnargs, role_arn=""):
        c = Conf()
        self.project, stg_conf = c.get_stage(stage)
        self.source = stg_conf.get("source")
        self.stage = stage
        self.role_arn = role_arn
        self.name = fnargs.get("name")
        self.handler = fnargs.get("handler")
        self.runtime = fnargs.get("runtime")
        self.lda = boto3.client('lambda')
        self.fullname = f"{self.project}-{self.name}-{self.stage}"

    def _create_function(self, zip_name):
        if not self.name:
            raise HatanoError("Function has no name")
    
        if not self.handler:
            raise HatanoError("Function has no handler")
    
        if not self.runtime:
            raise HatanoError("Function has no runtime")
    
        func = self.lda.create_function(
                FunctionName=self.fullname,
                Handler=self.handler,
                Runtime=self.runtime,
                Role=self.role_arn,
                Code={
                    'ZipFile': open(zip_name, 'rb').read()}
                )
        return func

    def create_function(self):
        with ZipSrc(self.source, self.stage) as zip_name:
            for attempt in range(5):
                try:
                    func = self._create_function(zip_name)
                    break
                except Exception as e:
                    pass
            else:
                sys.exit("Max retries exceeded")
        return func

    def update_function(self):
        with ZipSrc(self.source, self.stage) as zip_name:
            self.lda.update_function_code(
                    FunctionName=self.fullname,
                    ZipFile=open(zip_name, 'rb').read()
                    )

    def add_permission(self, principal):
        fullname = f"{self.project}-{self.name}-{self.stage}"
        self.lda.add_permission(
                FunctionName=fullname,
                StatementId=fullname + f"-{principal}",
                Action="lambda:InvokeFunction",
                Principal=f"{principal}.amazonaws.com"
                )


