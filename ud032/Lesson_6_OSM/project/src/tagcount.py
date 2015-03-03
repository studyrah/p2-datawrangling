#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple script (based upon Lesson 6 Part 1) that iteratively parses an OSM XML
file and reports counts of each tag type


References for iterative parsing performance issue:

http://stackoverflow.com/questions/7370801/measure-time-elapsed-in-python
http://www.ibm.com/developerworks/xml/library/x-hiperfparse/

"""
#import xml.etree.ElementTree as ET
from lxml import etree as ET

import pprint
#import timeit
import time

def count_tags(filename):
    tags = {}

    context = ET.iterparse(filename, events=("start", "end"))

    context = iter(context)
    
    event,root = context.next()
    
    for event,elem in context:
   
        if event == "end":
            tags[elem.tag] = tags.get(elem.tag,0) + 1

            #for k,v in elem.attrib.iteritems():
            #        print elem.tag + " attrib: " + k + " - " + v
            #    return tags
            
            elem.clear()
    
    
    pprint.pprint(tags2)
    return tags    

"""
def test():

    tags = count_tags('example.osm')
    pprint.pprint(tags)
    assert tags == {'bounds': 1,
                     'member': 3,
                     'nd': 4,
                     'node': 20,
                     'osm': 1,
                     'relation': 1,
                     'tag': 7,
                     'way': 1}

"""    

if __name__ == "__main__":

    start = time.time()
    tags = count_tags('../data/cardiff-newport-bristol-bath_england.osm')
    end = time.time()
    
    print "duration: " + str(end - start)
    pprint.pprint(tags)