import requests
import json
import sqlite3
import os
import plotly as py
import plotly.express as px
import plotly.graph_objects as go


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

""" Requires: cur, conn (database connection), genres (list)
Modifies: data_dict
Effects: Gathers number of artists in database from each genre
         in the genre list and returns a dictionary with the genres as keys, and counts as values"""
def gatherArtistsPerGenre(cur, conn, genres):
    data_dict = dict()
    for g in genres:
        cur.execute("SELECT * FROM Artists WHERE genre = ?", (g,))
        for row in cur:
            data_dict[g] = data_dict.get(g, 0) + 1
    return data_dict

""" Requires: cur, conn (database connection)
Modifies: data_dict
Effects: Gathers number of artists in database organized by gender (F, M, None)
         in the genre list and returns a dictionary with the genders as keys, and counts as values"""
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

""" Requires: cur, conn (database connection)
Modifies: male_probs, fem_probs
Effects: Gathers the probability of each gender prediction for every artist that was 
         determined to be male or female, as predictions of none have no probability returned. """
def gatherProbabilities(cur, conn):
    male_probs = []
    fem_probs = []
    cur.execute("SELECT probability FROM ArtistGender JOIN Genders ON ArtistGender.gender_id = Genders.gender_id WHERE Genders.gender_id = 0")
    i = 0
    for row in cur:
        male_probs.append(row[0])
        i += 1
    cur.execute("SELECT probability FROM ArtistGender JOIN Genders ON ArtistGender.gender_id = Genders.gender_id WHERE Genders.gender_id = 1")
    i = 0
    for row in cur:
        fem_probs.append(row[0])
        i += 1
    return male_probs, fem_probs

""" Requires: cur, conn (database connection), gender (int), genre (list)
Modifies: data_dict
Effects: Gathers the number of artists from gender passed, organized by genre. """
def gatherGenderbyGenre(cur, conn, gender, genres):
    data_dict = dict()
    cur.execute("SELECT genre FROM Artists JOIN ArtistGender ON Artists.artist_id = ArtistGender.artist_id WHERE ArtistGender.gender_id = ?", (gender,))
    for g in cur:
        data_dict[g[0]] = data_dict.get(g[0], 0) + 1
    return data_dict

""" Requires: gender_dict
Modifies: nothing
Effects: Generates a bar graph displaying the number of artists of each gender (Male, Female, None) """
def makeBarChart(gender_dict):
    pass

""" Requires: ??????
Modifies: nothing
Effects: Generates a radar plot displaying the number of artists of each gender per genre. """
def makeRadarPlot():
    genres = ['rock', 'pop', 'folk', 'rnb', 'singer-songwriter', 'indie']
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[17, 8, 21, 17, 22, 17],
        theta= genres,
        fill='toself',
        name='Male'
    ))
    fig.add_trace(go.Scatterpolar(
        r=[4, 15, 3, 5, 3, 2],
        theta= genres,
        fill='toself',
        name='Female'
    ))
    fig.add_trace(go.Scatterpolar(
        r=[4, 2, 1, 3, 0, 0],
        theta= genres,
        fill= 'toself',
        name='None'

    ))
    fig.update_layout(
        polar=dict(
            radialaxis = dict(
                visible = True,
                range= [0, 25]
            )
        ),
        showlegend = True
    )
    fig.write_image('radar_plot.jpeg')


""" Requires: male_probs, fem_probs
Modifies: nothing
Effects: Generates a scatter plot displaying the probability of correctness of each gender predictiton, 
         organized by gender(Male, Female, None) with the average probability noted. """
def makeScatterPlot():
    pass

def main():
    genres = ['rock', 'pop', 'folk', 'rnb', 'singer-songwriter', 'indie']
    cur, conn = connectToDatabase('lastfm.db')
    #call to practice function - can be deleted later:
    #genre_dict = gatherArtistsPerGenre(cur, conn, genres)
    gender_dict = gatherArtistsPerGender(cur, conn)
    male_probs, fem_probs= gatherProbabilities(cur, conn)
    fem_count = gatherGenderbyGenre(cur, conn, 1, genres)
    male_count = gatherGenderbyGenre(cur, conn, 0, genres)
    none_count = gatherGenderbyGenre(cur, conn, 2, genres)
    conn.close()

    #WRITE DATA TO FILE HERE (10 pts)
    with open('resultsdemo.txt', 'w') as file:
        file.write("Number of artists of each reported gender (M, F, None) \n")
        file.write(json.dumps(gender_dict) + "\n\n")
        file.write("Collection of probabilities of each male artist prediction \n")
        file.write(json.dumps(male_probs) + "\n\n")
        file.write("Collection of probabilities of each female artist prediction \n")
        file.write(json.dumps(fem_probs) + "\n\n")
        file.write("Number of male artists of each genre \n")
        file.write(json.dumps(male_count) + "\n\n")
        file.write("Number of female artists of each genre \n")
        file.write(json.dumps(fem_count) + "\n\n")
        file.write("Number of nonbinary artists of each genre \n")
        file.write(json.dumps(none_count))
    file.close()
    #CREATE VISUALIZATIONS
    makeRadarPlot()


if __name__ == "__main__":
    main()