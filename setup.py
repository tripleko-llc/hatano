from setuptools import setup

import os

here = os.path.abspath(os.path.dirname(__file__))
info = {}
pkg_name = "hatano"

with open(
        os.path.join(here, pkg_name, "__init__.py")) as f:
    exec(f.read(), None, info)

with open("requirements.txt") as f:
    pkgs = [line.strip() for line in f]

setup(name=pkg_name,
        version=info['__version__'],
        description=info['__description__'],
        author=info['__author__'],
        author_email=['__author_email__'],
        install_requires=pkgs,
        entry_points={
            'console_scripts': [
                'hatano = hatano:handle',
                'htn = hatano:handle'
                ]
            }
        )

