# SPDX-FileCopyrightText: Aurelie Herbelot, <aurelie.herbelot@cantab.net> 
#
# SPDX-License-Identifier: AGPL-3.0-only

import re
import bz2
import gzip
import shutil
import subprocess
from os import mkdir,remove, unlink
from os.path import join
from datetime import date
from pathlib import Path

def read_latest_wiki_paths():
    with open("./latest_wiki_paths.txt",'r') as f:
        return f.read().splitlines()

def bz2_uncompress(filepath):
    print("Uncompressing bz2:",filepath)
    newfilepath = filepath.replace(".bz2","")
    with open(newfilepath, 'wb') as new_file, bz2.BZ2File(filepath, 'rb') as file:
        for data in iter(lambda : file.read(100 * 1024), b''):
            new_file.write(data)
    return newfilepath

def get_book_xml(filename):
    f_content=""
    title=""
    book = False
    link_path = filename+".books.xml"
    out_file = open(link_path,'w')

    f=open(filename,'r')
    rec=False

    for l in f:
        f_content+=l
        if "<page" in l:
            f_content=l
        if "<title" in l:
            m = re.search(r'<title>(.*)</title>',l)
            title=m.group(1) 
        if re.search(r"{{Infobox book",l):
            rec = True
        if "</page>" in l and rec:
            title = ""
            rec = False
            out_file.write(f_content+'\n')
    f.close()
    out_file.close()
    return link_path

if __name__ == "__main__":
    today = str(date.today())
    wiki_dir = join("./wikipedia/",today)
    Path(wiki_dir).mkdir(exist_ok=True, parents=True)
    wiki_paths = read_latest_wiki_paths()

    for bz2_file in wiki_paths:
        print("Processing", bz2_file)

        subprocess.run(["wget",bz2_file])
        local_file = bz2_file.split('/')[-1]
        uncompressed = bz2_uncompress(local_file)
        remove(local_file)

        link_path = get_book_xml(uncompressed)
        print("Saving file to",link_path)

        with open(link_path, 'rb') as f_in:
            with gzip.open(join(wiki_dir,link_path+'.gz'), 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        unlink(link_path)
        remove(uncompressed)

