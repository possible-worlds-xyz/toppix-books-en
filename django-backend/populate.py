from pathlib import Path
import gzip
import re
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'toppixbackend.settings')

import django
django.setup()

from toppixapi.models import Book,Continent,Country,Time,Character


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


def read_locations(base_dir):
    continents = {}
    countries = {}
    country_names= []
    continent_names= []
    with open(os.path.join(base_dir,'categorisation/enwiki-book-locations.xml'),'r') as f:
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
                c = Country.objects.get(country=country)
                c.books.add(m)
                c.save()
        except:
            continue


def populate_wiki_times():
    for wiki,times in wiki_to_times.items():
        print("Adding",wiki,times)
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
            snippet = snippet.replace(' ##','\n\n')+'...'
            print("Adding",wiki,snippet[:150])
            try:
                m = Book.objects.get(title=wiki)
                m.snippet=snippet
                m.save()
            except:
                continue


# Start execution here!
if __name__ == '__main__':
    base_dir = Path("../preprocessing/pipeline/current_dir_path.txt").read_text().rstrip('\n')
    base_dir = os.path.join("../preprocessing/pipeline/",base_dir)
    print("Starting population script...")
    #books = read_books(base_dir)
    #print(len(books),"books read...")
    #populate_books()
    #wiki_to_continents, wiki_to_countries, continent_names, country_names = read_locations(base_dir)
    #populate_locations()
    #populate_wiki_locations()
    #populate_times()
    wiki_to_times = read_times()
    populate_wiki_times()
    populate_snippets()
    #wiki_chars = read_chars(base_dir)
    #populate_wiki_chars()
