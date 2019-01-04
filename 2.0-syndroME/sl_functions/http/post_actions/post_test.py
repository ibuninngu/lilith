def post_test(params):
    print(params)
    params = params.split("&")
    buf = ""
    for line in params:
        buf += "<p>" + line + "</p>"
    return(buf, "text/html", 200)