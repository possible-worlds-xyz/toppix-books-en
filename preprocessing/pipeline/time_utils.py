import re
from os.path import join, exists

def year_to_range(year):
    rangeStart = int(int(year) / 50) * 50
    rangeEnd = rangeStart + 50
    return rangeStart,rangeEnd

def century_to_range(century,bc=False):
    if not bc:
        rangeStart = int(century) * 100 - 100
        rangeEnd = rangeStart + 100
    else:
        rangeEnd = -(int(century) * 100 - 100)
        rangeStart = rangeEnd - 100
    return rangeStart,rangeEnd

def extract_time(category):
    time = None
    s = None
    e = None
    spacetime = None
    m = re.search("set in (.*)",category)
    spacetime = m.group(1)
    if len(spacetime) == 4 and spacetime.isdigit():
        time = spacetime
        s,e = year_to_range(time)
    century = re.search("the ([0-9]*).. century",spacetime.lower())
    if century:
        time = spacetime
        s,e = century_to_range(century.group(1))
    centurybc = re.search("the ([0-9]*).. century bc",spacetime.lower())
    if centurybc:
        time = spacetime
        s,e = century_to_range(centurybc.group(1),bc=True)
    decade = re.search("the ([0-9]{4})s",spacetime)
    if decade:
        time = decade.group(1)
        s,e = year_to_range(decade.group(1))
    if spacetime == "the future":
        time = "_future"
        s,e = ("unknown","unknown")
    return time,s,e


def read_existing_records():
    IDs = []
    times = {}
    time_on = False
    time_record_path = join(cat_dir,"enwiki-book-times.xml")
    if not exists(time_record_path):
        return IDs, times

    print("Reading existing time record before appending...")
    set_in_file = open(time_record_path,'r')
    for l in set_in_file:
        if "<doc" in l:
            m = re.search(r'id=\"([^\"]*)\"',l)
            IDs.append(m.group(1))
        if "<ne" in l:
            m = re.search("<ne>(.*)</ne>",l)
            loc = m.group(1)
            if loc not in locations:
                time_on = True
        if "<time>" in l and time_on:
            m = re.search("<time>(.*)</time>",l)
            country = m.group(1)
        if "</location>" in l and time_on:
            locations[loc] = (country,continent)
            time_on = False
            loc = ""
            country = ""
            continent = ""
    print("Found {0} records and {1} unique times.".format(len(IDs),len(times)))
    return IDs, times

