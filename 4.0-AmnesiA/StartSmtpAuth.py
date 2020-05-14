import asyncio
import sys
import ssl
import hashlib
import base64

from Lilith.Core.Stream import AsyncStream
from Lilith.Server.Smtp import SmtpServer
from Lilith.Lib.send_mail import send_mail, get_mail_servers

##### DEFAULTS #####
HOST = "localhost"
PORT = 587
SSL_CONTEXT = None
####################


class SmtpInitialize(SmtpServer):
    async def __new__(cls, *a, **kw):
        instance = await super().__new__(cls)
        await instance.__init__(*a, **kw)
        return instance

    async def __init__(self, my_domain=None, Ctx=None, host=HOST, port=PORT, ssl_context=SSL_CONTEXT):
        await super().__init__(host, port, ssl_context)
        self.MyDomain = my_domain
        self.CtxForStartTLS = Ctx
        self.ServerFunctions[b"AUTH"] = self.AUTH

    async def EHLO(self, connection, payload, database):
        await connection.Send(b"250-%b at you, %b\r\n" % (self.MyDomain, connection.PeerInfo[0].encode("utf-8")))
        await connection.Send(b"250-SIZE 157286400\r\n")
        await connection.Send(b"250-8BITMIME\r\n")
        await connection.Send(b"250-ENHANCEDSTATUSCODES\r\n")
        await connection.Send(b"250-AUTH PLAIN\r\n")
        if(not database.was_starttls):
            await connection.Send(b"250-STARTTLS\r\n")
        await connection.Send(b"250 SMTPUTF8\r\n")
        database.was_hello = True

    async def AUTH(self, connection, payload, database):
        if(database.was_starttls or True):
            plain = payload[-1]
            plain = base64.b64decode(plain).split(b"\x00")
            user_name1 = plain[0]
            user_name2 = plain[1]
            password = plain[2]
            if(user_name1 != b""):
                username = user_name1
            elif(user_name2 != b""):
                username = user_name2
            database.User = username.decode("utf-8")
            database.Password = hashlib.md5(password).hexdigest()
            print(database.User, database.Password)
            if(database.Auth()):
                await connection.Send(b"235 OK Authenticated\r\n")
            else:
                await connection.Send(b"502 hmm, nop.\r\n")
                await connection.Close()
        else:
            await connection.Send(b"502 hmm, nop.\r\n")
            await connection.Close()

    async def MAIL(self, connection, payload, database):
        if(database.Auth()):
            await super().MAIL(connection, payload, database)
        else:
            await connection.Send(b"502 hmm, nop.\r\n")
            await connection.Close()

    async def RCPT(self, connection, payload, database):
        if(database.Auth() and database.AckMail):
            database.RcptTo = []
            for p in payload:
                if(p.find(b"<") != -1 and p.find(b"<") != -1):
                    database.RcptTo.append(p[p.find(b"<")+1:p.find(b">")])
            await connection.Send(b"250 %b... Recipient ok\r\n" % (database.RcptTo[-1]))
        else:
            await connection.Send(b"502 hmm, nop.\r\n")
            await connection.Close()

    async def DATA(self, connection, payload, database):
        if(database.Auth()):
            await connection.Send(b"354 Ok, Go ahead.\r\n")
            mail_data = b""
            while(True):
                d_buf = await connection.Recv()
                mail_data += d_buf
                if(d_buf[-3:] == b".\r\n"):
                    await connection.Send(b"250 Message accepted for delivery\r\n")
                    for to in database.RcptTo:
                        args = (
                            database.MailFrom.decode("utf-8"),
                            to.decode("utf-8"))
                        target_domain = args[1].split("@")[-1]
                        SERVERS = get_mail_servers(
                            target_domain.encode("utf-8"))
                        mail_server = [10000, ""]
                        for a in SERVERS:
                            if(a[0] < mail_server[0]):
                                mail_server = a
                        send_mail(server=mail_server[1], mail_from=args[0].encode(
                            "utf-8"), rcpt_to=args[1].encode("utf-8"), data=mail_data)
                    break
        else:
            await connection.Send(b"502 hmm, nop.\r\n")
            await connection.Close()

    async def __InitHandlerSslLater__(self, reader, writer):
        # Connection MUST be argment
        connection = await AsyncStream(reader, writer, ssl_context=self.CtxForStartTLS, debug=True)
        await self.Handler(connection)

    async def Start(self):
        server = await asyncio.start_server(self.__InitHandlerSslLater__, self._Host, self._Port)
        async with server:
            await server.serve_forever()


async def start():
    print(sys.argv)
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    CTX = None
    if(len(sys.argv) == 6):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
        ctx.load_cert_chain(sys.argv[4], sys.argv[5])
        ctx.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        CTX = ctx
    print(HOST, PORT, CTX)
    smtp_server = await SmtpInitialize(my_domain=sys.argv[3].encode("utf-8"), Ctx=CTX, host=HOST, port=PORT, ssl_context=None)
    await smtp_server.Start()

if(len(sys.argv) < 3):
    print("[usage] python3 StartSmtp.py <bind ip address> <bind port> <bind domain> <SSL:cert.pem> <SSL:key.pem>")
    exit()

asyncio.run(start())
