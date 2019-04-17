# built-in
from io import open
from os import path

# external
from setuptools import setup


here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


# TODO: more info

setup(
    name='dephell',
    version='0.2.1',
    description='Dependency resolution for Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/orsinium/dephell',
    author='orsinium',

    packages=['dephell'],
    install_requires=[
        'attrs',
        'cached_property',
        'packaging',
        'requests',
    ],
    entry_points={
        'console_scripts': ['dephell = dephell.cli:main'],
    },
)
