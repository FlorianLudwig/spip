#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'pip',
    'pyyaml',
]

test_requirements = [
]

setup(
    name='spip',
    version='0.4.0',
    description="pip <3 dnf/apt-get",
    long_description=readme + '\n\n' + history,
    author="Florian Ludwig",
    author_email='f.ludwig@greyrook.com',
    url='https://github.com/florianludwig/spip',
    packages=[
        'spip',
    ],
    package_dir={'spip':
                 'spip'},
    entry_points={
        'console_scripts': [
            'spip=spip.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords='spip',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
