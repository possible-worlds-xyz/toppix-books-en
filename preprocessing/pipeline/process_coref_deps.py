import re
import gzip
import spacy, coreferee
import numpy as np
from collections import Counter
from os.path import join

nlp = spacy.load('en_core_web_lg')
nlp.add_pipe('coreferee')
vec_dim = 300


def attach_prep(token,doc):
    pp = ""
    for c in doc[token.i].children:
        if c.dep_ == "pobj" and c.tag_[0] == 'N':
            pp = "{0}_{1} {2}_{3} {4}_{5}".format(token.head.text.lower(),token.head.tag_,token.text.lower(),token.tag_,c.text.lower(),c.tag_)
            break
    return pp

def no_prp(s):
    #if s.tag_[:3] != "PRP": #Tag is not reliable!
    if s.lower() not in ["he","him","his","she","her","hers","it","its","they","them","their","theirs"]:
        return True
    else:
        return False

def vec_add(entity,tok):
    vec_to_add = np.zeros(vec_dim)
    #print(entity,tok.text,tok.tag_)
    if tok.tag_[0] in ["N","V"] and tok.has_vector:
        vec_to_add = tok.vector
    return vec_to_add

def vec_update(entity_vectors,vec_words,entity,tok,va):
    if sum(va) != 0:
        entity_vectors[entity]+= va
        vec_words[entity].append(tok.text)
    return entity_vectors, vec_words

def is_name(entity):
    name = True
    for tok in entity:
        if tok.tag_ != "NNP" and tok.text[0].islower():
            name = False
            break
    return name

def is_person(chain, ents):
    person = False
    for e in chain:
        e = e.pretty_representation
        m = re.search('(.*)\([0-9]*\)',e)
        if m.group(1) in ents['PERSON']:
            person = True
            break
    return person

def assess_gender(cluster):
    pronouns = [str(e).lower() for e in cluster if not no_prp(str(e))]
    gender = "person"
    for name in cluster:
        if str(name).lower() in ["she","her"]:
            gender = 'she'
        elif str(name).lower() in ["he","him","his"]:
            gender = 'he'
        elif str(name).lower() in ["they","them","their"]:
            gender = 'they'
    return gender
        

def name_cluster(cluster):
    shortest_name =cluster[0]
    for name in cluster:
        print(name)
        if no_prp(str(name)):
            if len(str(name)) < len(str(shortest_name)):
                shortest_name = name
    if no_prp(str(shortest_name)):
        return str(shortest_name).replace(' ','_'), assess_gender(cluster)
    else:
        return "",""

def process_book(doc,title,ID):
    entities = {}
    entity_vectors = {}
    vec_words = {}
    entity_ids = {}

    ents = {'PERSON':[],'LOC':[], 'ORG':[]}
    for ent in doc.ents:
        #print(ent.text,ent.label_,ent.start)
        if ent.text not in ents and ent.label_ in ['PERSON','LOC','ORG']:
            if ent.text not in ents[ent.label_]:
                ents[ent.label_].append(ent.text)
    #print(ents)

    '''Process chains'''
    for chain in doc._.coref_chains:
        #print("CHAIN",chain)
        if not is_person(chain, ents):
            continue
        #Resolve mentions
        for e in chain:
            name = doc._.coref_chains.resolve(doc[e[0]])
            if name is not None:
                name = name[0].text
                break
        surface_forms = []
        #print("RESOLUTION",name)
        for e in chain:
            surface_forms.append(doc[e[0]].text)
            gender = assess_gender(surface_forms)
        #print("PERSON:",name,surface_forms,gender)
        entity = name+'('+gender+')|'+title+'|'+ID
        entity = entity.lower()
        for group in chain:
            for e in group:
                entity_ids[e] = entity
        if entity not in entities:
            entities[entity] = []
            entity_vectors[entity] = nlp(gender).vector
            vec_words[entity]=[]

    '''Process remaining entities not in a chain'''
    for ent in doc.ents:
        if ent.label_ != 'PERSON':
            continue
        name = ent.text.replace(' ','_')
        gender = 'person'
        entity = name+'('+gender+')|'+title+'|'+ID
        entity = entity.lower()
        entity_ids[ent.end] = entity
         
        if entity not in entities:
            entities[entity] = []
            entity_vectors[entity] = nlp(gender).vector
            vec_words[entity]=[]
    #print(entity_ids)
    return entity_ids, entities, entity_vectors, vec_words

