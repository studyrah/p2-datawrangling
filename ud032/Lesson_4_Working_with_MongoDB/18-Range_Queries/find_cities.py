#!/usr/bin/env python
""" Your task is to write a query that will return all cities
that are founded in 21st century.
Please modify only 'range_query' function, as only that will be taken into account.

Your code will be run against a MongoDB instance that we have provided.
If you want to run this code locally on your machine,
you have to install MongoDB, download and insert the dataset.
For instructions related to MongoDB setup and datasets please see Course Materials.
"""
from datetime import datetime
    
def get_db():
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client.examples
    return db


def range_query():
    # You can use datetime(year, month, day) to specify date in the query
    
    #(rahaugh) returns plenty    
    #query = {"foundingDate" : {"$ne" : 'NULL'}}
    
    #(rahaugh)
    # works on Udacity but, probably due to the way I imported the data
    # this returns nothing    
    #query = {"foundingDate" : {"$gte" : datetime(2000,1,1)}}
    
    # this sort of works but actually gives entirely the wrong answers
    query = {"foundingDate" : {"$gte" : "2000-01-01", \
                               "$ne" : 'NULL'}}    
    
    return query
    


if __name__ == "__main__":

    db = get_db()
    query = range_query()

    print db.cities.find().count()

    cities = db.cities.find(query)

    print "Found cities:", cities.count()
    import pprint
    pprint.pprint(cities[12])
    #cits = db.cities.find()
    
    #for cit in cits:
    #    pprint.pprint(cit)
