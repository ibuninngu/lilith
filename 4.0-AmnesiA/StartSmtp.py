import asyncio
import sys
import ssl

from Lilith.Core.Stream import AsyncStream
from Lilith.Server.Smtp import SmtpServer

##### DEFAULTS #####
HOST = "localhost"
PORT = 25
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

    async def __InitHandlerSslLater__(self, reader, writer):
        # Connection MUST be argment
        connection = await AsyncStream(reader, writer, ssl_context=self.CtxForStartTLS)
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
