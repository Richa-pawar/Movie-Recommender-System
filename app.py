import streamlit as st
import pickle
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure retries and timeout
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)

def fetch_poster(movie_id):
    try:
        response = http.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=9d7d9b27fd278d6aadb023ee0a6c7374&language=en-US', timeout=10)
        response.raise_for_status()
        data = response.json()
        return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred while fetching the movie poster: {e}")
        return None

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id

        recommended_movies.append(movies.iloc[i[0]].title)
        # fetch poster from API
        poster = fetch_poster(movie_id)
        if poster:
            recommended_movies_posters.append(poster)
        else:
            recommended_movies_posters.append("")  # Placeholder for missing poster
    return recommended_movies, recommended_movies_posters

movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl', 'rb'))

st.title('Movie Recommender System')

selected_movie_name = st.selectbox(
    'Type or select a movie from the dropdown',
    movies['title'].values)

if st.button('Show Recommendation'):
    names, posters = recommend(selected_movie_name)

    col1, col2, col3, col4, col5 = st.columns(5)
    for col, name, poster in zip([col1, col2, col3, col4, col5], names, posters):
        with col:
            st.text(name)
            if poster:
                st.image(poster)
            else:
                st.text("Poster not available")



