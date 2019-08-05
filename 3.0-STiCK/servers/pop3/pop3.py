import asyncio
import sqlite3
import socket
import ssl

import lib.StreamWrapper as sw

BIND_IP = "localhost"
BIND_PORT = 995
database = "./files/mail/mail.db"
CERT_FILE="./files/encript/fullchain.pem"
KEY_FILE="./files/encript/privkey.pem"

class pop3_StreamWrapper(sw.StreamWrapper):
    async def Send(self, b):
        if(b[-2:] != b"\r\n"):
            b += b"\r\n"
        await self.Send(b)

async def pop3(reader, writer):
    conn = await pop3_StreamWrapper(reader, writer, debug=True)
    user_name = b""
    password = b""
    SESSION = None
    mail_vol = 0
    mail_octets = 0
    sq_conn = sqlite3.connect(database)
    c = sq_conn.cursor()
    m_list=[]
    try:
        await conn.Send(b"+OK STiCK-Lilith/3.0 pop3 ready.\r\n")
        while(True):
            buf = await conn.Recv()
            buf = buf.replace(b"\r\n", b"").split(b" ")
            command = buf[0].upper()
            if(command == b"CAPA"):
                await conn.Send(b"+OK Capability list follows\r\nSTAT\r\nLIST\r\nUIDL\r\nRETR\r\nDELE\r\nCAPA\r\nQUIT\r\nNOOP\r\n.\r\n")            
            elif(command == b"USER"):
                await conn.Send(b"+OK password please\r\n")
                user_name = buf[1]
            elif(command == b"PASS"):
                password = buf[1]
                c.execute("select id from accounts where user=? and pass=?", (user_name.decode("utf-8"), password.decode("utf-8")))
                r = c.fetchone()
                if(r is not None):
                    SESSION = r[0]
                    await conn.Send(b"+OK authed\r\n")
                else:
                    await conn.Send(b"-ERR \r\n")
                    buf = b""
            elif(command == b"QUIT"):
                await conn.Send(b"+OK\r\n")
                buf = b""
            elif(command == b"NOOP"):
                await conn.Send(b"+OK\r\n")        
            elif(SESSION is not None):
                if(command == b"STAT"):
                    c.execute("select count(id), total(octet) from mail_box where user_id=?", (SESSION,))
                    r = c.fetchone()
                    mail_vol = r[0]
                    mail_octets = int(r[1])
                    await conn.Send((b"+OK %d %d\r\n" % (mail_vol, mail_octets)))
                elif(command == b"LIST"):
                    c.execute("select count(id), total(octet) from mail_box where user_id=?", (SESSION,))
                    r = c.fetchone()
                    mail_vol = r[0]
                    mail_octets = int(r[1])
                    m_list = []
                    lis = b""
                    if(0 < mail_vol):
                        c.execute("select octet, uidl from mail_box where user_id=?", (SESSION,))
                        r = c.fetchall()
                        i = 1
                        for a in r:
                            m_list.append(a[1])
                            lis += (b"%d %d\r\n" % (i, a[0]))
                            i += 1
                    await conn.Send(b"+OK\r\n" + lis + b".\r\n")
                elif(command == b"UIDL"):
                    m_list = []
                    uilis = b""
                    if(0 < mail_vol):
                        c.execute("select uidl from mail_box where user_id=?", (SESSION,))
                        r = c.fetchall()
                        i = 1
                        for a in r:
                            m_list.append(a[0])
                            uilis += (b"%d %b\r\n" % (i, a[0].encode("utf-8")))
                            i += 1
                    await conn.Send(b"+OK\r\n" + uilis + b".\r\n")            
                elif(command == b"RETR"):
                    c.execute("select octet, message, mail_from from mail_box where uidl=? and user_id=?", (m_list[int(buf[1])-1], SESSION))
                    r = c.fetchone()
                    buf = (b"+OK %d octets\r\n" % (r[0]))
                    #msg = r[1].split("\\r\\n")
                    await conn.Send(r[1].encode("utf-8")[:-2])
                elif(command == b"TOP"):
                    lines = int(buf[2])
                    c.execute("select octet, message, mail_from from mail_box where uidl=? and user_id=?", (m_list[int(buf[1])-1], SESSION))
                    r = c.fetchone()
                    buf = (b"+OK %d lines\r\n" % (lines))
                    msg = r[1].split("\\r\\n")
                    for m in msg:
                        if(lines == 0):
                            buf += b"."
                            break
                        buf += m.encode("utf-8") + b"\r\n"
                        lines += 1
                    await conn.Send(buf)
                elif(command == b"DELE"):
                    await conn.Send(b"+OK message deleted\r\n")
                    c.execute("delete from mail_box where uidl=? and user_id=?", (m_list[int(buf[1])-1], SESSION))
                else:
                    await conn.Send(b"-ERR \r\n")
                    buf = b""                
            else:
                await conn.Send(b"-ERR \r\n")
                buf = b""
            if(len(buf)==0):
                writer.close()
                print("CLOSE")
                break
        sq_conn.commit()
        sq_conn.close()
    except:
        import traceback
        traceback.print_exc()        
        print("CONNECTION TIME-OUT")
        conn.Close()
        sq_conn.commit()
        sq_conn.close()

async def main():
    # make ssl context
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
    ctx.load_cert_chain(CERT_FILE, KEY_FILE)
    ctx.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
    server = await asyncio.start_server(pop3, BIND_IP, BIND_PORT, ssl=ctx)
    async with server:
        await server.serve_forever()

def start():
    asyncio.run(main())