def check_shortforms(token, ents):
    shortform = False
    for ent in doc.ents:
        name_parts = ent.text.split()
        if token in name_parts:
            shortform = True
            break
    return shortform

def parse_deps(doc, entity_ids, entities, entity_vectors, vec_words):
    individuals = {}
    events = {}

    for token in doc:
        e = (-1,-1) #Pair: token i, corresponding entity
        dep = "{7}: {2}({3}_{4}-{6}, {0}_{1}-{5})".format(token.text, token.tag_, token.dep_, token.head.text, token.head.tag_, token.i+1, token.head.i+1, token.i)
        print(dep)
        if token.i in entity_ids:
            e = (token.i, entity_ids[token.i])
            dep = "{2}({3}-{6}, PERSON-{5})".format(token.text, token.tag_, token.dep_, token.head.text, token.head.tag_, token.i+1, token.head.i+1)
            #print("ENT >>", dep)
        if token.head.i in entity_ids:
            e = (token.head.i, entity_ids[token.head.i])
            dep = "{2}(PERSON-{3}, {0}-{5})".format(token.text, token.tag_, token.dep_, token.head.text, token.head.tag_, token.i+1, token.head.i+1)
            #print("ENT >>", dep)

        if token.dep_ in ["amod","compound"]:
            print("                                     >>> MOD",token.text,token.head.text,token.head.i+1)
            x = ' '.join([token.text,token.head.text])
            idx = token.head.i+1
            if not(idx in individuals and len(individuals[idx]) > len(x)):
                individuals[idx] = x

        if token.tag_ in ["NN","NNS","NNP"]:
            print("                                     >>> ENT",token.text,token.i+1)
            x = token.text
            idx = token.i+1
            if idx not in individuals and token.head.tag_[:2] != "NN": #We deal with compounds elsewhere
                individuals[idx] = x

        if token.head.tag_ in ["NN","NNS"]:
            print("                                     >>> ENT",token.head.text,token.head.i+1)
            x = token.head.text
            idx = token.head.i+1
            if idx not in individuals:
                individuals[idx] = x

        if "VB" in token.tag_:
            print("                                     >>> EVENT",token.text,token.i+1)
            x = token.text
            idx = token.i+1
            if idx not in events:
                events[idx] = x

        if "VB" in token.head.tag_:
            print("                                     >>> EVENT HEAD",token.head.text,token.head.i+1)
            x = token.head.text
            idx = token.head.i+1
            if idx not in events:
                events[idx] = x

        if e[0] != -1: #If this dependency contains a person entity
            entity = e[1]

            #NSUBJ CASE
            if token.dep_ == 'nsubj':
                va = vec_add(entity,token.head)
                entity_vectors, vec_words = vec_update(entity_vectors,vec_words,entity,token.head,va)
                #print(token.text, token.dep_)
                for c in token.head.children:
                    #print(">>>",token.head.text,c.text,c.tag_,c.dep_)
                    if c.tag_ == "NNP":
                        obj = "_person"
                    else:
                        obj = c.text.lower()
                        va = vec_add(entity,c)
                        entity_vectors, vec_words = vec_update(entity_vectors,vec_words,entity,c,va)
                    if c.dep_ == 'dobj':
                        r = "X {0}_{1} {2}_{3}".format(token.head.text.lower(),token.head.tag_,obj,c.tag_)
                        entities[entity].append(r)
                    if c.dep_ in ['acomp','attr']:
                        r = "X is {0}_{1}".format(obj,c.tag_)
                        entities[entity].append(r)
                    if c.dep_ == "prep":
                        entities[entity].append('X '+attach_prep(c,doc))

            #DOBJ CASE
            if token.dep_ == 'dobj':
                va = vec_add(entity,token.head)
                entity_vectors, vec_words = vec_update(entity_vectors,vec_words,entity,token.head,va)
                #print(token.text, token.dep_)
                for c in token.head.children:
                    #print(">>>",token.head.text,c.text,c.tag_,c.dep_)
                    if c.tag_ == "NNP":
                        subj = "_person"
                    else:
                        subj = c.text.lower()
                        va = vec_add(entity,c)
                        entity_vectors, vec_words = vec_update(entity_vectors,vec_words,entity,c,va)
                    if c.dep_ == 'nsubj':
                        r = "{0}_{1} {2}_{3} X".format(subj,c.tag_,token.head.text.lower(),token.head.tag_)
                        entities[entity].append(r)

            #POSS CASE
            if token.dep_ == 'poss':
                #print(token.text, token.dep_, token.head.text)
                va = vec_add(entity,token.head)
                entity_vectors, vec_words = vec_update(entity_vectors,vec_words,entity,token.head,va)
                r = "X 's {0}_{1}".format(token.head.text.lower(),token.head.tag_)
                entities[entity].append(r)
            
            #APPOS / NSUBJPASS CASE - FIRST OR SECOND ARGUMENT
            if token.dep_ in ['appos','nsubjpass']:
                if e[0] < token.i: #entity is first part of compound
                    #print("APPOS",token.text, token.dep_, token.head.text)
                    va = vec_add(entity,token)
                    entity_vectors, vec_words = vec_update(entity_vectors,vec_words,entity,token,va)
                    r = "X is {0}_{1}".format(token.text.lower(),token.tag_)
                else:
                    #print("APPOS",token.head.text, token.head.dep_, token.text)
                    va = vec_add(entity,token.head)
                    entity_vectors, vec_words = vec_update(entity_vectors,vec_words,entity,token.head,va)
                    r = "X is {0}_{1}".format(token.head.text.lower(),token.head.tag_)
                entities[entity].append(r)

            #COMPOUND CASE
            if token.dep_ in ['compound']:
                #print("COMPOUND:",token.text, token.dep_, token.head.text)
                va = vec_add(entity,token)
                entity_vectors, vec_words = vec_update(entity_vectors,vec_words,entity,token,va)
                r = "{0}_{1} X".format(token.text.lower(),token.tag_)
                entities[entity].append(r)
    print("INDIVIDUALS",individuals)
    print("EVENTS:",events)
    return individuals, events, entities, entity_vectors

