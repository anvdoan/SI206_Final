import requests
import json
import sqlite3
import os
from genderize import Genderize

#Emma Brown and An Doan
#SI 206 Final Project FA2020

API_KEY = '502895a066a65f103a01d4463cf41430'
API_SECRET = '15a3fe9b112584efb5f7752dae84a1be'

def json_print(obj):
    #create formatted string of JSON object
    text = json.dumps(obj, sort_keys=True, indent= 4)
    print(text)

def get_first_name(string):
    #splits name and returns person's first name
    split_string = string.split()
    return split_string[0]

#get top artists by chart, limit number of data pieces and go by page to avoid duplicates
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

#gets top artists by genre tag, will need to make list of genres and use for loop to call function
def get_top_artist_by_genre(genre):
    artist_tag_url = f"http://ws.audioscrobbler.com/2.0/?method=tag.gettopartists&tag={genre}&api_key={API_KEY}&format=json"
    artist_tag_response = requests.get(artist_tag_url)
    topArtists = artist_tag_response.json()['topartists']['artist']
    artist_list = list()
    for d in topArtists:
        name = d['name']
        artist_list.append(name)
    first_name_list = list()
    for i in artist_list:
        first = get_first_name(i)
        first_name_list.append(first)
    return first_name_list

#take list of names and return genderize json response linked to the artist's full name for ease of adding to database
def genderize(artist_list):
    first_name_list = list()
    for i in artist_list:
        first = get_first_name(i)
        first_name_list.append(first)
    gender_data = Genderize().get(first_name_list)
    for i in range(len(gender_data)):
        gender_data[i]["name"] = artist_list[i]
    return gender_data

#create database
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

#set up Gender table in database: holds ids for gender to be connected to gender of artist table with genderize data
def setUpGenderTable(cur, conn):
    gender_list = ['male', 'female']
    cur.execute("DROP TABLE IF EXISTS Genders")
    cur.execute("CREATE TABLE Genders (name TEXT, gender_id INTEGER PRIMARY KEY)")
    for i in range(len(gender_list)):
        if gender_list[i] == "male":
            cur.execute("INSERT INTO Genders (name, gender_id) VALUES (?,?)",(gender_list[i], 0))
        else:
            cur.execute("INSERT INTO Genders (name, gender_id) VALUES (?,?)",(gender_list[i], 1))
    conn.commit()

#set up artist table with name, playcount, listeners
def setUpArtistTable(data, cur, conn):
    cur.execute("DROP TABLE IF EXISTS Artists")
    cur.execute("CREATE TABLE Artists (artist_id INTEGER PRIMARY KEY, name TEXT, playcount INTEGER, listeners INTEGER)")
    #loop through data and add to database
    i = 0
    for artist in data:
        artist_id = i
        i += 1
        name = artist["name"]
        pcount = artist["playcount"]
        listeners = artist["listeners"]
        cur.execute("INSERT INTO Artists (artist_id, name, playcount, listeners) VALUES (?, ?, ?, ?)", (artist_id, name, pcount, listeners))
    conn.commit()

#set up table with artist name and gender as decided by genderize api
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

def main():
    name_list, json_data = getArtistsbyChart()
    gender_data = genderize(name_list)
    cur, conn = setUpDatabase('lastfm.db')
    setUpArtistTable(json_data, cur, conn)
    setUpGenderTable(cur, conn)
    setUpArtistGenderTable(gender_data, cur, conn)
    conn.close()


if __name__ == "__main__":
    main()