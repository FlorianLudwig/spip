import os
import spip.install

def test_install_pillow():
    # AV needs git during setup phase and therefor is an intersting
    # test case.
    system = spip.install.System.get_current()
    package_data = spip.install.PACKAGES['pillow'][system.name]

    assert package_data['run'][0] not in system.installed_packages
    assert package_data['build'][0] not in system.installed_packages

    del system
    assert os.system('spip install Pillow') == 0
    system = spip.install.System.get_current()

    # build time requirements should be removed after install completes
    assert package_data['build'][0] not in system.installed_packages

    # runtime requirements should be present
    assert package_data['run'][0] in system.installed_packages

    import PIL.Image
