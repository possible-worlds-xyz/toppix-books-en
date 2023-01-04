import re
import gzip
from os.path import join
from pathlib import Path
from collections import Counter

def mk_stats_topics():
    '''Topic stats'''
    topics = []
    with gzip.open(join(base_dir,'categorisation/enwiki-book-categories.gz'),'rt') as f:
        for l in f:
            l = l.rstrip('\n')
            wiki, categories = l.split('::')
            wiki = wiki.replace('_',' ')
            for cat in categories.split(','):
                if "Novels about" in cat or "Fiction about" in cat:
                    m = re.search(".*about (.*)",cat)
                    topic = m.group(1).lower().replace(' ','_')
                    topics.append(topic)
    stats = Counter(topics)
    for topic in stats.most_common():
        print(topic[0],topic[1])
    

def mk_stats_locations():
    '''Location stats'''
    nes, countries, continents = [], [], []
    with open(join(base_dir,'categorisation/enwiki-book-locations.xml'),'r') as f:
        for l in f:
            l = l.rstrip('\n')
            m = re.search("<ne>(.*)</ne>",l)
            if m:
                nes.append(m.group(1))
            m = re.search("<country>(.*)</country>",l)
            if m:
                countries.append(m.group(1))
            m = re.search("<continent>(.*)</continent>",l)
            if m:
                continents.append(m.group(1))

    stats_nes = Counter(nes)
    stats_countries = Counter(countries)
    stats_continents = Counter(continents)
    
    print("\n## MOST COMMON CONTINENTS")
    for ne in stats_continents.most_common():
        print(ne[0],ne[1])
    print("\n## MOST COMMON COUNTRIES")
    for ne in stats_countries.most_common():
        print(ne[0],ne[1])
    print("\n## MOST COMMON LOCATIONS")
    for ne in stats_nes.most_common():
        print(ne[0],ne[1])


def mk_stats_nes():
    '''Dependency stats'''
    deps = []
    with open(join(base_dir,'parsed/named.entities.rels.txt'),'r') as f:
        for l in f:
            l = l.rstrip('\n')
            if '|' in l:
                dep = ' '.join(l.split()[1:])
                deps.append(dep)
    stats_deps = Counter(deps)

    print("\n## MOST COMMON DEPS")
    for dep in stats_deps.most_common():
        print(dep[0], dep[1])


def mk_stats_inds():
    '''Individuals stats'''
    inds = []
    with open(join(base_dir,'parsed/individuals.txt'),'r') as f:
        for l in f:
            l = l.rstrip('\n')
            if '<' not in l:
                inds.append(l)
    inds_deps = Counter(inds)

    print("\n## MOST COMMON INDIVIDUALS")
    for i in inds_deps.most_common():
        print(i[0], i[1])

def mk_stats_events():
    '''Events stats'''
    events = []
    with open(join(base_dir,'parsed/events.txt'),'r') as f:
        for l in f:
            l = l.rstrip('\n')
            if '<' not in l:
                events.append(l)
    events_deps = Counter(events)

    print("\n## MOST COMMON EVENTS")
    for i in events_deps.most_common():
        print(i[0], i[1])


if __name__ == '__main__':
    base_dir = Path("./current_dir_path.txt").read_text().rstrip('\n')
    #mk_stats_topics()
    #mk_stats_locations()
    #mk_stats_nes()
    mk_stats_inds()
    #mk_stats_events()
