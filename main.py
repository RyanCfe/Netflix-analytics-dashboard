from fastapi import FastAPI
import sqlite3
import pandas as pd

#API is mainly a thin reporting layer over the normalized database.
app = FastAPI()  #FastAPI() creates the web application

DB_PATH = "netflix.db"  #DB_PATH stores the database file location


#A route is a URL path linked to a function.  (/ - symbol)

def query_db(query):
    conn = sqlite3.connect(DB_PATH)  #opens database connection
    df = pd.read_sql(query, conn)    #runs sqp query and stores result in dataframe
    conn.close()                    #closes database connection
    return df                       # sends database back

# ---------- BASIC ----------
@app.get("/")    #decorator- someone opens root url it runs function below , route is a URL path linked to a function 
def home():
    return {"message": "Netflix API running"}

# ---------- TOP GENRES ----------
@app.get("/top-genres")   #How many times does each genre appear?
def top_genres():
    query = """
    SELECT genre, COUNT(*) as count
    FROM show_genres_view
    GROUP BY genre
    ORDER BY count DESC
    LIMIT 1000
    """ 
    df = query_db(query)   #Run the SQL and get DataFrame.
    return df.to_dict(orient="records")  #Convert DataFrame to a list of dictionaries. FastAPI automatically sends this as JSON.

# ---------- TOP ACTORS ----------
@app.get("/top-actors")
def top_actors():
    query = """
    SELECT actor, COUNT(*) as count
    FROM show_actors_view
    GROUP BY actor
    ORDER BY count DESC
    LIMIT 1000
    """
    df = query_db(query)
    return df.to_dict(orient="records")

# ---------- TOP DIRECTORS ----------
@app.get("/top-directors")
def top_directors():
    query = """
    SELECT director, COUNT(*) as count
    FROM show_directors_view
    GROUP BY director
    ORDER BY count DESC
    LIMIT 1000
    """
    df = query_db(query)
    return df.to_dict(orient="records")

# ---------- CONTENT BY COUNTRY ----------
@app.get("/top-countries")
def top_countries():
    query = """
    SELECT country, COUNT(*) as count
    FROM show_countries_view
    GROUP BY country
    ORDER BY count DESC
    LIMIT 1000
    """
    df = query_db(query)
    return df.to_dict(orient="records")

# ---------- SEARCH SHOW ----------
@app.get("/search")
def search(title: str):
    query = f"""
    SELECT * FROM shows
    WHERE title LIKE '%{title}%'
    LIMIT 2000
    """
    df = query_db(query)
    return df.to_dict(orient="records")

# ---------- SHOW DETAILS ----------  This endpoint fetches details for one show.

@app.get("/show/{show_id}")
def show_details(show_id: str):
    query = f"""
    SELECT s.title, s.release_year,
           g.genre, a.actor, d.director, c.country
    FROM shows s
    LEFT JOIN show_genres_view g ON s.show_id = g.show_id
    LEFT JOIN show_actors_view a ON s.show_id = a.show_id
    LEFT JOIN show_directors_view d ON s.show_id = d.show_id
    LEFT JOIN show_countries_view c ON s.show_id = c.show_id
    WHERE s.show_id = '{show_id}'
    """
    df = query_db(query)
    return df.to_dict(orient="records")



#FastAPI sits between:

#the database  and the Streamlit dashboard
#So the dashboard does not write SQL directly.

#Instead:

#Streamlit sends an HTTP request
#FastAPI receives it
#FastAPI runs SQL
#FastAPI sends JSON back

#This separation is good design because:

#frontend and backend are independent
#database logic stays in one place
#the same API can be used by dashboard, mobile app, or other clients