import sl_functions.http.post_action_list as post_action_list

def gept(req, arg):
    try:
        content, content_type, p_status = post_action_list.gept_list[req](arg)
        return(content, content_type, p_status)
    except KeyError as error:
        f = open("./sl_contents/http/messages/421.html", "rb")
        buf = f.read()
        f.close()
        return(buf, "text/html", 421)