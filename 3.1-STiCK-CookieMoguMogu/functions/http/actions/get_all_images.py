import os

def get_all_images(params, header):
    buf = b""
    files = os.listdir("./files/web/contents/upload/")
    for f in files:
        buf += b"<img src='./upload/"+f.encode('utf-8')+b"' />"
    return(buf, "text/html", 200, "")