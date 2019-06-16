from hatano.errors import HatanoError

import boto3
import zipfile
import shutil
import subprocess as sp
import os
import random
import string
import sys
import yaml

conf_file = './hatano_settings.yml'
region = boto3.session.Session().region_name


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
        #if not os.path.isdir(src):
        #    return False
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


def temp_name(ext=""):
    allow = string.ascii_lowercase + string.ascii_uppercase
    lets = [random.choice(allow) for _ in range(8)]
    return ''.join(lets) + f"{ext}"


def get_stage(stage):
    if not os.path.isfile(conf_file):
        raise HatanoError(f"No {conf_file} found")

    with open(conf_file) as f:
        conf = yaml.safe_load(f.read())
    project = conf.get("project", "")
    stages = conf.get("stages", {})
    
    return project, stages.get(stage, {})


