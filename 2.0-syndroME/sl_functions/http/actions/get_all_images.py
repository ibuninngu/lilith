import os

def get_all_images(params):
    buf = b""
    files = os.listdir("./sl_contents/example.com/http/www/upload/")
    for f in files:
        buf += b"<img src='./upload/"+f.encode('utf-8')+b"' />"
    return(buf, "text/html", 200)