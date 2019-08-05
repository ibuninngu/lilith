# file : /3.0-STiCK/servers/http2/http2.py

import asyncio
import ssl
import hpack
import io

import lib.parser as parser
import lib.StreamWrapper as sw
import servers.http2.http2_frame as http2_frame
import servers.http2.http2_parser as http2_parser

import functions.http.get as get
import functions.http.post as post
import functions.http.gept as gept

########## DEFINES ##########
SERVER_NAME = "STiCK-Lilith/3.0"
BIND_IP = "127.0.0.1"
BIND_PORT = 443
CERT_FILE="./files/encript/cert.pem"
KEY_FILE="./files/encript/privkey.pem"
preface_length = 24
default_max_frame_size = 2**14
PREFACE = b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"
root_dir="./files/web/contents"
message_dir="./files/web/messages"
#############################

class http2_StreamWrapper():
    async def __new__(cls, *a, **kw):
        instance = super().__new__(cls)
        await instance.__init__(*a, **kw)
        return instance    
    async def __init__(self, reader, writer):
        self.conn = await sw.StreamWrapper(reader, writer)
        self.Window = 0
        self.Stream = io.BytesIO(await self.conn.Recv())
    async def read(self, i):
        R = self.Stream.read(i)
        if(len(R) != i):
            #print(len(R), i)
            self.Stream = io.BytesIO(await self.conn.Recv())
            R += self.Stream.read(i - len(R))
            #print(len(R))
        self.Window += i
        if(self.Window > 0xFFFFFF):
            wuf = Http2Frame()
            wuf.SetFrameType(http2_frame.frame_type_name["WINDOW_UPDATE"])
            wuf.SetStreamIdentifire(0)
            wuf.SetFramePayload(b"\x00\xff\xff\xff")
            wuf.SetFlags([http2_frame.frame_flag["NONE"]])
            await self.conn.Send(writer, wuf.Gen())
            self.Window = 0
        return R

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
        R = self.Length.to_bytes(3, "big") + http2_frame.frame_type[self.Type] + self.Flags.to_bytes(1, "big") + self.StreamIdentifire.to_bytes(4, "big") + self.FramePayload
        return R

