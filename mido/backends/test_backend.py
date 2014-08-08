from pytest import raises
from .backend import Backend, _import_module

def test_import_module():
    _import_module('sys')
    _import_module('os.path')
    with raises(ImportError):
        _import_module('!!!!!!!!!')

def test_split_api():
    backend = Backend('test')
    assert backend.name == 'test'
    assert backend.api is None

    backend = Backend('test/ALSA')
    assert backend.name == 'test'
    assert backend.api == 'ALSA'
