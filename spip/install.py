# -*- coding: utf-8 -*-
import logging
import sys
import subprocess
import platform

import pip.req
import pip.commands.install

logger = logging.getLogger(__name__)


PACKAGES = {
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
            'build': ['git', 'ffmpeg-devel'],
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
    @classmethod
    def get_current(cls):
        system = platform.dist()[0]
        if system == 'fedora':
            return Fedora()
        else:
            return Ubuntu()

    def install_python_pkg_deps(self, python_packages):
        build_packages = set()
        run_packages = set()
        for dep in python_packages:
            # ignore version for now
            if '=' in dep:
                dep = dep[:dep.find('=')]

            package = dep.strip().lower()
            if package in PACKAGES:
                deps = PACKAGES[package][self.name]
                build_packages.update(deps.get('build', []))
                run_packages.update(deps.get('run', []))

        to_install = set(self.build_system)
        to_install.update(build_packages)
        to_install.update(run_packages)
        self.build_packages = build_packages
        if to_install:
            self.install(to_install)

    def cleanup(self):
        to_remove = set(self.build_packages).union(self.build_system)
        for pkg in self.installed_packages:
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
        global dnf
        import dnf
        self.base = None
        self._get_dnf()
        installed = self.base.sack.query().installed()
        self.installed_packages = [p.name for p in installed.run()]

    def _get_dnf(self):
        if self.base is not None:
            self.base.close()
        self.base = dnf.Base()
        self.base.conf.assumeyes = True
        self.base.read_all_repos()
        self.base.fill_sack(load_system_repo='auto')

    def install(self, packages):
        for pkg in packages:
            self.base.install(pkg)
        self.base.resolve()
        self.base.download_packages(self.base.transaction.install_set)
        self.base.do_transaction()
        self._get_dnf()

    def remove(self, packages):
        for pkg in packages:
            self.base.remove(pkg)
        self.base.resolve()
        self.base.do_transaction()
        self._get_dnf()


class Ubuntu(System):
    build_system = ['build-essential']
    name = 'ubuntu'



def monkeypatch():
    def install(self, *args, **kwargs):
        pip.req.RequirementSet.__doc__

        # collecting system dependencies
        py_pkgs = [pkg.name for pkg in self._to_install()]

        system = System.get_current()
        system.install_python_pkg_deps(py_pkgs)
        original_install(self, *args, **kwargs)
        system.cleanup()

    original_install = pip.req.RequirementSet.install
    pip.req.RequirementSet.install = install
