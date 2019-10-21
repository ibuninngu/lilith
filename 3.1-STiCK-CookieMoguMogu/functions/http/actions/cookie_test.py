def cookie_test(params, header):
    print(params, header)
    return(b"Set-Cookie: Session=session\r\nSet-Cookie: Lilith=3.1", "text/html", 200, "Set-Cookie: Session=session\r\nSet-Cookie: Lilith=3.1")