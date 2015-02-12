"""
Your task is to check the "productionStartYear" of the DBPedia autos datafile for valid values.
The following things should be done:
- check if the field "productionStartYear" contains a year
- check if the year is in range 1886-2014
- convert the value of the field to be just a year (not full datetime)
- the rest of the fields and values should stay the same
- if the value of the field is a valid year in range, as described above,
  write that line to the output_good file
- if the value of the field is not a valid year, 
  write that line to the output_bad file
- discard rows (neither write to good nor bad) if the URI is not from dbpedia.org
- you should use the provided way of reading and writing data (DictReader and DictWriter)
  They will take care of dealing with the header.

You can write helper functions for checking the data and writing the files, but we will call only the 
'process_file' with 3 arguments (inputfile, output_good, output_bad).
"""
import csv
import pprint

INPUT_FILE = 'autos.csv'
OUTPUT_GOOD = 'autos-valid.csv'
OUTPUT_BAD = 'FIXME-autos.csv'

h = ["URI","rdf-schema#label","rdf-schema#comment","assembly_label","assembly","automobilePlatform_label","automobilePlatform","bodyStyle_label","bodyStyle","class_label","class","designCompany_label","designCompany","designer_label","designer","engine_label","engine","fuelCapacity","height","layout_label","layout","length","manufacturer_label","manufacturer","modelEndYear","modelStartYear","parentCompany_label","parentCompany","predecessor_label","predecessor","productionEndDate","productionEndYear","productionStartDate","productionStartYear","relatedMeanOfTransportation_label","relatedMeanOfTransportation","sales_label","sales","successor_label","successor","thumbnail_label","thumbnail","transmission","variantOf_label","variantOf","vehicle_label","vehicle","weight","wheelbase","width","point","22-rdf-syntax-ns#type_label","22-rdf-syntax-ns#type","wgs84_pos#lat","wgs84_pos#long","depiction_label","depiction","name"]

def ensure_int(data):
    try:
        return int(data)
    except ValueError:
        return None
    
def process_file(input_file, output_good, output_bad):

    GOODDATA = []
    BADDATA = []
    with open(input_file, "r") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames

        #COMPLETE THIS FUNCTION
        for row in reader:
            
            if row["URI"] == "http://dbpedia.org/resource/Saab_900":
                for i in h:
                    print row[i]

            
            if not row["URI"].startswith("http://dbpedia.org"):
                continue
                
            year = ensure_int(row["productionStartYear"][:4])
            if year and (year >= 1886 and year <= 2014):
                GOODDATA.append(row)
            else:
                BADDATA.append(row)
                
    print len(BADDATA)
        

    # This is just an example on how you can use csv.DictWriter
    # Remember that you have to output 2 files
    with open(output_good, "w") as g:
        writer = csv.DictWriter(g, delimiter=",", fieldnames= header)
        writer.writeheader()
        for row in GOODDATA:
            writer.writerow(row)
            
    with open(output_bad, "w") as g:
        writer = csv.DictWriter(g, delimiter=",", fieldnames= header)
        writer.writeheader()
        for row in BADDATA:
            writer.writerow(row)


def test():

    process_file(INPUT_FILE, OUTPUT_GOOD, OUTPUT_BAD)


if __name__ == "__main__":
    test()

