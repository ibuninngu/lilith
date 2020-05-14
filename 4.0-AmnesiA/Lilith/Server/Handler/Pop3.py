import asyncio

from Lilith.Server.Base import AsyncTcp
from Lilith.Database.Sqlite3 import MailDB


class Pop3Handler(AsyncTcp):
    async def __new__(cls, *a, **kw):
        instance = await super().__new__(cls)
        await instance.__init__(*a, **kw)
        return instance

    async def __init__(self, host, port, ssl_context):
        await super().__init__(host, port, ssl_context)

        self.ServerFunctions = {
            b"CAPA": self.CAPA,
            b"USER": self.USER,
            b"PASS": self.PASS,
            b"QUIT": self.QUIT,
            b"NOOP": self.NOOP,
            b"STAT": self.STAT,
            b"LIST": self.LIST,
            b"UIDL": self.UIDL,
            b"RETR": self.RETR,
            b"TOP": self.TOP,
            b"DELE": self.DELE
        }

    async def CAPA():
        pass

    async def USER():
        pass

    async def PASS():
        pass

    async def QUIT():
        pass

    async def NOOP():
        pass

    async def STAT():
        pass

    async def LIST():
        pass

    async def UIDL():
        pass

    async def RETR():
        pass

    async def TOP():
        pass

    async def DELE():
        pass

    async def Handler(self, connection):
        try:
            database_driver = MailDB()
            await connection.Send(b"+OK AmnesiA-Lilith/4.0 pop3 ready.\r\n")
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
