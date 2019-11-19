# built-in
from io import open
from os import path

# external
from setuptools import setup


here = path.abspath(path.dirname(__file__))
root = path.dirname(path.dirname(here))
with open(path.join(root, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


# TODO: more info

setup(
    name='dephell',
    version='0.2.0',
    description='Dependency resolution for Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://dephell.org/',
    author='orsinium',

    packages=[],
    install_requires=[
        'attrs',
        'cached_property',
        'packaging',
        'requests',

        'libtest',
    ],
    dependency_links=[
        'git+https://github.com/gwtwod/poetrylibtest#egg=libtest-0.1.0',
    ],
    extras_require=dict(
        windows=['colorama'],
    ),

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
    ],
    keywords='sample setuptools development',
    project_urls={  # Optional
        'Source': 'https://github.com/dephell/dephell/',
    },
    entry_points={
        'console_scripts': ['dephell = dephell.cli:entrypoint'],
    },
)
