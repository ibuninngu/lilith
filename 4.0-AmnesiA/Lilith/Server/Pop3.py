import asyncio
import hashlib

from Lilith.Server.Handler.Pop3 import Pop3Handler


class Pop3Server(Pop3Handler):
    async def __new__(cls, *a, **kw):
        instance = await super().__new__(cls)
        await instance.__init__(*a, **kw)
        return instance

    async def __init__(self, host, port, ssl_context):
        await super().__init__(host, port, ssl_context)

    async def CAPA(self, connection, payload, database):
        await connection.Send(b"+ OK Capability list follows\r\n")
        await connection.Send(b"STAT\r\nLIST\r\nUIDL\r\nRETR\r\nDELE\r\nCAPA\r\nQUIT\r\nNOOP\r\nUSER\r\nPASS\r\n.\r\n")

    async def USER(self, connection, payload, database):
        database.User = payload[0].decode("utf-8")
        await connection.Send(b"+OK password please\r\n")

    async def PASS(self, connection, payload, database):
        database.Password = hashlib.md5(payload[0]).hexdigest()
        if(database.Auth()):
            await connection.Send(b"+OK authed\r\n")
        else:
            await connection.Send(b"-ERR \r\n")
            await connection.Close()

    async def QUIT(self, connection, payload, database):
        await connection.Send(b"+OK Bye.\r\n")
        database.Close()
        await connection.Close()

    async def NOOP(self, connection, payload, database):
        await connection.Send(b"+OK \r\n")

    async def STAT(self, connection, payload, database):
        if(database.is_Authed):
            mail_vol, mail_octets = database.GetStat()
            await connection.Send((b"+OK %d %d\r\n" % (mail_vol, mail_octets)))
        else:
            await connection.Send(b"-ERR \r\n")

    async def LIST(self, connection, payload, database):
        if(database.is_Authed):
            R = database.GetList()
            await connection.Send(b"+OK\r\n" + R + b".\r\n")
        else:
            await connection.Send(b"-ERR \r\n")

    async def UIDL(self, connection, payload, database):
        if(database.is_Authed):
            R = database.GetUidl(payload)
            await connection.Send(R)
        else:
            await connection.Send(b"-ERR \r\n")

    async def RETR(self, connection, payload, database):
        if(database.is_Authed):
            R = database.Retr(int(payload[0]) - 1)
            buf = (b"+OK %d octets\r\n" % (R[0]))
            await connection.Send(b"+OK\r\n" + buf + R[1].encode("utf-8") + b".\r\n")
        else:
            await connection.Send(b"-ERR \r\n")

    async def TOP(self, connection, payload, database):
        if(database.is_Authed):
            lines = int(payload[1])
            R = database.Retr(int(payload[0]))
            buf = (b"+OK %d lines\r\n" % (lines))
            msg = R[1].split("\\r\\n")
            for m in msg:
                if(lines == 0):
                    buf += b"."
                    break
                buf += m.encode("utf-8") + b"\r\n"
                lines += 1
            await connection.Send(buf)
        else:
            await connection.Send(b"-ERR \r\n")

    async def DELE(self, connection, payload, database):
        if(database.is_Authed):
            database.Delete(int(payload[0])-1)
            database.Commit()
            await connection.Send(b"+OK message deleted\r\n")
        else:
            await connection.Send(b"-ERR \r\n")
