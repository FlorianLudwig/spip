# -*- coding: utf-8 -*-
import logging
import sys
import subprocess
import platform

import pip.req
import pip.commands.install

logger = logging.getLogger(__name__)

# install system PACKAGES for python packages
build_system = ['redhat-rpm-config', 'gcc', 'python-devel']
build_system_ubuntu = ['build-essential']


PACKAGES = {
    'pillow': {
        'fedora': {
            'build': build_system + ['lcms2-devel', 'zlib-devel', 'libjpeg-turbo-devel', 'freetype-devel', 'openjpeg2-devel', 'libtiff-devel', 'libwebp-devel'],
            'run': ['lcms2', 'zlib', 'libjpeg-turbo', 'freetype', 'openjpeg2', 'libtiff', 'libwebp']
        },
        'ubuntu': {
            'build': build_system_ubuntu + ['liblcms2-dev', 'liblz-dev', 'libjpeg-turbo8-dev', 'libfreetype6-dev', 'libopenjpeg-dev', 'libtiff5-dev', 'libwebp-dev'],
            'run': ['liblcms2-2']
        }
    },
    'gitpython': {
        'fedora': {
            'run': ['git']
        }
    },
    'av': {
        'fedora': {
            'run': ['git'],
            'build': ['ffmpeg-devel']
        }
    },
    'cryptography': {
        'fedora': {
            'build': ['libffi-devel', 'openssl-devel']
        }
    },
    'lxml': {
        'fedora': {
            'build': ['libxml2-devel', 'libxslt-devel']
        }
    }
}

def collect_dependencies(python_packages):
    """install system package dependencies"""
    system = platform.dist()[0]
    build_packages = set()
    run_packages = set()
    for dep in python_packages:
        # ignore version for now
        if '=' in dep:
            dep = dep[:dep.find('=')]

        package = dep.strip().lower()
        if package in PACKAGES:
            deps = PACKAGES[package][system]
            build_packages.update(deps.get('build', []))
            run_packages.update(deps.get('run', []))

    return build_packages.union(run_packages)


def install_packages(packages):
    system = platform.dist()[0]
    if system == 'fedora':
        cmd = ['dnf', 'install', '-y']
    elif system in ('ubuntu', 'debian'):
        cmd = ['apt-get', 'install', '-y']

    cmd += packages
    subprocess.check_call(cmd)


def monkeypatch():
    def install(self, *args, **kwargs):
        pip.req.RequirementSet.__doc__

        # collecting system dependencies
        py_pkgs = [pkg.name for pkg in self._to_install()]
        sys_pkgs = collect_dependencies(py_pkgs)

        if sys_pkgs:
            logger.info('installing system packages: %s', ' '.join(sys_pkgs))
            install_packages(sys_pkgs)

        original_install(self, *args, **kwargs)

    original_install = pip.req.RequirementSet.install
    pip.req.RequirementSet.install = install
