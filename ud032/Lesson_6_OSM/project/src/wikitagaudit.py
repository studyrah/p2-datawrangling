# -*- coding: utf-8 -*-
#!/usr/bin/env python
import csv
import os
import pprint
import Levenshtein
import sys
from lxml import etree as ET

reload(sys)
sys.setdefaultencoding('utf8')


"""
Performs an audit of dataset tags against the best practice tag keys and 
values listed on the osmwiki

Essentially we look for exact matches on keys/values and where this fails
we look for substring matches on key/values and calculate the closest
key/value matches based upon edit distance
"""


OSMFILE = "../data/cardiff-newport-bristol-bath_england.osm"

# our reference data file
KEYFILE = "../data/keys.csv"
TAGFILE = "../data/tags.csv"

# generated lookup of keys and values
tag_lookup = {}

#
#variety of counters to calculate and report
#

#simply number of tags in the dataset
numtags = 0 
#number of times we do and don't match an osm wiki key
kmatch = 0
knomatch = 0
#number of times we do and don't get a substring match to an osm wiki key
ksubmatch = {}
kbestmatch = {}
# vpopulated corresponds to the case whereby the matching osm wiki key
# has associated best practice values to match against
vpopulated = 0
vnopopulated = 0
# value matches an osm wiki value for the matching key
vmatch = 0
vnomatch = 0
# value substring matches an osm wiki value for the matchin key
vsubmatch = {}
vbestmatch = {}

"""
process csv file to produce lookup
"""
def parse_csv_file(datafile, add_lookup_entry, lookup):
    with open(datafile, 'rb') as f:
        rows = csv.reader(f, delimiter='|', quotechar='\"')
                
        for row in rows:
            add_lookup_entry(lookup, row)            


"""
Add the key (at position 0 of the given row) to the lookup

One of the lookups contains just the keys, there are no associated values
so we just create an empty set
"""            
def add_key_to_lookup(lookup, row):
    ukey = unicode(row[0])    
    
    if not lookup.has_key(ukey):
        lookup[ukey] = set()

"""
Add the key/value pair (position 0,1 respectively in row) to the lookup
"""        
def add_tag_to_lookup(lookup, row):
    ukey = unicode(row[0])    
    uval = unicode(row[1])
    
    vals = lookup.get(ukey, set())            
    vals.add(uval)
    lookup[ukey] = vals

"""
Calculates the edit distance of the given string (value) from each
string in the lookup (essentially an iterable of strings), returning a set of
the closest matching.

Distance is calculated using the Levenshtein edit distance algorithm
"""
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

"""
Performs a sub string match of the given string (value) agaisnt each string
in the given lookup (key_lookup), returning a set of all the matches
"""
def substring_matches(key_lookup, value):
    uvalue = unicode(value)
    
    keys = set()
    for key in key_lookup:
        if key.find(uvalue) >= 0:
            keys.add(key)
            
    return keys

"""
Audit the given key/value against the lookup
"""
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
