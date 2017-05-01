# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import sys
import subprocess
import platform

import pip.req
import pip.commands.install

logger = logging.getLogger(__name__)


PACKAGES = {
    'cairocffi': {
        'fedora': {
            'collect': ['libffi-devel'],
            'run': ['libffi']
        }
    },
    'pillow': {
        'fedora': {
            'build': ['lcms2-devel', 'zlib-devel', 'libjpeg-turbo-devel', 'freetype-devel', 'openjpeg2-devel', 'libtiff-devel', 'libwebp-devel'],
            'run': ['lcms2', 'zlib', 'libjpeg-turbo', 'freetype', 'openjpeg2', 'libtiff', 'libwebp']
        },
        'ubuntu': {
            'build': ['liblcms2-dev', 'liblz-dev', 'libjpeg-turbo8-dev', 'libfreetype6-dev', 'libopenjpeg-dev', 'libtiff5-dev', 'libwebp-dev'],
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
            'collect': ['git'],
            'build': ['ffmpeg-devel'],
            'run': ['ffmpeg']
        }
    },
    'cryptography': {
        'fedora': {
            'build': ['libffi-devel', 'openssl-devel'],
            'run': ['libffi', 'openssl']
        }
    },
    'lxml': {
        'fedora': {
            'build': ['libxml2-devel', 'libxslt-devel'],
            'run': ['libxml2', 'libxslt']
        }
    }
}

class System(object):
    def __init__(self):
        self.build_packages = set()
        self.run_packages = set()

    @classmethod
    def get_current(cls):
        system = platform.dist()[0]
        if system == 'fedora':
            return Fedora()
        else:
            return Ubuntu()

    def install_python_pkg_deps(self, dep):
        stages = ['build', 'run', 'collect']
        build_packages = set()
        run_packages = set()

        if dep is None:
            # we are installing a directory / file
            #
            # since to reliable determine the package name
            # we need to execute the setup.py we basically are screwed
            # at this poined because the setup.py might have dependencies.
            #
            # For now we don't even try to solve this case.
            return

        # ignore version for now
        if '=' in dep:
            dep = dep[:dep.find('=')]

        package = dep.strip().lower()
        if package in PACKAGES:
            deps = PACKAGES[package][self.name]
            build_packages.update(deps.get('collect', []))
            build_packages.update(deps.get('build', []))
            run_packages.update(deps.get('run', []))

        to_install = set(self.build_system)
        to_install.update(build_packages)
        to_install.update(run_packages)
        self.run_packages.update(run_packages)
        self.build_packages.update(build_packages)
        if to_install:
            self.install(to_install)

    def cleanup(self):
        to_remove = set(self.build_packages).union(self.build_system)
        for pkg in self.initial_packages.union(self.run_packages):
            to_remove.discard(pkg)

        if to_remove:
            self.remove(to_remove)

    def install(self, packages):
        """install given packages"""
        raise NotImplementedError()

    def remove(self, packages):
        """remove packages if not already installed on pip startup"""
        raise NotImplementedError()


class Fedora(System):
    build_system = ['redhat-rpm-config', 'gcc', 'python-devel']
    name = 'fedora'

    def __init__(self):
        super(Fedora, self).__init__()

        global dnf
        import dnf
        self.base = None
        self._get_dnf()
        self.initial_packages = self.installed_packages

    def _get_dnf(self):
        if self.base is not None:
            self.base.close()
        self.base = dnf.Base()
        self.base.conf.assumeyes = True
        self.base.read_all_repos()
        self.base.fill_sack(load_system_repo='auto')
        installed = self.base.sack.query().installed()
        self.installed_packages = set(p.name for p in installed.run())

    def install(self, packages):
        for pkg in packages:
            if pkg not in self.installed_packages:
                self.base.install(pkg)
        self.base.resolve()
        self.base.download_packages(self.base.transaction.install_set)
        self.base.do_transaction()
        self._get_dnf()

    def remove(self, packages):
        for pkg in packages:
            self.base.remove(pkg)

        # ensure we are not losing runtime packages
        for pkg in self.run_packages:
            self.base.install(pkg)

        self.base.resolve()
        self.base.do_transaction()
        self._get_dnf()


class Ubuntu(System):
    build_system = ['build-essential']
    name = 'ubuntu'


def monkeypatch():
    system = System.get_current()

    def install(self, *args, **kwargs):
        pip.req.RequirementSet.install.__doc__

        # run install and remove installed build dependencies afterward
        original_install(self, *args, **kwargs)
        system.cleanup()

    def _prepare_file(self, *args, **kwargs):
        pip.req.RequirementSet._prepare_file.__doc__
        system.install_python_pkg_deps(args[1].name)
        return original_collect(self, *args, **kwargs)

    original_install = pip.req.RequirementSet.install
    pip.req.RequirementSet.install = install

    original_collect = pip.req.RequirementSet._prepare_file
    pip.req.RequirementSet._prepare_file = _prepare_file
