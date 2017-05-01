import os

def test_install_pillow():
    # case should not matter
    assert os.system('spip install Pillow') == 0
