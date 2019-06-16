from hatano.deploy import deploy
from hatano.update import update
from hatano.delete import delete
from hatano.init import init

import argparse

__version__ = '1.0.0'
__author__ = 'Jared Nishikawa'
__author_email__ = 'jared@tripleko.com'
__description__ = 'Microframework for Lambda/API gateway'


def handle():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="action")

    init_parser = subparsers.add_parser("init")
    deploy_parser = subparsers.add_parser("deploy")
    update_parser = subparsers.add_parser("update")
    delete_parser = subparsers.add_parser("delete")

    parser.add_argument("stage")

    args = parser.parse_args()

    if args.action == "init":
        pass

    elif args.action == "deploy":
        deploy(args)

    elif args.action == "update":
        update(args)

    elif args.action == "delete":
        delete(args)

    elif args.action == "init":
        init(args)
