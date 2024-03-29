# SPDX-FileCopyrightText: Aurelie Herbelot, <aurelie.herbelot@cantab.net> 
#
# SPDX-License-Identifier: AGPL-3.0-only


from pathlib import Path
import gzip
import re
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'toppixbackend.settings')

import django
django.setup()

from toppixapi.models import Book,Topic,Continent,Country,Time,Character,Setting


def read_books(base_dir):
    books = {}
    with gzip.open(os.path.join(base_dir,'linear/enwiki_books.gz'),'rt') as f:
        for l in f:
            l=l.rstrip('\n')
            if l[:4] == "<doc":
                m = re.search('title=\"([^\"]*)\"',l)
                title = m.group(1)
                m = re.search('url=\"([^\"]*)\"',l)
                url = m.group(1)
                if "Category" not in title:
                    books[url] = title
    return books


def read_locations(location_file):
    continents = {}
    countries = {}
    country_names= []
    continent_names= []
    with open(location_file,'r') as f:
        for l in f:
            l=l.rstrip('\n')
            if l[:4] == "<doc":
                m = re.search('title=\"([^\"]*)\"',l)
                wiki_title = m.group(1)
                continents[wiki_title] = []
                countries[wiki_title] = []
            if "<continent" in l:
                m = re.search("<continent>(.*)</continent>",l)
                continent = m.group(1)
                if continent != "unknown":
                    if continent not in continent_names:
                        continent_names.append(continent)
                    if continent not in continents[wiki_title]:
                        continents[wiki_title].append(continent)
            if "<country" in l:
                m = re.search("<country>(.*)</country>",l)
                country = m.group(1)
                if country != "unknown":
                    if country not in country_names:
                        country_names.append(country)
                    if country not in countries[wiki_title]:
                        countries[wiki_title].append(country)
    return continents, countries, continent_names, country_names

def read_times():
    times = {}
    r = None
    with open(os.path.join(base_dir,'categorisation/enwiki-book-times.xml'),'r') as f:
        for l in f:
            l=l.rstrip('\n')
            if l[:4] == "<doc":
                m = re.search('title=\"([^\"]*)\"',l)
                wiki_title = m.group(1)
                times[wiki_title] = []
            if "<rangeStart" in l:
                m = re.search("<rangeStart>(.*)</rangeStart>",l)
                if m.group(1) != "unknown":
                    s = int(m.group(1))
            if "<rangeEnd" in l:
                m = re.search("<rangeEnd>(.*)</rangeEnd>",l)
                if m. group(1) != "unknown":
                    e = int(m.group(1))
                    r = (s,e)
                if r not in times[wiki_title] and r != None:
                    times[wiki_title].append(r)
                r = None
    return times


def read_chars(base_dir):
    chars = {}
    char_names = []
    with open(os.path.join(base_dir,'parsed/enwiki-entities.tmp.txt'),'r') as f: #Correct filename
        for l in f:
            l=l.rstrip('\n')
            if l[:4] == "<doc":
                m = re.search('title=\"([^\"]*)\"',l) #better to index by url, for sure?
                wiki_title = m.group(1)
                chars[wiki_title] = [[],0.0]
            if l[:5] == "CHAIN":
                fields = l.split()
                ent = fields[1]
                gender = fields[-1]
                if ent not in char_names:
                    chars[wiki_title][0].append((ent,gender))
                    char_names.append(ent)
            if l[:12] == "FEMALE RATIO":
                m = re.search('FEMALE RATIO (.*)',l)
                chars[wiki_title][1] = float(m.group(1))
            if l[:5] == "</doc":
                print(chars[wiki_title])
                char_names.clear()
        return chars



def populate_books():
    Book.objects.all().delete()
    for url, title in books.items():
        print("Adding",url,title)
        p = Book.objects.get_or_create(wiki_url=url)[0]
        p.title=title
        p.save()


