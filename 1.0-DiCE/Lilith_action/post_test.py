# -*- coding: utf-8 -*-

def post_test(params):
    params = params[-1].split("&")
    buf = ""
    for line in params:
        buf += "<p>" + line + "</p>"
    return(buf, "text/html")