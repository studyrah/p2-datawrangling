#!/usr/bin/env python
# -*- coding: utf-8 -*-
#import xml.etree.ElementTree as ET
from lxml import etree as ET
import pprint
import re
"""
Simple script (based upon Lesson 6 Part 2) that iteratively parses an OSM XML
file and tests keys against a set of regular expressions with a view to 
determining whether they can be loaded into MongoDb
"""

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


"""
 It the element is a "tag", test the key ('k') against a number of regexes
 to determine validity
 
 returns dictionary containing a count of how many time each regex hit
"""
def key_type(element, keys):

    if element.tag == "tag":

        #key = element.get('k')
        key = element.attrib['k']

        if lower.search(key):
            keys['lower'] = keys['lower'] + 1
        elif lower_colon.search(key):
            keys['lower_colon'] = keys['lower_colon'] + 1
        elif problemchars.search(key):
            keys['problemchars'] = keys['problemchars'] + 1
        else:     
            keys['other'] = keys['other'] + 1
                
    return keys


"""
 Iterates through each element and generates a dictionary of counts for each
 flavour of tag key name format (as determined by matching regexes)
"""
def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    
    osm_file = open(filename, "r")

    context = ET.iterparse(osm_file, events=("start", "end"))

    context = iter(context)
   
    # step over root
    event,root = context.next()
    
   
    for event,elem in context:

        if event == "end":

            keys = key_type(elem, keys)

            #clear the element to stop building an in memory document
            elem.clear()
                            
    return keys    
    
"""
  main()
"""
if __name__ == "__main__":

    keys = process_map('../data/cardiff-newport-bristol-bath_england.osm')
    pprint.pprint(keys)
