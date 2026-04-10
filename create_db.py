import sqlite3
import pandas as pd

df = pd.read_csv('C:/Users/ryann/Downloads/netflix.csv')

conn = sqlite3.connect("netflix.db")
df.to_sql("netflix_raw", conn, if_exists="replace", index=False)

print(" Database created successfully!")