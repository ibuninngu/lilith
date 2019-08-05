import asyncio
import ssl

########## DEFAULT DEFINES ##########
DEFAULT_TIMEOUT = 30.0
RECV_SIZE = 1024 * 4
TLS_READ_SIZE = 8
#####################################

# Stream wrapper for asyncio.start_server, serve_forever
class StreamWrapper():
    async def __new__(cls, *a, **kw):
        instance = super().__new__(cls)
        await instance.__init__(*a, **kw)
        return instance
    async def __init__(self, reader, writer, recvsize=RECV_SIZE, timeout=DEFAULT_TIMEOUT, ssl_context=None, tls_read_size=TLS_READ_SIZE, debug=False):
        self.__Reader = reader
        self.__Writer = writer
        self.__Recvsize = recvsize
        self.__Timeout = timeout
        self.__SSL_context = ssl_context
        self.__tls_Readsize = tls_read_size
        self.__tls_in_buff = None
        self.__tls_out_buff = None
        self.__tls_obj = None
        self.__PeerInfo = writer.get_extra_info("peername")
        self.__Debug = debug
        
        self.__normal_send = self.__non_ssl_send
        self.__normal_recv = self.__non_ssl_recv
        if(self.__Debug):
            print("PeerInfo ip:",self.__PeerInfo[0],"port:",self.__PeerInfo[1])
            self.Send = self.__debug_send
            self.Recv = self.__debug_recv
            self.Close = self.__debug_close
        else:
            self.Send = self.__normal_send
            self.Recv = self.__normal_recv
            self.Close = self.__normal_close
    ### Send ###
    async def Send():
        pass
    async def __normal_send():
        pass    
    async def __debug_send(self, b):
        print("SEND...>>>",b)
        await self.__normal_send(b)
    async def __non_ssl_send(self, b):
        self.__Writer.write(b)
        await asyncio.wait_for(self.__Writer.drain(), timeout=self.__Timeout)
    async def __ssl_send(self, b):
        self.__tls_obj.write(b)
        self.__Writer.write(self.__tls_out_buff.read())
        await asyncio.wait_for(self.__Writer.drain(), timeout=self.__Timeout)
    ### Recv ###
    async def Recv():
        pass
    async def __normal_recv():
        pass    
    async def __debug_recv(self, i=0):
        R = await self.__normal_recv(i)
        print("<<<...RECV", self.__PeerInfo[0], R)
        return(R)
    async def __non_ssl_recv(self, i=0):
        R = b""
        if(i==0):
            i = self.__Recvsize        
        R = await asyncio.wait_for(self.__Reader.read(i), timeout=self.__Timeout)
        return(R)
    async def __ssl_recv(self, i=0):
        R = b""
        if(i==0):
            i = self.__Recvsize
        self.__tls_in_buff.write(await asyncio.wait_for(self.__Reader.read(i), timeout=self.__Timeout))
        while(True):
            try:
                R += self.__tls_obj.read(self.__tls_Readsize)
            except:
                break
        return(R)
    async def StartTLS(self):
        self.__normal_send = self.__ssl_send
        self.__normal_recv = self.__ssl_recv
        if(self.__Debug):
            self.Send = self.__debug_send
            self.Recv = self.__debug_recv
            self.Close = self.__debug_close
        else:
            self.Send = self.__normal_send
            self.Recv = self.__normal_recv
            self.Close = self.__normal_close
            
        self.__tls_in_buff = ssl.MemoryBIO()
        self.__tls_out_buff = ssl.MemoryBIO()
        self.__tls_obj = self.__SSL_context.wrap_bio(self.__tls_in_buff, self.__tls_out_buff, server_side=True)
        # || TLS Handshake
        self.__tls_in_buff.write(await asyncio.wait_for(self.__Reader.read(self.__Recvsize), timeout=self.__Timeout))
        try:
            self.__tls_obj.do_handshake()
        except ssl.SSLWantReadError:
            self.__Writer.write(self.__tls_out_buff.read())
            await asyncio.wait_for(self.__Writer.drain(), timeout=self.__Timeout)
            self.__tls_in_buff.write(await asyncio.wait_for(self.__Reader.read(self.__Recvsize), timeout=self.__Timeout))
            self.__tls_obj.do_handshake()
            self.__Writer.write(self.__tls_out_buff.read())
            await asyncio.wait_for(self.__Writer.drain(), timeout=self.__Timeout)
        # -- TLS Handshake
    def Close():
        return
    def __debug_close(self):
        self.__Writer.close()
        print("Peer",self.__PeerInfo[0],"closed")
    def __normal_close(self):
        self.__Writer.close()
