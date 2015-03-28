# -*- coding: utf-8 -*-
import re

"""
Purpose of this module is to provide helper methods to both validate and
cleanse postcodes.
"""


# known variations on postcode key
postcode_keys = ["addr:postcode","postal_code","postcode"]

# some postcode meta keys
note_postcode = "note:postcode"
source_postcode = "source:postcode"

# prefered postcode key
POSTCODE_KEY = "addr:postcode"

# valid postcode regex
postcode_regex = re.compile(r'^([Gg][Ii][Rr] 0[Aa]{2})$|((([A-Za-z][0-]{1,2})|(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})|(([AZa-z][0-9][A-Za-z])|([A-Za-z][A-Ha-hJ-Yj-y][0-9]?[A-Za-z])))) [0-9][A-Za-z]{2})$')
# almost valid postcode regex, just missing the space between the 2 parts
postcode_missing_space_regex = re.compile(r'^([Gg][Ii][Rr]0[Aa]{2})$|((([A-Za-z][0-]{1,2})|(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})|(([AZa-z][0-9][A-Za-z])|([A-Za-z][A-Ha-hJ-Yj-y][0-9]?[A-Za-z]))))[0-9][A-Za-z]{2})$')

# valid partial postcode regex
partial_postcode_regex = re.compile(r'^([Gg][Ii][Rr]( 0)?)$|((([A-Za-z][0-]{1,2})|(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})|(([AZa-z][0-9][A-Za-z])|([A-Za-z][A-Ha-hJ-Yj-y][0-9]?[A-Za-z]))))( [0-9])?)$')

"""
Given key is one of the known postcode variants
"""
def is_postcode_key(key):
    return key in postcode_keys

"""
Given value is a valid postcode
"""    
def is_valid_postcode_value(value):
    return postcode_regex.match(value) != None
    
"""
Given value is a valid partial postcode

i.e. it is just the first half of the postcode or first half plus the first
digit of the second half
"""    
def is_valid_partial_postcode_value(value):
    return partial_postcode_regex.match(value) != None

"""
Is it a valid postcode just with a missing space

TODO: also cope with partial postcodes
"""
def is_valid_postcode_missing_space(v):
    return postcode_missing_space_regex.match(v) != None   

"""
On the assumption that this is would be a valid postcode if we added a space,
add a space

TODO: also cope with partial postcodes

"""
def add_space_to_postcode(v):
    return v[0:-3] + " " + v[-3:]

"""
Currently we have just one case, map Nottingham to Newport so keep it simple
"""
def map_postcode_region(v):
    if v[:2] == "NG":
        return "NP" + v[2:]
    
    return v

"""
Cleanse the given postcode key and value, note that if either (or both) of
key and value don't cleanse we just return the original values.  That is to
say we fix if we can else we leave well alone
"""    
def cleanse_postcode(k,v):
    return (cleanse_key(k), cleanse_value(v))

"""
For now at least this is very simple the key should always be addr:postcode,
BUT we will only make the change if the key is within the list of mappable
variants
"""
def cleanse_key(k):

    if k in postcode_keys:
        return POSTCODE_KEY

    return k        
    
"""
Currently we look to make 3 alterations:

1. convert to uppercae
2. if the given value looks like a valid postcode with a missing space, we add
the space in the appropriate place
3. map the postcode region if we know its wrong
"""    
def cleanse_value(v):
    newv = None
    
    if is_valid_postcode_value(v) or is_valid_partial_postcode_value(v):
        newv = v
        
    elif is_valid_postcode_missing_space(v):
        newv = add_space_to_postcode(v)
    else:
        # just return the original, cos we don't recognise it
        return v
    
    newv = newv.upper()
    newv = map_postcode_region(newv)
    
    return newv
        

"""
Given key is one of the known postcode meta field variants
"""    
def is_postcode_meta_key(key):
    return key == note_postcode or key == source_postcode
    
"""
As we only have a couple of cases, just alter the key if applicable
"""
def cleanse_meta_key(key):
    if key == note_postcode:
        return "note:addr:postcode"
    elif key == source_postcode:
        return "source:addr:postcode"
    
    return key
    
    
if __name__ == '__main__':


    # is postcode key
    assert is_postcode_key("addr:postcode") == True
    assert is_postcode_key("postcode") == True
    assert is_postcode_key("postal_code") == True
    assert is_postcode_key("nonsence") == False
    
    # cleanse key
    assert cleanse_key("addr:postcode") == "addr:postcode"
    assert cleanse_key("postcode") == "addr:postcode"
    assert cleanse_key("postal_code") == "addr:postcode"
    assert cleanse_key("nonsence") == "nonsence"

    # just check a couple of valid and invalid postcodes
    assert is_valid_postcode_value("GIR 0AA") == True
    assert is_valid_postcode_value("DN26 9AP") == True
    assert is_valid_postcode_value("DN26") == False
    
    # check a couple of valid partial postcodes
    assert is_valid_partial_postcode_value("dn26") == True
    assert is_valid_partial_postcode_value("GIR 0") == True
    assert is_valid_partial_postcode_value("GIR 05") == False
    
    # check for a valid postcode missing a space
    assert is_valid_postcode_missing_space("DN26 9AP") == False
    assert is_valid_postcode_missing_space("DN269AP") == True    
        
    # cleanse value
    assert cleanse_value("DN26 9AP") == "DN26 9AP"
    assert cleanse_value("dn26 9AP") == "DN26 9AP"    
    assert cleanse_value("dn269AP") == "DN26 9AP" 
    assert cleanse_value("ng269AP") == "NP26 9AP"
    assert cleanse_value("nonsence") == "nonsence"       
    
    # is postcode meta
    assert is_postcode_meta_key("note:postcode") == True
    assert is_postcode_meta_key("source:postcode") == True
    assert is_postcode_meta_key("note:post----code") == False
    
    # cleanse postcode meta
    assert cleanse_meta_key("note:postcode") == "note:addr:postcode"
    assert cleanse_meta_key("source:postcode") == "source:addr:postcode"
    assert cleanse_meta_key("note:post----code") == "note:post----code"
    
    