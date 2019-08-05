# file : /servers/http2/http2_parser.py

import lib.parser as parser

# Length(24) Type(8) flagss(8) [R(1) StreamIdentifier(31)] FramePayload(Length)
def frame_parser(data):
    R = []
    tmp_data = []
    while True:
        tmp_data = parser.bytes_parse(data, [3, 1, 1, 4])
        payload_and_data = parser.bytes_parse(tmp_data[-1], [int.from_bytes(tmp_data[0], "big")])
        tmp_data = tmp_data[:-1]
        if(tmp_data[1] == b"\x09"):
            R[0] += tmp_data[-1]
        else:
            tmp_data.append(frame_payload_parsers[tmp_data[1]](payload_and_data[0], int.from_bytes(tmp_data[2], "big")))
            R.append(tmp_data)
        if(len(payload_and_data) == 1):
            break
        data = payload_and_data[1]
    return R

# Type 0
# PadLength?(8) Data(*) Padding?(PadLength)
def data_frame_parser(data, flags):
    R = []
    # PADDED
    if(flags & 0x8):
        # tmp_data=[PadLength, Data+Padding]
        tmp_data = (parser.bytes_parse(data, [1]))
        R = parser.bytes_parse(tmp_data[1], [len(tmp_data[1])-tmp_data[0]])
    else:
        R.append(data)
    return R

# Type 1
# PadLength?(8) [E(1) StreamDependency?(31)] Weight?(8) HeaderBlockFragment(*) Padding?(PadLength)
def headers_frame_parser(data, flags):
    #print(data.hex())
    R = []
    tmp_data = []
    # R will... [E+StreamDependency, Weight, HeaderBlockFragment]
    # PADDED
    tmp_data = data
    if(flags & 0x8):
        # tmp_data=[PadLength, Data+Padding]
        tmp_data = (parser.bytes_parse(data, [1]))
        tmp_data = parser.bytes_parse(tmp_data[1], [len(tmp_data[1])-tmp_data[0]])[0]
        #R = [b"\xff\xff\xff\xff", b"\xff",parser.bytes_parse(tmp_data[1], [len(tmp_data[1])-tmp_data[0]])[0]]
        R = [parser.bytes_parse(tmp_data[1], [len(tmp_data[1])-tmp_data[0]])[0]]
    if(flags & 0x20):
        R = parser.bytes_parse(tmp_data, [4, 1])
    return R

# Type 2
def priority_frame_parser(data, flags):
    R = []
    R = parser.bytes_parse(data, [4, 1])
    return R

# Type 3
def rst_stream_frame_parser(data, flags):
    return data

# Type 4
# Identifier(16) Value(32) ... 48bits = 6bytes
def settings_frame_parser(data, flagss):
    R = []
    tmp_data = parser.bytes_parse(data, [2, 4])
    length = int(len(data)/6)
    if(1 < length):
        for _ in range(length):
            R.append([tmp_data[0], tmp_data[1]])
            tmp_data = parser.bytes_parse(tmp_data[-1], [2, 4])
    else:
        R = tmp_data
    return R

# Type 5
# PadLength?(8) R(1) PromisedStreamId(31) HeaderBlockFragment(*) Padding(PadLength)
def push_promise_frame_parser(data, flags):
    R = []
    tmp_data = []
    # R will... [R+PromisedStreamId, HeaderBlockFragment]
    if(flags & 0x8):
        # tmp_data=[PadLength, Data+Padding]
        tmp_data = (parser.bytes_parse(data, [1]))
        tmp_data = parser.bytes_parse(tmp_data[1], [len(tmp_data[1])-tmp_data[0]])[0]
        R = parser.bytes_parse(tmp_data, [4])
    else:
        R = parser.bytes_parse(data, [4])
    return R

# Type 6
# OpaqueData(64)
def ping_frame_parser(data, flags):
    return data

# Type 7
# R(1) LastStreamID(31) ErrorCode(32) AdditionalDebugData(*)
def goaway_frame_parser(data, flags):
    R = []
    R = parser.bytes_parse(data, [4, 4])
    return R

# Type 8
# R(1) WindowSizeIncrement(31)
def window_update_frame_parser(data, flags):
    R = []
    R.append(data)
    return R

# Type 9
# HeaderBlockFragment(*)
def continuation_frame_parser(data, flags):
    R = []
    R.append(data)
    return R

frame_payload_parsers = {
    b"\x00":data_frame_parser,
    b"\x01":headers_frame_parser,
    b"\x02":priority_frame_parser,
    b"\x03":rst_stream_frame_parser,
    b"\x04":settings_frame_parser,
    b"\x05":push_promise_frame_parser,
    b"\x06":ping_frame_parser,
    b"\x07":goaway_frame_parser,
    b"\x08":window_update_frame_parser,
    b"\x09":continuation_frame_parser
}