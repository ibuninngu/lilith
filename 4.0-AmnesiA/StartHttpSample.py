import asyncio
import socket

from Lilith.Server.Http import HttpServer

status_codes = {
    200: b"200 OK",
    303: b"303 See Other",
    304: b"304 Not Modified",
    400: b"400 Bad Request",
    401: b"401 Unauthorized",
    403: b"403 Forbidden",
    404: b"404 Not Found",
    408: b"408 Request Timeout",
    411: b"411 Length Required",
    413: b"413 Payload Too Large",
    414: b"414 URI Too Long",
    415: b"415 Unsupported Media Type",
    418: b"418 I'm a teapot",
    421: b"421 Misdirected Request",
    426: b"426 Upgrade Required",
    451: b"451 Unavailable For Legal Reasons",
    500: b"500 Internal Server Error",
    501: b"501 Not Implemented",
    502: b"502 Bad Gateway",
    505: b"505 HTTP Version Not Supported"
}

mime = {
    b"txt": b"text/plain",
    b"html": b"text/html",
    b"css": b"text/css",
    b"js": b"text/js",
    b"jpg": b"image/jpg",
    b"jpeg": b"image/jpeg",
    b"png": b"image/png",
    b"gif": b"image/gif",
    b"ico": b"image/ico",
    b"mp4": b"video/mp4",
    b"mp3": b"audio/mp3",
    b"otf": b"application/x-font-otf",
    b"woff": b"application/x-font-woff",
    b"ttf": b"application/x-font-ttf"
}

##### DEFAULTS #####
HOST = "localhost"
PORT = 80
SSL_CONTEXT = None
####################

class HttpInitialize(HttpServer):
    async def __new__(cls, *a, **kw):
        instance = await super().__new__(cls)
        await instance.__init__(*a, **kw)
        return instance

    async def __init__(self, host=HOST, port=PORT, ssl_context=SSL_CONTEXT):
        await super().__init__(host, port, ssl_context)
        self.StatusCodes = status_codes
        self.MIME = mime
        self.RootDirectory = b"./"
        self.MessageDirectory = b"./"
        self.PostFunctions = {}
        self.GePtFunctions = {}
        self.PostFunctions = {b"/PostTest.post": self.PostTest}
        self.GePtFunctions = {b"/PostTest.post": self.PostTest}

    async def Get(self, connection, Request, ReplyHeader):
        print("GET", Request[b"path"])
        await super().Get(connection, Request, ReplyHeader)

    async def Post(self, connection, Request, ReplyHeader):
        print("POST", Request[b"path"], Request[b"content"])
        await super().Post(connection, Request, ReplyHeader)

    async def PostTest(self, connection, Request, ReplyHeader):
        print(Request[b"content"])
        ReplyHeader[b"ReplyContent"] = Request[b"content"]
        ReplyHeader[b"Content-Type"] = b"text/html"
        ReplyHeader[b"Status"] = 200
        await self.Reply(connection, ReplyHeader)

async def start():
    HOST = socket.gethostbyname(socket.gethostname())
    PORT = 80
    CTX = None
    print(HOST, PORT, CTX)
    http_server = await HttpInitialize(host=HOST, port=PORT, ssl_context=CTX)
    http_server.RootDirectory = b"./SampleContents"
    http_server.MessageDirectory = b"./SampleContents"
    await http_server.Start()

asyncio.run(start())
