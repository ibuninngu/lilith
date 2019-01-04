# -*- coding: utf-8 -*-

import action_list
import logging

def post(req):
    try:
        arg = req.split("\r\n")
        req = arg[0].split(" ")[1].split("/")[-1]
        status = "200"
        content, content_type = action_list.post_list[req](arg[-1])
    except:
        status = "400"
        content = "<h1>Status 400</h1><br><p>THERE'S A BAD MOON ON THE RISE</p>"
        content_type = "text/html"
    logging.info(status + ":" + req + "<--" + arg[-1])
    return(content, content_type, status)