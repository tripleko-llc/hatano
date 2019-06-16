def init(args):
    stage = args.stage
    stg_conf = get_stage(stage)

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



