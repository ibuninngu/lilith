# file : /sl_server/http/http.py

import sl_functions.http.get as get
import sl_functions.http.post as post
import sl_functions.http.make_http_header as make_http_header

# ========== DEFINES ========== #
recv_val = 4096
#1024...1kb **2...1Mb
buf_limit = 1024 ** 3
buf_limit_int = int(buf_limit / recv_val)
root_dir = "./sl_contents/example.com/http/www"
message_dir = "./sl_contents/example.com/http/messages"

def GET(header_params):
    print("GET...>>> ", header_params[b"path"])
    if(header_params[b"path"].find(b"?") != -1):
        pfg = header_params[b"path"].split(b"?")
        content, content_type, p_status = post.post(pfg[0].decode("utf-8"), pfg[1], message_dir + "/412.html")
        return make_http_header.make_http_header(status=p_status, Content_Length=str(len(content)), Content_Type=content_type), content
    content, content_type, g_status = get.get(req=header_params[b"path"].decode("utf-8"),root_dir=root_dir, message_dir=message_dir)
    return make_http_header.make_http_header(status=g_status, Content_Length=str(len(content)), Content_Type=content_type), content

def POST(header_params, body):
    print("POST...>>> ", header_params[b"path"], ":::::", body[:5])
    # body is always Binary
    content, content_type, p_status = post.post(header_params[b"path"].decode("utf-8"), body, message_dir + "/404.html")
    return make_http_header.make_http_header(status=p_status, Content_Length=str(len(content)), Content_Type=content_type), content

def main(socket):
    header_params = {}
    body = b""
    buf = socket.recv(recv_val)
    packet = buf.split(b"\r\n\r\n")
    header = packet[0].split(b"\r\n")
    for b in packet[1:]:
        body += b"\r\n\r\n" + b
    body=body[4:]
    #http headers to hash-map
    first_line = header[0].split(b" ")
    header_params.update({b"method":first_line[0]})
    header_params.update({b"path":first_line[1]})
    #header_params.update({"version":first_line[2]})
    for param in header[1:]:
        p = param.split(b": ")
        header_params.update({p[0]:p[1]})
    if(header_params[b"method"] == b"GET"):
        h, get_buf = GET(header_params)
        message = h + get_buf
        return message
    elif(header_params[b"method"] == b"POST"):
        content_length = int(header_params[b"Content-Length"].decode("utf-8"))
        # first, check Content_Length from header
        if(buf_limit < content_length):
            content, content_type, g_status = get.get("/413.html", root_dir=message_dir)
            message = make_http_header.make_http_header(status=413, Content_Length=str(len(content)), Content_Type=content_type)
            return message + content
        # recv while Content_Length
        body_len_int = -(-(content_length - len(body)) // recv_val)
        for _ in range(body_len_int):
            # don't tmp_buf.decode('utf-8'), "multipart/form-data" is binary
            tmp_buf = socket.recv(recv_val)
            body += tmp_buf
        h, post_buf = POST(header_params, body)
        message = h + post_buf
        return message
    else:
        get_buf, content_type, g_status = get.get("/501.html", root_dir=message_dir)
        message = make_http_header.make_http_header(status=501, Content_Length=str(len(get_buf)), Content_Type=content_type)
        return message + get_buf