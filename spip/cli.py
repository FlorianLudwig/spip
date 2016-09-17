import spip.install

def main():
    spip.install.monkeypatch()

    import pip
    pip.main()


if __name__ == '__main__':
    main()
