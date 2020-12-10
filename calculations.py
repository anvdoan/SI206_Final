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

""" Requires: nothing
Modifies: nothing
Effects: Generates a bar graph displaying the number of artists of each gender (Male, Female, None) """
def makeBarChart():
    gender= ['Male', 'Female', 'None'] 
    numArtists=[107,33, 10]
    colors = ['goldenrod','midnightblue', 'violet']
    fig = go.Figure(data=go.Bar(x= gender, y=numArtists, 
    marker_color= colors))
    fig.update_layout(title='Number of Artists on Top Artist Charts (all genres) by Gender')
    fig.write_image('barChart.jpeg')


""" Requires: nothing
Modifies: nothing
Effects: Generates a radar plot displaying the number of artists of each gender per genre. """
def makeRadarPlot():
    genres = ['rock', 'pop', 'folk', 'rnb', 'singer-songwriter', 'indie']
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[18, 7, 22, 16, 22, 22],
        theta= genres,
        mode='lines',
        name='Male', 
        line_color='aquamarine'
    ))
    fig.add_trace(go.Scatterpolar(
        r=[3, 16, 3, 5, 3, 3],
        theta= genres,
        mode='lines',
        name='Female', 
        line_color='darkkhaki'
    ))
    fig.add_trace(go.Scatterpolar(
        r=[4, 2, 0, 4, 0, 0],
        theta= genres,
        mode='lines',
        name='None', 
        line_color='coral'

    ))
    fig.update_layout(
        polar=dict(
            radialaxis = dict(
                visible = True,
                range= [0, 23]
            )
        ),
        title="Number of Top Artists on Top Charts for Genres by Gender",
        showlegend = True
    )
    fig.write_image('radar_plot.jpeg')


""" Requires: nothing
Modifies: nothing
Effects: Generates a scatter plot displaying the probability of correctness of each gender predictiton, 
         organized by gender(Male, Female) with the average probability noted. """
def makeScatterPlot():
    gender = ['Male', 'Female']
    
    maleProbs = [0.88, 0.92, 0.79, 0.99, 0.75, 0.97, 0.92, 0.86, 1.0, 0.95, 0.87, 0.98, 0.97, 0.94, 0.98, 1.0, 0.86, 0.8, 0.99, 0.88, 0.78, 0.98, 0.88, 0.98, 0.99, 0.95, 0.8, 1.0, 0.75, 0.75, 0.98, 0.93, 0.98, 0.99, 0.86, 0.95, 0.89, 0.86, 0.68, 0.92, 0.94, 0.99, 0.93, 0.86, 0.74, 0.95, 0.88, 0.86, 0.99, 0.9, 0.97, 0.98, 0.56, 0.99, 0.9, 0.67, 0.97, 0.96, 0.99, 0.99, 0.94, 0.94, 0.82, 0.99, 0.98, 0.99, 0.99, 0.99, 0.99, 0.99, 0.99, 0.98, 0.99, 0.99, 0.95, 0.98, 0.94, 0.95, 0.97, 0.99, 0.99, 0.99, 0.99, 0.99, 0.99, 0.86, 0.97, 0.86, 0.86, 0.83, 0.97, 0.61, 0.96, 0.65, 0.91, 0.86, 0.97, 1.0, 0.77, 0.86, 0.86, 1.0, 0.78, 0.76, 0.76, 0.86, 0.92]
    femProbs = [0.71, 0.52, 0.74, 0.97, 0.97, 0.97, 0.97, 0.98, 0.94, 0.98, 0.92, 0.67, 0.96, 0.98, 0.77, 0.98, 0.95, 0.78, 0.96, 0.98, 0.77, 0.97, 0.98, 0.97, 0.99, 0.98, 0.93, 0.52, 0.98, 0.86, 0.98, 0.95, 0.59]
    
    
    fig = go.Figure()

    #work around with box plot bc scatter does not show individual vals

    fig.add_trace(go.Box(y=maleProbs, name='Male', boxpoints='all', jitter=1))

    fig.add_trace(go.Box(y=femProbs, name='Female', boxpoints='all', jitter=1))
    
    fig.update_layout(title='Probablity of Genderize API by Gender',
    showlegend=False)

    fig.write_image('scatter_plot.jpeg')


""" Requires: nothing
Modifies: gender_dict, male_probs, fem_probs, fem_count, male_count, none_count
Effects: calls connectToDatabase(), gatherArtistsPerGender(), gatherProbabilities(), gatherGenderbyGenre() 3 times. 
         writes results to resultsdemo.txt. 
         calls makeRadarPlot(), makeBarChart(), makeScatterPlot(). """
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
    makeBarChart()
    makeScatterPlot()



if __name__ == "__main__":
    main()