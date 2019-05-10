using Sockets

module DEF
    ServerName = "STiCK-Lilith/3.0"
    ListenPort = 80
    RootDirectory = "./contents"
    MediaList = Dict("html" => "text",
                    "css" => "text",
                    "js" => "text",
                    "jpg" => "image",
                    "png" => "image",
                    "mp4" => "video",
                    "mp3" => "audio",
                    "ico" => "image")

function PostTest(params)
    params = split(string(params), "&")
    buf = ""
    for line in params
        buf = string(buf, "<p>", line, "</p>")
    end
    return(buf, "text/html", "200")
end

    PostList = Dict("/PostTest.post" => PostTest)

end

function MakeHttpHeader(Status = "200", ContentType = "media/binary",  ContentLength = "0", KeepAlive = "timeout=15, max=100", Server = DEF.ServerName, AcceptRanges = "bytes")
    return(
        """
        HTTP/1.1 $Status\r
        Server: $Server\r
        Accept-Ranges: $AcceptRanges\r
        Content-Length: $ContentLength\r
        Keep-Alive: $KeepAlive\r
        Content-Type: $ContentType\r
        \r
        """)
end

function GET(request)
    if request == "/"
        request = "/index.html"
    end
    println("GET...> $request")
    try
        s = request[findfirst(isequal('.'), request) + 1:end]
        n = DEF.MediaList[s]
        open("$(DEF.RootDirectory)$request", "r") do f
            return(read(f), "$n/$s", "200")
        end
    catch
        return("404", "text/html", "404")
    end
end

function POST(target, request)
    println("POST...> $target ::: $request")
    try
        return(DEF.PostList[target](request))
    catch
        return("500", "text/html", "500")
    end
end

function ClientHandler(socket)
    buffer = String(readavailable(socket))
    hashes = Dict("" => "")
    splited = split(buffer, "\r\n")
    for line in splited[2:end - 2]
        tmp = split(line, ":")
        merge!(hashes, Dict(tmp[1] => tmp[2]))
    end
    if "GET" == splited[1][1:3]
        r, m, s = GET(split(splited[1], " ")[2])
        buf = Vector{UInt8}(MakeHttpHeader(s, m, length(r)))
        append!(buf, r)
        write(socket, buf)
    elseif "POST" == splited[1][1:4]
        r, m, s = POST(split(splited[1], " ")[2], splited[end])
        buf = Vector{UInt8}(MakeHttpHeader(s, m, length(r)))
        append!(buf, r)
        write(socket, buf)
    else
        close(socket)
    end
    return
end

server = listen(DEF.ListenPort)
while true
    client = accept(server)
    @async while isopen(client)
        ClientHandler(client)
    end
end