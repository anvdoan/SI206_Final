import unittest
import sqlite3
import json
import os

#Emma Brown and An Doan
#SI 206 Final Project FA2020

def readDataFromFile(filename):
    full_path = os.path.join(os.path.dirname(__file__), filename)
    f = open(full_path, encoding='utf-8')
    file_data = f.read()
    f.close()
    json_data = json.loads(file_data)
    return json_data

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def setUpTabsTable(data, cur, conn):
    tabs_list = []
    #get list of tabs from json object 'data'
    #requires: get artists API function, also get top tags API function. might be separate json file?
    cur.execute("DROP TABLE IF EXISTS Tabs")
    cur.execute("CREATE TABLE Tabs (id INTEGER PRIMARY KEY, title TEXT)")
    for i in range(len(tabs_list)):
        cur.execute("INSERT INTO Categories (id,title) VALUES (?,?)",(i,tabs_list[i]))
    conn.commit()

def setUpArtistTable(data, cur, conn):
    cur.execute("DROP TABLE IF EXISTS Artists")
    cur.execute("CREATE TABLE Artists (artist_id INTEGER PRIMARY KEY, name TEXT, playcount INTEGER, url TEXT)")
    #loop through data and add to database
    conn.commit()

#insert analysis functions here

def main():
    filename = "placeholder"
    json_data = readDataFromFile(filename)
    cur, conn = setUpDatabase('lastfm.db')
    setUpTabsTable(json_data, cur, conn)
    setUpArtistTable(json_data, cur, conn)
    #insert tests here
    conn.close()
    

if __name__ == "__main__":
    main()