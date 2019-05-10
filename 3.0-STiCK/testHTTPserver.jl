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
    params = join(map(x->Char(x), params), "")
    println(params)
    params = split(params, "&")
    buf = ""
    for line in params
        buf = string(buf, "<p>$line</p>")
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
        open("$(DEF.RootDirectory)$request") do f
            return(read(f, String), "$n/$s", "200")
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
    buffer = readuntil(socket, "\r\n\r\n")
    hashes = Dict("" => "")
    splited = split(buffer, "\r\n")
    for line in splited[2:end]
        tmp = split(line, ":")
        merge!(hashes, Dict(tmp[1] => tmp[2]))
    end
    if occursin(r"GET", buffer)
        r, m, s = GET(split(splited[1], " ")[2])
        buf = MakeHttpHeader(s, m, length(r))
        write(socket, "$buf$r")
    elseif occursin(r"POST", buffer)
        r, m, s = POST(split(splited[1], " ")[2], read(socket, parse(Int64, hashes["Content-Length"])))
        buf = MakeHttpHeader(s, m, length(r))
        write(socket, "$buf$r")
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