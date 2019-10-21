import asyncio
import socket
import ssl

import lib.StreamWrapper as sw

import functions.http.get as get
import functions.http.post as post
import functions.http.gept as gept
import functions.http.make_http_header as make_http_header

########## DEFINES ##########
SERVER_NAME = b"STiCK-Lilith/3.0"
BIND_IP = "localhost"
BIND_PORT = 80
SSL = False
CERT_FILE="./files/encript/cert.pem"
KEY_FILE="./files/encript/privkey.pem"
recv_val = 1024 * 4
root_dir="./files/web/contents"
message_dir="./files/web/messages"
#############################

def GET(header):
    print("GET...>>> ", header[b"path"])
    if(header[b"path"].find(b"?") != -1):
        pfg = header[b"path"].split(b"?")
        content, content_type, p_status, additional = gept.gept(pfg[0].decode("utf-8"), pfg[1], message_dir + "/412.html", header)
        return make_http_header.make_http_header(status=p_status, Content_Length=len(content), Content_Type=content_type.encode("utf-8"), Additional=additional) + content
    content, content_type, g_status = get.get(req=header[b"path"].decode("utf-8"), root_dir=root_dir, message_dir=message_dir)
    return make_http_header.make_http_header(status=g_status, Content_Length=len(content), Content_Type=content_type.encode("utf-8")) + content

def POST(header, body):
    print("POST...>>> ", header[b"path"], ":::::", body[:10], body[-20:])
    # body is always Binary
    content, content_type, p_status, additional = post.post(header[b"path"].decode("utf-8"), body, message_dir + "/404.html", header)
    return make_http_header.make_http_header(status=p_status, Content_Length=len(content), Content_Type=content_type.encode("utf-8"), Additional=additional) + content

async def http(reader, writer):
    connection = await sw.StreamWrapper(reader, writer, debug=False)
    try:
        while(True):
            buf = await connection.Recv()
            if(len(buf)==0):
                connection.Close()
                return
            header_params = {}
            body_pointer = buf.find(b"\r\n\r\n")
            headers = buf[:body_pointer].split(b"\r\n")
            request = headers[0].split(b" ")
            R=b"<<>>"
            header_params.update({b"method":request[0]})
            header_params.update({b"path":request[1]})
            header_params.update({b"version":request[2]})
            try:
                for param in headers[1:]:
                    p = param.split(b": ")
                    header_params.update({p[0].lower():p[1]})
            except:
                pass
            if(header_params[b"method"] == b"GET"):
                R=GET(header_params)
            elif(header_params[b"method"] == b"POST"):
                body = buf[body_pointer+4:]
                while(len(body) < int(header_params[b'content-length'])):
                    body += await connection.Recv()
                R=POST(header_params, body)
            await connection.Send(R)
    except:
        connection.Close()

async def main():
    if(SSL):
        # make ssl context
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
        ctx.load_cert_chain(CERT_FILE, KEY_FILE)
        ctx.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        # make en run server
        server = await asyncio.start_server(http, BIND_IP, BIND_PORT, ssl=ctx)
        async with server:
            await server.serve_forever()
    else:
        server = await asyncio.start_server(http, BIND_IP, BIND_PORT)
        async with server:
            await server.serve_forever()

def start():
    asyncio.run(main())
