(import asyncio)
(import [Lilith.Core.Stream [AsyncStream]])

(setv StatusCodes {
    200 b"200 OK"
    404 b"404 Not Found"
})

(setv MIME {
    b"txt" b"text/plain"
    b"html" b"text/html"
    b"css" b"text/css"
    b"js" b"text/js"
    b"jpg" b"image/jpg"
    b"jpeg" b"image/jpeg"
    b"png" b"image/png"
    b"gif" b"image/gif"
    b"ico" b"image/ico"
    b"mp4" b"video/mp4"
    b"mp3" b"audio/mp3"
    b"otf" b"application/x-font-otf"
    b"woff" b"application/x-font-woff"
    b"ttf" b"application/x-font-ttf"
})

(setv ResponceHeader [
    b"HTTP/1.1 "
    b"Server: "
    b"Accept-Ranges: "
    b"Content-Length: "
    b"Keep-Alive: "
    b"Content-Type: "
    ]
)

(setv ContentLengthLimit (* 1024 1024))
(setv DefaultFile b"/index.html")
(setv RootDirectory b"./SampleContents")

(defn NewHeader [] {
    b"Status" 0
    b"Server" b"AmnesiA-Lilith/4.0"
    b"Accept-Ranges" b"bytes"
    b"Content-Length" 0
    b"Keep-Alive" b"timeout=30, max=100"
    b"Content-Type" b""
    b"Additional" []
    b"ReplyContent" b""
})

(setv GePtFunctions {
    ; b"/PostTest" PostTest
})

(defn/a Reply [connection header]
    (setv R 
        (+
            b"HTTP/1.1 " (get StatusCodes (get header b"Status"))
            b"\r\nServer: " (get header b"Server")
            b"\r\nAccept-Ranges: " (get header b"Accept-Ranges")
            b"\r\nContent-Length: " ((. (str (len (get header b"ReplyContent"))) encode) "utf-8")
            b"\r\nKeep-Alive: " (get header b"Keep-Alive")
            b"\r\nContent-Type: " (get header b"Content-Type")
            b"\r\n"
        )
    )
    (for [a (get header b"Additional")]
        (+= R (+ a b"\r\n"))
    )
    
    (await (connection.Send (+ R b"\r\n" (get header b"ReplyContent"))))
)

(defn/a Get [connection Request]
    (print Request)
    (if (!= ((. (get Request b"path") find) b"?") -1)
        (do
            (setv data ((. (get Request b"path") split) b"?"))
            (Request.update {b"path" (get data 0)})
            (Request.update {b"content" (get data 1)})
            (try
                (await ((get GePtFunctions (get Request b"path")) connection Request))
            (except [e KeyError] (print "?ContentNotFound"))
            )
        )
    )
    (try
        (setv ResponceHeader (NewHeader))
        (if (= (get Request b"path") b"/")
            (Request.update {b"path" DefaultFile})
        )
        (with [fp (open (+ RootDirectory (get Request b"path")) "rb")]
            (ResponceHeader.update {b"ReplyContent" (fp.read)})
        )
        (ResponceHeader.update
            {b"Content-Type" (get MIME
                    (cut (get Request b"path") (+ ((. (get Request b"path") find) b".") 1))
                )
            }
        )
        (ResponceHeader.update {b"Status" 200})
    (except [e KeyError] (print "?ContentNotFound"))
    )
    (await (Reply connection ResponceHeader))
)

(defn/a Post [connection Request]

)

(setv ServerFunctions {
    b"GET" Get
    b"POST" Post
})

(defn/a handler [connection]
    (setv Request {})
    (try
        (while connection.OnLine
            (if (= 0 (len (setx buf (await (connection.Recv)))))
                (do
                    (await (connection.Close)) (return)
                )
            )
            (setv Request {})
            (setv body_pointer (buf.find b"\r\n\r\n"))
            (setv headers ((. (cut buf 0 body_pointer) split) b"\r\n"))
            (setv request ((. (get headers 0) split) b" "))
            (Request.update {b"method" (get request 0)})
            (Request.update {b"path" (get request 1)})
            (Request.update {b"version" (get request 2)})

            (try
                (for [param [(cut headers 1)]]
                    (setv p (param.split b": "))
                    (Request.update {(get p 0) (get p 1)})
                )
                (except [])
            )

            (if (= (get Request b"method") b"GET")
                    (do )
                (= (get Request b"method") b"POST")
                    (do
                        (setv body (cut buf (+ body_pointer 4)))
                        (if (< ContentLengthLimit (int (get Request b"Content-Length")))
                            (do
                                (await (connection.Close)) (break)
                            )
                        )
                        (while (< (len body) (int (get Request b"Content-Length")))
                            (+= body (await (connection.Recv)))
                        )
                        (Request.update {b"content" body})
                    )
                ; else
                ((await (connection.Close)) (return))
            )
            (await ((get ServerFunctions (get Request b"method")) connection Request))
        )
    (except []
        (import traceback)
        (traceback.print_exc)
        (connection.Close)
    )
    )
)

(defn/a init_connection [reader writer]
    (await (handler
        ; (await (AsyncStream reader writer :ssl_context None :debug True)))
        (await (AsyncStream reader writer :ssl_context None)))
    )
)

(defn/a main []
    (print (setx bind_ip "127.0.0.1") (setx bind_port 8080))
    (with/a [server
        (await
            (asyncio.start_server init_connection bind_ip bind_port)
        )]
        (await (server.serve_forever))
    )
)

(asyncio.run (main))
