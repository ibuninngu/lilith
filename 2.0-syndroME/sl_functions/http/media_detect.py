import sl_defines.http.media_list as media_list

def media_detect(s):
    try:
        return(media_list.media_list[s.split(".")[1]] + "/" + s.split(".")[1], 200)
    except:
        return("",415)