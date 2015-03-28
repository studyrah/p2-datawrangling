#!/usr/bin/env python
# -*- coding: utf-8 -*-
#import xml.etree.ElementTree as ET
from lxml import etree as ET
import pprint
import re
import codecs
import json
import sys
"""

"""


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

def shape_element(element):
    node = {}

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
                
                #- if second level tag "k" value starts with "addr:", it should be added to a dictionary "address"                
                if k.startswith('addr'):
                    splits = k.split(':')
                    
                    #- if second level tag "k" value contains problematic characters, it should be ignored
                    if problemchars.search(k) == None:
                        #- if there is a second ":" that separates the type/direction of a street,
                        if len(splits) == 2:
                            address[splits[1]] = v
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




def process_map(file_in, pretty = False):
    
    file_out = "{0}.first.json".format(file_in)
    
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
