import sys
import socket
import ssl
import lib.parser as parser

recv_val = 4096
CERT_FILE="./files/encript/cert.pem"
KEY_FILE="./files/encript/privkey.pem"

def send(sock, b):
    print(b)
    sock.send(b)

def recv(sock):
    replay = sock.recv(recv_val)
    print(replay.decode("utf-8"))
    return replay

def get_mail_servers(domain):
    HOST, PORT = "8.8.8.8", 53
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((HOST, PORT))
    domain = domain.split(b".")
    domain_name = b""
    for a in domain:
        leng = len(a)
        domain_name += leng.to_bytes(1, "big") + a
    sock.send(b'\x00\x01\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00'+domain_name+b'\x00\x00\x0f\x00\x01')
    R = sock.recv(1024*10)
    # ID, FLAGS, QDCOUNT, ANCOUNT, NSCOUNT, ARCOUNT
    H = parser.bytes_parse(R, (2, 2, 2, 2, 2, 2))
    #print("ID", H[0])
    #print("FLAGS", H[1])
    QDCOUNT = int.from_bytes(H[2], "big")
    ANCOUNT = int.from_bytes(H[3], "big")
    NSCOUNT = int.from_bytes(H[4], "big")
    ARCOUNT = int.from_bytes(H[5], "big")
    counts = (QDCOUNT, ANCOUNT, NSCOUNT, ARCOUNT)
    sections = [H[6]]
    
    for a in range(QDCOUNT):
        sections = parser.bytes_parse(sections[-1], (sections[-1].find(b"\x00")+1,2,2))
    for a in range(ANCOUNT):
        tmp = sections[:-1]
        if(sections[-1][0] & 0b11000000):
            tmp += parser.bytes_parse(sections[-1], (2,2,2,4,2))
        else:
            tmp += parser.bytes_parse(sections[-1], (sections[-1].find(b"\x00")+1,2,2,4,2))
        if(int.from_bytes(tmp[-2], "big") != len(tmp[-1])):
            tmp2 = tmp[:-1]
            tmp2 += parser.bytes_parse(tmp[-1], (int.from_bytes(tmp[-2], "big"),))
            tmp = tmp2
        sections = tmp
    
    #for a in range(QDCOUNT):
        #print(str(sections[a*3:a*3+3]))
    servers = []
    for a in range(ANCOUNT):
        l = sections[3:][a*6:a*6+6]
        mail_server = l[-1][2:]
        preference = l[-1][:2]
        #print(int.from_bytes(preference, "big"), mail_server)
        name = b""
        i = 0
        while(i < len(mail_server)):
            leng = mail_server[i]
            if((leng >> 6) == 0b11):
                cm = R[int.from_bytes(mail_server[i:i+2], "big") & 0x3fff:]
                cm = cm[:cm.find(b"\x00")+1]
                mail_server = mail_server[:i] + cm + mail_server[i+3:]
            else:
                st = mail_server[i+1:i+leng+1]
                if(st != b"\x00"):
                    name += st + b"."
                i += leng+1
        servers.append([int.from_bytes(preference, "big"), name[:-2].decode("utf-8")])
    return servers


def send_mail(server, mail_from, rcpt_to, data):
    HOST, PORT = socket.gethostbyname(server), 25
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    #context.load_cert_chain(CERT_FILE, KEY_FILE)
    #context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
    context = ssl.create_default_context()
    sock.connect((HOST, PORT))
    recv(sock)
    hello = mail_from[mail_from.find(b"@")+1:]
    send(sock, b"EHLO " + hello + b"\r\n")
    rp = recv(sock)
    
    if(rp.find(b"STARTTLS") != -1):
        send(sock, b"STARTTLS\r\n")
        recv(sock)
        sock = context.wrap_socket(sock, server_hostname=server)
        send(sock, b"EHLO " + hello + b"\r\n")
        recv(sock)

    send(sock, b"MAIL FROM: <" + mail_from + b">\r\n")
    recv(sock)
    send(sock, b"RCPT TO: <" + rcpt_to + b">\r\n")
    recv(sock)
    send(sock, b"DATA\r\n")
    recv(sock)
    data = data.split(b"\r\n")
    for a in data:
        send(sock, a + b"\r\n")
    recv(sock)
    send(sock, b"QUIT\r\n")
    recv(sock)
    sock.close()