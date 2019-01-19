def file_upload(params):
    #print(params)
    buf = b""
    # simple way. for one file
    boundary = params[:params.find(b"\r\n")]
    p=params.split(boundary)
    content_type = p[1][p[1].find(b"Content-Type")+14:p[1].find(b"\r\n\r\n")].decode('utf-8')
    buf = p[1][p[1].find(b"\r\n\r\n")+4:-2]
    return(buf, content_type, 200)