#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Let's assume that you combined the code from the previous 2 exercises
# with code from the lesson on how to build requests, and downloaded all the data locally.
# The files are in a directory "data", named after the carrier and airport:
# "{}-{}.html".format(carrier, airport), for example "FL-ATL.html".
# The table with flight info has a table class="dataTDRight".
# There are couple of helper functions to deal with the data files.
# Please do not change them for grading purposes.
# All your changes should be in the 'process_file' function
from bs4 import BeautifulSoup
from zipfile import ZipFile
import os

datadir = "data"


def open_zip(datadir):
    with ZipFile('{0}.zip'.format(datadir), 'r') as myzip:
        myzip.extractall()


def process_all(datadir):
    files = os.listdir(datadir)
    return files


def process_file(f):
    # This is example of the datastructure you should return
    # Each item in the list should be a dictionary containing all the relevant data
    # Note - year, month, and the flight data should be integers
    # You should skip the rows that contain the TOTAL data for a year
    # data = [{"courier": "FL",
    #         "airport": "ATL",
    #         "year": 2012,
    #         "month": 12,
    #         "flights": {"domestic": 100,
    #                     "international": 100}
    #         },
    #         {"courier": "..."}
    # ]
    data = []
    info = {}
    info["courier"], info["airport"] = f[:6].split("-")
    
    
    with open("{}/{}".format(datadir, f), "r") as html:

        soup = BeautifulSoup(html)
        
        t = soup.find("table", class_="dataTDRight")
        
        for tr in t.find_all("tr", class_="dataTDRight"):
            datarow = tr.find_all("td")
            
            month = datarow[1].text

            if month != "TOTAL":            
            
                year = int(datarow[0].text)
                month = int(datarow[1].text)
            
                #note that domestic/international are of form "222,0234"
                #remove commas to parse into an int
                domestic = int(datarow[2].text.replace(",",""))
                international = int(datarow[3].text.replace(",",""))
                
                if month != "TOTAL":
                    data.append({"courier" : info["courier"], "airport" : info["airport"], 
                                 "year": year, "month" : month,
                                 "flights": {"domestic": domestic,
                                             "international": international}})
                
    return data


def test():
    print "Running a simple test..."
    open_zip(datadir)
    files = process_all(datadir)
    data = []
    for f in files:
        data += process_file(f)
    assert len(data) == 3
    for entry in data[:3]:
        assert type(entry["year"]) == int
        assert type(entry["flights"]["domestic"]) == int
        assert len(entry["airport"]) == 3
        assert len(entry["courier"]) == 2
    print "... success!"

def test_local():
    print "Running a simple test..."
    #open_zip(datadir)
    #files = process_all(datadir)
    
    files = []
    files.append("FL-ATL.html")
    
    data = []
    for f in files:
        data += process_file(f)
    assert len(data) == 3
    for entry in data[:3]:
        assert type(entry["year"]) == int
        assert type(entry["flights"]["domestic"]) == int
        assert len(entry["airport"]) == 3
        assert len(entry["courier"]) == 2
    print "... success!"

if __name__ == "__main__":
    #test()
    test_local()