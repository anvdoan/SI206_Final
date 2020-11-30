import pylast
import requests
import json
from genderize import Genderize

API_KEY = '502895a066a65f103a01d4463cf41430'
API_SECRET = '15a3fe9b112584efb5f7752dae84a1be'

username = 'anvidoan'
password_hash = pylast.md5('B6T2P34TG&o^')

network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET, username=username, password_hash=password_hash)

def json_print(obj):
    #create formatted string of JSON object
    text = json.dumps(obj, sort_keys=True, indent= 4)
    print(text)

def get_first_name(string):
    #splits name and returns person's first name
    split_string = string.split()
    return split_string[0]

#get top artists by chart

top_chart_url = f"http://ws.audioscrobbler.com/2.0/?method=chart.gettopartists&api_key={API_KEY}&format=json"
top_chart_response = requests.get(top_chart_url)
top_artists= top_chart_response.json()['artists']['artist']
artist_list = list()
for d in top_artists:
    name = d['name']
    artist_list.append(name)
"""
for i in range(len(artist_list)):
    print(get_first_name(artist_list[i]))
"""
first_name_list = list()
for i in artist_list:
    first = get_first_name(i)
    first_name_list.append(first)
print(Genderize().get(first_name_list))


#get top artists by genre

#get top artists by country
