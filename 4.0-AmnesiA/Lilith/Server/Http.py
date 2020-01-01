import asyncio

from Lilith.Server.Handler.Http import HttpHandler


class HttpServer(HttpHandler):
    async def __new__(cls, *a, **kw):
        instance = await super().__new__(cls)
        await instance.__init__(*a, **kw)
        return instance

    async def __init__(self, host, port, ssl_context):
        await super().__init__(host, port, ssl_context)
        self.RootDirectory = b"./"
        self.MessageDirectory = b"./"
        self.DefaultFile = b"/index.html"
        self.PostFunctions = {}
        self.GePtFunctions = {}
        self.StatusCodes = {}
        self.MIME = {}
        self._Header = (
            b"HTTP/1.1 %b\r\n" +
            b"Server: %b\r\n" +
            b"Accept-Ranges: %b\r\n" +
            b"Content-Length: %i\r\n" +
            b"Keep-Alive: %b\r\n" +
            b"Content-Type: %b\r\n"
        )
        self.Status = 0
        self.ServerName = b"AmnesiA-Lilith/4.0"
        self.AcceptRanges = b"bytes"
        self.ContentLength = 0
        self.KeepAlive = b"timeout=30, max=100"
        self.ContentType = b""
        self.Additional = []
        self.ReplyContent = b""
        self._ReplyBuffer = b""

    async def Flush(self):
        self._ReplyBuffer = b""

    async def Reply(self, connection):
        self._ReplyBuffer = self._Header % (
            self.StatusCodes[self.Status],
            self.ServerName,
            self.AcceptRanges,
            len(self.ReplyContent),
            self.KeepAlive,
            self.ContentType)

        for a in self.Additional:
            self._ReplyBuffer += a + b"\r\n"

        await connection.Send(self._ReplyBuffer + b"\r\n" + self.ReplyContent)
        await self.Flush()

    async def Get(self, connection):
        if(self.Request[b"path"].find(b"?") != -1):
            data = self.Request[b"path"].split(b"?")
            self.Request[b"path"] = data[0]
            self.Request.update({b"content": data[1]})
            try:
                await self.GePtFunctions[self.Request[b"path"]](connection)
            except KeyError as error:
                try:
                    f = open(self.MessageDirectory + b"/404.html", "rb")
                    self.ReplyContent = f.read()
                    f.close()
                    self.ContentType = b"text/plain"
                    self.Status = 404
                except:
                    self.ReplyContent = b"ContentNotFound & 404 Message Not Found :("
                    self.ContentType = b"text/plain"
                    self.Status = 404
                await self.Reply(connection)
        else:
            try:
                if(self.Request[b"path"] == b"/"):
                    self.Request[b"path"] = self.DefaultFile
                f = open(self.RootDirectory + self.Request[b"path"], "rb")
                self.ReplyContent = f.read()
                f.close()
                try:
                    self.ContentType = self.MIME[
                        self.Request[b"path"].split(b".")[1]
                    ]
                    self.Status = 200
                except:
                    f = open(self.MessageDirectory + b"/415.html", "rb")
                    self.ReplyContent = f.read()
                    f.close()
                    self.ContentType = b"text/html"
                    self.Status = 415
            except:
                try:
                    f = open(self.MessageDirectory + b"/404.html", "rb")
                    self.ReplyContent = f.read()
                    f.close()
                    self.ContentType = b"text/plain"
                    self.Status = 404
                except:
                    self.ReplyContent = b"ContentNotFound & 404 Message Not Found :("
                    self.ContentType = b"text/plain"
                    self.Status = 404
            await self.Reply(connection)

    async def Post(self, connection):
        try:
            await self.PostFunctions[self.Request[b"path"]](connection)
        except KeyError as error:
            try:
                f = open(self.MessageDirectory + b"/404.html", "rb")
                self.ReplyContent = f.read()
                f.close()
                self.ContentType = b"text/plain"
                self.Status = 404
            except:
                self.ReplyContent = b"ContentNotFound & 404 Message Not Found :("
                self.ContentType = b"text/plain"
                self.Status = 404
            await self.Reply(connection)
