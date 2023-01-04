# SPDX-FileCopyrightText: Aurelie Herbelot, <aurelie.herbelot@cantab.net> 
#
# SPDX-License-Identifier: AGPL-3.0-only


import re
import gzip
import glob
import json
import pickle
import shutil
import subprocess
from pprint import pprint
from pathlib import Path
from os import mkdir, remove, unlink
from os.path import join, exists, isdir

from infobox_utils import parse
from time_utils import extract_time
import location_utils

import spacy, coreferee
import wikipediaapi

def gzip_file(f):
    fz = f.replace('.txt','.gz')
    with open(f, 'rb') as f_in:
        with gzip.open(fz, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    unlink(f)
    return fz


def read_header():
    with open("./enwiki_header.txt",'r') as f:
        return f.read()


def assemble_xml(xml_dir):
    print("-----Assembling corpus...")
    header = read_header()

    tmp_xml_file = "./tmp_book_file.xml"
    uncompressed = open(tmp_xml_file,'w')
    uncompressed.write(header)
    uncompressed.close()

    uncompressed = open(tmp_xml_file,'a')
    xml_paths = glob.glob(join(xml_dir,'*gz'))
    for gz_file in xml_paths:
        with gzip.open(gz_file,'rt') as in_file:
            file_content=in_file.read()
            uncompressed.write(file_content)
    uncompressed.close()
    return tmp_xml_file


def mk_book_titles(linear_dir,linear_file_zipped):
    print("\n--- Creating book title file in",linear_dir)
    book_title_file = join(linear_dir,"enwiki_book_titles.txt")
    out_file = open(book_title_file,'w')

    with gzip.open(linear_file_zipped,'rt') as in_file:
        doc_length=0
        title=""
        for l in in_file:
            if "<doc id" in l:
                doc_length=0
                m = re.search('.*title="([^"]*)">',l)
                title = m.group(1)
                title = re.sub('\([^\)]*\)','',title)
                title = re.sub('\s*$','',title)
            if "</doc" in l:
                if doc_length >= 500:
                    out_file.write(title+'\n')
            doc_length+=len(l.split())
    in_file.close()
    out_file.close()
    print("All done. Book title file can be found in",linear_dir,".")
    return gzip_file(book_title_file)

def mk_book_excerpts(linear_dir,linear_file_zipped):
    print("\n--- Creating book excerpt file file in",linear_dir)
    book_excerpt_file = join(linear_dir,"enwiki_book_excerpts.txt")
    out_file = open(book_excerpt_file,'w')

    excerpt = ""
    with gzip.open(linear_file_zipped,'rt') as in_file:
        for l in in_file:
            l = l.rstrip('\n')
            if "<doc id" in l:
                doc_length=0
                m = re.search('.*title="([^"]*)">',l)
                title = m.group(1)
            elif "</doc" in l:
                out_file.write(title+'::'+excerpt+'\n')
                excerpt = ""
            else:
                if len(excerpt.split()) < 200 and l!=title:
                    excerpt+=l
    in_file.close()
    out_file.close()
    print("All done. Book excerpt file can be found in",linear_dir,".")
    return gzip_file(book_excerpt_file)


def mk_book_infoboxes(xml_dir):
    #Adapted from https://raw.githubusercontent.com/woutster/wikipedia_infobox_parser/master/scraper.py
    print("\n--- Generating infobox file for book corpus located in ",xml_dir)
    tmp_xml_file = assemble_xml(xml_dir)
    f_content=""
    title=""

    f=open(tmp_xml_file,'r')
    infobox_file = join(xml_dir,"enwiki-infoboxes.txt")
    error_file = join(xml_dir,"enwiki-infobox-error.log")
    outf = open(infobox_file,'w')
    errf = open(error_file,'w')

    for l in f:
        f_content+=l
        if "<page" in l:
            f_content=l
        if "<title" in l:
            m = re.search(r'<title>(.*)</title>',l)
            title=m.group(1)
        if "</page>" in l:
            outf.write("<doc title="+title+">\n")
            try:
                parse(f_content, outf)
            except:
                errf.write("Failed parsing "+title+'\n')
            #print(json.dumps(d, indent=1))
            outf.write("</doc>\n")
            title = ""

    outf.close()
    errf.close()

    remove(tmp_xml_file)
    print("All done. Infobox file can be found in",xml_dir,".")
    return gzip_file(infobox_file)


def mk_book_times(xml_dir,cat_dir):
    print("\n--- Applying time processing to book corpus located in ",xml_dir)
    #existing, known_times = read_existing_records()
    existing = []
    categories = []
    tmp_xml_file = assemble_xml(xml_dir)
    set_in_file = open(join(cat_dir,"enwiki-book-times.xml"),'a')
    title_line = ""
    title= ""
    ID = ""

    with open("./tmp_book_file.xml") as f:
        for l in f:
            if "<title>" in l:
                m = re.search(r'<title>(.*)<',l)
                title=m.group(1)
            if "<id>" in l and title !='':
                m = re.search(r'<id>(.*)<',l)
                ID=m.group(1)
                if ID not in existing:
                    title_line = "<doc id=\"{0}\" url=\"https://en.wikipedia.org/wiki?curid={0}\" title=\"{1}\">\n".format(ID,title)
                    set_in_file.write(title_line)
                title = ""
                ID = ""
            m = re.search("\[\[Category:(.*)\]\]",l)
            if m and title_line !="" and ID not in existing:
                cat = m.group(1)
                categories.append(cat)
                if "Novels set in" in cat or "Fiction set in" in cat:
                     time,rangeStart,rangeEnd = extract_time(cat)
                     if time != None:
                         set_in_file.write("  <time>\n")
                         set_in_file.write("    <ne>{0}</ne>\n".format(time))
                         set_in_file.write("    <rangeStart>{0}</rangeStart>\n".format(rangeStart))
                         set_in_file.write("    <rangeEnd>{0}</rangeEnd>\n".format(rangeEnd))
                         set_in_file.write("  </time>\n")
                         print(cat,time, rangeStart, rangeEnd)
                     else:
                         #print("Category discarded:",cat)
                         continue
            if "</page>" in l and len(categories) > 0 and ID not in existing:
                set_in_file.write("</doc>\n")
                title_line = ""

        set_in_file.close()
        f.close()



def mk_book_locations(xml_dir,cat_dir):
    print("\n--- Applying location processing to book corpus located in ",xml_dir)
    wiki_api = wikipediaapi.Wikipedia('en')
    categories = []
    set_in = {}

    places = location_utils.mk_place_list()
    countries = location_utils.read_countries()
    continents = location_utils.read_continents()
    states = location_utils.read_states()
    locations_to_countries = location_utils.read_locations_to_countries()
    existing, known_locations = location_utils.read_existing_location_records(cat_dir)

    tmp_xml_file = assemble_xml(xml_dir)
    set_in_file = open(join(cat_dir,"enwiki-book-locations.xml"),'a')
    title_line = ""
    title= ""
    ID = ""

    with open("./tmp_book_file.xml") as f:
        for l in f:
            if "<title>" in l:
                m = re.search(r'<title>(.*)<',l)
                title=m.group(1)
            if "<id>" in l and title !='':
                m = re.search(r'<id>(.*)<',l)
                ID=m.group(1)
                if ID not in existing:
                    title_line = "<doc id=\"{0}\" url=\"https://en.wikipedia.org/wiki?curid={0}\" title=\"{1}\">\n".format(ID,title)
                    set_in_file.write(title_line)
                title = ""
                ID = ""
            m = re.search("\[\[Category:(.*)\]\]",l)
            if m and title_line !="" and ID not in existing:
                cat = m.group(1)
                categories.append(cat)
                if "Novels set in" in cat or "Fiction set in" in cat:
                    location = location_utils.extract_location(cat, places + list(locations_to_countries.keys()))
                    country = "unknown"
                    continent = "unknown"
                    print("CAT:",cat, location)
                    if location in ["Africa", "Antarctica", "the Arctic", "Asia", "Europe", "North America", "Oceania", "South America"]:
                        continent = location
                    elif location in locations_to_countries:
                        country = locations_to_countries[location][0]
                        continent = locations_to_countries[location][1]
                    else:
                        country, known_locations = location_utils.get_country(location, known_locations, states, countries, continents, wiki_api)
                        continent = location_utils.get_continent(country,continents)
                    if location != None:
                        set_in_file.write("  <location>\n")
                        set_in_file.write("    <ne>{0}</ne>\n".format(location))
                        set_in_file.write("    <country>{0}</country>\n".format(country))
                        set_in_file.write("    <continent>{0}</continent>\n".format(continent))
                        set_in_file.write("  </location>\n")
                    else:
                        #print("Category discarded:",cat)
                        continue
            if "</page>" in l and len(categories) > 0 and ID not in existing:
                set_in_file.write("</doc>\n")
                title_line = ""

    set_in_file.close()
    f.close()
    remove(tmp_xml_file)



def ner(cat_dir):
    nlp = spacy.load("en_core_web_sm")
    print("\n--- Applying NER to book corpus located in ",xml_dir)
    cat_dir = xml_dir.replace('xml','categorisation')
    saved_locations_pkl = join(cat_dir,'saved_locations.pkl')
    if exists(saved_locations_pkl):
        with open(saved_locations_pkl, 'rb') as df:
            saved_locations = pickle.load(df)
    else:
        saved_locations = {}

    loc_file = join(cat_dir,"books-per-location.txt")
    time_file = join(cat_dir,"books-per-time.txt")
    unk_file = join(cat_dir,"books-uncategorised.txt")

    locs = open(loc_file,'w')
    times = open(time_file,'w')
    unks = open(unk_file,'w')

    with gzip.open(join(cat_dir,"enwiki-books-set-in.gz"),'r') as f:
        for l in f:
            cat = l.split('::')[0]
            doc = nlp(cat)

            for ent in doc.ents:
                print(ent.text, ent.start_char, ent.end_char, ent.label_)
                if ent.label_ in("LOC","GPE","FAC"):
                    typ = "unk"
                    if ent.text in saved_locations:
                        typ = saved_locations[ent.text] 
                        print("Location saved:",typ)
                        locs.write(typ+'::'+l)
                        continue
                    try:
                        print("Location unknown, trying wikipedia...")
                        summary = str(wikipedia.summary(ent.text, sentences=1))
                        m = re.search("is a city|is the capital|is [^ ]* [^ ]* city", summary)
                        if m:
                            typ='city'
                        m = re.search("is a country|is [^ ]* [^ ]* country", summary)
                        if m:
                            typ='country'
                        m = re.search("is a county|is a state|is a region|is [^ ]* [^ ]* county|is [^ ]* [^ ]* state|is [^ ]* [^ ]* region", summary)
                        if m:
                            typ='region'
                        saved_locations[ent.text] = typ
                    except:
                        pass
                    locs.write(typ+'::'+l)
                elif ent.label_ in("DATE","TIME"):
                    times.write(l)
                else:
                    unks.write(l)
        f.close()
        locs.close()
        times.close()
        unks.close()

    with open(saved_locations_pkl, 'wb') as df:
        pickle.dump(saved_locations, df, protocol=pickle.HIGHEST_PROTOCOL)
    return gzip_file(loc_file), gzip_file(time_file), gzip_file(unk_file)


def get_chain_gender(chain):
    gender = 'U'
    mentions = chain.pretty_representation.lower()
    if "he" in mentions or "his" in mentions:
        gender = 'M'
    if "she" in mentions or "her" in mentions:
        gender = 'F'
    return gender

def is_person(chain, ents):
    person = False
    for e in chain:
        e = e.pretty_representation
        m = re.search('(.*)\([0-9]*\)',e)
        if m.group(1) in ents['PERSON']:
            person = True
            break
    return person

def get_word_distribution(doc):
    dist = {}
    for token in doc:
        if token.pos_ in ["NOUN","VERB","ADJ","PROPN"]:
            if token.lemma_ in dist:
                dist[token.lemma_]+=1
            else:
                dist[token.lemma_] = 1
    return dist


def parse_content(parsed_dir,linear_file_zipped):
    nlp = spacy.load("en_core_web_lg")
    nlp.add_pipe('coreferee')
    print("\n--- Parsing book corpus from ",linear_file_zipped)

    record = False
    doc_content = ""
    title = ""
    parsed_file = join(parsed_dir,'enwiki-parsed.tmp.txt')
    entity_file = join(parsed_dir,'enwiki-entities.tmp.txt')
    fparse = open(parsed_file,'w')
    fents = open(entity_file,'w')
    content_titles_7chars = ["## Plot", "## Syno", "## Cont", "== Stor"]

    with gzip.open(linear_file_zipped,'rt') as in_file:
        for l in in_file:
            l=l.rstrip('\n')
            if l[:4] == "<doc":
                fparse.write(l+'\n')
                fents.write(l+'\n')
            elif l[:7] in content_titles_7chars:
                doc_content = ""
                record = True
            elif (l.startswith("##") or l.startswith("==")) and record:
                record = False
            elif l[:5] == "</doc":
                fparse.write(doc_content+'\n')
                doc = nlp(doc_content)
                dist = get_word_distribution(doc)
                male_chars = 0
                female_chars = 0

                for k,v in dist.items():
                    fparse.write(k+':'+str(v)+'\n')
                doc = nlp(doc_content)
                for token in doc:
                    fparse.write(token.text+' '+token.head.text+' '+token.dep_+'\n')
                ents = {'PERSON':[],'LOC':[]}
                for ent in doc.ents:
                    if ent.text not in ents and ent.label_ in ['PERSON','LOC']:
                        if ent.text not in ents[ent.label_]:
                            ents[ent.label_].append(ent.text)

                for lbl,names in ents.items():
                    names = '|'.join(names)
                    fents.write(lbl+':'+names+'\n')
                for chain in doc._.coref_chains:
                    if not is_person(chain, ents):
                        continue
                    n_mentions = len(chain)
                    gender = get_chain_gender(chain)
                    if gender == 'F':
                        female_chars+=n_mentions
                    else:
                        male_chars+=n_mentions
                    #Resolve mentions
                    names = []
                    for e in chain:
                        resolution = doc._.coref_chains.resolve(doc[e[0]])
                        if resolution != None:
                            names.extend(resolution)
                    names = list(set(names))
                    fents.write('CHAIN '+','.join([n.text for n in names])+' '+chain.pretty_representation+' '+str(n_mentions)+' '+gender+'\n')
                if female_chars == 0 and male_chars == 0:
                    fents.write('FEMALE RATIO NaN\n')
                else:
                    fents.write('FEMALE RATIO '+str(female_chars / (female_chars + male_chars))+'\n')
                fparse.write(l+'\n')
                fents.write(l+'\n')
                doc_content = ""
            else:
                doc_content+=l+' '
    fparse.close()
    fents.close()
    print("All done. Output of parse can be found in",parsed_dir,".")
    return gzip_file(parsed_file),gzip_file(entity_file)


def parse_content_old(parsed_dir,linear_file_zipped):
    nlp = spacy.load("en_core_web_lg")
    print("\n--- Parsing book corpus from ",linear_file_zipped)

    doc_content = ""
    title = ""
    parsed_file = join(parsed_dir,'enwiki-parsed.txt')
    entity_file = join(parsed_dir,'enwiki-entities.txt')
    fparse = open(parsed_file,'w')
    fents = open(entity_file,'w')

    with gzip.open(linear_file_zipped,'rt') as in_file:
        for l in in_file:
            l=l.rstrip('\n')
            if l[:4] == "<doc":
                fparse.write(l+'\n')
                fents.write(l+'\n')
            else:
                if l.startswith("##") or "</doc>" in l:
                    doc = nlp(doc_content)
                    for token in doc:
                        fparse.write(token.text+' '+token.head.text+' '+token.dep_+'\n')
                    for ent in doc.ents:
                        fents.write(ent.text+':'+ent.label_+'\n')
                    fparse.write(l+'\n')
                    fents.write(l+'\n')
                    doc_content = ""
                else:
                    doc_content+=l+' '
    fparse.close()
    fents.close()
    print("All done. Output of parse can be found in",parsed_dir,".")
    return gzip_file(parsed_file),gzip_file(entity_file)


def mk_linear(xml_dir):
    print("\n--- Generating linear version of wiki book corpus located in ",xml_dir)
    linear_dir = xml_dir.replace('xml','linear')
    tmp_xml_file = assemble_xml(xml_dir)

    linear_file = join(base_dir,"linear/enwiki_books.txt")
    command = ['wikiextractor','--output',linear_file,'--no-templates','--html-safe','False',tmp_xml_file]
    subprocess.run(command)
    
    remove(tmp_xml_file)
    print("All done. Linear version of corpus can be found in",linear_dir,".")
    return gzip_file(linear_file)


def mk_categories(xml_dir,cat_dir):
    print("\n--- Generating category files for book corpus located in ",xml_dir)
    tmp_xml_file = assemble_xml(xml_dir)
    
    categories = []
    set_in = {}
    f = open(tmp_xml_file)
    all_cats_file = join(cat_dir,"enwiki-book-categories.txt")
    set_in_file = join(cat_dir,"enwiki-books-set-in.txt")
    fcats = open(join(cat_dir,"enwiki-book-categories.txt"),'w')
    fset = open(join(cat_dir,"enwiki-books-set-in.txt"),'w')

    for l in f:
        if "<title>" in l:
            m = re.search(r'<title>(.*)<',l)
            title=m.group(1)
            title=title.replace(' ','_')
        m = re.search("\[\[Category:(.*)\]\]",l)
        if m and title !="":
            cat = m.group(1)
            categories.append(cat)
            if "Novels set in" in cat or "Fiction set in" in cat:
                if cat in set_in:
                    set_in[cat].append(title)
                else:
                    set_in[cat] = [title]
        if "</page>" in l and len(categories) > 0:
            fcats.write(title+"::"+','.join([c for c in categories])+'\n')
            categories.clear()

    for k,v in set_in.items():
        fset.write(k+"::"+','.join([book for book in v])+'\n')

    fcats.close()
    fset.close()
    f.close()
    
    remove(tmp_xml_file)
    print("All done. Category files can be found in",cat_dir,".")
    return gzip_file(all_cats_file),gzip_file(set_in_file)


if __name__ == "__main__":
    #base_dir = "/home/admin/share/4tera/corpora/wikipedia/2021-12-28/books/"
    base_dir = "./wikipedia/2022-12-02/books/"
    xml_dir = join(base_dir,"xml")
    print('XML',xml_dir)
    Path(xml_dir).mkdir(exist_ok=True, parents=True)
    linear_dir = xml_dir.replace('xml','linear')
    Path(linear_dir).mkdir(exist_ok=True, parents=True)
    parsed_dir = xml_dir.replace('xml','parsed')
    Path(parsed_dir).mkdir(exist_ok=True, parents=True)
    cat_dir = xml_dir.replace('xml','categorisation')
    #linear_file_zipped = mk_linear(xml_dir)


    #mk_book_infoboxes(xml_dir)

    #mk_categories(xml_dir,cat_dir)
    #mk_book_locations(xml_dir, cat_dir)
    #mk_book_times(xml_dir, cat_dir)
    #ner(xml_dir)
    
    #book_title_file_zipped = mk_book_titles(linear_dir,linear_file_zipped)
    #book_excerpt_file_zipped = mk_book_excerpts(linear_dir,linear_file_zipped)
    linear_file_zipped = "wikipedia/2022-12-02/books/linear/enwiki_books.gz"
    dependency_file_zipped, entity_file_zipped = parse_content(parsed_dir,linear_file_zipped)