async def http2(reader, writer):
    addr = writer.get_extra_info("peername")
    print("OPEN:", addr)
    stream = await http2_StreamWrapper(reader, writer)
    if(PREFACE != await stream.read(preface_length)):
        stream.conn.Close()
        return
    hpack_decoder = hpack.Decoder()
    hpack_encoder = hpack.Encoder()
    # Length(24) Type(8) flags(8) [R(1) StreamIdentifier(31)] FramePayload(Length)
    while(True):
        Length = int.from_bytes(await stream.read(3), "big")
        if(Length == 0):
            stream.conn.Close()
            return
        Type = await stream.read(1)
        flags = int.from_bytes(await stream.read(1), "big")
        RnS = await stream.read(4)
        #print(http2_frame.bytes_frame_name[Type])
        FramePayload = await stream.read(Length)
        Payload = http2_parser.frame_payload_parsers[Type](FramePayload, flags)
        frame_type = http2_frame.bytes_frame_name[Type]
        stream_identifire = int.from_bytes(RnS, "big")
        if(frame_type is "HEADERS"):
            content, content_type, status = b"", "", 404
            request = {}
            for p in hpack_decoder.decode(Payload[-1]):
                request[p[0]] = p[1]
            if(request[":method"] == "GET"):
                if(request[":path"].find("?") != -1):
                    print("GEPT...>>> ", request[":path"])
                    pfg = request[":path"].split("?")
                    content, content_type, status = gept.gept(pfg[0], pfg[1].encode("utf-8"), message_dir + "/412.html")
                else:
                    print("GET...>>> ", request[":path"])
                    content, content_type, status = get.get(req=request[":path"],root_dir=root_dir, message_dir=message_dir)
            elif(request[":method"] == "POST"):
                print("POST--->:", request[":path"])
                post_data = b""
                print("reading ...")
                if(not (flags & 0x01)):
                    while True:
                        Length = int.from_bytes(await stream.read(3), "big")
                        Type = await stream.read(1)
                        flags = int.from_bytes(await stream.read(1), "big")
                        RnS = await stream.read(4)
                        FramePayload = await stream.read(Length)
                        if(Type == b"\x00"):
                            Payload = http2_parser.frame_payload_parsers[Type](FramePayload, flags)
                            post_data += Payload[0]
                            if(flags & 0x01):
                                break
                    print(len(post_data))
                content, content_type, status = post.post(request[":path"], post_data, message_dir)
            rh = [(":status",status),("server",SERVER_NAME),
                ("content-type",content_type),("content-length",len(content)),
                ("x-frame-options","SAMEORIGIN"),("x-xss-protection","1; mode=block"), ("cache-control", "no-cache")]
            res_header_frame = Http2Frame()
            res_header_frame.SetFrameType(http2_frame.frame_type_name["HEADERS"])
            res_header_frame.SetStreamIdentifire(stream_identifire)
            res_header_frame.SetFramePayload(hpack_encoder.encode(rh))
            res_header_frame.SetFlags([http2_frame.frame_flag["END_HEADERS"]])
            await stream.conn.Send(res_header_frame.Gen())
            res_data = parser.bytes_parseq(content, default_max_frame_size)
            res_header_frame.SetFlags([http2_frame.frame_flag["NONE"]])
            res_data_frame = res_header_frame
            res_data_frame.SetFrameType(http2_frame.frame_type_name["DATA"])
            if(len(res_data)==1):
                res_data_frame.SetFramePayload(res_data[0])
                res_data_frame.SetFlags([http2_frame.frame_flag["END_STREAM"]])
                await stream.conn.Send(res_data_frame.Gen())
            for d in res_data[:-1]:
                res_data_frame.SetFramePayload(d)
                await stream.conn.Send(res_data_frame.Gen())
            res_data_frame.SetFramePayload(res_data[-1])
            res_data_frame.SetFlags([http2_frame.frame_flag["END_STREAM"]])
            await stream.conn.Send(res_data_frame.Gen())
        elif(frame_type is "SETTINGS"):
            print(Payload)
            if(flags == b"\x01"):
                break
            hpack_encoder.header_table_size = int.from_bytes(Payload[0][1], "big")
            res_settings_frame = Http2Frame()
            res_settings_frame.SetFrameType(http2_frame.frame_type_name["SETTINGS"])
            res_settings_frame.SetStreamIdentifire(stream_identifire)
            res_settings_frame.SetFlags([http2_frame.frame_flag["NONE"]])
            res_settings_frame.SetFramePayload(b"\x00\x01\x00\x02\x00\x00\x00\x03\x00\x00\x03\xe8\x00\x04\x00\xff\xff\xff\x00\x05\x00\xff\xff\xff")
            await stream.conn.Send(res_settings_frame.Gen())
            wuf = Http2Frame()
            wuf.SetFrameType(http2_frame.frame_type_name["WINDOW_UPDATE"])
            wuf.SetStreamIdentifire(0)
            wuf.SetFramePayload(b"\x00\xff\xff\xff")
            wuf.SetFlags([http2_frame.frame_flag["NONE"]])
            await stream.conn.Send(wuf.Gen())
        elif(frame_type is "WINDOW_UPDATE"):
            print(Payload)
        elif(frame_type is "RST_STREAM"):
            print(Payload)
            stream.conn.Close()
        elif(frame_type is "DATA"):
            #print(Payload)
            pass
        elif(frame_type is "PING"):
            print("PING")
            ping_frame = Http2Frame()
            ping_frame.SetFrameType(http2_frame.frame_type_name["PING"])
            ping_frame.SetStreamIdentifire(stream_identifire)
            ping_frame.SetFramePayload(Payload)
            ping_frame.SetFlags([http2_frame.frame_flag["ACK"]])
            await stream.conn.Send(ping_frame.Gen())                

async def main():
    # make ssl context
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
    ctx.load_cert_chain(CERT_FILE, KEY_FILE)
    ctx.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
    ctx.set_alpn_protocols(["h2"])
    # make en run server
    server = await asyncio.start_server(http2, BIND_IP, BIND_PORT, ssl=ctx)
    async with server:
        await server.serve_forever()

def start():
    asyncio.run(main())