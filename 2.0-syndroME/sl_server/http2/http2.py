# file : /sl_server/http2/http2.py

import ssl
import socket
import select
import threading
import copy

import out_lib.hpack.hpack as hpack

import sl_lib.parser as parser
import sl_server.http2.http2_defines as http2_defines
import sl_server.http2.http2_frame as http2_frame
import sl_server.http2.http2_parser as http2_parser

import sl_functions.http2.get as get
import sl_functions.http2.post as post
import sl_functions.http2.gept as gept

cert_file=""
key_file=""
root_directory="./sl_contents/example.com/http/www"
message_directory="./sl_contents/example.com/http/message"

read_waiters = {}
write_waiters = {}

connections_info = {}
recv_datas = {}
hpack_decoders = {}
hpack_encoders = {}

def get_stream(data):
    message = b""
    if(len(data)>0):
        for r in data:
            message += r.Gen()
    return message
def del_fileno(fileno):
    #print("DEL_FILENO...",fileno,"...")
    del recv_datas[fileno]
    del hpack_decoders[fileno]
    del hpack_encoders[fileno]

def client_handler(fileno):
    client_socket, client_address, tls_obj, tls_in_buff, tls_out_buff = connections_info[fileno]
    recv_data = recv_datas[fileno]
    while True:
        tmp_data = parser.bytes_parse(recv_data, [3, 1, 1, 4])
        payload_and_data = parser.bytes_parse(tmp_data[-1], [int.from_bytes(tmp_data[0], "big")])
        tmp_data = tmp_data[:-1]
        tmp_data.append(http2_parser.frame_payload_parsers[tmp_data[1]](payload_and_data[0], int.from_bytes(tmp_data[2], "big")))
        if(len(payload_and_data)==2):
            recv_data = payload_and_data[1]
        else:
            recv_data = b""
        # tmp_data = [Length, Types, Flags, (R&S), [FramePayload]]
        #////////////////////////////////////////////////////////////////////
        frame = tmp_data
        print("type:",http2_frame.bytes_frame_name[frame[1]])
        if(frame[1] == http2_frame.frame_type[4]):
            # SETTINGS
            if(int.from_bytes(frame[2], "big") == http2_frame.frame_flag["NONE"]):
                hpack_encoders[fileno].header_table_size = int.from_bytes(frame[-1][0][1], "big")
                stream_identifire = int.from_bytes(frame[2], "big")
                res_settings_frame = http2_frame.Http2Frame()
                res_settings_frame.SetFrameType(http2_frame.frame_type_name["SETTINGS"])
                res_settings_frame.SetStreamIdentifire(stream_identifire)
                res_settings_frame.SetFlags([http2_frame.frame_flag["NONE"]])
                res_settings_frame.SetFramePayload(b"")
                SEND(fileno, res_settings_frame.Gen())
        if(frame[1] == http2_frame.frame_type[1]):
            # HEADERS
            stream_identifire = int.from_bytes(frame[3], "big")
            request_header = hpack_decoders[fileno].decode(frame[-1][-1])
            params = {}
            data, m_type, status = b"", "", 200
            for p in request_header:
                params[p[0]] = p[1]
            #print(params)
            if(params[":method"] == "GET"):
                if(params[":path"].find("?") != -1):
                    pfg = params[":path"].split("?")
                    data, m_type, status = gept.gept(pfg[0], pfg[1])
                    data = data.encode("utf-8")
                else:
                    data, m_type, status = get.get(params[":path"], root_dir=root_directory, message_dir=message_directory)
                print("GET--->:", params[":path"])
            elif(params[":method"] == "POST"):
                post_data = []
                while True:
                    tmp_data = parser.bytes_parse(recv_data, [3, 1, 1, 4])
                    payload_and_data = parser.bytes_parse(tmp_data[-1], [int.from_bytes(tmp_data[0], "big")])
                    tmp_data = tmp_data[:-1]
                    tmp_data.append(http2_parser.frame_payload_parsers[tmp_data[1]](payload_and_data[0], int.from_bytes(tmp_data[2], "big")))
                    if(len(payload_and_data)==2):
                        recv_data = payload_and_data[1]
                    else:
                        recv_data = b""
                    post_data += tmp_data
                    if(int.from_bytes(tmp_data[2], "big") & 0x01):
                        break
                    # tmp_data = [Length, Types, Flags, (R&S), [FramePayload]]
                print("POST--->:", params[":path"])
                print(post_data)
                data, m_type, status = post.post(params[":path"], (post_data[-1][0]).decode("utf-8"))
                data = data.encode("utf-8")
            else:
                data, m_type, status = get.get("/400.html", root_dir="./sl_contents/example.com/http/messages")
                status = 400
            rh = [(":status",str(status)),
                  ("server",http2_defines.server_name),
                  ("content-type", m_type),
                  ("content-length",str(len(data)))]
            res_header_frame = http2_frame.Http2Frame()
            res_header_frame.SetFrameType(http2_frame.frame_type_name["HEADERS"])
            res_header_frame.SetStreamIdentifire(stream_identifire)
            res_header_frame.SetFramePayload(hpack_encoders[fileno].encode(rh))
            res_header_frame.SetFlags([http2_frame.frame_flag["END_HEADERS"]])
            SEND(fileno, res_header_frame.Gen())
            res_data = parser.bytes_parseq(data, http2_defines.default_max_frame_size)
            res_header_frame.SetFlags([http2_frame.frame_flag["NONE"]])
            res_data_frame = res_header_frame
            res_data_frame.SetFrameType(http2_frame.frame_type_name["DATA"])
            if(len(res_data)==1):
                res_data_frame.SetFramePayload(res_data[0])
                res_data_frame.SetFlags([http2_frame.frame_flag["END_STREAM"]])
                SEND(fileno, res_data_frame.Gen())
            for d in res_data[:-1]:
                res_data_frame.SetFramePayload(d)
                SEND(fileno, res_data_frame.Gen())
            res_data_frame.SetFramePayload(res_data[-1])            
            res_data_frame.SetFlags([http2_frame.frame_flag["END_STREAM"]])
            SEND(fileno, res_data_frame.Gen())
        if(len(recv_data) == 0):
            break
        #////////////////////////////////////////////////////////////////////

