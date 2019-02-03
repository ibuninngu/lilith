import threading

def save(name, b):
    f = open("./sl_contents/example.com/http/www/upload/"+name, "wb")
    f.write(b)
    f.close()

def file_upload(params):
    buf = b""
    # simple way. for one file
    boundary = params[:params.find(b"\r\n")]
    p=params.split(boundary)
    content_type = p[1][p[1].find(b"Content-Type")+14:p[1].find(b"\r\n\r\n")].decode('utf-8')
    tmp = p[1].find(b"filename")
    file_name = p[1][tmp+10:p[1][tmp:].find(b"\r\n")+tmp-1].decode('utf-8')
    buf = p[1][p[1].find(b"\r\n\r\n")+4:-2]
    thread = threading.Thread(target=save, args=(file_name,buf))
    thread.start()    
    return(buf, content_type, 200)