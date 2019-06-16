from hatano.util import ZipSrc
from hatano.util import Conf
from hatano.lmbda import Lambda

import boto3


def update(args):
    stage = args.stage
    c = Conf()
    project, stg_conf = c.get_stage(stage)

    for fn in stg_conf.get("functions", []):
        lmb = Lambda(stage, fn)
        lmb.update_function()

