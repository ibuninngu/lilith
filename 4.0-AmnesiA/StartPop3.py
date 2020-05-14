import asyncio
import sys
import ssl

from Lilith.Server.Pop3 import Pop3Server

##### DEFAULTS #####
HOST = "localhost"
PORT = 995
SSL_CONTEXT = None
####################


class Pop3Initialize(Pop3Server):
    async def __new__(cls, *a, **kw):
        instance = await super().__new__(cls)
        await instance.__init__(*a, **kw)
        return instance

    async def __init__(self, host=HOST, port=PORT, ssl_context=SSL_CONTEXT):
        await super().__init__(host, port, ssl_context)


async def start():
    print(sys.argv)
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    CTX = None
    if(len(sys.argv) == 5):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
        ctx.load_cert_chain(sys.argv[3], sys.argv[4])
        ctx.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        CTX = ctx
    print(HOST, PORT, CTX)
    pop3_server = await Pop3Initialize(host=HOST, port=PORT, ssl_context=CTX)
    await pop3_server.Start()

if(len(sys.argv) < 3):
    print("[usage] python3 StartPop3.py <bind ip address> <bind port> <SSL:cert.pem> <SSL:key.pem>")
    exit()

asyncio.run(start())
