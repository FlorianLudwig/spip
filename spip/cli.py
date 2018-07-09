import sys
import subprocess

import click
import dparse 

import spip.install


@click.group()
def main():
    pass


@main.command(context_settings=dict(
    allow_extra_args=True,
))
@click.option('--pip', )
@click.argument('install_args', nargs=-1, type=click.UNPROCESSED)
def install(install_args):
    raise NotImplementedError()
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
    file_content = open(path).read()
    parsed_req = dparse.parse(file_content, file_type="requirements.txt")
    return parsed_req.dependencies


@main.command()
@click.option('--requirement', '-r', multiple=True, type=click.Path(exists=True))
@click.argument('install_args', nargs=-1, type=click.UNPROCESSED)
def sinstall(requirement, install_args):
    system = spip.install.System.get_current()
    
    for req in requirement:
        for dep in read_requirements(req):
            system.install_python_pkg_deps(dep)
            
    for dep in install_args:
        pkg = dparse.parser.RequirementsTXTLineParser.parse(dep)
        system.install_python_pkg_deps(pkg)
    

if __name__ == '__main__':
    main()
