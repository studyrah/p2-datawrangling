#!/usr/bin/env python
import sys
import json
from optparse import OptionParser

def get_from_file(filename):
    with open(filename, "r") as f:
        return json.loads(f.read())

def get_db(db_name):
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client[db_name]
    return db

def runqry(db, coll, pipeline):
    result = db[coll].aggregate(pipeline)
    return result

if __name__ == '__main__':
    
    # a bit half hearted command line arg parsing but hey
    #
    # require a -f option containing a file with json pipeline
    # require a -d option for db
    # require a -c option for collection
    parser = OptionParser()
    
    parser.add_option("-f", "--file", help="input pipeline")
    parser.add_option("-d", "--db", help="mongo db")
    parser.add_option("-c", "--coll", help="mongo db coll")
    
    
    (options,args) = parser.parse_args()
    
    if not options.db:
        parser.error("no input db")

    if not options.coll:
        parser.error("no input collection")

    if not options.file:
        parser.error("no input query file")

    #  now get on with it at last
        
    pipeline = get_from_file(options.file)
    
    db = get_db(options.db)

    result = runqry(db, options.coll, pipeline)

    import pprint
    pprint.pprint(result)