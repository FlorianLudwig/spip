import sys
import subprocess

import click

from . import install

# import spip.install

@click.group()
def main():
    pass


# @main.command()
# context_settings=dict(
#     allow_extra_args=True,
# ))
# @click.option('--pip', )
# @click.argument('install_args', nargs=-1, type=click.UNPROCESSED)
# def install(install_args):
#     system = spip.install.System.get_current()
#     print(install_args)
    # with open(sys.argv[1]) as f:
    #     for line in f:
    #         if line.startswith('#'):
    #             continue
    #
    #         line = line.split('==')[0]
    #         system.install_python_pkg_deps(line)
    #
    # subprocess.Popen(['pip', 'install', '-r', sys.argv[1]]).wait()
    #
    # system.cleanup()
    

def read_requirements(path):
    with open(path) as f:
        for line in f:
            line = line.split('#')[0]
            line = line.strip()
            if line:
                yield line


@main.command()
@click.argument('install_args', nargs=-1, type=click.UNPROCESSED)
def sinstall(install_args):
    system = install.System.get_current()
    mode = None
    for arg in install_args:
        if arg.startswith('-'):
            mode = arg.lstrip('-')
            continue
        
        if mode == 'r':
            for req in read_requirements(arg):
                system.install_python_pkg_deps(req)
        else:
            system.install_python_pkg_deps(arg)
        mode = None
    


if __name__ == '__main__':
    main()
