import requests
import json
import sqlite3
import os
import plotly as px


#Emma Brown and An Doan
#SI 206 Final Project FA2020
#Calculations and Visualizations

""" Requires: db_name (string)
Modifies: cur, conn
Effects: connects to SQLite database and returns connection and cursor"""
def connectToDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def gatherArtistsPerGenre(cur, conn, genres):
    data_dict = dict()
    for g in genres:
        cur.execute("SELECT * FROM Artists WHERE genre = ?", (g,))
        for row in cur:
            data_dict[g] = data_dict.get(g, 0) + 1
    return data_dict

def gatherArtistsPerGender(cur, conn):
    data_dict = {}
    cur.execute("SELECT * FROM ArtistGender JOIN Genders ON ArtistGender.gender_id = Genders.gender_id WHERE Genders.gender_id = 0")
    for row in cur:
        data_dict["male"] = data_dict.get("male", 0) + 1
    cur.execute("SELECT * FROM ArtistGender JOIN Genders ON ArtistGender.gender_id = Genders.gender_id WHERE Genders.gender_id = 1")
    for row in cur:
        data_dict["female"] = data_dict.get("female", 0) + 1
    cur.execute("SELECT * FROM ArtistGender JOIN Genders ON ArtistGender.gender_id = Genders.gender_id WHERE Genders.gender_id = 2")
    for row in cur:
        data_dict["none"] = data_dict.get("none", 0) + 1
    return data_dict

def gatherProbabilities(cur, conn):
    pass

def main():
    genres = ['rock', 'pop', 'folk', 'rnb', 'singer-songwriter', 'indie']
    cur, conn = connectToDatabase('lastfm.db')
    genre_dict = gatherArtistsPerGenre(cur, conn, genres)
    gender_dict = gatherArtistsPerGender(cur, conn)
    conn.close()


if __name__ == "__main__":
    main()