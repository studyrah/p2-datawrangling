# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""

"""
import csv
import os
import pprint
import Levenshtein
import sys
from lxml import etree as ET

reload(sys)
sys.setdefaultencoding('utf8')

OSMFILE = "../data/cardiff-newport-bristol-bath_england.osm"
KEYFILE = "../data/keys.csv"
TAGFILE = "../data/tags.csv"

tag_lookup = {}

numtags = 0
kmatch = 0
knomatch = 0
ksubmatch = {}
kbestmatch = {}

vpopulated = 0
vnopopulated = 0
vmatch = 0
vnomatch = 0
vsubmatch = {}
vbestmatch = {}


def parse_csv_file(datafile, add_lookup_entry, lookup):
    with open(datafile, 'rb') as f:
        rows = csv.reader(f, delimiter='|', quotechar='\"')
                
        for row in rows:
            add_lookup_entry(lookup, row)            


            
def add_key_to_lookup(lookup, row):
    ukey = unicode(row[0])    
    
    if not lookup.has_key(ukey):
        lookup[ukey] = set()

        
def add_tag_to_lookup(lookup, row):
    ukey = unicode(row[0])    
    uval = unicode(row[1])
    
    vals = lookup.get(ukey, set())            
    vals.add(uval)
    lookup[ukey] = vals


def best_matches(key_lookup, value):
    uvalue = value
    lowest_keys = set()
    lowest_score = 1000000 # ridiculously high

    for key in key_lookup:        
        score = Levenshtein.distance(key,uvalue)
        
        if score == lowest_score:
            lowest_keys.add(key)
            lowest_score = score
        elif score < lowest_score:
            lowest_keys = set()
            lowest_keys.add(key)
            lowest_score = score
    
    return (lowest_keys,lowest_score)

def substring_matches(key_lookup, value):
    uvalue = unicode(value)
    
    keys = set()
    for key in key_lookup:
        if key.find(uvalue) >= 0:
            keys.add(key)
            
    return keys

def audittag(tag_lookup,test_key,test_val):
    global numtags
    global kmatch
    global knomatch
    global ksubmatch
    global kbestmatch

    global vpopulated
    global vnopopulated
    global vmatch
    global vnomatch
    global vsubmatch
    global vbestmatch
    
    
    test_key = unicode(test_key)
    test_val = unicode(test_val)

    kout = {"value" : test_key}
    vout = {"value" : test_val}        
    
    # 1.  check exact match on - tags key
    if test_key in tag_lookup:
        kout["match"] = True  
        kmatch += 1             

        if len(tag_lookup[test_key]) == 0:
            vnopopulated += 1
            vout["populated"] = False
        elif test_val in tag_lookup[test_key]:
            # 1.1 check exact match on tags val                        
            vout["populated"] = True        
            vpopulated += 1
            vout["match"] = True                    
            vmatch += 1
        else:
            # 1.2 substring match on tags val
            vout["populated"] = True        
            vpopulated += 1
            vnomatch += 1

            partials = substring_matches(tag_lookup[test_key], test_val)        
            
            vsubmatch[len(partials)] = vsubmatch.get(len(partials), 0) + 1

            vout["substring"] = \
            {
                "count" : len(partials),
                "match" : list(partials)
            }
        
            # 1.3 best match on tags val            
            lowest_vals,lowest_score = best_matches(tag_lookup[test_key], test_val)                

            vbestmatch[len(lowest_vals)] = vbestmatch.get(len(lowest_vals), 0) + 1

            vout["bestmatch"] = \
            {
                "score" : lowest_score,                
                "count" : len(lowest_vals),
                "match" : list(lowest_vals)
            }

    # 3. look at key substring and best matches
    else:
        kout["match"] = False   
        knomatch += 1            

        # 3.1  substring key
        partials = substring_matches(tag_lookup, test_key)        

        ksubmatch[len(partials)] = ksubmatch.get(len(partials), 0) + 1
        
        kout["substring"] = \
        {
            "count" : len(partials),
            "match" : list(partials)
        }
               
        # 3.2  best match key
        lowest_keys,lowest_score = best_matches(tag_lookup, test_key)                

        kbestmatch[len(lowest_keys)] = kbestmatch.get(len(lowest_keys), 0) + 1

        kout["bestmatch"] = \
        {
            "score" : lowest_score,                
            "count" : len(lowest_keys),
            "match" : list(lowest_keys)
        }
    
    return {"k" : kout, "v" : vout}



"""
  iterates through the xml elements asking whether/how close the key/values
  are to matching those declared on the wiki:
"""
def auditfile(osmfile):
    
    osm_file = open(osmfile, "r")

    context = ET.iterparse(osm_file, events=("start", "end"))

    context = iter(context)
    
    # skip over root
    event,root = context.next()    
    
    for event,elem in context:

        if event == "end":

            if elem.tag == "node" or elem.tag == "way":
                for tag in elem.iter("tag"):
                    k = tag.attrib['k']
                    v = tag.attrib['v']
                    
                    print(audittag(tag_lookup,k,v))
                        
                # clear else we build the whole document in memory        
                elem.clear()                              
        

def test():
    
    print("===========================")
    # 1.1 matching tag key and value
    audittag(tag_lookup,"sport","basketball")
    
    print("===========================")
    # 1.2 matching tag key and substring value
    audittag(tag_lookup,"sport","ball")   
    
    print("===========================")
    # 1.3 matching tag key and value not substring but close to a value
    audittag(tag_lookup,"sport","climbinh")
    
    print("===========================")
    # 1.3 matching tag key and value not substring and not close to a value
    audittag(tag_lookup,"sport","couch potato")    
        
    print("===========================")
    # 1.x matching both key and tag key
    audittag(tag_lookup,"cycleway","doesn't matter")    

    print("===========================")    
    # 2. matching key only
    audittag(tag_lookup,"is_in:county","doesn't matter")

    print("===========================")    
    # 3.1 substring match on key
    audittag(tag_lookup,"spor","doesn't matter")

    print("===========================")    
    # 3.2 substring match on key
    audittag(tag_lookup,"street_name","doesn't matter")

    print("===========================")    
    # 3.3 best match tag key
    audittag(tag_lookup,"sporty","doesn't matter")

    print("===========================")    
    # 3.2 best match on key
    audittag(tag_lookup,"street_namr","doesn't matter")
    

if __name__ == "__main__":

    # first load the lookup files
    parse_csv_file(KEYFILE, add_key_to_lookup, tag_lookup)
    parse_csv_file(TAGFILE, add_tag_to_lookup, tag_lookup)
    
    #test()   
    auditfile(OSMFILE)     
    
    print("numtags: " + str(numtags))

    print("kmatch: " + str(kmatch))
    print("knomatch: " + str(knomatch))
    print("ksubmatch: ")
    pprint.pprint(ksubmatch)
    print("kbestmatch: ")
    pprint.pprint(kbestmatch)

    print("vpopulated: " + str(vpopulated))
    print("vnopopulated: " + str(vnopopulated))

    print("vmatch: " + str(vmatch))
    print("vnomatch: " + str(vnomatch))
    print("vsubmatch: ")
    pprint.pprint(vsubmatch)
    print("vbestmatch: ")
    pprint.pprint(vbestmatch)
