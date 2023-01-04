# SPDX-FileCopyrightText: Aurelie Herbelot, <aurelie.herbelot@cantab.net> 
#
# SPDX-License-Identifier: AGPL-3.0-only


import re
import gzip, shutil
import glob
from collections import Counter
from os import mkdir, remove, unlink
from os.path import join, exists, isdir

'''Special locations'''
special_locations = ['forest','woods','wilderness','countryside','mountain','mountains','moor','moors','glade','desert','beach','lake','sea','ocean','garden','farm','maze','castle','mansion','fortress','city','town','village','university','college','school','colony','convent','monastery','church','courtroom','tribunal','bank','factory','supermarket','office','hospital','café','restaurant','car','lorry','truck','road','train','plane','ship','battlefield','hell','paradise','purgatory','space','galaxy','spaceship']

'''Weather'''
weather = ['snow','snowfall','snowstorm','rain','flood','wind','storm','fog','mist','drought','sun','sunshine']

def gzip_file(f):
    fz = f.replace('.txt','.gz')
    with open(f, 'rb') as f_in:
        with gzip.open(fz, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    unlink(f)
    return fz


def get_special_locations(parsed_file_zipped):
    locs_file = parsed_file_zipped.replace('.gz','-locations.txt')
    lfile = open(locs_file,'w')
    doc_content = ''
    has_locs = False
    with gzip.open(parsed_file_zipped,'rt') as in_file:
        for l in in_file:
            l=l.rstrip('\n')
            if l[:4] == "<doc":
                doc_content = l+'\n'
            elif l[:5] == "</doc":
                if has_locs:
                    lfile.write(doc_content+'\n')
                    lfile.write(l+'\n')
                has_locs = False
            else:
                if l[-4:] == 'pobj' and any([True if l.startswith(loc+' ') else False for loc in special_locations]):
                    doc_content+=l+'\n'
                    has_locs = True
    lfile.close()
    print("All done. Output of special location processing can be found in", parsed_dir, ".")
    return gzip_file(locs_file)


def get_setting(ind_file):
    setting_file = ind_file.replace('.txt','-setting.txt')
    sfile = open(setting_file,'w')
    title_line = ''
    setting_elements = []
    setting_elements_min_idx = {}
    has_el = False
    c = 0

    with open(ind_file,'r') as in_file:
        for l in in_file:
            l=l.rstrip('\n')
            if l[:4] == "<doc":
                title_line = l
            elif l[:5] == "</doc":
                if has_el:
                    sfile.write(title_line+'\n')
                    els = dict(Counter(setting_elements))
                    for k,v in els.items():
                        idx = setting_elements_min_idx[k]
                        sfile.write(k+'::'+str(v)+'::'+str(idx)+'\n')
                    sfile.write(l+'\n')
                has_el = False
                c = 0
                setting_elements.clear()
            else:
                c+=1
                if l in special_locations or l in weather:
                    if l not in setting_elements:
                        setting_elements_min_idx[l] = c
                    setting_elements.append(l)
                    has_el = True
    sfile.close()
    print("All done. Output of setting processing can be found in", parsed_dir, ".")
    return gzip_file(setting_file)



if __name__ == "__main__":
    #base_dir = "/home/admin/share/4tera/corpora/wikipedia/2021-12-28/books/"
    base_dir = "./wikipedia/2022-12-02/books/"
    xml_dir = join(base_dir,"xml")
    linear_dir = xml_dir.replace('xml','linear')
    parsed_dir = xml_dir.replace('xml','parsed')
    cat_dir = xml_dir.replace('xml','categorisation')

    #get_special_locations(join(parsed_dir,'enwiki-parsed.gz'))
    get_setting(join(parsed_dir,'individuals.txt'))
