import functions.http.actions_list as actions_list

def gept(req, arg, message_dir, header):
    try:
        content, content_type, p_status, additional_header = actions_list.gept_list[req](arg, header)
        return(content, content_type, p_status, additional_header)
    except KeyError as error:
        f = open(message_dir + "/404.html", "rb")
        buf = f.read()
        f.close()
        return(buf, "text/html", 404)