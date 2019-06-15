import argparse
import json
import os
import yaml
import boto3
import zipfile
import random
import string
import time
import shutil
import subprocess as sp

__version__ = '1.0.0'
__author__ = 'Jared Nishikawa'
__author_email__ = 'jared@tripleko.com'
__description__ = 'Microframework for Lambda/API gateway'

conf_file = './hatano_settings.yml'

trust = {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}



def handle():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="action")

    init_parser = subparsers.add_parser("init")
    deploy_parser = subparsers.add_parser("deploy")
    update_parser = subparsers.add_parser("update")
    delete_parser = subparsers.add_parser("delete")

    init_parser.add_argument("stage")
    deploy_parser.add_argument("stage")
    update_parser.add_argument("stage")
    delete_parser.add_argument("stage")

    args = parser.parse_args()

    if args.action == "init":
        pass

    elif args.action == "deploy":
        handle_deploy(args)

    elif args.action == "update":
        handle_update(args)

    elif args.action == "delete":
        handle_delete(args)


def get_stage(stage):
    if not os.path.isfile(conf_file):
        return {}
    with open(conf_file) as f:
        conf = yaml.safe_load(f.read())
    project = conf.get("project", "")
    stages = conf.get("stages", {})
    
    return project, stages.get(stage, {})


#def handle_init(args):
#    stage = args.stage
#    stg_conf = get_stage(stage)
#
#    if not os.path.isfile(conf_file):
#        # New file
#        conf = {}
#    else:
#        with open(conf_file) as f:
#            conf = yaml.safe_load(f.read())
#        if stage in conf:
#            print("Stage already exists:", stage)
#            return
#        conf[stage] = {
#                "runtime": "",
#                "functions": []
#                }
#
#    with open(conf_file, 'w') as f:
#        yaml.dump(conf, f)


def handle_deploy(args):
    stage = args.stage
    project, stg_conf = get_stage(stage)
    runtime = stg_conf.get("runtime", "")
    source = stg_conf.get("source", "")

    if not (runtime or source or project):
        print("Invalid runtime, source, or project")
        return

    lda = boto3.client('lambda')
    iam = boto3.client('iam')


    for fn in stg_conf.get("functions", []):
        name = fn.get("name", "")
        fullname = f"{project}-{name}-{stage}"
        handler = fn.get("handler", "")
        if not (name or handler):
            print("Invalid name or handler")
            print(name)
            print(handler)
            continue

        role = iam.create_role(
                Path=f"/{project}/",
                RoleName=fullname,
                AssumeRolePolicyDocument=json.dumps(trust)
                )
        role_arn = role['Role']['Arn']
        time.sleep(20)

        #zip_name = zip_src(source)
        with ZipSrc(source, stage) as zip_name:
            lda.create_function(
                    FunctionName=fullname,
                    Handler=handler,
                    Runtime=runtime,
                    Role=role_arn,
                    Code={
                        'ZipFile': open(zip_name, 'rb').read()}
                    )
        print("Success creating", fullname)


def handle_update(args):
    stage = args.stage
    project, stg_conf = get_stage(stage)
    runtime = stg_conf.get("runtime", "")
    source = stg_conf.get("source", "")

    if not (runtime or source or project):
        print("Invalid runtime, source, or project")
        return

    lda = boto3.client('lambda')

    for fn in stg_conf.get("functions", []):
        name = fn.get("name", "")
        fullname = f"{project}-{name}-{stage}"
        handler = fn.get("handler", "")
        if not (name or handler):
            print("Invalid name or handler")
            print(name)
            print(handler)
            continue

        lda.update_function_configuration(
                FunctionName=fullname,
                Handler=handler)

        with ZipSrc(source, stage) as zip_name:
            lda.update_function_code(
                    FunctionName=fullname,
                    ZipFile=open(zip_name, 'rb').read()
                    )
        print("Success updating", fullname)

class ZipSrc:
    def __init__(self, src, stage):
        self.src = src
        self.stage = stage
        self.name = ""

    def __enter__(self):
        tmp_dir = '.' + temp_name()
        self.tmp_dir = tmp_dir
        shutil.copytree(self.src, tmp_dir)
        cmd = f"pip install -r requirements-{self.stage}.txt"\
              f" -t {tmp_dir} -q"
        sp.call(cmd.split())

        src = tmp_dir
        if not os.path.isdir(src):
            return False
        head = f"{src}{os.path.sep}"
        zip_name = temp_name('.zip')
        zf = zipfile.ZipFile(zip_name, 'x')
        for dirname,subdirs,fnames in os.walk(src):
            for name in subdirs+fnames:
                zpath = os.path.join(dirname, name)
                path = zpath
                if path.startswith(head):
                    path = path[len(head):]
                zf.write(zpath, path)
        zf.close()
        self.name = zip_name
        return zip_name

    def __exit__(self, typ, value, traceback):
        if self.name and os.path.isfile(self.name):
            try:
                os.remove(self.name)
            except:
                pass
            try:
                shutil.rmtree(self.tmp_dir)
            except:
                pass

def zip_src(src):
    if not os.path.isdir(src):
        return False
    head = f"{src}{os.path.sep}"
    name = temp_name('.zip')
    zf = zipfile.ZipFile(name, 'x')
    for dirname,subdirs,fnames in os.walk(src):
        for name in subdirs+fnames:
            zpath = os.path.join(dirname, name)
            path = zpath
            if path.startswith(head):
                path = path[len(head):]
            zf.write(zpath, path)
    zf.close()
    return name


def temp_name(ext=""):
    allow = string.ascii_lowercase + string.ascii_uppercase
    lets = [random.choice(allow) for _ in range(8)]
    return ''.join(lets) + f"{ext}"


def handle_delete(args):
    stage = args.stage
    project, stg_conf = get_stage(stage)
    runtime = stg_conf.get("runtime", "")
    source = stg_conf.get("source", "")

    if not (runtime or source or project):
        print("Invalid runtime, source, or project")
        return

    lda = boto3.client('lambda')
    iam = boto3.client('iam')
    for fn in stg_conf.get("functions", []):
        name = fn.get("name", "")
        fullname = f"{project}-{name}-{stage}"
        handler = fn.get("handler", "")
        if not (name or handler):
            print("Invalid name or handler")
            print(name)
            print(handler)
            continue
        try:
            lda.delete_function(FunctionName=fullname)
        except:
            pass

        try:
            iam.delete_role(RoleName=fullname)
        except:
            pass
   



