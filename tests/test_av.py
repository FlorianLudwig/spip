import os
import spip.install

def test_install_av():
    # AV needs git during setup phase and therefor is an intersting
    # test case.
    system = spip.install.System.get_current()
    package_data = spip.install.PACKAGES['pillow'][system.name]


    # git should not be installed
    assert 'git' not in system.initial_packages
    assert package_data['run'][0] not in system.initial_packages
    assert package_data['build'][0] not in system.initial_packages

    del system
    assert os.system('spip install Pillow') == 0
    system = spip.install.System.get_current()

    # git and build time requirements should be removed after install completes
    assert 'git' not in system.initial_packages
    assert package_data['build'][0] not in system.initial_packages

    # runtime requirements should be present
    assert package_data['run'][0] in system.initial_packages
