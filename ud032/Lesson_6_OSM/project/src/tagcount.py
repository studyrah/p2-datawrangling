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
import time

def count_tags(filename):
    tags = {}

    context = ET.iterparse(filename, events=("start", "end"))

    context = iter(context)

    #skip over root    
    event,root = context.next()    
    
    for event,elem in context:
   
        if event == "end":
            tags[elem.tag] = tags.get(elem.tag,0) + 1

            # important to clear, else we will build the whole document in mem                
            elem.clear()
    
    return tags    

    
if __name__ == "__main__":

    start = time.time()

    tags = count_tags('../data/cardiff-newport-bristol-bath_england.osm')

    end = time.time()
    
    print "duration: " + str(end - start)
    pprint.pprint(tags)