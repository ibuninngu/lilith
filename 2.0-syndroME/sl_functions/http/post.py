import sl_functions.http.post_action_list as post_action_list

def post(req, arg, message_dir):
    try:
        if(post_action_list.post_list[req][1]):
            content, content_type, p_status = post_action_list.post_list[req][0](arg)
            return(content, content_type, p_status)
        else:
            f = open(message_dir + "/405.html", "rb")
            buf = f.read()
            f.close()
            return(buf, "text/html", 405)            
    except KeyError as error:
        f = open(message_dir + "/404.html", "rb")
        buf = f.read()
        f.close()
        return(buf, "text/html", 404)