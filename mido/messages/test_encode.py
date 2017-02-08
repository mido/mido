from .specs import SPEC_BY_STATUS
from .encode import encode_message
from .decode import decode_message

def test_encode_decode_all():
    """Encode and then decode all messages on all channels.

    Each data byte is different so that the test will fail if the
    bytes are swapped during encoding or decoding.
    """

    data_bytes = [1, 2, 3]
    
    for status_byte, spec in SPEC_BY_STATUS.items():
        if status_byte == 0xf0:
            msg_bytes = [0xf0] + data_bytes + [0xf7]
        else:
            msg_bytes = [status_byte] + data_bytes[:spec['length'] - 1]
            
        assert encode_message(decode_message(msg_bytes)) == msg_bytes
