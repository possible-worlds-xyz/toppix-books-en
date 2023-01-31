# SPDX-FileCopyrightText: Aurelie Herbelot, <aurelie.herbelot@cantab.net> 
#
# SPDX-License-Identifier: AGPL-3.0-only


import re
import gzip, shutil
import glob
from collections import Counter
from os import mkdir, remove, unlink
from os.path import join, exists, isdir
import location_utils
import wikipediaapi

'''Special locations'''
special_locations = ['forest','woods','wilderness','countryside','mountain','mountains','moor','moors','glade','desert','beach','lake','sea','ocean','garden','farm','maze','castle','mansion','fortress','city','town','village','university','college','school','colony','convent','monastery','church','courtroom','tribunal','bank','factory','supermarket','office','hospital','café','restaurant','battlefield','hell','paradise','purgatory','space','galaxy']

'''Weather'''
weather = ['snow','snowfall','snowstorm','rain','flood','wind','storm','fog','mist','drought','sun','sunshine']

'''Named locations'''
named_locations = location_utils.mk_place_list()

def gzip_file(f):
    fz = f.replace('.txt','.gz')
    fz = fz.replace('.xml','.gz')
    with open(f, 'rb') as f_in:
        with gzip.open(fz, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    unlink(f)
    return fz


def get_setting(ind_file):
    setting_file = ind_file.replace('individuals.txt','enwiki-settings.txt')
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
                if l in special_locations or l in weather or l in named_locations:
                    if l not in setting_elements:
                        setting_elements_min_idx[l] = c
                    setting_elements.append(l)
                    has_el = True
    sfile.close()
    print("All done. Output of setting processing can be found in", parsed_dir, ".")
    return gzip_file(setting_file)


def write_named_locations_file(setting_file, cat_dir):
    loc_file = setting_file.replace('enwiki-settings.gz','enwiki-book-locations.xml')
    lfile = open(loc_file,'w')
    title_line = ''
    settings = []

    wiki_api = wikipediaapi.Wikipedia('en')
    places = location_utils.mk_place_list()
    countries = location_utils.read_countries()
    continents = location_utils.read_continents()
    states = location_utils.read_states()

    locations_to_countries = location_utils.read_locations_to_countries()
    existing, known_locations = location_utils.read_existing_location_records(cat_dir.replace('parsed','categorisation'))

    with gzip.open(setting_file,'rt') as in_file:
        for l in in_file:
            l=l.rstrip('\n')
            if l[:4] == "<doc":
                title_line = l
            elif l[:5] == "</doc":
                lfile.write(title_line+'\n')
                for setting in settings:
                    country = "unknown"
                    continent = "unknown"
                    print("SETTING:", setting)
                    if setting in ["Africa", "Antarctica", "the Arctic", "Asia", "Europe", "North America", "Oceania", "South America"]:
                        continent = setting
                    elif setting in locations_to_countries:
                        country = locations_to_countries[setting][0]
                        continent = locations_to_countries[setting][1]
                    else:
                        country, known_locations = location_utils.get_country(setting, known_locations, states, countries, continents, wiki_api)
                        continent = location_utils.get_continent(country,continents)
                    if setting != None:
                        print(setting,country,continent)
                        lfile.write("  <location>\n")
                        lfile.write("    <ne>{0}</ne>\n".format(setting))
                        lfile.write("    <country>{0}</country>\n".format(country))
                        lfile.write("    <continent>{0}</continent>\n".format(continent))
                        lfile.write("  </location>\n")

                lfile.write(l+'\n')
                settings.clear()
            else:
                setting,freq,min_pos = l.split('::')
                if not setting[0].isupper():#Not a named entity
                    continue
                elif int(freq) == 1 and int(min_pos) < 15: #Only one occurrence of the setting but early on in the description
                    settings.append(setting)
                elif int(freq) > 1 and int(min_pos) < 50: #Several occurrences and still reasonably at the beginning
                    settings.append(setting)
                else:
                    continue


    lfile.close()
    print("All done. Output of named location processing can be found in", parsed_dir, ".")


if __name__ == "__main__":
    #base_dir = "/home/admin/share/4tera/corpora/wikipedia/2021-12-28/books/"
    base_dir = "./wikipedia/2022-12-02/books/"
    xml_dir = join(base_dir,"xml")
    parsed_dir = xml_dir.replace('xml','parsed')
    cat_dir = xml_dir.replace('xml','categorisation')

    #get_setting(join(parsed_dir,'individuals.txt')) #From dependency parse
    setting_file = join(parsed_dir,'enwiki-settings.gz')
    write_named_locations_file(setting_file, cat_dir)
