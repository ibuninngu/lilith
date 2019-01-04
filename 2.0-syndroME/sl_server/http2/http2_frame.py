# file : /pl_server/http2/http2_frame.py

# Length(24) Type(8) Flags(8) R(1) StreamIdentifier(31) FramePayload(Length)
# frame_type ...
# DATA[0] HEADERS[1] PRIORITY[2] RST_STREAM[3] SETTINGS[4] PUSH_PROMISE[5] PING[6] GOAWAY[7] WINDOW_UPDATE[8] CONTINUATION[9]
frame_type = [b"\x00",b"\x01",b"\x02",b"\x03",b"\x04",b"\x05",b"\x06",b"\x07",b"\x08",b"\x09"]
frame_flag = {
    "NONE":0x00,
    "ACK":0x01,
    "END_STREAM":0x01,
    "END_HEADERS":0x04,
    "PADDED":0x08,
    "PRIORITY":0x20
}

bytes_frame_name = {
    b"\x00":"DATA",
    b"\x01":"HEADERS",
    b"\x02":"PRIORITY",
    b"\x03":"RST_STREAM",
    b"\x04":"SETTINGS",
    b"\x05":"PUSH_PROMISE",
    b"\x06":"PING",
    b"\x07":"GOAWAY",
    b"\x08":"WINDOW_UPDATE",
    b"\x09":"CONTINUATION"
}
frame_type_name = {
    "DATA":0,
    "HEADERS":1,
    "PRIORITY":2,
    "RST_STREAM":3,
    "SETTINGS":4,
    "PUSH_PROMISE":5,
    "PING":6,
    "GOAWAY":7,
    "WINDOW_UPDATE":8,
    "CONTINUATION":9
}

settings_param = {
    "SETTINGS_HEADER_TABLE_SIZE":b"\x00\x01",
    "SETTINGS_ENABLE_PUSH":b"\x00\x02",
    "SETTINGS_MAX_CONCURRENT_STREAMS":b"\x00\x03",
    "SETTINGS_INITIAL_WINDOW_SIZE":b"\x00\x04",
    "SETTINGS_MAX_FRAME_SIZE":b"\x00\x05",
    "SETTINGS_MAX_HEADER_LIST_SIZE":b"\x00\x06"
}

error_code = {
    "NO_ERROR":b"\x00\x00\x00\x00",
    "PROTOCOL_ERROR":b"\x00\x00\x00\x01",
    "INTERNAL_ERROR":b"\x00\x00\x00\x02",
    "FLOW_CONTROL_ERROR":b"\x00\x00\x00\x03",
    "SETTINGS_TIMEOUT":b"\x00\x00\x00\x04",
    "STREAM_CLOSED":b"\x00\x00\x00\x05",
    "FRAME_SIZE_ERROR":b"\x00\x00\x00\x06",
    "REFUSED_STREAM":b"\x00\x00\x00\x07",
    "CANCEL":b"\x00\x00\x00\x08",
    "COMPRESSION_ERROR":b"\x00\x00\x00\x09",
    "CONNECT_ERROR":b"\x00\x00\x00\x0a",
    "ENHANCE_YOUR_CALM":b"\x00\x00\x00\x0b",
    "INADEQUATE_SECURITY":b"\x00\x00\x00\x0c",
    "HTTP_1_1_REQUIRED":b"\x00\x00\x00\x0d"
}

first_responce_settings = b"\x00\x01\x00\x01\x00\x00\x00\x03\x00\x00\x03\xe8\x00\x04\x00\x60\x00\x00"

client_pri = b"\x50\x52\x49\x20\x2a\x20\x48\x54\x54\x50\x2f\x32\x2e\x30\x0d\x0a\x0d\x0a\x53\x4d\x0d\x0a\x0d\x0a"

class Http2Frame:
    def __init__(self):
        self.Length = 0x0
        self.Type = 0x0
        self.Flags = 0x0
        self.StreamIdentifire = 0x0
        self.FramePayload = b""
    def SetFramePayload(self, payload):
        self.FramePayload = payload
        self.Length = len(self.FramePayload)
    def SetFrameType(self, frametype):
        self.Type = frametype
    def SetFlags(self, flags):
        self.Flags = sum(flags)
    def SetStreamIdentifire(self, streamidentifire):
        self.StreamIdentifire = streamidentifire
    def Gen(self):
        R = self.Length.to_bytes(3, "big") + frame_type[self.Type] + self.Flags.to_bytes(1, "big") + self.StreamIdentifire.to_bytes(4, "big") + self.FramePayload
        return R