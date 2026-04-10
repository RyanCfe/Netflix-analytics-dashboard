import streamlit as st
import requests
import pandas as pd  #convert returned JSON into DataFrames for charts/tables.

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="Netflix Dashboard", layout="wide")

st.title("Netflix Analytics Dashboard")

# KPI ROW
col1, col2, col3, col4 = st.columns(4)

# Using top endpoints as proxies (since no count API)
genres = requests.get(f"{API}/top-genres").json()
actors = requests.get(f"{API}/top-actors").json()
directors = requests.get(f"{API}/top-directors").json()
countries = requests.get(f"{API}/top-countries").json()

col1.metric("Top Genres Count", len(genres))
col2.metric("Top Actors Count", len(actors))
col3.metric("Top Directors Count", len(directors))
col4.metric("Top Countries Count", len(countries))

st.divider()

# CHARTS
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top Genres")
    df = pd.DataFrame(genres)
    st.bar_chart(df.set_index("genre"))

with col2:
    st.subheader("Top Actors")
    df = pd.DataFrame(actors)
    st.bar_chart(df.set_index("actor"))

col3, col4 = st.columns(2)

with col3:
    st.subheader("Top Directors")
    df = pd.DataFrame(directors)
    st.bar_chart(df.set_index("director"))

with col4:
    st.subheader("Top Countries")
    df = pd.DataFrame(countries)
    st.bar_chart(df.set_index("country"))

st.divider()

# SEARCH

st.subheader("Search Shows")

search_query = st.text_input("Enter show name")

if search_query:
    results = requests.get(f"{API}/search?title={search_query}").json()
    df = pd.DataFrame(results)

    if not df.empty:
        st.dataframe(df)
    else:
        st.warning("No results found")

st.divider()

# SHOW DETAILS
st.subheader("Show Details")

show_id = st.text_input("Enter show_id (e.g. s1)")

if show_id:
    details = requests.get(f"{API}/show/{show_id}").json()
    df = pd.DataFrame(details)

    if not df.empty:
        st.dataframe(df)
    else:
        st.warning("No data found")

st.divider()

# MORE EXPLORING
st.subheader("Quick Explore (Top Genres Data)")

df = pd.DataFrame(genres)
st.dataframe(df)