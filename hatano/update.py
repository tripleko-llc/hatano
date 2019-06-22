from hatano.util import ZipSrc
from hatano.util import Conf
from hatano.lmbda import Lambda

import boto3


def update(args):
    stage = args.stage
    c = Conf()
    conf = c.read()

    if args.function:
        functions = [args.function]

    else:
        functions = conf.get("function", {}).keys()

    for fname in functions:
        print(f"Updating function {fname}")
        fn = conf["function"][fname]
        fn["name"] = fname

        lmb = Lambda(stage, fn)
        lmb.update_function()

