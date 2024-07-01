import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import random
import numpy as np
from textblob import TextBlob
import base64

# Database setup
conn = sqlite3.connect('cinematic_vault.db')
c = conn.cursor()

# Create table with unique fields
c.execute('''CREATE TABLE IF NOT EXISTS cinematic_treasures
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              title TEXT NOT NULL,
              director TEXT NOT NULL,
              release_year INTEGER NOT NULL,
              language TEXT NOT NULL,
              rating FLOAT NOT NULL,
              genre TEXT NOT NULL,
              runtime INTEGER NOT NULL,
              box_office REAL,
              awards TEXT,
              cinematographer TEXT,
              soundtrack_composer TEXT,
              critical_reception FLOAT,
              user_reviews TEXT,
              cultural_impact TEXT,
              trivia TEXT,
              added_date TEXT NOT NULL)''')
conn.commit()

# Helper functions
def add_cinematic_gem(title, director, release_year, language, rating, genre, runtime, box_office, awards, cinematographer, soundtrack_composer, critical_reception, user_reviews, cultural_impact, trivia):
    added_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO cinematic_treasures (title, director, release_year, language, rating, genre, runtime, box_office, awards, cinematographer, soundtrack_composer, critical_reception, user_reviews, cultural_impact, trivia, added_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (title, director, release_year, language, rating, genre, runtime, box_office, awards, cinematographer, soundtrack_composer, critical_reception, user_reviews, cultural_impact, trivia, added_date))
    conn.commit()

def get_all_cinematic_treasures():
    return pd.read_sql_query("SELECT * FROM cinematic_treasures", conn)

def update_cinematic_gem(id, title, director, release_year, language, rating, genre, runtime, box_office, awards, cinematographer, soundtrack_composer, critical_reception, user_reviews, cultural_impact, trivia):
    c.execute("UPDATE cinematic_treasures SET title=?, director=?, release_year=?, language=?, rating=?, genre=?, runtime=?, box_office=?, awards=?, cinematographer=?, soundtrack_composer=?, critical_reception=?, user_reviews=?, cultural_impact=?, trivia=? WHERE id=?",
              (title, director, release_year, language, rating, genre, runtime, box_office, awards, cinematographer, soundtrack_composer, critical_reception, user_reviews, cultural_impact, trivia, id))
    conn.commit()

def delete_cinematic_gem(id):
    c.execute("DELETE FROM cinematic_treasures WHERE id=?", (id,))
    conn.commit()

def filter_cinematic_treasures(criteria, value):
    if criteria in ['release_year', 'rating', 'runtime', 'box_office', 'critical_reception']:
        return pd.read_sql_query(f"SELECT * FROM cinematic_treasures WHERE {criteria} = ?", conn, params=(value,))
    else:
        return pd.read_sql_query(f"SELECT * FROM cinematic_treasures WHERE {criteria} LIKE ?", conn, params=('%' + value + '%',))

def count_cinematic_treasures_by_language(language):
    return c.execute("SELECT COUNT(*) FROM cinematic_treasures WHERE language=?", (language,)).fetchone()[0]

def get_top_rated_cinematic_treasures(limit=10):
    return pd.read_sql_query(f"SELECT * FROM cinematic_treasures ORDER BY rating DESC LIMIT {limit}", conn)

def get_cinematic_treasures_by_era(start_year, end_year):
    return pd.read_sql_query("SELECT * FROM cinematic_treasures WHERE release_year BETWEEN ? AND ?", conn, params=(start_year, end_year))

def analyze_user_reviews(reviews):
    blob = TextBlob(reviews)
    return blob.sentiment.polarity

def calculate_cultural_impact_score(impact):
    words = impact.lower().split()
    impact_words = ['influential', 'groundbreaking', 'iconic', 'revolutionary', 'landmark']
    return sum(word in impact_words for word in words) / len(impact_words)

# Unique functions
def generate_movie_dna(movie):
    """Generate a unique 'DNA' sequence for a movie based on its attributes"""
    dna = ""
    for char in movie['title']:
        dna += format(ord(char), '08b')
    dna += format(int(movie['rating'] * 10), '08b')
    dna += format(movie['release_year'], '016b')
    return dna

def movie_dna_similarity(dna1, dna2):
    """Calculate the similarity between two movie DNA sequences"""
    return sum(c1 == c2 for c1, c2 in zip(dna1, dna2)) / len(dna1)