def populate_locations():
    for continent in continent_names:
        print("Adding ",continent)
        p = Continent.objects.get_or_create(continent=continent)[0]
        p.save()
    for country in country_names:
        print("Adding ",country)
        country = country.replace('the ','') #To cater for the United States, etc
        p = Country.objects.get_or_create(country=country)[0]
        p.save()


def populate_times():
    Time.objects.all().delete()
    for time in range(-1000,3000,100):
        #print("Adding ",time)
        p = Time.objects.get_or_create(rangeStart=time,rangeEnd=time+99)[0]
        p.save()


def populate_wiki_locations():
    for wiki,continents in wiki_to_continents.items():
        print("Adding continent to ",wiki, continents)
        try:
            m = Book.objects.get(title=wiki)
            for continent in continents:
                c = Continent.objects.get(continent=continent)
                c.books.add(m)
                c.save()
        except:
            continue
    for wiki,countries in wiki_to_countries.items():
        print("Adding countries to ",wiki, countries)
        try:
            m = Book.objects.get(title=wiki)
            for country in countries:
                country = country.replace('the ','') #To cater for the United States, etc
                c = Country.objects.get(country=country)
                c.books.add(m)
                c.save()
        except:
            continue


def populate_wiki_times():
    for wiki,times in wiki_to_times.items():
        try:
            m = Book.objects.get(title=wiki)
        except:
            continue
        print("Adding",wiki,times)
        if len(times) == 0:
            if m.release_date is not None and m.release_date.isdigit():
                release_date = int(m.release_date)
                i = int(release_date / 100) * 100
                try:
                    t = Time.objects.get(rangeStart=i)
                    t.books.add(m)
                    t.save()
                except:
                    print("Issues finding time",i,"in times.")
            continue

        try:
            m = Book.objects.get(title=wiki)
            for time in times:
                for i in range(time[0],time[1],100):
                    t = Time.objects.get(rangeStart=i)
                    t.books.add(m)
                    t.save()
        except:
            continue

def populate_wiki_chars():
    Character.objects.all().delete()
    for wiki,char_info in wiki_chars.items():
        chars = char_info[0]
        gender_ratio = float(char_info[1])
        m = Book.objects.get(title=wiki)
        if gender_ratio > 0.3:
            m.female_lead = 'Y'
        else:
            m.female_lead = 'N'
        m.save()
        for char in chars:
            print(char)
            name = char[0]
            p = Character.objects.get_or_create(name=name)[0]
            p.gender = char[1]
            print(char[0],char[1])
            p.book = m
            p.save()

def populate_snippets():
    with gzip.open(os.path.join(base_dir,'linear/enwiki_book_excerpts.gz'),'rt') as f:
        for l in f:
            wiki,snippet = l.rstrip('\n').split("::")
            snippet = snippet.replace('##','\n\n')
            snippet = snippet.replace('()',' ')
            snippet = snippet.replace('\"','"')
            snippet+='...'
            print("Adding",wiki,snippet[:150])
            try:
                m = Book.objects.get(title=wiki)
                m.snippet=snippet
                m.save()
            except:
                continue

def populate_release_dates():
    title = ""
    date = ""
    with gzip.open(os.path.join(base_dir,'xml/enwiki-infoboxes.gz'),'rt') as f:
        for l in f:
            l = l.rstrip('\n')
            if "<doc title" in l:
                title = l[:-1].replace("<doc title=","")
            elif "</doc" in l:
                if date.isdigit():
                    #print("Adding release date for",title,":",date)
                    try:
                        m = Book.objects.get(title=title)
                        m.release_date=date
                        m.save()
                    except:
                        continue

            else: 
                m = re.search('^pub_date.*:\s*(.*)',l)
                if m:
                    date = m.group(1)
                m = re.search('^release_date.*:\s*(.*)',l)
                if m:
                    date = m.group(1)


