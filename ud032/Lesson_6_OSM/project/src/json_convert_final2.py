#!/usr/bin/env python
# -*- coding: utf-8 -*-
#import xml.etree.ElementTree as ET
from lxml import etree as ET
import pprint
import re
import codecs
import json
import sys
from streetaudit import update_name
from streetaudit import mapping
from streetaudit import is_street_name
import postcode_utils

"""
cleanse the data and produce output json fit for Mongo.

In particular this will adhere to the format and rules set out in lesson 6
but will additionally cleanse street names and postcodes
"""
cntr = 0

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

"""
converts the given element into appropriate json ready data
"""
def shape_element(element):
    node = {}
    global cntr
    #- you should process only 2 types of top level tags: "node" and "way"    
    if element.tag == "node" or element.tag == "way" :

        #I have not used type as my key as there are
        #tags with key = type which will accidentally
        #overwrite
        node['etype'] = element.tag
        
        #
        #process top level element attributes        
        #
        created = {}

        lat = None
        lon = None
        
        for k,v in element.attrib.iteritems():

            #- attributes in the CREATED array should be added under a key "created"                       
            if k in CREATED:
                
                # need to do somthing special for timestamp, else it will
                # be imported by mongoimport as a string
                if k == 'timestamp':
                    v = {"$date" : v}
                    
                created[k] = v                
            #- attributes for latitude and longitude should be added to a "pos" array,                
            elif k == 'lat':
                lat = float(v)
            elif k == 'lon':
                lon = float(v)
            else:
                #- if second level tag "k" value does not start with "addr:", but contains ":", you can process it                
                #if k.find(':') != -1
                node[k] = v                
        
        if lat and lon:
            node['pos'] = [lat,lon]
        
        if created:
            node['created'] = created
                        
        #    
        #process each child element
        #
        address = {}
        node_refs = []
                
        for child in element:
            #process each child elements attributes
            if child.tag == 'tag':
                k = child.attrib['k']
                v = child.attrib['v']                

                # we want to 'do some cleansing' if its a postcode
                # or metadata about postcodes
                if postcode_utils.is_postcode_key(k):
                    k,v = postcode_utils.cleanse_postcode(k,v)
                elif postcode_utils.is_postcode_meta_key(k):
                    k = postcode_utils.cleanse_meta_key(k)
                
                #- if second level tag "k" value starts with "addr:", it should be added to a dictionary "address"                
                if k.startswith('addr'):
                    splits = k.split(':')
                    
                    # if its a street name then map it
                    if k == "addr:street":
                        address["street"] = update_name(v, mapping)
                    #- if second level tag "k" value contains problematic characters, it should be ignored
                    elif problemchars.search(k) == None:
                        if len(splits) == 2:
                            address[splits[1]] = v
                            
                elif k == "source:addr:postcode":
                    # a better model might be to make postcode a compound
                    # object with a value, a source and a note but not yet                    
                    address["postcode.source"] = v
                elif k == "note:addr:postcode":
                    address["postcode.note"] = v
                else:
                    node[k] = v

            elif child.tag == 'nd':
                """
                - for "way" specifically:

                  <nd ref="305896090"/>
                  <nd ref="1719825889"/>

                should be turned into
                "node_refs": ["305896090", "1719825889"]
                """                
                node_refs.append(child.attrib['ref'])
            
        
        if len(address) > 0:
            node['address'] = address
            
        if len(node_refs) > 0:
            node['node_refs'] = node_refs            
                                                
        #pprint.pprint(node)
        
        return node
    else:
        return None


def is_postcode(k):
    return k == "addr:postcode"


"""
Iterate the given file, converting to cleansed json
"""
def process_map(file_in, pretty = False):
    
    file_out = "{0}.final.json".format(file_in)
    
    with codecs.open(file_out, "w") as fo:
 
        context = ET.iterparse(file_in, events=("start", "end"))

        context = iter(context)
    
        event,root = context.next()    
   
        for event,elem in context:

            if event == "end":
                el = shape_element(elem)
                if el:
                    #data.append(el)
                    if pretty:
                        fo.write(json.dumps(el, indent=2)+"\n")
                    else:
                        fo.write(json.dumps(el) + "\n")
                        #fo.write(json.dumps(el))

                    elem.clear()
                            
    
    
if __name__ == "__main__":
    #data = process_map('../data/cardiff-newport-bristol-bath_england.osm', True)
    #data = process_map('../../part5/example.osm', True)
    process_map('../data/cardiff-newport-bristol-bath_england.osm', False)

