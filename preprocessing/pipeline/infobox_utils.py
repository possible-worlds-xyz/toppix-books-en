# SPDX-FileCopyrightText: Aurelie Herbelot, <aurelie.herbelot@cantab.net> 
#
# SPDX-License-Identifier: AGPL-3.0-only


import re

def mk_regex():
    #Adapted from https://raw.githubusercontent.com/woutster/wikipedia_infobox_parser/master/scraper.py
    box_title = None

    #Build a regexp to get the source artery from the artery infobox
    exp = r'\{\{'                  # the opening brackets for the infobox
    exp = exp + r'\s*'           # any amount of whitespace
    exp = exp + r'[Ii]nfobox book+'  # the word "infobox", capitalized or not followed by at least one space
    if box_title:
        exp = exp + box_title     # the infobox title, capitalized or not
        exp = exp + r'\s*\|'         # any number of spaces or returns followed by a pipe character
    exp = exp + r'.*'           # a bunch of other stuff in the infobox
    exp3 = exp                  # save the regexp so far so that I can use it later
    exp3 = exp3 + r'.*\}\}'          # any amount of anything, followed by the end of the infobox

    exp3_obj = re.compile(exp3, re.DOTALL)
    return exp3_obj

def get_infobox_from_text(article_text):
    exp3_obj = mk_regex()
    search_result = exp3_obj.search(article_text)
    if search_result:
        result_text = search_result.group(0) # returns the entire matching sequence
    else:
        return None
    # the regex isn't perfect, so look for the closing brackets of the infobox
    count = 0
    last_ind = None
    for ind, c in enumerate(result_text):
        if c == '}':
            count = count -1
        elif c == '{':
            count = count +1
        if count == 0 and not ind == 0:
            last_ind = ind
            break
    return result_text[0:last_ind+1]

def process_string(s):
    proc = s.replace("&lt;","<").replace("&gt;",">")
    proc = re.sub("<br\s*/*>"," AND ",proc)
    proc = re.sub("<!--[^>]*>","",proc)
    matches = re.findall("<ref[^<]*</ref>",proc)
    for m in matches:
        proc = proc.replace(m,"")
    matches = re.findall("<ref name[^>]*>",proc)
    for m in matches:
        proc = proc.replace(m,"")
    matches = re.findall("\[\[([^\]]*)\|([^\]]*)\]\]",proc)
    for m in matches:
        proc = proc.replace(m[0]+"|","")

    m = re.search("{{([^}]*)}}",proc)
    if m:
        l = m.group(1).split('|')
        if any(l[0].lower() in u for u in ['ubl', 'unbulleted list']) and len(l) > 1:
            proc = ' AND '.join(l[1:])
        if any(l[0].lower() in u for u in ['plainlist', 'plain list']) and len(l) > 1:
            proc = l[1][2:].replace('*',' AND ')
    proc = proc.replace("[[","").replace("]]","")
    return proc

def parse_infobox_text(text, outf):
    k = ""
    v = ""
    text = text.split('\n')
    print(text)
    for l in text:
        m = re.search('(\S*)\s*=\s*(.*)',l)
        if m:
            if "infobox" not in v.lower():
                outf.write(k+' : '+process_string(v)+'\n')
            k = m.group(1)
            v = m.group(2)
        else:
            v+=l

def parse(article_text, outf):
    data = parse_infobox_text(get_infobox_from_text(article_text), outf)
    return data

