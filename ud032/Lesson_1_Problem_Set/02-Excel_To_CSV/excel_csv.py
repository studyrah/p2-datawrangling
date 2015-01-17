# -*- coding: utf-8 -*-
# Find the time and value of max load for each of the regions
# COAST, EAST, FAR_WEST, NORTH, NORTH_C, SOUTHERN, SOUTH_C, WEST
# and write the result out in a csv file, using pipe character | as the delimiter.
# An example output can be seen in the "example.csv" file.
import xlrd
import os
import csv
from zipfile import ZipFile
datafile = "2013_ERCOT_Hourly_Load_Data.xls"
outfile = "2013_Max_Loads.csv"

headers = ["Station","Year","Month","Day","Hour","Max Load"]

regions = [("COAST",1),
           ("EAST",2),
           ("FAR_WEST",3),
           ("NORTH",4),
           ("NORTH_C",5),
           ("SOUTHERN",6),
           ("SOUTH_C",7),
           ("WEST",8)]

def open_zip(datafile):
    with ZipFile('{0}.zip'.format(datafile), 'r') as myzip:
        myzip.extractall()


def parse_file(datafile):
    workbook = xlrd.open_workbook(datafile)
    sheet = workbook.sheet_by_index(0)
    data = []
    # YOUR CODE HERE
    # Remember that you can use xlrd.xldate_as_tuple(sometime, 0) to convert
    # Excel date to Python tuple of (year, month, day, hour, minute, second)

    

    for region in regions:
        name = region[0]
        index = region[1]
        load_col = sheet.col_values(index,start_rowx=1, end_rowx=None)
        max_load = max(load_col)

        #now lets handle dates for the corresponding rows    
        max_load_index = load_col.index(max_load)
    
        max_load_time_tuple = xlrd.xldate_as_tuple(sheet.cell_value(max_load_index + 1,0), 0)
        
        summary = [name] + list(max_load_time_tuple)[0:4] + [max_load]
        
        data.append(summary)
        
    
    return data

def save_file(data, filename):
    
    with open(filename,'wb') as f:    
        w = csv.writer(f, delimiter='|',        
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)    

        w.writerow(headers)

        for row in data:
            w.writerow(row)            
        
    
def test():
    open_zip(datafile)
    data = parse_file(datafile)
    save_file(data, outfile)

    ans = {'FAR_WEST': {'Max Load': "2281.2722140000024", 'Year': "2013", "Month": "6", "Day": "26", "Hour": "17"}}
    
    fields = ["Year", "Month", "Day", "Hour", "Max Load"]
    with open(outfile) as of:
        csvfile = csv.DictReader(of, delimiter="|")
        for line in csvfile:                                    
            s = line["Station"]
            if s == 'FAR_WEST':
                for field in fields:
                    assert ans[s][field] == line[field]

        
test()