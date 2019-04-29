import sl_functions.http.actions_list as actions_list

def post(req, arg, message_dir):
    try:
        content, content_type, p_status = actions_list.gept_list[req](arg)
        return(content, content_type, p_status)
    except KeyError as error:
        f = open(message_dir + "/404.html", "rb")
        buf = f.read()
        f.close()
        return(buf, "text/html", 404)