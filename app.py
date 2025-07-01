import streamlit as st
import pickle
import pandas as pd
import requests
import os
import gdown

# --- Ensure similarity.pkl is available ---
file_id = '1QZ_rm-1CJVRUKPWJzwzKlxmQoBiYm_w8'
output = 'similarity.pkl'

if not os.path.exists(output):
    url = f"https://drive.google.com/uc?id={file_id}"
    st.info("Downloading similarity.pkl from Google Drive...")
    gdown.download(url, output, quiet=False)
    st.success("Download complete.")

# --- Load data ---
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# --- Fetch poster using TMDB API ---
def fetch_poster(movie_id):
    response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US')
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/" + data['poster_path']

# --- Recommend movies ---
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_movies_posters

# --- Streamlit App ---
st.header('Movie Recommender System')

selected_movie_name = st.selectbox(
    'Type or select a movie from the dropdown',
    movies['title'].values
)

if st.button('Show Recommendation'):
    try:
        names, posters = recommend(selected_movie_name)
        cols = st.columns(5)
        for idx, col in enumerate(cols):
            with col:
                st.markdown(f"""
                    <div style='text-align:center; font-weight:bold; min-height:72px; margin-bottom:8px;'>
                        {names[idx]}
                    </div>""", unsafe_allow_html=True)
                st.image(posters[idx], use_container_width=True)
    except Exception as e:
        st.error(f"An error occurred: {e}")
