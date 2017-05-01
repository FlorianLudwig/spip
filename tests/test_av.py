import os
import spip.install

def test_install_av():
    # AV needs git during setup phase and therefor is an intersting
    # test case.
    system = spip.install.System.get_current()
    package_data = spip.install.PACKAGES['av'][system.name]

    # git should not be installed
    assert 'git' not in system.initial_packages
    assert package_data['run'][0] not in system.initial_packages
    assert package_data['build'][0] not in system.initial_packages

    del system
    assert os.system('spip install av') == 0
    system = spip.install.System.get_current()

    # git and build time requirements should be removed after install completes
    assert 'git' not in system.initial_packages
    assert package_data['build'][0] not in system.initial_packages

    # runtime requirements should be present
    assert package_data['run'][0] in system.initial_packages

    import av


def test_install_av_and_gitpython():
    # git python has a runtime dependency on git
    # while av a build time.
    # installing both at the same time should result in git staying available
    # after install
    system = spip.install.System.get_current()
    package_data = spip.install.PACKAGES['av'][system.name]

    # git should not be installed
    assert 'git' not in system.initial_packages

    del system
    assert os.system('spip install av gitpython') == 0
    system = spip.install.System.get_current()

    assert 'git' in system.initial_packages