def find_cinematic_soulmate(movie_id):
    """Find the most similar movie based on 'DNA' similarity"""
    movies = get_all_cinematic_treasures()
    target_movie = movies[movies['id'] == movie_id].iloc[0]
    target_dna = generate_movie_dna(target_movie)
    
    max_similarity = 0
    soulmate = None
    for _, movie in movies.iterrows():
        if movie['id'] != movie_id:
            similarity = movie_dna_similarity(target_dna, generate_movie_dna(movie))
            if similarity > max_similarity:
                max_similarity = similarity
                soulmate = movie
    
    return soulmate, max_similarity

def generate_movie_poster(title, director, year):
    poster = """
+-------------------------------------------+
|                                           |
|  {title:<34}       |
|                                           |
|  Director: {director:<30} |
|                                           |
|           {year:<4}                            | 
+-------------------------------------------+
    """
    return poster.format(
        title=title[:34],
        director=director[:30],
        year=year
    )
    

def calculate_cinematic_quotient(movie):
    """Calculate a unique 'Cinematic Quotient' for a movie"""
    base_score = movie['rating'] * 10
    year_factor = (datetime.now().year - movie['release_year']) / 100
    impact_score = calculate_cultural_impact_score(movie['cultural_impact'])
    awards_score = len(movie['awards'].split(',')) if movie['awards'] else 0
    return base_score + (year_factor * 5) + (impact_score * 10) + (awards_score * 2)

# Streamlit app
st.set_page_config(page_title="Cinematic Vault: A Movie List Application", layout="wide")

st.title("🎬 Cinematic Vault: A Movie List Application")

# Sidebar navigation
page = st.sidebar.selectbox("Navigate", ["Home", "Add Cinematic Gem", "Discover Treasures", "Update Cinematic Gem", "Remove from Vault", "Cinematic Analysis"])

if page == "Home":
    st.header("📋 All Cinematic Treasures")
    movies = get_all_cinematic_treasures()
    st.dataframe(movies)

    st.subheader("🌍 Cinematic Diversity")
    language_counts = movies['language'].value_counts()
    fig = px.pie(values=language_counts.values, names=language_counts.index, title="Films by Language")
    st.plotly_chart(fig)

    st.subheader("🌟 Cream of the Crop")
    top_movies = get_top_rated_cinematic_treasures()
    for _, movie in top_movies.iterrows():
        st.markdown(f"**{movie['title']}** ({movie['release_year']}) - ⭐ {movie['rating']}")
        st.text(generate_movie_poster(movie['title'], movie['director'], movie['release_year']))

elif page == "Add Cinematic Gem":
    st.header("➕ Add a New Cinematic Gem")
    title = st.text_input("Title")
    director = st.text_input("Director")
    release_year = st.number_input("Release Year", min_value=1800, max_value=datetime.now().year, step=1)
    language = st.text_input("Language")
    rating = st.slider("Rating", 0.0, 10.0, 5.0, 0.1)
    genre = st.text_input("Genre")
    runtime = st.number_input("Runtime (minutes)", min_value=1, step=1)
    box_office = st.number_input("Box Office (million $)", min_value=0.0, step=0.1)
    awards = st.text_input("Awards")
    cinematographer = st.text_input("Cinematographer")
    soundtrack_composer = st.text_input("Soundtrack Composer")
    critical_reception = st.slider("Critical Reception", 0.0, 10.0, 5.0, 0.1)
    user_reviews = st.text_area("User Reviews")
    cultural_impact = st.text_area("Cultural Impact")
    trivia = st.text_area("Trivia")

    if st.button("Add to Vault"):
        add_cinematic_gem(title, director, release_year, language, rating, genre, runtime, box_office, awards, cinematographer, soundtrack_composer, critical_reception, user_reviews, cultural_impact, trivia)
        st.success("Cinematic gem added to the vault!")

elif page == "Discover Treasures":
    st.header("🔍 Discover Cinematic Treasures")
    filter_option = st.selectbox("Filter by", ["Title", "Director", "Release Year", "Language", "Rating", "Genre", "Awards", "Cinematographer", "Soundtrack Composer"])
    filter_value = st.text_input("Enter filter value")

    if st.button("Unearth Treasures"):
        filtered_movies = filter_cinematic_treasures(filter_option.lower().replace(" ", "_"), filter_value)
        st.dataframe(filtered_movies)

    st.subheader("🧬 Find Cinematic Soulmates")
    selected_movie = st.selectbox("Select a movie", get_all_cinematic_treasures()['title'])
    if st.button("Find Soulmate"):
        movie_id = get_all_cinematic_treasures()[get_all_cinematic_treasures()['title'] == selected_movie]['id'].iloc[0]
        soulmate, similarity = find_cinematic_soulmate(movie_id)
        st.write(f"The cinematic soulmate of '{selected_movie}' is '{soulmate['title']}' with {similarity*100:.2f}% DNA similarity!")
        st.text(generate_movie_poster(soulmate['title'], soulmate['director'], soulmate['release_year']))

