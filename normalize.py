import sqlite3
import pandas as pd

# ---------- CONNECT ----------
conn = sqlite3.connect("netflix.db")

# Load raw data
df = pd.read_sql("SELECT * FROM netflix_raw", conn)

# Clean column names
df.columns = df.columns.str.strip()

# ---------- MASTER TABLES ---------- //lookup tables or dimension tables - They store unique values only.

# TYPES
types = df[['type']].dropna().drop_duplicates().reset_index(drop=True).copy()  #df[['type']] gives a DataFrame
types['type_id'] = types.index + 1
types.to_sql("types", conn, if_exists="replace", index=False)  #Save this DataFrame into database as table types

# RATINGS
ratings = df[['rating']].dropna().drop_duplicates().reset_index(drop=True).copy()
ratings['rating_id'] = ratings.index + 1
ratings.to_sql("ratings", conn, if_exists="replace", index=False)

# GENRES
genres = df[['listed_in']].dropna().copy()
genres['listed_in'] = genres['listed_in'].str.split(', ')
genres = genres.explode('listed_in')                     #If a cell contains a list, explode() makes each item into its own row.
genres = genres[['listed_in']].drop_duplicates().reset_index(drop=True).copy()
genres['genre_id'] = genres.index + 1
genres.to_sql("genres", conn, if_exists="replace", index=False)  #Store it in database as genres

# ACTORS
actors = df[['cast']].dropna().copy()
actors['cast'] = actors['cast'].str.split(', ')
actors = actors.explode('cast')
actors = actors[['cast']].drop_duplicates().reset_index(drop=True).copy()
actors['actor_id'] = actors.index + 1
actors.to_sql("actors", conn, if_exists="replace", index=False)

# DIRECTORS
directors = df[['director']].dropna().copy()
directors['director'] = directors['director'].str.split(', ')
directors = directors.explode('director')
directors = directors[['director']].drop_duplicates().reset_index(drop=True).copy()
directors['director_id'] = directors.index + 1
directors.to_sql("directors", conn, if_exists="replace", index=False)

# COUNTRIES
countries = df[['country']].dropna().copy()
countries['country'] = countries['country'].str.split(', ')
countries = countries.explode('country')
countries = countries[['country']].drop_duplicates().reset_index(drop=True).copy()
countries['country_id'] = countries.index + 1
countries.to_sql("countries", conn, if_exists="replace", index=False)

# ---------- SHOWS TABLE (MAIN FACT TABLE) ---------- #It is the center of the database. Other tables connect to it through show_id.

shows = df[['show_id', 'title', 'release_year', 'duration', 'date_added', 'type', 'rating']].copy()

# Map type_id
shows = shows.merge(types, on='type', how='left')

# Map rating_id
shows = shows.merge(ratings, on='rating', how='left')   #If a row has type = "Movie", 
                                                        #and in the types table Movie has type_id = 1, 
                                                        #then after merging the row gets type_id = 1.

# Final columns
shows = shows[['show_id', 'title', 'release_year', 'duration', 'date_added', 'type_id', 'rating_id']]
shows.to_sql("shows", conn, if_exists="replace", index=False)

# ---------- RELATION TABLES (JUNCTION TABLES) ---------- 

#Why junction tables are needed

#A show can have:
#many actors many genres many directors many countries
#And each actor/genre/director/country can belong to many shows.
#That is a many-to-many relationship.
#Relational databases cannot directly store many-to-many inside one field properly, so we create bridge/junction tables.

# SHOW-GENRES
sg = df[['show_id', 'listed_in']].dropna().copy()  #show id and listed in = genres column
sg['listed_in'] = sg['listed_in'].str.split(', ')  #genre text into list
sg = sg.explode('listed_in')  #one row per genre. 
sg = sg.merge(genres, on='listed_in', how='left')   #Join with genres table to get genre_id
sg[['show_id', 'genre_id']].to_sql("show_genres", conn, if_exists="replace", index=False)  #Keep only the relationship columns and save them.

# SHOW-ACTORS
sa = df[['show_id', 'cast']].dropna().copy()
sa['cast'] = sa['cast'].str.split(', ')
sa = sa.explode('cast')
sa = sa.merge(actors, on='cast', how='left')
sa[['show_id', 'actor_id']].to_sql("show_actors", conn, if_exists="replace", index=False)

# SHOW-DIRECTORS
sd = df[['show_id', 'director']].dropna().copy()
sd['director'] = sd['director'].str.split(', ')
sd = sd.explode('director')
sd = sd.merge(directors, on='director', how='left')
sd[['show_id', 'director_id']].to_sql("show_directors", conn, if_exists="replace", index=False)

# SHOW-COUNTRIES
sc = df[['show_id', 'country']].dropna().copy()
sc['country'] = sc['country'].str.split(', ')
sc = sc.explode('country')
sc = sc.merge(countries, on='country', how='left')
sc[['show_id', 'country_id']].to_sql("show_countries", conn, if_exists="replace", index=False)


# ----------TABLES-------------  

#Technically these are not real SQL VIEW objects.
#You are creating actual tables from query results using to_sql().
#But conceptually they act like reporting views.

# SHOW + ACTORS
query = """
SELECT s.show_id, s.title, a.cast AS actor
FROM shows s
JOIN show_actors sa ON s.show_id = sa.show_id
JOIN actors a ON sa.actor_id = a.actor_id
"""
pd.read_sql(query, conn).to_sql("show_actors_view", conn, if_exists="replace", index=False)

# SHOW + GENRES
query = """
SELECT s.show_id, s.title, g.listed_in AS genre
FROM shows s
JOIN show_genres sg ON s.show_id = sg.show_id
JOIN genres g ON sg.genre_id = g.genre_id
"""
pd.read_sql(query, conn).to_sql("show_genres_view", conn, if_exists="replace", index=False)

# SHOW + DIRECTORS
query = """
SELECT s.show_id, s.title, d.director
FROM shows s
JOIN show_directors sd ON s.show_id = sd.show_id
JOIN directors d ON sd.director_id = d.director_id
"""
pd.read_sql(query, conn).to_sql("show_directors_view", conn, if_exists="replace", index=False)

# SHOW + COUNTRIES
query = """
SELECT s.show_id, s.title, c.country
FROM shows s
JOIN show_countries sc ON s.show_id = sc.show_id
JOIN countries c ON sc.country_id = c.country_id
"""
pd.read_sql(query, conn).to_sql("show_countries_view", conn, if_exists="replace", index=False)


print("SUCCESS: Fully normalized database created (16 tables)")


#“I normalized the raw Netflix dataset by separating repeated and multi-valued columns into independent lookup tables and 
# many-to-many bridge tables. For example, I split comma-separated columns like cast, listed_in, director, and country using 
# str.split() and explode(), removed duplicates to create master tables such as actors, genres, directors, and countries, 
# assigned IDs to them, and then created mapping tables such as show_actors and show_genres to connect them to the 
# central shows table.”