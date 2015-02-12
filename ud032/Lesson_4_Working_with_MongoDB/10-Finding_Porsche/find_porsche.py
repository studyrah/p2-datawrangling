#!/usr/bin/env python
"""
Your task is to complete the 'porsche_query' function and in particular the query
to find all autos where the manufacturer field matches "Porsche".
Please modify only 'porsche_query' function, as only that will be taken into account.

Your code will be run against a MongoDB instance that we have provided.
If you want to run this code locally on your machine,
you have to install MongoDB and download and insert the dataset.
For instructions related to MongoDB setup and datasets please see Course Materials at
the following link:
https://www.udacity.com/wiki/ud032
"""


def get_db(db_name):
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    #print client.database_names()
    db = client[db_name]
    return db

"""
(rahaugh)
I had to manually get the autos db (there was a link on Udacity):

~/nanodegree/.........../Lesson_4_Work..../10-Finding-Porsche/autos.csv

Import into Mongodb:

mongoimport --db examples --collection autos --type csv --headerline --file ./autos.csv

Once done I tried to query:

{'manufacturer' : 'Porsche'}

Got nothing so successfully tried:

{'manufacturer_label' : 'Porsche'}
"""
def porsche_query():
    # Please fill in the query to find all autos manuafactured by Porsche
    query = {"manufacturer_label" : "Porsche"}
    return query


def find_porsche(db, query):
    return db.autos.find(query)


if __name__ == "__main__":

    db = get_db('examples')
    query = porsche_query()
    p = find_porsche(db, query)
    import pprint
    
    print "hello"
    for ans in p:
        pprint.pprint(ans)
        
    #pprint.pprint(db.autos.find_one())
    
    #print db.collection_names()
    
    #c = db.autos.find()
    #for ans in c:
    #    pprint.pprint(ans)
    
    