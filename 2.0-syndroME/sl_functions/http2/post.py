# file : /sl_functions/http2/post_action_list.py
import sl_functions.http2.post_action_list as post_action_list

def post(req, arg):
    try:
        content, content_type, p_status = post_action_list.post_list[req](arg)
        return(content, content_type, p_status)
    except KeyError as error:
        f = open("./sl_contents/http/messages/404.html", "rb")
        buf = f.read()
        f.close()
        return(buf, "text/html", 404)