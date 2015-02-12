#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
In this problem set you work with another type of infobox data, audit it, clean it, 
come up with a data model, insert it into a MongoDB and then run some queries against your database.
The set contains data about Arachnid class.

The data is already in the database. But you have been given a task to also include 'binomialAuthority'
information in the data, so you have to go through the data and update the existing entries.

The following things should be done in the function add_field:
- process the csv file and extract 2 fields - 'rdf-schema#label' and 'binomialAuthority_label'
- clean up the 'rdf-schema#label' same way as in the first exercise - removing redundant "(spider)" suffixes
- return a dictionary, with 'label' being the key, and 'binomialAuthority_label' the value
- if 'binomialAuthority_label' is "NULL", skip the item

The following should be done in the function update_db:
- query the database by using the field 'label'
- update the data, by adding a new item under 'classification' with a key 'binomialAuthority'


The resulting data should look like this:
- the output structure should be as follows:
{ 'label': 'Argiope',
  'uri': 'http://dbpedia.org/resource/Argiope_(spider)',
  'description': 'The genus Argiope includes rather large and spectacular spiders that often ...',
  'name': 'Argiope',
  'synonym': ["One", "Two"],
  'classification': {
                    'binomialAuthority': None,
                    'family': 'Orb-weaver spider',
                    'class': 'Arachnid',
                    'phylum': 'Arthropod',
                    'order': 'Spider',
                    'kingdom': 'Animal',
                    'genus': None
                    }
}
"""
import codecs
import csv
import json
import pprint
import re

DATAFILE = 'arachnid.csv'
FIELDS ={'rdf-schema#label': 'label',
         'binomialAuthority_label': 'binomialAuthority'}


def add_field(filename, fields):

    process_fields = fields.keys()
        
    print(process_fields)
    data = {}
    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        for i in range(3):
            l = reader.next()
        # YOUR CODE HERE
            
        #(rahaugh) not sure why we are given 'fields' and then add the
        #keys to process_fields.  This implies we can loop through these
        #and process the data.  BUT we have distinct processing for
        #label and binomialAuthority respectively and as fields is a dict
        #we can't rely upon the ordering of fields.keys()?????
        
        for l in reader:            
            label = l['rdf-schema#label']
            bina = l['binomialAuthority_label']
            
            if bina != 'NULL':
                label = re.sub(" *\(.*\)","",label).strip()
            
            data[label] = bina
            
    return data


def update_db(data, db):

    for label in data:
        record = db.arachnid.find_one({'label': label})
        if (record != None):
            record['classification']['binomialAuthority'] = data[label]

            db.arachnid.save(record)

def test():
    # Please change only the add_field and update_db functions!
    # Changes done to this function will not be taken into account
    # when doing a Test Run or Submit, they are just for your own reference
    # and as an example for running this code locally!
    
    data = add_field(DATAFILE, FIELDS)
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017")
    db = client.examples

    update_db(data, db)

    updated = db.arachnid.find_one({'label': 'Opisthoncana'})
    assert updated['classification']['binomialAuthority'] == 'Embrik Strand'
    pprint.pprint(data)



if __name__ == "__main__":
    test()