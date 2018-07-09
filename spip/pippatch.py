import pip._internal.req

def monkeypatch():
    system = System.get_current()

    def install(self, *args, **kwargs):
        pip._internal.req.RequirementSet.install.__doc__

        # run install and remove installed build dependencies afterward
        original_install(self, *args, **kwargs)
        system.cleanup()

    def _prepare_file(self, *args, **kwargs):
        pip._internal.req.RequirementSet._prepare_file.__doc__
        system.install_python_pkg_deps(args[1].name)
        return original_collect(self, *args, **kwargs)

    original_install = pip._internal.req.RequirementSet.install
    pip._internal.req.RequirementSet.install = install

    original_collect = pip._internal.req.RequirementSet._prepare_file
    pip._internal.req.RequirementSet._prepare_file = _prepare_file
