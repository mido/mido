import os
import types
import importlib

class Backend(object):
    # Todo: doc strings.
    # Todo: add load() and unload() methods.
    # Todo: call an exit() function on the module or something when
    #       it is unloaded?

    def __init__(self, module, on_demand=False, use_environ=False):
        self.use_environ = use_environ

        if isinstance(module, types.ModuleType):
            self.path = module.__name__
            self.module = module
        else:
            self.path = module
            self.module = None
            if not on_demand:
                self._import()

    def _import(self):
        if self.module is None:
            self.module = importlib.import_module(self.path)

    def _env(self, name):
        if self.use_environ:
            return os.environ.get(name)
        else:
            return None

    def __getattr__(self, name):
        self._import()
        if name in ['Input', 'Output', 'IOPort', 'get_devices']:
            return getattr(self.module, name)
        else:
            raise AttributeError(name)

    def open_input(self, name=None, **kwargs):
        """Open an input port.

        If the environment variable MIDO_DEFAULT_INPUT is set,
        if will override the default port.
        """
        self._import()
        if name is None:
            name = self._env('MIDO_DEFAULT_INPUT')
        return self.module.Input(name, **kwargs)

    def open_output(self, name=None, **kwargs):
        """Open an output port.
        
        If the environment variable MIDO_DEFAULT_OUTPUT is set,
        if will override the default port.
        """
        self._import()
        if name is None:
            name = self._env('MIDO_DEFAULT_OUTPUT')
        return self.module.Output(name, **kwargs)

    def open_ioport(self, name=None, **kwargs):
        """Open a port for input and output.

        If the environment variable MIDO_DEFAULT_IOPORT is set,
        if will override the default port.
        """
        self._import()

        if name is None:
            name = self._env('MIDO_DEFAULT_IOPORT')
        if hasattr(self.module, 'IOPort'):
            if name is None:
                name = self._env('MIDO_DEFAULT_IOPORT')
            return self.module.IOPort(name, **kwargs)
        else:
            if name is None:
                # MIDO_DEFAULT_IOPORT overrides the other two variables.
                name = self._env('MIDO_DEFAULT_IOPORT')
                if name is not None:
                    input_name = output_name = name
                else:
                    input_name = self._env('MIDO_DEFAULT_INPUT')
                    output_name = self._env('MIDO_DEFAULT_OUTPUT')
            else:
                input_name = output_name = name

            return ports.IOPort(self.module.Input(input_name, **kwargs),
                                self.module.Output(output_name, **kwargs))

    def get_input_names(self):
        """Return a sorted list of all input port names."""
        self._import()
        devices = self.module.get_devices()
        names = [device['name'] for device in devices if device['is_input']]
        return list(sorted(names))

    def get_output_names(self):
        """Return a sorted list of all output port names."""
        self._import()
        devices = self.module.get_devices()
        names = [device['name'] for device in devices if device['is_input']]
        return list(sorted(names))

    def get_ioport_names(self):
        """Return a sorted list of all I/O port names."""
        self._import()
        return sorted(
            set(self.get_input_names()) & set(self.get_output_names()))        

    def __repr__(self):
        if self.module is None:
            status = 'not loaded'
        else:
            status = 'loaded'

        return '<backend {!r} ({})>'.format(self.path, status)
