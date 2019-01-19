import sl_functions.http.post_action_list as post_action_list

def post(req, arg, error_message):
    try:
        content, content_type, p_status = post_action_list.post_list[req](arg)
        return(content, content_type, p_status)
    except KeyError as error:
        f = open(error_message, "rb")
        buf = f.read()
        f.close()
        return(buf, "text/html", 404)