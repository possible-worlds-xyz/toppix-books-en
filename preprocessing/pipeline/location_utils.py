import re
from os.path import join,exists
import pandas as pd
  
def read_cities():
    df = pd.read_csv("./lists/cities.csv")
    cities = df['Name'].tolist()
    return cities

def read_countries():
    countries= []
    with open("./lists/countries.txt") as f:
        countries = f.read().splitlines()
    return countries

def read_states():
    states = []
    with open("./lists/states.txt") as f:
        states = f.read().splitlines()
    return states

def read_special_locations():
    special_locations = []
    with open("./lists/special_locations.txt") as f:
        special_locations = f.read().splitlines()
    return special_locations

def record_continent(continents,filename,continent_name):
    with open(filename) as f:
        countries = f.read().splitlines()
        for c in countries:
            continents[c] = continent_name
    return continents

def read_continents():
    continents = {}
    record_continent(continents,"./lists/countries_of_africa.txt","Africa")
    record_continent(continents,"./lists/countries_of_asia.txt","Asia")
    record_continent(continents,"./lists/countries_of_europe.txt","Europe")
    record_continent(continents,"./lists/countries_of_north_america.txt","North America")
    record_continent(continents,"./lists/countries_of_oceania.txt","Oceania")
    record_continent(continents,"./lists/countries_of_south_america.txt","South America")
    return continents

def get_continent(country,continents):
    if country in continents:
        return continents[country]
    else:
        return "unknown"

def mk_place_list():
    places = [["fictional places", "Africa", "Antarctica", "the Arctic", "Asia", "Europe", "North America", "Oceania", "South America"]]
    places.append(read_countries())
    places.append(read_cities())
    places.append(read_states())
    places = [item for sublist in places for item in sublist]
    return places

def get_country(location, known_locations, states, countries, continents, wiki_api):
    locations_to_countries_file = open("./lists/locations_to_countries.txt",'a')
    country = "unknown"
    if location in known_locations:
        #print("Location {0} already known: {1}.".format(location,known_locations[location]))
        country = known_locations[location][0]
        known_locations[location] = (country,continent)
    elif location == None:
        country = "unknown"
    elif location in countries and location not in states: #to avoid confusion with e.g. Georgia the state and Georgia the country
        country = location
    else:
        print("Location {0} unknown. Calling Wiki API.".format(location))
        wiki_page = wiki_api.page(location)
        if wiki_page.exists():
            pos = 500
            summary = wiki_page.summary[:500]
            for c in countries:
                if c in summary and summary.index(c) < pos and summary.index(c) != summary.index(location):
                    country = c
                    pos = summary.index(c)
        continent = get_continent(country,continents)
        known_locations[location] = (country,continent)
        locations_to_countries_file.write(location+'::'+country+'::'+continent+'\n')
    locations_to_countries_file.close()
    return country, known_locations

def read_locations_to_countries():
    locations = {}
    locations_to_countries = open("./lists/locations_to_countries.txt")
    for l in locations_to_countries:
        l = l.rstrip('\n')
        location, country, continent = l.split('::')
        locations[location] = (country,continent)
    locations_to_countries.close()
    return locations

def read_existing_location_records(cat_dir):
    IDs = []
    locations = {}
    loc_on = False
    loc = ""
    country = ""
    continent = ""
    location_record_path = join(cat_dir,"enwiki-books-set-in.xml")
    if not exists(location_record_path):
        return IDs, locations

    print("Reading existing location record before appending...")
    set_in_file = open(location_record_path,'r')
    for l in set_in_file:
        if "<doc" in l:
            m = re.search(r'id=\"([^\"]*)\"',l)
            IDs.append(m.group(1))
        if "<ne" in l:
            m = re.search("<ne>(.*)</ne>",l)
            loc = m.group(1)
            if loc not in locations:
                loc_on = True
        if "<country>" in l and loc_on:
            m = re.search("<country>(.*)</country>",l)
            country = m.group(1)
        if "<continent>" in l and loc_on:
            m = re.search("<continent>(.*)</continent>",l)
            continent = m.group(1)
        if "</location>" in l and loc_on:
            locations[loc] = (country,continent)
            loc_on = False
            loc = ""
            country = ""
            continent = ""
    print("Found {0} records and {1} unique locations.".format(len(IDs),len(locations)))
    return IDs, locations



def extract_location(category, places):
    location = None
    m = re.search("set in (.*)",category)
    spacetime = m.group(1)
    if spacetime in places or spacetime in read_special_locations():
        location = spacetime
    return location
