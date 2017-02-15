from pytest import raises
from .messages import Message
from .syx import read_syx_file, write_syx_file


def test_read(tmpdir):
    path = tmpdir.join("test.syx").strpath
    msg = Message('sysex', data=(1, 2, 3))


    with open(path, 'wb') as outfile:
        outfile.write(msg.bin())


    assert read_syx_file(path) == [msg]


    with open(path, 'wt') as outfile:
        outfile.write(msg.hex())
    assert read_syx_file(path) == [msg]


    with open(path, 'wt') as outfile:
        outfile.write('NOT HEX')
    with raises(ValueError):
        read_syx_file(path)


def test_handle_any_whitespace(tmpdir):
    path = tmpdir.join("test.syx").strpath

    with open(path, 'wt') as outfile:
        outfile.write('F0 01 02 \t F7\n   F0 03 04 F7\n')
    assert read_syx_file(path) == [Message('sysex', data=[1, 2]),
                                   Message('sysex', data=[3, 4])]


def test_write(tmpdir):
    # p = tmpdir.mkdir("sub").join("hello.txt")
    path = tmpdir.join("test.syx").strpath
    msg = Message('sysex', data=(1, 2, 3))


    write_syx_file(path, [msg])
    with open(path, 'rb') as infile:
        assert infile.read() == msg.bin()


    write_syx_file(path, [msg], plaintext=True)
    with open(path, 'rt') as infile:
        assert infile.read().strip() == msg.hex()