def populate_basic_info():
    author = None
    genre = None
    with gzip.open(os.path.join(base_dir,'xml/enwiki-infoboxes.gz'),'rt') as f:
        for l in f:
            l = l.rstrip('\n')
            if "<doc title" in l:
                title = l[:-1].replace("<doc title=","")
            elif "</doc" in l:
                try:
                    m = Book.objects.get(title=title)
                    print("Adding",genre,"to title",title)
                    if genre != None:
                        m.genre = genre
                    print("Adding",author,"to title",title)
                    if author != None:
                        m.author = author
                    m.save()
                except:
                    continue
            else:
                m = re.search("^author : (.*)",l)
                if m:
                    author = m.group(1)
                m = re.search("^genre : (.*)",l)
                if m:
                    genre = m.group(1)

def populate_wiki_topics():
    replacements = {'extraterrestrial life':'aliens'}
    Topic.objects.all().delete()
    with gzip.open(os.path.join(base_dir,'categorisation/enwiki-book-categories.gz'),'rt') as f:
        for l in f:
            l = l.rstrip('\n')
            wiki, categories = l.split('::')
            wiki = wiki.replace('_',' ')
            for cat in categories.split(','):
                if "Novels about" in cat or "Fiction about" in cat:
                    m = re.search(".*about (.*)",cat)
                    topic = m.group(1).lower().replace('_',' ')
                    if topic in replacements:
                        topic = replacements[topic]
                    print(topic)
                    try:
                        print("Adding topic",topic,"to",wiki)
                        t = Topic.objects.get_or_create(topic=topic)[0]
                        m = Book.objects.get(title=wiki)
                        t.books.add(m)
                        t.save()
                    except:
                        continue

def populate_wiki_settings():
    Setting.objects.all().delete()
    settings = []
    with gzip.open(os.path.join(base_dir,'parsed/enwiki-settings.gz'),'rt') as f:
        for l in f:
            l = l.rstrip('\n')
            if "<doc" in l:
                m = re.search('title=\"([^\"]*)\"',l)
                title = m.group(1)
            elif "</doc" in l:
                for setting in settings:
                    if setting[0].isupper(): #Ignore named entities
                        continue
                    try:
                        print("Adding setting",setting,"to",title)
                        t = Setting.objects.get_or_create(setting=setting)[0]
                        m = Book.objects.get(title=title)
                        t.books.add(m)
                        t.save()
                    except:
                        continue
                settings.clear()
            else:
                print(l)
                setting,freq,min_pos = l.split('::')
                if int(freq) == 1 and int(min_pos) < 15: #Only one occurrence of the setting but early on in the description
                    settings.append(setting)
                elif int(freq) > 1 and int(min_pos) < 50: #Several occurrences and still reasonably at the beginning
                    settings.append(setting)
                else:
                    continue

def cleanup():
    books = Book.objects.all()
    print(len(books))

    #Clearing books with empty plot snippets
    for book in books:
       if len(book.snippet) < 20:
            print("Deleting",book.title,book.snippet)
            book.delete()

    print(len(books))

# Start execution here!
if __name__ == '__main__':
    base_dir = Path("../preprocessing/pipeline/current_dir_path.txt").read_text().rstrip('\n')
    base_dir = os.path.join("../preprocessing/pipeline/",base_dir)
    print("Starting population script...")
    books = read_books(base_dir)
    print(len(books),"books read...")
    populate_books()
    populate_release_dates()

    #Locations
    locations_from_cats = os.path.join(base_dir,'categorisation/enwiki-book-locations.xml')
    wiki_to_continents, wiki_to_countries, continent_names, country_names = read_locations(locations_from_cats)
    populate_locations()
    populate_wiki_locations()
    #locations_from_parse = os.path.join(base_dir,'parsed/enwiki-book-locations.xml')
    #wiki_to_continents, wiki_to_countries, continent_names, country_names = read_locations(locations_from_parse)
    #populate_locations()
    #populate_wiki_locations()

    #Times
    populate_times()
    wiki_to_times = read_times()
    populate_wiki_times()

    #Snippets
    populate_snippets()
    cleanup()

    populate_basic_info()
    populate_wiki_topics()
    #populate_wiki_settings()
    
    #wiki_chars = read_chars(base_dir)
    #populate_wiki_chars()