def parse_title_line(l):
    m=re.search("id=\"([^\"]*)\"",l)
    ID=m.group(1)
    m=re.search("title=\"([^\"]*)\"",l)
    title=m.group(1).replace(' ','_')
    return ID,title

def output_vector(v):
    s = ' '.join(str(f) for f in v)
    return s



if __name__ == "__main__":
    #base_dir = "/home/admin/share/4tera/corpora/wikipedia/2021-12-28/books/"
    base_dir = "./wikipedia/2022-12-02/books/"
    xml_dir = join(base_dir,"xml")
    linear_dir = xml_dir.replace('xml','linear')
    parsed_dir = xml_dir.replace('xml','parsed')
    cat_dir = xml_dir.replace('xml','categorisation')

    doc_content = ""
    title_line = ""
    parse = False
    write = True

    if write:
        out_nes=open(join(parsed_dir,'named.entities.rels.txt'),'w')
        out_inds=open(join(parsed_dir,'individuals.txt'),'w')
        out_events=open(join(parsed_dir,'events.txt'),'w')
        #out_vecs=open(join(parsed_dir,'entity.vecs.txt'),'w')

    f = gzip.open(join(linear_dir,'enwiki_books.gz'),'rt')
    for l in f:
        l=l.rstrip('\n')
        if l[:4] == "<doc":
            doc_content = ''
            title_line = l
            ID,title= parse_title_line(l)
            print(title_line)
        if "##" in l and parse == True:
            parse=False
        if "## Plot" in l or "## Synopsis" in l:
            parse=True
        if "</doc>" in l:
            if doc_content != '':
                print(doc_content)
                doc = nlp(doc_content)
                entity_ids, entities, entity_vectors, vec_words = process_book(doc,title,ID)
                if len(entity_ids) == 0:
                    continue
                individuals, events, entities, entity_vectors = parse_deps(doc, entity_ids, entities, entity_vectors, vec_words)
                if write:
                    out_nes.write(title_line+'\n')
                    for k,relations in entities.items():
                        for rel in relations:
                            out_nes.write(k+' '+rel+'\n')
                    out_inds.write(title_line+'\n')
                    for k,v in individuals.items():
                        out_inds.write(v+'\n')
                    out_events.write(title_line+'\n')
                    for k,v in events.items():
                        out_events.write(v+'\n')
                else:
                    print(title_line+'\n')
                    for k,relations in entities.items():
                        for rel in relations:
                            print(k+' '+rel+'\n')
                #for k,v in entity_vectors.items():
                    #out_vecs.write(k+' '+output_vector(v)+'\n')
                parse=False
                if write:
                    out_nes.write(l+'\n')
                    out_inds.write(l+'\n')
                    out_events.write(l+'\n')
                else:
                    print(l+'\n')
        if parse == True and "##" not in l:
            doc_content+=l+' '
    f.close()

        
