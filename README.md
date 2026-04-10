# Netflix Analytics Dashboard 🎬

## Overview

This project is a full-stack data analytics system built using Python. It processes raw Netflix data from a CSV file, normalizes it into a relational database using SQLite, exposes data through a FastAPI backend, and visualizes insights using a Streamlit dashboard.

---

## Architecture

CSV → SQLite → Normalized Database → FastAPI → Streamlit Dashboard

---

## Features

* Data normalization into multiple relational tables
* REST API using FastAPI
* Interactive dashboard using Streamlit
* Search functionality for shows
* Analytics (Top genres, actors, directors, countries)

---

## Tech Stack

* Python
* Pandas
* SQLite
* FastAPI
* Streamlit

---

## How to Run

1. Load data:

```
python create_database.py
```

2. Normalize data:

```
python normalize.py
```

3. Start API:

```
uvicorn main:app --reload
```

4. Run dashboard:

```
streamlit run dashboard.py
```

---

## Project Structure

```
├── create_database.py
├── normalize.py
├── main.py
├── dashboard.py
├── README.md
├── requirements.txt
├── .gitignore
```

---

##  Key Concepts

* Database Normalization (1NF, removing multi-valued fields)
* Many-to-Many Relationships (junction tables)
* REST API design
* Data visualization

---

## Author

Ryan
