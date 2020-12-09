import requests
import json
import sqlite3
import os
import time
from genderize import Genderize

#Emma Brown and An Doan
#SI 206 Final Project FA2020
#Data Collection

API_KEY = '502895a066a65f103a01d4463cf41430'
API_SECRET = '15a3fe9b112584efb5f7752dae84a1be'

""" Requires: string
Modifies: split_string
Effects: returns first word separated by whitespace in string"""
def get_first_name(string):
    #splits name and returns person's first name
    split_string = string.split()
    return split_string[0]

""" Requires: genre (string)
Modifies: artist_list, full_json
Effects: returns json object of all artists, gathered by genre from last.fm API, as well as a list of artist names from the same API calls."""
def getArtistsbyGenre(genre):
    artist_list = list()
    full_json = list()

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
Effects: returns json object of all artists gathered from last.fm API with predicted gender and probability for each artist.
         calls get_first_name() to get first names of artists."""
def genderize(artist_list):
    first_name_list = list()
    gender_data = list()
    for i in artist_list:
        first = get_first_name(i)
        first_name_list.append(first)
    
    names = Genderize().get(first_name_list)
    for item in names:
        gender_data.append(item)
       
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
    cur.execute("CREATE TABLE IF NOT EXISTS Genders (name TEXT, gender_id INTEGER PRIMARY KEY)")
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
def setUpArtistTable(data, cur, conn, i):
    cur.execute("CREATE TABLE IF NOT EXISTS Artists (artist_id INTEGER PRIMARY KEY, name TEXT, genre TEXT)")
    #loop through data and add to database
    for artist in data:
        artist_id = i
        i+=1
        name = artist["name"]
        genre = artist["genre"]
        cur.execute("INSERT INTO Artists (artist_id, name, genre) VALUES (?, ?, ?)", (artist_id, name, genre))
    conn.commit()

""" Requires: data (json obj), cur, conn (database)
Modifies: SQLite database
Effects: creates ArtistGender table in database and adds rows for each artist, their respective predicted gender, and probability of correctness."""
def setUpArtistGenderTable(data, cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS ArtistGender (artist_id INTEGER PRIMARY KEY, gender_id INTEGER, probability FLOAT)")
    for item in data:
        cur.execute("SELECT artist_id FROM Artists WHERE name = ?", (item['name'],))
        artist_id = int(cur.fetchone()[0])
        cur.execute("SELECT gender_id FROM Genders WHERE name = ?", (item['gender'],))
        gender_id = int(cur.fetchone()[0])
        prob = item['probability']
        cur.execute("INSERT INTO ArtistGender  (artist_id, gender_id, probability) VALUES (?, ?, ?)", (artist_id, gender_id, prob))
    conn.commit()

""" Requires: nothing
Modifies: genre, name_list, json_data, gender_data, cur, conn, i, lastfm.db
Effects: calls getArtistsbyGenre(), genderize(), setUpDatabase(), setUpGenderTable(), setUpArtistTable(), setUpArtistGenderTable()"""
def main():
    genres = ['rock', 'pop', 'folk', 'rnb', 'singer-songwriter', 'indie']
    #change index every time you run the program, 0-5
    genre = genres[0]
    name_list, json_data = getArtistsbyGenre(genre)
    gender_data = genderize(name_list)
    cur, conn = setUpDatabase('lastfm.db')
    if genre == 'rock':
        i = 0
    elif genre == 'pop':
        i = 25
    elif genre == 'folk':
        i = 50
    elif genre == 'rnb':
        i = 75
    elif genre == 'singer-songwriter':
        i = 100
    else: i = 125
    if i == 0:
        setUpGenderTable(cur, conn)
    setUpArtistTable(json_data, cur, conn, i)
    setUpArtistGenderTable(gender_data, cur, conn)
    conn.close()


if __name__ == "__main__":
    main()