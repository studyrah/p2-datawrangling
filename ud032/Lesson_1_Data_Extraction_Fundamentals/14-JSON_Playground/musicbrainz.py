# To experiment with this code freely you will have to run this code locally.
# We have provided an example json output here for you to look at,
# but you will not be able to run any queries through our UI.
import json
import requests


BASE_URL = "http://musicbrainz.org/ws/2/"
ARTIST_URL = BASE_URL + "artist/"

query_type = {  "simple": {},
                "atr": {"inc": "aliases+tags+ratings"},
                "aliases": {"inc": "aliases"},
                "releases": {"inc": "releases"}}


def query_site(url, params, uid="", fmt="json"):
    params["fmt"] = fmt
    r = requests.get(url + uid, params=params)
    print "requesting", r.url

    if r.status_code == requests.codes.ok:
        return r.json()
    else:
        r.raise_for_status()


def query_by_name(url, params, name):
    params["query"] = "artist:" + name
    return query_site(url, params)


def pretty_print(data, indent=4):
    if type(data) == dict:
        print json.dumps(data, indent=indent, sort_keys=True)
    else:
        print data


#(rahaugh) Question1: how many bands named FIRST AID KIT
def question1():
    
    fak_results = query_by_name(ARTIST_URL, query_type["simple"], "\"First+Aid+Kit\"")
    print "Q1 - Number of Bands Called First Aid Kit: " + str(len(fak_results["artists"]))
    #for artist in fak_results["artists"]:
        #print artist["name"]

#(rahaugh) Question2: What is the begin area for Queen
def question2():
    results = query_by_name(ARTIST_URL, query_type["simple"], "\"Queen\"")
    
    #first we've go to find the right Queen
    #which we did below, note that it is the first one
    #there are 2 more called just Queen and lots
    #with Queen in there title
    justqueen = []
    for artist in results["artists"]:
        #print "queen artists: " + artist["name"]
        if artist["name"] == "Queen":
            justqueen.append(artist["id"])
            #pretty_print(artist)

        
    #Queens id is - 0383dadf-2a4e-4d10-a46a-e9e041da8eb3
    #and there index is 0 (Q. is this always reliable?)
        
    #now get there begin area:
    print "Q2 - Queen begin area: " + results["artists"][0]["begin-area"]["name"]
        
    #artist_id = results["artists"][1]["id"]
    #if
    #print "justqueen: " + str(len(justqueen))
 
#(rahaugh) Question3: Spanish alias for Beatles    
def question3():
    results = query_by_name(ARTIST_URL, query_type["simple"], "\"The+Beatles\"")
    #pretty_print(results)

    #first we've go to find the right Beatles
    #which we did below, note that it is the first one
    justbeatles = []
    for artist in results["artists"]:
        #print "beatles artists: " + artist["name"]
        if artist["name"] == "The Beatles":
            justbeatles.append(artist["id"])
            #pretty_print(artist)
            
    thebeatles = results["artists"][0]
    

    for alias in thebeatles["aliases"]:
        if alias["locale"] == "es":
            print("Q3 - Spanish alias for Beatles is: " + alias["name"])
            break


   
#(rahaugh) Question 4: disambiguation for NIRVANA
def question4():
    results = query_by_name(ARTIST_URL, query_type["simple"], "Nirvana")

    #(rahaugh) looking for index = 1 is there dodgy code not mine!
    
    print "Q4 - Nirvana Disambiguation: " + results["artists"][0]["disambiguation"]
    
    

#(rahaugh) Question5: What is the start date for One Direction    
def question5():
    results = query_by_name(ARTIST_URL, query_type["simple"], "\"One+Direction\"")
    #pretty_print(results)

    #print len(results["artists"])
    #huzzah there's only one!!!!
    
    #pretty_print(results["artists"][0])
    
    print "Q5 - One Direction Start Date: " + results["artists"][0]["life-span"]["begin"]
    

def main():

    question1()
    question2()
    question3()
    question4()    
    question5()


    results = query_by_name(ARTIST_URL, query_type["simple"], "Nirvana")
    #pretty_print(results)

    artist_id = results["artists"][1]["id"]
    #print "\nARTIST:"
    #pretty_print(results["artists"][1])
    
    
    
    #(rahaugh) Question 4: disambiguation for NIRVANA
    #print results["artists"][1]["disambiguation"]
    
    #for artist in results["artists"]:
     #   for k,v in enumerate(artist):
      #      print k
       #     print v
    

    artist_data = query_site(ARTIST_URL, query_type["releases"], artist_id)
    releases = artist_data["releases"]
    #print "\nONE RELEASE:"
    #pretty_print(releases[0], indent=2)

    release_titles = [r["title"] for r in releases]

    #print "\nALL TITLES:"
    #for t in release_titles:
        #print t


if __name__ == '__main__':
    main()
