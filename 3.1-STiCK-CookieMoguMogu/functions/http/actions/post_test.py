def post_test(params, header):
    print(params, header)
    params = params.decode("utf-8").split("&")
    buf = ""
    for line in params:
        buf += "<p>" + line + "</p>"
    return(buf.encode("utf-8"), "text/html", 200, "")