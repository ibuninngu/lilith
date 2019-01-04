# -*- coding: utf-8 -*-

import content_detect
import logging

def get(req, direc, normal = "/index.html"):
    req = req.split("\r\n")[0].split(" ")[1]
    try:
        if req == "/":
            req = normal
        f = open(direc + req, "rb")
        buf = f.read()
        f.close()
        logging.info("200:" + direc + req)
        return(buf, content_detect.content_detect(req), "200")
    except:
        logging.info("404:" + direc + req)
        return("<h1>Status 404</h1><br><p>" + req + " is NOT FOUND</p>", "text/html", "404")
