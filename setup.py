import glob
import os
from setuptools import setup

version = os.environ.get('RELEASE_VERSION', '99.0.0.dev0')

setup(
    name='metadb',
    version=version,
    author='UPF-MTG',
    author_email='',
    packages=['metadb'],
    scripts=[x for x in glob.glob('bin/*.py') if x != 'bin/__init__.py'],
    license='LICENSE.txt',
    description='metadata storage db',
    install_requires=[
        "SQLAlchemy == 1.0.8"
    ],
    zip_safe=False
)
