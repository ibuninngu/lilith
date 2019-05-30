import lilith_defines
import sl_defines.http.http_status_code as http_status_code

def make_http_header(status=200, server=lilith_defines.server_name, Accept_Ranges="bytes", Content_Length="0", Keep_Alive="timeout=15, max=100", Content_Type="media/binary"):
    return ("HTTP/1.1 " + http_status_code.status_code[status] + \
           "\r\nServer: " + server + \
           "\r\nAccept-Ranges: " + Accept_Ranges + \
           "\r\nContent-Length: " + Content_Length + \
           "\r\nKeep-Alive: " + Keep_Alive + \
           "\r\nContent-Type: " + Content_Type + \
           "\r\nContent-Security-Policy: default-src 'self" + \
           "\r\nX-Frame-Options: SAMEORIGIN" + \
           "\r\nX-XSS-Protection: 1; mode=block" + \
           "\r\n\r\n").encode("utf-8")