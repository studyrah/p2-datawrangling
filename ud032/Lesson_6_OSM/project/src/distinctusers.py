#!/usr/bin/env python
# -*- coding: utf-8 -*-
#import xml.etree.ElementTree as ET
from lxml import etree as ET
import pprint


"""
Simple script (based upon Lesson 6 Part 3) that iteratively parses an OSM XML
file and reports a count of distinct users
"""

"""
Extracts the user attribute out of a tag, if it exists

returns the user name or None
"""
def get_user(element):
    for tag in element.iter():
        if tag.attrib.has_key('user'):
            return tag.attrib['user']
    return None


"""
Processes the map and returens the list of contributing users
"""
def process_map(filename):
    users = set()
    
    context = ET.iterparse(filename, events=("start", "end"))

    context = iter(context)
    
    event,root = context.next()
    
    for event,elem in context:

        if event == "end":

            user = get_user(elem)
            if user:            
                users.add(user)
            
            elem.clear()
                        
    return users


"""
  main()
"""
if __name__ == "__main__":
    users = process_map('../data/cardiff-newport-bristol-bath_england.osm')
    pprint.pprint(users)