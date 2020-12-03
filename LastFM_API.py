import requests
import json
import sqlite3
import os
from genderize import Genderize

#Emma Brown and An Doan
#SI 206 Final Project FA2020
#Data Collection

API_KEY = '502895a066a65f103a01d4463cf41430'
API_SECRET = '15a3fe9b112584efb5f7752dae84a1be'

""" Requires: json object
Modifies: nothing
Effects: prints json object to console"""
def json_print(obj):
    #create formatted string of JSON object
    text = json.dumps(obj, sort_keys=True, indent= 4)
    print(text)

""" Requires: string
Modifies: split_string
Effects: returns first word separated by whitespace in string"""
def get_first_name(string):
    #splits name and returns person's first name
    split_string = string.split()
    return split_string[0]


""" Requires: nothing
Modifies: artist_list, full_json
Effects: returns json object of all artists, gathered by chart from last.fm API, as well as a list of artist names from the same API calls."""
def getArtistsbyChart():
    artist_list = list()
    full_json = list()
    for num in range(4):
        top_chart_url = f"http://ws.audioscrobbler.com/2.0/?method=chart.gettopartists&page={num+1}&limit=25&api_key={API_KEY}&format=json"
        top_chart_response = requests.get(top_chart_url)
        top_artists= top_chart_response.json()['artists']['artist']

        #make complete 100 item json obj for database
        for artist in top_artists:
            full_json.append(artist)
        
        #get names for genderize
        for d in top_artists:
            name = d['name']
            artist_list.append(name)
        

    return artist_list, full_json

""" Requires: genre_list (list of strings)
Modifies: artist_list, full_json
Effects: returns json object of all artists, gathered by genre from last.fm API, as well as a list of artist names from the same API calls."""
def getArtistsbyGenre(genre_list):
    artist_list = list()
    full_json = list()
    for genre in genre_list:
        artist_tag_url = f"http://ws.audioscrobbler.com/2.0/?method=tag.gettopartists&tag={genre}&limit=25&api_key={API_KEY}&format=json"
        artist_tag_response = requests.get(artist_tag_url)
        topArtists = artist_tag_response.json()['topartists']['artist']

        #add to json by genre
        for artist in topArtists:
            artist["genre"] = genre
            full_json.append(artist)

        #add to artist list - will get first names in genderize function, send full names for now
        for d in topArtists:
            name = d['name']
            artist_list.append(name)
    
    return artist_list, full_json


""" Requires: artist_list (list of strings)
Modifies: first_name_list, gender_data
Effects: returns json object of all artists gathered from last.fm API with predicted gender and probability for each artist."""
def genderize(artist_list):
    first_name_list = list()
    gender_data = list()
    for i in artist_list:
        first = get_first_name(i)
        first_name_list.append(first)
    i = 0
    j = 24
    while j < 150:
        names = Genderize().get(first_name_list[i:j])
        for item in names:
            gender_data.append(item)
        i += 25
        j += 25
    for i in range(len(gender_data)):
        gender_data[i]["name"] = artist_list[i]
        if gender_data[i]["gender"] == None:
            gender_data[i]["gender"] = "none"
    return gender_data

""" Requires: db_name (string)
Modifies: cur, conn
Effects: creates SQLite database and returns connection and cursor"""
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

""" Requires: cur, conn (database)
Modifies: SQLite database
Effects: creates Genders table in database and adds rows for each gender category from Genderize."""
def setUpGenderTable(cur, conn):
    gender_list = ['male', 'female', 'none']
    cur.execute("DROP TABLE IF EXISTS Genders")
    cur.execute("CREATE TABLE Genders (name TEXT, gender_id INTEGER PRIMARY KEY)")
    for i in range(len(gender_list)):
        if gender_list[i] == "male":
            cur.execute("INSERT INTO Genders (name, gender_id) VALUES (?,?)",(gender_list[i], 0))
        elif gender_list[i] == 'female':
            cur.execute("INSERT INTO Genders (name, gender_id) VALUES (?,?)",(gender_list[i], 1))
        else:
           cur.execute("INSERT INTO Genders (name, gender_id) VALUES (?,?)",(gender_list[i], 2)) 
    conn.commit()

""" Requires: data (json obj), cur, conn (database)
Modifies: SQLite database
Effects: creates Artists table in database and adds rows for each artist collected from last.fm API."""
def setUpArtistTable(data, cur, conn):
    cur.execute("DROP TABLE IF EXISTS Artists")
    cur.execute("CREATE TABLE Artists (artist_id INTEGER PRIMARY KEY, name TEXT, genre TEXT)")
    #loop through data and add to database
    i = 0
    for artist in data:
        artist_id = i
        i += 1
        name = artist["name"]
        genre = artist["genre"]
        cur.execute("INSERT INTO Artists (artist_id, name, genre) VALUES (?, ?, ?)", (artist_id, name, genre))
    conn.commit()

""" Requires: data (json obj), cur, conn (database)
Modifies: SQLite database
Effects: creates ArtistGender table in database and adds rows for each artist, their respective predicted gender, and probability of correctness."""
def setUpArtistGenderTable(data, cur, conn):
    cur.execute("DROP TABLE IF EXISTS ArtistGender")
    cur.execute("CREATE TABLE ArtistGender (artist_id INTEGER PRIMARY KEY, gender_id INTEGER, probability FLOAT)")
    for item in data:
        cur.execute("SELECT artist_id FROM Artists WHERE name = ?", (item['name'],))
        artist_id = int(cur.fetchone()[0])
        cur.execute("SELECT gender_id FROM Genders WHERE name = ?", (item['gender'],))
        gender_id = int(cur.fetchone()[0])
        prob = item['probability']
        cur.execute("INSERT INTO ArtistGender  (artist_id, gender_id, probability) VALUES (?, ?, ?)", (artist_id, gender_id, prob))
    conn.commit()

def main():
    name_list, json_data = getArtistsbyGenre(['rock', 'pop', 'folk', 'rnb', 'singer-songwriter', 'indie'])
    gender_data = genderize(name_list)
    cur, conn = setUpDatabase('lastfm.db')
    setUpArtistTable(json_data, cur, conn)
    setUpGenderTable(cur, conn)
    setUpArtistGenderTable(gender_data, cur, conn)
    conn.close()


if __name__ == "__main__":
    main()