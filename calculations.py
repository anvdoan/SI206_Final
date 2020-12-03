import requests
import json
import sqlite3
import os


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

def gatherData(cur, conn, genres):
    data_dict = {}
    return data_dict


def main():
    genres = ['rock', 'pop', 'folk', 'rnb', 'singer-songwriter', 'indie']
    cur, conn = connectToDatabase('lastfm.db')
    data_dict = gatherData(cur, conn, genres)
    conn.close()


if __name__ == "__main__":
    main()