"""
Simple script (based upon Lesson 6 Part 4) that iteratively parses an OSM XML
file checks for non standard street type variants and where appropriate
maps to standard.
"""
#import xml.etree.cElementTree as ET
from lxml import etree as ET

from collections import defaultdict
import re
import pprint
from optparse import OptionParser


OSMFILE = "../data/cardiff-newport-bristol-bath_england.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


#expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
#            "Trail", "Parkway", "Commons"]

expected = ['Street', 'Avenue', 'Boulevard', 'Drive', 'Court', 'Place', 'Square', 
            'Lane', 'Road', 'Trail', 'Parkway', 'Commons', 
            
            'Ham', 'Cottages', 'Maltings', 'Causeway', 'Passage', 'Hill',             
            'Gate', 'Mews', 'Bottoms', 'Path', 'Ponds', 'Wharf', 'Steps', 
            'Chase', 'Glen', 'End', 'Arcade', 'West', 'Mills', 'Down', 'Quay', 
            'Rise', 'Park', 'Paddock', 'Orchard', 'Grove', 'Green', 
            'Corner', 'Grounds', 'Meadow', 'Circus', 'Woods', 'Row', 
            'Crescent,', 'Way', 'Approach', 'Pavilions', 'Croft', 'North',
            'Mead', 'Vale', 'South', 'Lawn', 'Ridgeway', 'Villas', 
            'Parade', 'Cresent', 'Esplanade', 'Walk', 'Close', 'Ground', 
            'Bush', 'Wood', 'Willows', 'Highway', 'East', 'Promenade', 
            'Dale', 'Fields', 'Run', 'Gardens', 'View', 'Bridge', 
            'Terrace']



mapping = { "St": "Street",
            "St.": "Street",
            "Ave": "Avenue",
            "Rd.": "Road",
            "Rd": "Road",
            "avenue": "Avenue",
            "croft": "Croft",
            "road": "Road",
            "st": "Street",
            "lane": "Lane",
            "Cresent" : "Crescent"
            }

"""
# for completenes here are all the others we observed
others = ['Awel', 'Kingsway', 'Kanetone', 'Berrycroft', 'Heol-Y-Deri', 
          'Northcliffe', 'Coed-Y-Felin', 'Woodmarsh', 'Elm', 'Dene', 
          'Westside', 'Haven', 'Building', 'Longcross', 'Yard', 'Bristol', 
          'Gwaun', 'Quarter', 'Heol-Y-Gyfraith', 'Llantrithyd', 'Friars', 
          'Millfield', 'caerphilly_road', 'Canol', 'Fromefield', 'Chedworth', 
          'Horsefair', 'Broadway', 'Tolldown', 'Pentagon', 'Quadrant', 'Mare', 
          'Ael-y-Bryn', 'Bryn', 'Bryntirion', 'Burltons', '3', 'Chatham', 
          'Spur', 'Eglwys', 'A431)', 'Town', 'Beachley', 'Central', 
          'Heol-y-Parc', 'Pierheadstreet', 'Counterslip', 'Tynings', 'Mall', 
          'Isaf', 'Edwardsville', 'Coldra', 'Gateway', 'Fieldview', 'Neston', 
          'Hendy', 'Hillcrest', 'Estate', 'Lakeside', 'Lewis', 'Afon', 
          'Broadway,Chilcompton', 'Paragon', 'Bronhall', 'Oak', 'Southra', 
          'Bibstone', 'Common', 'Embankment', 'Gillingstool', 'Glo', 'Sully', 
          'Ffos-y-Fran', 'Fardre', 'Springfield', 'Cilffrydd', 'Plain', 
          'Streamleaze', 'Weind', 'Abottside', 'Maes-Y-Coed', u'Glas', 'Rhiw', 
          'Ysgol', 'Parklands', 'Falcondale', 'De-Winton', 'Hamfields', 
          'Gorgeous', 'Johnson', 'Fach', 'Trelai', 'Back', 'Hector', 'Llyswen', 
          'Terrell', 'Dolwen', 'Marics', 'Quadeast', 'Bury', 'Homefield', 
          'Broadacres', 'Hillside', 'Badgeworth', 'Woodlands', 'Spinney', 
          'Dockyard', 'Pound', 'Sawclose', 'Miles', 'Treharris', 'Bath', 
          'Complex', 'Onen', 'Pennar', 'Pen-Y-Bryn', 'Goleu', 'Gooselands', 
          'Oaks', 'Townsend', 'EArl', 'RCT,' , 'Sunningdale', 'Ashgrove', 
          'Broadhaven' 'Tredomen', 'Buildings', 'Churchyard', 'Chipping', 
          'Chalford', 'Fanheulog', 'Llan', 'Leigh', 'Elmgrove', 'Trecastell', 
          'Queensway', 'Fedw', 'Houses', 'Pen-y-Dre', 'Bach', 'Tyning', 
          'Barns', 'Centre', 'Heol', 'Twyn', 'Teigr', 'Trefeddyg', 'Townwell', 
          'Hart', 'Teg', 'Lees', 'Coombe', 'Fairway', 'Bluebells', 'Birchgrove', 
          'Riverside', 'Catwg', 'Pinwydden']
"""


"""
  if street_name contains a street and it is an unexpected type add, the
  type as key, street_name as value to the given dict
"""
def audit_street_type(street_types, street_name):

    m = street_type_re.search(street_name)
    
    if m:
        street_type = m.group()

        if street_type not in expected:
            street_types[street_type].add(street_name)


"""
returns true if the elem has an addr:street 'k' attribute
"""
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


"""
  iterates through the xml elements looking for streets and returns a dict
  of unexepcted street types with:
  
  key - the unexpected street type
  val - a set of streets with that type
"""
def audit(osmfile):
    
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)

    context = ET.iterparse(osm_file, events=("start", "end"))

    context = iter(context)
    
    # skip over root
    event,root = context.next()
        
    for event,elem in context:

        if event == "end":

            if elem.tag == "node" or elem.tag == "way":
                for tag in elem.iter("tag"):
                    #for i in tag.attrib.iteritems():
                    #    print i
                    
                    #    print i
                    if is_street_name(tag):
                        audit_street_type(street_types, tag.attrib['v'])
                        
                # clear else we build the whole document in memory        
                elem.clear()                              
    
    return street_types    


"""
Updates name accoring to the provided mapping, expliticlty looks for and
updates the street part of name (if it contains one)
"""
def update_name(name, mapping):

    m = street_type_re.search(name)
    if m:
        street_type = m.group()
        
        if mapping.has_key(street_type):
            name = name.replace(street_type, mapping[street_type])
            
            
    return name


"""
 main()
"""
if __name__ == '__main__':
    
    parser = OptionParser()

    #provide an option to perform both audit and update
    #default will be to just audit
    parser.add_option("-u", action="store_true", dest="update_streets", 
                      help="audit and update", default=False)
    
    (options,args) = parser.parse_args()
       
    st_types = audit(OSMFILE)
    
    # if we are updting
    if(options.update_streets):
        
        for st_type, ways in st_types.iteritems():
            for name in ways:
                better_name = update_name(name, mapping)
                pprint.pprint("{\""+ name + "\": \"" + better_name + "\"}")
    
    #if we are just auditing
    else:
        pprint.pprint(dict(st_types))