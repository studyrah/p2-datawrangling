#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
In this problem set you work with cities infobox data, audit it, come up with a cleaning idea and then clean it up.
In the first exercise we want you to audit the datatypes that can be found in some particular fields in the dataset.
The possible types of values can be:
- 'NoneType' if the value is a string "NULL" or an empty string ""
- 'list', if the value starts with "{"
- 'int', if the value can be cast to int
- 'float', if the value can be cast to float, but is not an int
- 'str', for all other values

The audit_file function should return a dictionary containing fieldnames and the datatypes that can be found in the field.
All the data initially is a string, so you have to do some checks on the values first.

"""
import codecs
import csv
import json
import pprint

CITIES = 'cities.csv'

FIELDS = ["name", "timeZone_label", "utcOffset", "homepage", "governmentType_label", "isPartOf_label", "areaCode", "populationTotal", 
          "elevation", "maximumElevation", "minimumElevation", "populationDensity", "wgs84_pos#lat", "wgs84_pos#long", 
          "areaLand", "areaMetro", "areaUrban"]

def getType(value):
    if value == "NULL" or value == "":                
        return type(None)
    
    if value.startswith("{"):
        return type([])
        
    try:
        i = int(value)
        return type(i)
        
    except:
        pass
    
    try:    
        f = float(value)
        return type(f)
    except:    
        return type(value)
    

def audit_file(filename, fields):
    fieldtypes = {}

    # YOUR CODE HERE
    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames
        
        #jump over schema'esque lines
        reader.next()
        reader.next()
        reader.next()
        
        for row in reader:
            
            for field in fields:
                
                s = fieldtypes.get(field, set())
                s.add(getType(row[field]))      
                fieldtypes[field] = s
    
    return fieldtypes


def test():
    fieldtypes = audit_file(CITIES, FIELDS)

    pprint.pprint(fieldtypes)
    
    assert fieldtypes["areaLand"] == set([type(1.1), type([]), type(None)])
    assert fieldtypes['areaMetro'] == set([type(1.1), type(None)])
    
if __name__ == "__main__":
    test()
