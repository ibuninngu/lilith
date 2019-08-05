import asyncio
import sqlite3
import socket
import hashlib
import ssl

import lib.StreamWrapper as sw

my_domain = b"example.com"
BIND_IP = "localhost"
BIND_PORT = 25
database = "./files/mail/mail.db"
CERT_FILE="./files/encript/cert.pem"
KEY_FILE="./files/encript/privkey.pem"
async_timeout = 30.0

class smtp_StreamWrapper(sw.StreamWrapper):
    async def smtp_Send(self, b):
        if(b[-2:] != b"\r\n"):
            b += b"\r\n"
        await self.Send(b)

async def smtp(reader, writer):
    addr = writer.get_extra_info("peername")
    ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
    ssl_ctx.load_cert_chain(CERT_FILE, KEY_FILE)
    ssl_ctx.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
    conn = await smtp_StreamWrapper(reader, writer, ssl_context=ssl_ctx, debug=True)
    
    flags = {b"EHLO":False,b"STARTTLS":False,b"MAIL":False,b"RCPT":False}
    host = b""
    mail_from = b""
    rcpt_to = []
    mail_data = b""
    try:
        await conn.smtp_Send(b"220 STiCK-Lilith/3.0 smtp on <%b> ready." % my_domain)
        while(True):
            BUFFER = await conn.Recv()
            buf_tmp = BUFFER.split(b"\r\n")
            if(0 < len(buf_tmp[1])):
                BUFFER = buf_tmp[1]
            buf = BUFFER.replace(b"\r\n", b"").split(b" ")
            command = buf[0].upper()
            if(command == b"EHLO" or command == b"HELO"):
                host = buf[1]
                await conn.smtp_Send(b"250-%b at you, %b" % (my_domain, addr[0].encode("utf-8")))
                await conn.smtp_Send(b"250-SIZE 157286400")
                await conn.smtp_Send(b"250-8BITMIME")
                await conn.smtp_Send(b"250-ENHANCEDSTATUSCODES")
                if(not flags[b"STARTTLS"]):
                    await conn.smtp_Send(b"250-STARTTLS")
                await conn.smtp_Send(b"250 SMTPUTF8")
                flags[command]=True
            elif(command == b"QUIT"):
                await conn.smtp_Send(b"221 closing connection... bye.")
                buf = b""
            elif(flags[b"EHLO"] or flags[b"HELO"]):
                if(command == b"STARTTLS"):
                    await conn.smtp_Send(b"220 Ready to start TLS")
                    await conn.StartTLS()
                    print("============== TLS OK ==============")
                    flags[b"EHLO"]=False
                    flags[command]=True
                elif(command == b"MAIL"):
                    mail_from = BUFFER[BUFFER.find(b"<")+1:BUFFER.find(b">")]
                    await conn.smtp_Send(b"250 %b... Sender ok" % mail_from)
                    flags[command]=True
                elif(flags[b"MAIL"]):
                    if(command == b"RCPT"):
                        rcpt_domain = buf[-1][buf[-1].find(b"@")+1:buf[-1].find(b">")]
                        if(rcpt_domain == my_domain):
                            rcpt_to.append(buf[-1][buf[-1].find(b"<")+1:buf[-1].find(b"@")])
                            await conn.smtp_Send(b"250 %b... Recipient ok" % (rcpt_to[-1]))
                            flags[command]=True
                        else:
                            command = b""
                    elif(flags[b"RCPT"]):
                        if(command == b"DATA"):
                            await conn.smtp_Send(b"354 Ok, Go ahead.")
                            while(True):
                                print("tryng RECV")
                                d_buf = await conn.Recv()
                                mail_data += d_buf
                                if(d_buf[-3:] == b".\r\n"):
                                    await conn.smtp_Send(b"250 Message accepted for delivery")
                                    #mf = mail_data.find(b"From:")
                                    #mail_from_data = mail_data[mf:mf + mail_data[mf:].find(b"\r\n")]
                                    #mail_from_data = mail_from_data[mail_from_data.find(b"<")+1:mail_from_data.find(b">")]
                                    sq_conn = sqlite3.connect(database)
                                    c = sq_conn.cursor()
                                    try:
                                        for to in rcpt_to:
                                            c.execute("select id from accounts where user=?", (to.decode("utf-8"),))
                                            r = c.fetchone()
                                            c.execute("insert into mail_box(user_id, message, octet, uidl, mail_from) values(?, ?, ?, ?, ?)",
                                                      (r[0], mail_data.decode("utf-8"), len(mail_data), hashlib.md5(mail_data).hexdigest(), mail_from.decode("utf-8")))
                                    except:
                                        pass
                                    sq_conn.commit()
                                    sq_conn.close()
                                    break
            else:
                await conn.smtp_Send(b"502 hmm, nop. go away.")
                buf = b""
            if(command == b""):
                await conn.smtp_Send(b"451 hmm, nop. go away.")
                buf = b""
            if(len(buf)==0):
                conn.Close()
                print("CLOSE")
                return
    except:
        import traceback
        traceback.print_exc()        
        print("CONNECTION TIME-OUT")
        conn.Close()

async def main():
    server = await asyncio.start_server(smtp, BIND_IP, BIND_PORT)
    async with server:
        await server.serve_forever()

def start():
    asyncio.run(main())