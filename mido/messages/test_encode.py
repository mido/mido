from .specs import SPEC_BY_STATUS
from .encode import encode_msg
from .decode import decode_msg

def test_encode_decode_all():
    """Encode and then decode all messages on all channels.

    First with all data bytes 0x00, then 0x7f (min and max values).
    """

    for data_byte in [0x00, 0x7f]:
        for status_byte, spec in SPEC_BY_STATUS.items():
            if status_byte == 0xf0:
                msg_bytes = [0xf0, data_byte, 0xf7]
            else:
                msg_bytes = [status_byte] + [data_byte] * (spec['length'] - 1)

            assert encode_msg(decode_msg(msg_bytes)) == msg_bytes
