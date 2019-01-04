# file: /sl_lib/parser.py

# data = "\x00\x11\x22\x33"
# bytes_format = [1, 2, 1] ... bytes
# return -> ['\x00', '\x11"', '3', '']

def bytes_parse(data, bytes_format):
    R = []
    pointer = 0
    for p in bytes_format:
        R.append(data[pointer:pointer+p])
        pointer += p
    bottom = data[pointer:]
    if(len(bottom) != 0):
        R.append(bottom)
    return R

def bytes_parseq(data, size):
    bytes_format=[size]*int(len(data)/size)
    return bytes_parse(data, bytes_format)