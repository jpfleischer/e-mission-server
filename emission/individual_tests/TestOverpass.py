from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import *
import unittest
import os
import requests
import emission.net.ext_service.transit_matching.match_stops as enetm

#Set up query
OVERPASS_KEY = os.environ.get("OVERPASS_KEY")

#Sample loc1 = NREL East Gate
loc1 = {'coordinates': [-105.16844103184974, 39.740428870224605]}
#Sample loc2 = Denver Union Station
loc2 = {'coordinates': [-105.00083982302972, 39.753710532185025]}
#Sample loc3 = Grand Junction Train Station, CO
loc3 = {'coordinates': [-108.57055213129632, 39.06472424640481]}

class OverpassTest(unittest.TestCase):
    def setUp(self):
        sample_data = '[out:json][bbox];way[amenity=parking];out;&bbox=-122.1111238,37.4142118,-122.1055791,37.4187945'
        call_base = 'api/interpreter?data='
        self.de_url_base = 'https://lz4.overpass-api.de/'+ call_base + sample_data
        self.gfbk_url_base = 'http://overpass.geofabrik.de/' + OVERPASS_KEY + '/' + call_base + sample_data

    def test_overpass(self):
        r_gfbk = requests.get(self.gfbk_url_base)
        r_de = requests.get(self.de_url_base)
        
        if r_gfbk.status_code == 200 and r_de.status_code == 200:
            print("requests successful!")
            r_gfbk_len, r_de_len = len(r_gfbk.json()), len(r_de.json())
            self.assertEqual(r_gfbk_len, r_de_len)
        else:
            print("status_gfbk", r_gfbk.status_code, type(r_gfbk.status_code), "status_de", r_de.status_code)

    #Test utilizes the functions get_stops_near, get_public_transit_stops, and make_request_and_catch.  
    def test_get_stops_near(self):
        actual_result = enetm.get_stops_near(loc1, 150.0)[0]['routes'][0]['tags']
        print("ACTUAL_RESULT:", actual_result, type(actual_result))
        expected_result = {'from': 'National Renewable Energy Lab', 'name': 'RTD Route 125: Red Rocks College', 'network': 'RTD', 'network:wikidata': 'Q7309183', 'network:wikipedia': 'en:Regional Transportation District', 'operator': 'Regional Transportation District', 'public_transport:version': '1', 'ref': '125', 'route': 'bus', 'to': 'Red Rocks College', 'type': 'route'}
        self.assertEqual(expected_result, actual_result)
   
    #Get_stops_near generates two stops from the given coordinates.
    # Get_predicted_transit_mode finds a common route between them (train).
    def test_get_predicted_transit_mode(self):
        stop1 = enetm.get_stops_near(loc2, 400.0)
        stop2 = enetm.get_stops_near(loc3, 400.0)
        actual_result = enetm.get_predicted_transit_mode(stop1, stop2)
        print("ACTUAL TRANSIT MODE: ", actual_result)
        expected_result = ['train', 'train']
        self.assertEqual(actual_result, expected_result)

if __name__ == '__main__':
    unittest.main()

