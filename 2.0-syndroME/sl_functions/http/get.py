import sl_functions.http.media_detect as media_detect

#reg="/index.html"
def get(req, default_file = "/index.html", direc="./sl_contents/example.com/http/www"):
    print("GET: "+direc + req)
    try:
        if req == "/":
            req = default_file
        f = open(direc + req, "rb")
        buf = f.read()
        f.close()
        media, status = media_detect.media_detect(req)
        if(status == 200):
            return(buf, media, status)
        elif(status == 415):
            f = open("./sl_contents/example.com/http/messages/415.html", "rb")
            buf = f.read()
            f.close()
            return(buf, "text/html", 415)
    except:
        import traceback
        traceback.print_exc()        
        f = open("./sl_contents/example.com/http/messages/404.html", "rb")
        buf = f.read()
        f.close()
        return(buf, "text/html", 404)