def make_tls_objects():
    tls_in_buff = ssl.MemoryBIO()
    tls_out_buff = ssl.MemoryBIO()
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
    ctx.load_cert_chain(cert_file, key_file)
    ctx.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
    ctx.set_alpn_protocols(["h2"])
    tls_obj = ctx.wrap_bio(tls_in_buff, tls_out_buff, server_side=True)
    return tls_obj, tls_in_buff, tls_out_buff

def accept_handler(server_socket):
    (client_socket, address) = server_socket.accept()
    tls_obj, tls_in_buff, tls_out_buff = make_tls_objects()
    client_socket.setblocking(False)
    client_socket.settimeout(http2_defines.socket_timeout)
    # || TLS Handshake
    tls_in_buff.write(client_socket.recv(http2_defines.recv_val))
    try:
        tls_obj.do_handshake()
    except ssl.SSLWantReadError:
        client_socket.sendall(tls_out_buff.read())
        tls_in_buff.write(client_socket.recv(http2_defines.recv_val))
        tls_obj.do_handshake()
        client_socket.sendall(tls_out_buff.read())
    # -- TLS Handshake
    client_socket, (client_address) = client_socket, (address, client_socket)
    print("CONNECTED :",client_address[0])
    hpack_decoder = hpack.Decoder()
    hpack_encoder = hpack.Encoder()
    hpack_decoders.update({client_socket.fileno():hpack_decoder})
    hpack_encoders.update({client_socket.fileno():hpack_encoder})
    recv_datas.update({client_socket.fileno():b""})
    connections_info[client_socket.fileno()] = (client_socket, client_address, tls_obj, tls_in_buff, tls_out_buff)
    read_waiters[client_socket.fileno()] = (first_recv_handler, (client_socket.fileno(),))
    read_waiters[server_socket.fileno()] = (accept_handler, (server_socket,))
    return

def first_recv_handler(fileno):
    #print("first_recv_handler")
    try:
        client_socket, client_address, tls_obj, tls_in_buff, tls_out_buff = connections_info[fileno]
        tls_in_buff.write(client_socket.recv(http2_defines.recv_val))
        recv_data = tls_obj.read()
        #print("RECEIVED___",len(recv_data))
        recv_datas[fileno] = recv_data[24:]
        write_waiters[fileno] = (send_handler, (fileno,))
        return
    except OSError:
        del connections_info[client_socket.fileno()]
        client_socket.close()
        del_fileno(fileno)
        #print("--------------------SOCKET TERMINATED--------------------")
        return

def recv_handler(fileno):
    try:
        client_socket, client_address, tls_obj, tls_in_buff, tls_out_buff = connections_info[fileno]
        #print("<<< TRYING RECV >>>")
        tls_in_buff.write(client_socket.recv(http2_defines.recv_val))
        buf = tls_obj.read()
        recv_data = buf
        while True:
            try:
                buf = tls_obj.read()
                recv_data += buf
            except:
                break
        recv_datas[fileno] = recv_data
        write_waiters[fileno] = (send_handler, (fileno,))
        return
    except OSError:
        del connections_info[client_socket.fileno()]
        client_socket.close()
        del_fileno(fileno)
        #print("--------------------SOCKET TERMINATED--------------------")
        return

def SEND(fileno, data):
    if(len(data) == 0):
        #print("ZERO_LENGTH_SHOT")
        return
    client_socket, client_address, tls_obj, tls_in_buff, tls_out_buff = connections_info[fileno]
    try:
        tls_obj.write(data)
        send_message = tls_out_buff.read()
        send_len = client_socket.sendall(send_message)
        if(send_len == None):
            return
        else:
            write_waiters[fileno] = (SEND, (fileno, send_message[send_len:]))
    except OSError:
        del connections_info[client_socket.fileno()]
        client_socket.close()
        del_fileno(fileno)
        #print("===========================SOCKET TERMINATED===========================")
        return

def send_handler(fileno):
    client_handler(fileno)
    read_waiters[fileno] = (recv_handler, (fileno,))

def main(server_sock):
    read_waiters[server_sock.fileno()] = (accept_handler, (server_sock,))
    while True:
        read_list, write_list, _ = select.select(read_waiters.keys(), write_waiters.keys(), [])
        for write_fileno in write_list:
            handler, args = write_waiters.pop(write_fileno)
            handler(*args)        
        for read_fileno in read_list:
            handler, args = read_waiters.pop(read_fileno)
            handler(*args)