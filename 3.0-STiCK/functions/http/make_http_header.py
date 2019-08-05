import defines.http.http_status_code as http_status_code

SERVER_NAME = b"STiCK-Lilith/3.0"

HEADER=(
b"HTTP/1.1 %b\r\n" + \
b"Server: %b\r\n" + \
b"Accept-Ranges: %b\r\n" + \
b"Content-Length: %i\r\n" + \
b"Keep-Alive: %b\r\n" + \
b"Content-Type: %b\r\n" + \
#b"Content-Security-Policy: default-src 'self'\r\n" + \
b"Cache-Control: no-cache\r\n" + \
b"X-Frame-Options: SAMEORIGIN\r\n" + \
b"X-XSS-Protection: 1; mode=block\r\n\r\n")

def make_http_header(status=200, server=SERVER_NAME, Accept_Ranges=b"bytes", Content_Length=0, Keep_Alive=b"timeout=30, max=100", Content_Type=b"media/binary"):
    return (HEADER % (http_status_code.status_code[status], server, Accept_Ranges, Content_Length, Keep_Alive, Content_Type))