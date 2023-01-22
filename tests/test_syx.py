from pytest import raises
from mido.messages import Message
from mido.syx import read_syx_file, write_syx_file


def test_write(tmpdir):
    path = tmpdir.join("test.syx").strpath
    syx = Message('sysex', data=(1, 2, 3))
    eox = Message('end_of_exclusive')

    write_syx_file(path, [syx, eox])
    with open(path, 'rb') as infile:
        assert infile.read() == bytes(syx.bin() + eox.bin())

    write_syx_file(path, [syx, eox], plaintext=True)
    with open(path, 'rt') as infile:
        assert infile.read().strip() == syx.hex() + ' ' + eox.hex()


def test_read(tmpdir):
    path = tmpdir.join("test.syx").strpath
    syx = Message('sysex', data=(1, 2, 3))
    eox = Message('end_of_exclusive')

    with open(path, 'wb') as outfile:
        outfile.write(syx.bin() + eox.bin())

    assert read_syx_file(path) == [syx, eox]

    with open(path, 'wt') as outfile:
        outfile.write(syx.hex() + eox.hex())

    assert read_syx_file(path) == [syx, eox]

    with open(path, 'wt') as outfile:
        outfile.write('NOT HEX')

    with raises(ValueError):
        read_syx_file(path)


def test_handle_any_whitespace(tmpdir):
    path = tmpdir.join("test.syx").strpath

    with open(path, 'wt') as outfile:
        outfile.write('F0 01 02 \t F7\n   F0 03 04 F7\n')
    assert read_syx_file(path) == [Message('sysex', data=[1, 2]), Message('end_of_exclusive'),
                                   Message('sysex', data=[3, 4]), Message('end_of_exclusive')]
