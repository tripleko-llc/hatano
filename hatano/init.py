from hatano.util import Conf
from hatano.errors import HatanoError

import sys


def init(args):
    stage = args.stage
    c = Conf()
    if not c.exists():
        try:
            proj_name = input("Project name: ")
        except KeyboardInterrupt:
            sys.exit("Aborted")
        conf = {
                "project": proj_name,
                "stages": {}
                }
        c.write(conf)

    conf = c.read()
    if stage in conf.get("stages", {}):
        print(f"Stage {stage} already exists")
        return

    conf["stages"][stage] = {
            "funtions": [],
            "source": ""}
    c.write(conf)

    #if not os.path.isfile(conf_file):
    #    # New file
    #    conf = {}
    #else:
    #    with open(conf_file) as f:
    #        conf = yaml.safe_load(f.read())
    #    if stage in conf:
    #        print("Stage already exists:", stage)
    #        return
    #    conf[stage] = {
    #            "runtime": "",
    #            "functions": []
    #            }

    #with open(conf_file, 'w') as f:
    #    yaml.dump(conf, f)



