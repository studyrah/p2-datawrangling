#!/usr/bin/env python
# -*- coding: utf-8 -*-
#import xml.etree.ElementTree as ET
from lxml import etree as ET
import pprint
import re
"""
Your task is to explore the data a bit more.
The first task is a fun one - find out how many unique users
have contributed to the map in this particular area!

The function process_map should return a set of unique user IDs ("uid")
"""

def get_user(element):
    for tag in element.iter():
        if tag.attrib.has_key('user'):
            return tag.attrib['user']
    return None


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


def test():

    users = process_map('../data/cardiff-newport-bristol-bath_england.osm')
    pprint.pprint(users)
    print "num distinct users: " + str(len(users))
    #assert len(users) == 6



if __name__ == "__main__":
    test()