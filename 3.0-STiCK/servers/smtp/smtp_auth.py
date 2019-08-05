import asyncio
import socket
import base64
import ssl
import sqlite3

import lib.send_mail as send_mail
import lib.StreamWrapper as sw

my_domain = b"example.com"
BIND_IP = "localhost"
BIND_PORT = 587
database = "./files/mail/mail.db"
CERT_FILE="./files/encript/cert.pem"
KEY_FILE="./files/encript/privkey.pem"
async_timeout = 30.0

class smtp_StreamWrapper(sw.StreamWrapper):
    async def smtp_Send(self, b):
        if(b[-2:] != b"\r\n"):
            b += b"\r\n"
        await self.Send(b)

async def smtp_auth(reader, writer):
    addr = writer.get_extra_info("peername")
    ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
    ssl_ctx.load_cert_chain(CERT_FILE, KEY_FILE)
    ssl_ctx.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
    conn = await smtp_StreamWrapper(reader, writer, ssl_context=ssl_ctx, debug=True)
    
    flags = {b"EHLO":False,b"STARTTLS":False,b"AUTH":False,b"MAIL":False,b"RCPT":False}
    host = b""
    mail_from = b""
    rcpt_to = []
    mail_data = b""
    username = b""
    try:
        await conn.smtp_Send(b"220 STiCK-Lilith/3.0 smtp_auth on <%b> ready." % my_domain)
        while(True):
            BUFFER = await conn.Recv()
            buf = BUFFER.replace(b"\r\n", b"").split(b" ")
            command = buf[0].upper()
            if(command == b"EHLO"):
                await conn.smtp_Send(b"250-%b at you, %b" % (my_domain, addr[0].encode("utf-8")))
                await conn.smtp_Send(b"250-SIZE 157286400")
                await conn.smtp_Send(b"250-8BITMIME")
                await conn.smtp_Send(b"250-ENHANCEDSTATUSCODES")
                await conn.smtp_Send(b"250-AUTH PLAIN")
                if(not flags[b"STARTTLS"]):
                    await conn.smtp_Send(b"250-STARTTLS")
                await conn.smtp_Send(b"250 SMTPUTF8")
                flags[command]=True
            elif(command == b"QUIT"):
                await conn.smtp_Send(b"221 closing connection... bye.")
                buf = b""
            elif(flags[b"EHLO"]):
                if(command == b"STARTTLS"):
                    await conn.smtp_Send(b"220 Ready to start TLS")
                    await conn.StartTLS()
                    print("============== TLS OK ==============")
                    flags[b"EHLO"]=False
                    flags[command]=True
                elif(flags[b"STARTTLS"]):
                    if(command == b"AUTH"):
                        plain = buf[-1]
                        plain = base64.b64decode(plain).split(b"\x00")
                        user_name1 = plain[0]
                        user_name2 = plain[1]                
                        password = plain[2]
                        if(user_name1 != b""):
                            username = user_name1
                        elif(user_name2 != b""):
                            username = user_name2
                        sq_conn = sqlite3.connect(database)
                        c = sq_conn.cursor()
                        c.execute("select id from accounts where user=? and pass=?", (username.decode("utf-8"), password.decode("utf-8")))
                        r = c.fetchone()
                        sq_conn.close()
                        if(r is not None):
                            await conn.smtp_Send(b"235 OK Authenticated")
                            flags[b"AUTH"] = True
                        else:
                            command = b""
                    elif(flags[b"AUTH"]):
                        if(command == b"MAIL"):
                            mail_from = BUFFER[BUFFER.find(b"<")+1:BUFFER.find(b">")]
                            if(username == mail_from[:-len(my_domain)-1]):
                                await conn.smtp_Send(b"250 %b [%b]... Sender ok" % (mail_from, addr[0].encode("utf-8")))
                                flags[command]=True
                            else:
                                command = b""
                        elif(flags[b"MAIL"]):
                            if(command == b"RCPT"):
                                rcpt_domain = buf[-1][buf[-1].find(b"@")+1:buf[-1].find(b">")]
                                rcpt_to.append(buf[-1][buf[-1].find(b"<")+1:buf[-1].find(b">")])
                                await conn.smtp_Send(b"250 %b... Recipient ok" % (rcpt_to[-1]))
                                flags[command]=True
                            elif(flags[b"RCPT"]):
                                if(command == b"DATA"):
                                    await conn.smtp_Send(b"354 Ok, Go ahead.")
                                    while(True):
                                        d_buf = await conn.Recv()
                                        mail_data += d_buf
                                        if(d_buf[-3:] == b".\r\n"):
                                            await conn.smtp_Send(b"250 Message accepted for delivery")
                                            for to in rcpt_to:
                                                args = (mail_from.decode("utf-8"), to.decode("utf-8"))
                                                target_domain = args[1].split("@")[-1]
                                                print("< %s > searching mail server..." % target_domain)
                                                SERVERS = send_mail.get_mail_servers(target_domain.encode("utf-8"))
                                                mail_server = [10000, ""]
                                                for a in SERVERS:
                                                    print(" Priority:",a[0],"Name:",a[1])
                                                    if(a[0]<mail_server[0]):
                                                        mail_server = a
                                                print("< %s > use this... %s" % (target_domain, mail_server[1]))
                                                print("Sending...")
                                                send_mail.send_mail(server=mail_server[1], mail_from=args[0].encode("utf-8"), rcpt_to=args[1].encode("utf-8"), data=mail_data)
                                                print("Done.")
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
    server = await asyncio.start_server(smtp_auth, BIND_IP, BIND_PORT)
    async with server:
        await server.serve_forever()

def start():
    asyncio.run(main())