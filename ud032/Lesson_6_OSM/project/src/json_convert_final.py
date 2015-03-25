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
"""
Your task is to wrangle the data and transform the shape of the data
into the model we mentioned earlier. The output should be a list of dictionaries
that look like this:

{
"id": "2406124091",
"type: "node",
"visible":"true",
"created": {
          "version":"2",
          "changeset":"17206049",
          "timestamp":"2013-08-03T16:43:42Z",
          "user":"linuxUser16",
          "uid":"1219059"
        },
"pos": [41.9757030, -87.6921867],
"address": {
          "housenumber": "5157",
          "postcode": "60625",
          "street": "North Lincoln Ave"
        },
"amenity": "restaurant",
"cuisine": "mexican",
"name": "La Cabana De Don Luis",
"phone": "1 (773)-271-5176"
}

You have to complete the function 'shape_element'.
We have provided a function that will parse the map file, and call the function with the element
as an argument. You should return a dictionary, containing the shaped data for that element.
We have also provided a way to save the data in a file, so that you could use
mongoimport later on to import the shaped data into MongoDB. 

Note that in this exercise we do not use the 'update street name' procedures
you worked on in the previous exercise. If you are using this code in your final
project, you are strongly encouraged to use the code from previous exercise to 
update the street names before you save them to JSON. 

In particular the following things should be done:
- you should process only 2 types of top level tags: "node" and "way"
- all attributes of "node" and "way" should be turned into regular key/value pairs, except:
    - attributes in the CREATED array should be added under a key "created"
    - attributes for latitude and longitude should be added to a "pos" array,
      for use in geospacial indexing. Make sure the values inside "pos" array are floats
      and not strings. 
- if second level tag "k" value contains problematic characters, it should be ignored
- if second level tag "k" value starts with "addr:", it should be added to a dictionary "address"
- if second level tag "k" value does not start with "addr:", but contains ":", you can process it
  same as any other tag.
- if there is a second ":" that separates the type/direction of a street,
  the tag should be ignored, for example:

<tag k="addr:housenumber" v="5158"/>
<tag k="addr:street" v="North Lincoln Avenue"/>
<tag k="addr:street:name" v="Lincoln"/>
<tag k="addr:street:prefix" v="North"/>
<tag k="addr:street:type" v="Avenue"/>
<tag k="amenity" v="pharmacy"/>

  should be turned into:

{...
"address": {
    "housenumber": 5158,
    "street": "North Lincoln Avenue"
}
"amenity": "pharmacy",
...
}

- for "way" specifically:

  <nd ref="305896090"/>
  <nd ref="1719825889"/>

should be turned into
"node_refs": ["305896090", "1719825889"]
"""
cntr = 0

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

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

                # we have some postcode variants we want to make consistent
                if k == "postal_code" or k == "postcode":
                    k = "addr:postalcode"
                if k == "source:postcode":
                    k = "source:addr:postcode"
                if k == "note:postcode":
                    k = "note:addr:postcode"
                
                #- if second level tag "k" value starts with "addr:", it should be added to a dictionary "address"                
                if k.startswith('addr'):
                    splits = k.split(':')
                    
                    # if its a street name then map it
                    if k == "addr:street":
                        address["street"] = update_name(v, mapping)
                    elif is_postcode(k):
                        address["postcode"] = v
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


def process_map(file_in, pretty = False):
    
    file_out = "{0}.first.json".format(file_in)
    
    #data = []

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
                            
        """
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
        """
    #return data

    
    
if __name__ == "__main__":
    #data = process_map('../data/cardiff-newport-bristol-bath_england.osm', True)
    #data = process_map('../../part5/example.osm', True)
    process_map('../data/cardiff-newport-bristol-bath_england.osm', False)
