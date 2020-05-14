import asyncio
import hashlib

from Lilith.Server.Handler.Smtp import SmtpHandler


class SmtpServer(SmtpHandler):
    async def __new__(cls, *a, **kw):
        instance = await super().__new__(cls)
        await instance.__init__(*a, **kw)
        return instance

    async def __init__(self, host, port, ssl_context):
        await super().__init__(host, port, ssl_context)

    async def HELO(self, connection, payload, database):
        self.EHLO(connection, payload, database)

    async def EHLO(self, connection, payload, database):
        await connection.Send(b"250-%b at you, %b\r\n" % (self.MyDomain, connection.PeerInfo[0].encode("utf-8")))
        await connection.Send(b"250-SIZE 157286400\r\n")
        await connection.Send(b"250-8BITMIME\r\n")
        await connection.Send(b"250-ENHANCEDSTATUSCODES\r\n")
        if(not database.was_starttls):
            await connection.Send(b"250-STARTTLS\r\n")
        await connection.Send(b"250 SMTPUTF8\r\n")
        database.was_hello = True

    async def MAIL(self, connection, payload, database):
        if(database.was_hello):
            database.MailFrom = b""
            database.MailFrom = payload[-1][payload[-1].find(
                b"<")+1:payload[-1].find(b">")]
            await connection.Send(b"250 %b... Sender ok\r\n" % database.MailFrom)
            database.AckMail = True
        else:
            await connection.Send(b"502 hmm, nop.\r\n")
            await connection.Close()

    async def RCPT(self, connection, payload, database):
        if(database.AckMail):
            database.RcptTo = []
            rcpt_domain = payload[-1][payload[-1].find(
                b"@")+1:payload[-1].find(b">")]
            if(rcpt_domain == self.MyDomain):
                database.RcptTo.append(
                    payload[-1][payload[-1].find(b"<")+1:payload[-1].find(b"@")])
                await connection.Send(b"250 %b... Recipient ok\r\n" % (database.RcptTo[-1]))
        else:
            await connection.Send(b"502 hmm, nop.\r\n")
            await connection.Close()

    async def DATA(self, connection, payload, database):
        if(0 < len(database.RcptTo) and len(database.RcptTo) < 10):
            await connection.Send(b"354 Ok, Go ahead.\r\n")
            mail_data = b""
            while(True):
                d_buf = await connection.Recv()
                mail_data += d_buf
                if(d_buf[-3:] == b".\r\n"):
                    await connection.Send(b"250 Message accepted for delivery\r\n")
                    for to in database.RcptTo:
                        try:
                            database.RecvMail(to, mail_data)
                        except:
                            import traceback
                            traceback.print_exc()
                            await connection.Close()
                    database.Commit()
                    break
        else:
            await connection.Send(b"502 hmm, nop.\r\n")
            await connection.Close()

    async def QUIT(self, connection, payload, database):
        await connection.Send(b"221 closing connection... bye.\r\n")
        database.Close()
        await connection.Close()

    async def STARTTLS(self, connection, payload, database):
        if(database.was_hello):
            await connection.Send(b"220 Ready to start TLS\r\n")
            await connection.StartTLS()
            database.was_hello = False
            database.was_hello = False
            database.AckMail = False
            database.RcptTo = []
            database.MailFrom = None
        else:
            await connection.Send(b"502 hmm, nop.\r\n")
            await connection.Close()
