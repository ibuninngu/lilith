import asyncio

from Lilith.Server.Base import AsyncTcp
from Lilith.Database.Sqlite3 import MailDB


class SmtpHandler(AsyncTcp):
    async def __new__(cls, *a, **kw):
        instance = await super().__new__(cls)
        await instance.__init__(*a, **kw)
        return instance

    async def __init__(self, host, port, ssl_context):
        await super().__init__(host, port, ssl_context)
        self.MyDomain = b""
        self.ServerFunctions = {
            b"HELO": self.HELO,
            b"EHLO": self.EHLO,
            b"MAIL": self.MAIL,
            b"RCPT": self.RCPT,
            b"DATA": self.DATA,
            b"QUIT": self.QUIT,
            b"STARTTLS": self.STARTTLS
        }

    async def HELO():
        pass

    async def EHLO():
        pass

    async def MAIL():
        pass

    async def RCPT():
        pass

    async def DATA():
        pass

    async def QUIT():
        pass

    async def STARTTLS():
        pass

    async def Handler(self, connection):
        try:
            database_driver = MailDB()
            await connection.Send(b"220 AmnesiA-Lilith/4.0 smtp on <%b> ready.\r\n" % self.MyDomain)
            while(connection.OnLine):
                buf = await connection.Recv()
                if(len(buf) == 0):
                    await connection.Close()
                    return
                commands = []
                for c in buf.split(b"\r\n")[:-1]:
                    commands += [c.split(b" ")]
                for command in commands:
                    await self.ServerFunctions[command[0].upper()](connection, command[1:], database_driver)
        except:
            import traceback
            traceback.print_exc()
            await connection.Close()
