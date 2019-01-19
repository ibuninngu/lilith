# file : /sl_server/http/http.py

import sl_functions.http.get as get
import sl_functions.http.post as post
import sl_functions.http.make_http_header as make_http_header

# ========== DEFINES ========== #
recv_val = 4096
#1024...1kb **2...1Mb
buf_limit = 1024 ** 4
buf_limit_int = int(buf_limit / recv_val)
root_dir = "./sl_contents/example.com/http/www"
message_dir = "./sl_contents/example.com/http/messages"

# socket
SOCKET = None

def GET(header_params):
    if(header_params["path"].find("?") != -1):
        pfg = header_params["path"].split("?")
        content, content_type, p_status = post.post(pfg[0], pfg[1], message_dir + "/412.html")
        return make_http_header.make_http_header(status=p_status, Content_Length=str(len(content)), Content_Type=content_type), content
    content, content_type, g_status = get.get(req=header_params["path"],root_dir=root_dir, message_dir=message_dir)
    return make_http_header.make_http_header(status=g_status, Content_Length=str(len(content)), Content_Type=content_type), content

def POST(header_params, body):
	# body is always Binary
    content, content_type, p_status = post.post(header_params["path"], body, message_dir + "/404.html")
    return make_http_header.make_http_header(status=p_status, Content_Length=str(len(content)), Content_Type=content_type), content

def main(socket):
    header_params = {}
    body = b""
    buf = socket.recv(recv_val)
    header = buf.decode("utf-8").split("\r\n")
    #http headers to hash-map
    first_line = header[0].split(" ")
    header_params.update({"method":first_line[0]})
    header_params.update({"path":first_line[1]})
    #header_params.update({"version":first_line[2]})
    for param in header[1:-2]:
        p = param.split(": ")
        header_params.update({p[0]:p[1]})
        print(p)
    if(header_params["method"] == "GET"):
        h, get_buf = GET(header_params)
        message = h + get_buf
        return message
    elif(header_params["method"] == "POST"):
        # recv message body
        content_length = int(header_params["Content-Length"])
        # first, check Content_Length from header
        if(buf_limit < content_length):
            content, content_type, g_status = get.get("/413.html", direc=message_dir)
            message = make_http_header.make_http_header(status=413, Content_Length=str(len(content)), Content_Type=content_type)
            return message + content
        # recv while Content_Length
        body_len_int = -(-(content_length) // recv_val)+1
        for _ in range(body_len_int):
			# don't tmp_buf.decode('utf-8'), "multipart/form-data" is binary
            tmp_buf = socket.recv(recv_val)
            body += tmp_buf
        h, post_buf = POST(header_params, body)
        message = h + post_buf
        return message
    else:
        get_buf, content_type, g_status = get.get("/501.html", direc=messages_dir)
        message = make_http_header.make_http_header(status=501, Content_Length=str(len(get_buf)), Content_Type=content_type)
        return message + content