elif page == "Update Cinematic Gem":
    st.header("✏️ Update Cinematic Gem")
    movies = get_all_cinematic_treasures()
    movie_to_update = st.selectbox("Select Cinematic Gem to Update", movies['title'])
    movie_data = movies[movies['title'] == movie_to_update].iloc[0]

    title = st.text_input("Title", movie_data['title'])
    director = st.text_input("Director", movie_data['director'])
    release_year = st.number_input("Release Year", min_value=1800, max_value=datetime.now().year, step=1, value=movie_data['release_year'])
    language = st.text_input("Language", movie_data['language'])
    rating = st.slider("Rating", 0.0, 10.0, float(movie_data['rating']), 0.1)
    genre = st.text_input("Genre", movie_data['genre'])
    runtime = st.number_input("Runtime (minutes)", min_value=1, step=1, value=movie_data['runtime'])
    box_office = st.number_input("Box Office (million $)", min_value=0.0, step=0.1, value=movie_data['box_office'])
    awards = st.text_input("Awards", movie_data['awards'])
    cinematographer = st.text_input("Cinematographer", movie_data['cinematographer'])
    soundtrack_composer = st.text_input("Soundtrack Composer", movie_data['soundtrack_composer'])
    critical_reception = st.slider("Critical Reception", 0.0, 10.0, float(movie_data['critical_reception']), 0.1)
    user_reviews = st.text_area("User Reviews", movie_data['user_reviews'])
    cultural_impact = st.text_area("Cultural Impact", movie_data['cultural_impact'])
    trivia = st.text_area("Trivia", movie_data['trivia'])

    if st.button("Update Cinematic Gem"):
        update_cinematic_gem(movie_data['id'], title, director, release_year, language, rating, genre, runtime, box_office, awards, cinematographer, soundtrack_composer, critical_reception, user_reviews, cultural_impact, trivia)
        st.success("Cinematic gem updated successfully!")

elif page == "Remove from Vault":
    st.header("🗑️ Remove Cinematic Gem from Vault")
    movies = get_all_cinematic_treasures()
    movie_to_delete = st.selectbox("Select Cinematic Gem to Remove", movies['title'])

    if st.button("Remove from Vault"):
        movie_id = movies[movies['title'] == movie_to_delete]['id'].iloc[0]
        delete_cinematic_gem(movie_id)
        st.success("Cinematic gem removed from the vault!")

elif page == "Cinematic Analysis":
    st.header("📊 Cinematic Analysis")

    st.subheader("Cinematic Timeline")
    movies = get_all_cinematic_treasures()
    fig = px.scatter(movies, x="release_year", y="rating", size="box_office", color="language", hover_name="title", 
                     labels={"release_year": "Release Year", "rating": "Rating", "box_office": "Box Office (millions $)"},
                     title="Cinematic Treasures Through Time")
    st.plotly_chart(fig)

    st.subheader("Language Diversity Over Time")
    language_by_year = movies.groupby('release_year')['language'].nunique().reset_index()
    fig = px.line(language_by_year, x="release_year", y="language", 
                  labels={"release_year": "Year", "language": "Number of Languages"},
                  title="Language Diversity in Cinema Over Time")
    st.plotly_chart(fig)

    st.subheader("Cinematic Quotient Analysis")
    movies['cinematic_quotient'] = movies.apply(calculate_cinematic_quotient, axis=1)
    top_cq_movies = movies.nlargest(10, 'cinematic_quotient')
    fig = px.bar(top_cq_movies, x="title", y="cinematic_quotient", 
                 labels={"title": "Movie", "cinematic_quotient": "Cinematic Quotient"},
                 title="Top 10 Movies by Cinematic Quotient")
    st.plotly_chart(fig)

    st.subheader("Sentiment Analysis of User Reviews")
    movies['sentiment'] = movies['user_reviews'].apply(analyze_user_reviews)
    fig = px.scatter(movies, x="rating", y="sentiment", hover_name="title", 
                     labels={"rating": "IMDb Rating", "sentiment": "User Review Sentiment"},
                     title="IMDb Rating vs User Review Sentiment")
    st.plotly_chart(fig)

# Close the database connection when the app is done
conn.close()
