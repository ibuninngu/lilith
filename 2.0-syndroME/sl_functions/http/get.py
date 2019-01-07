import sl_functions.http.media_detect as media_detect

#reg="/index.html"
def get(req, default_file = "/index.html", root_dir="./sl_contents/example.com/http/www", message_dir="./sl_contents/example.com/http/messages"):
    #print("GET: "+root_dir + req)
    try:
        if req == "/":
            req = default_file
        f = open(root_dir + req, "rb")
        buf = f.read()
        f.close()
        media, status = media_detect.media_detect(req)
        if(status == 200):
            return(buf, media, status)
        elif(status == 415):
            f = open(message_dir+"/415.html", "rb")
            buf = f.read()
            f.close()
            return(buf, "text/html", 415)
    except:
        import traceback
        traceback.print_exc()
        f = open(message_dir+"/404.html", "rb")
        buf = f.read()
        f.close()
        return(buf, "text/html", 404)
