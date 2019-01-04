# -*- coding: utf-8 -*-

import media_list

def content_detect(s):
    return(media_list.media_list[s.split(".")[1]] + "/" + s.split(".")[1])
