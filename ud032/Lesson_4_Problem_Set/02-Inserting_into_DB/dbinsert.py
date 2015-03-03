import json

def insert_data(data, db):

    # Your code here. Insert the data into a collection 'arachnid'
    if 'arachnid' not in db.collection_names():
        db.create_collection("arachnid")
    
    db.arachnid.insert(data)
    
    
    #for rec in data:
    #    db.arachnid.insert(rec)


if __name__ == "__main__":
    
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017")
    db = client.examples

    with open('arachnid.json') as f:
        
        data = json.loads(f.read())
        insert_data(data, db)
        print db.arachnid.find_one()