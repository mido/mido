from pytest import raises
from .messages import Message
from .syx import read_syx_file, write_syx_file

def test_read(tmpdir):
    # p = tmpdir.mkdir("sub").join("hello.txt")
    path = tmpdir.join("test.syx").strpath

    message = Message('sysex', data=(1, 2, 3))

    with open(path, 'wb') as outfile:
        outfile.write(message.bin())
    assert read_syx_file(path) == [message]

    with open(path, 'wt') as outfile:
        outfile.write(message.hex())
    assert read_syx_file(path) == [message]

    with open(path, 'wt') as outfile:
        outfile.write('NOT HEX')
    with raises(ValueError):
        read_syx_file(path)

def test_write(tmpdir):
    # p = tmpdir.mkdir("sub").join("hello.txt")
    path = tmpdir.join("test.syx").strpath

    message = Message('sysex', data=(1, 2, 3))

    write_syx_file(path, [message])
    with open(path, 'rb') as infile:
        assert infile.read() == message.bin()

    write_syx_file(path, [message], plaintext=True)
    with open(path, 'rt') as infile:
        assert infile.read().strip() == message.hex()
