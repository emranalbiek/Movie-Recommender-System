import pickle
import streamlit as st
import requests
import os
import gdown
import pandas as pd
from src.model_training import ModelTraining

@st.cache_resource(ttl=86400) # Cache for 1 day
def download_artifacts():
    """Download model artifacts from Google Drive if not exist"""
    
    files = {
        'artifacts/movies_processed.pkl': '1CW_jp-3g1QB7m4_eJKv_a4ju_8vRZ9yH',
        'artifacts/X_matrix.pkl': '1Tm12kl9iof1u1_wGBRkjCWGouQUI1r1D',
        'artifacts/movie_mapper.pkl': '1cPMSfpL51i6umQQO8SFVcsLHhnqMpfjQ',
        'artifacts/movie_inv_mapper.pkl': '1oDjj9HryQ8IbAxXZrJwFuBSkZ5B4u6wX'
    }
    
    os.makedirs('artifacts', exist_ok=True)
    
    for filepath, file_id in files.items():
        if not os.path.exists(filepath):
            url = f'https://drive.google.com/uc?id={file_id}'
            gdown.download(url, filepath, quiet=False)

download_artifacts()

@st.cache_data
def fetch_poster(movie_id):
    """Fetches the movie poster URL from TMDB API."""
    if pd.isna(movie_id):
        return "https://placehold.co/500x750/333/FFFFFF?text=No+Poster"
    
    url = f"https://api.themoviedb.org/3/movie/{int(movie_id)}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    try:
        data = requests.get(url, timeout=5)
        data.raise_for_status()
        data = data.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
    except:
        pass
    return "https://placehold.co/500x750/333/FFFFFF?text=No+Poster"


@st.cache_resource
def recommend(movie_title, metric, algorithm):
    """Recommends similar movies using k-NN collaborative filtering."""
    try:
        # Find movie in dataset
        movie_data = movies[movies['title'] == movie_title]
        if movie_data.empty:
            st.error("Movie not found.")
            return [], [], [], []
        
        movie_id = movie_data.iloc[0]['movieId']
        
        # Use k-NN to find similar movies
        model = ModelTraining(
            movie_id=movie_id,
            X=X,
            movie_mapper=movie_mapper,
            movie_inv_mapper=movie_inv_mapper,
            k=13,
            metric=metric,
            algorithm=algorithm
        )
        
        similar_movie_ids = model.find_similar_movies()
        
        # Collect recommendations
        recommended_movie_names = []
        recommended_movie_posters = []
        recommended_movie_years = []
        recommended_movie_ratings = []
        
        for rec_movie_id in similar_movie_ids:
            movie_info = movies[movies['movieId'] == rec_movie_id]
            if not movie_info.empty:
                row = movie_info.iloc[0]
                
                recommended_movie_names.append(row['title'])
                recommended_movie_posters.append(fetch_poster(row.get('movie_id')))
                recommended_movie_years.append(row.get('year', 'N/A'))
                recommended_movie_ratings.append(row.get('avg_rating', 0))
        
        return recommended_movie_names, recommended_movie_posters, recommended_movie_years, recommended_movie_ratings
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return [], [], [], []


# ============= Streamlit Configuration =============
st.set_page_config(layout="wide", page_title="Movie Recommender System")
st.header("🎬 Movie Recommender System")

# Load the data files
try:
    movies = pd.read_pickle('artifacts/movies_processed.pkl')
    X = pickle.load(open('artifacts/X_matrix.pkl', 'rb'))
    movie_mapper = pickle.load(open('artifacts/movie_mapper.pkl', 'rb'))
    movie_inv_mapper = pickle.load(open('artifacts/movie_inv_mapper.pkl', 'rb'))
    
    st.success(f"Loaded {movies['title'].nunique():,} movies with {X.nnz:,} ratings for {X.shape[0]:,} users.")
    
except FileNotFoundError:
    st.error("Model files not found. Please run `python main.py` first.")
    st.info("""
    **Steps to generate artifacts:**
```bash
    python main.py
```
    """)
    st.stop()

# Choose the recommendation style
metric = st.selectbox(
    "Select Recommendation Style",
    ('Netflix', 'TMDB|IMDb')
) 
if metric == 'Netflix':
    metric_value = 'cosine' # Netflix-style recommendations (It has diversity than any other metric)
    algorithm_value = 'brute'
else:
    metric_value = 'manhattan' # TMDB/IMDb-style recommendations 
    algorithm_value = 'auto'

# Sidebar
with st.sidebar:
    st.markdown("### Connect with me")
    st.markdown("""
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <div style="display: flex; gap: 20px; font-size: 28px;">
            <a href="http://linkedin.com/in/emranalbeik" target="_blank"><i class="fab fa-linkedin"></i></a>
            <a href="https://github.com/RedDragon30" target="_blank"><i class="fab fa-github"></i></a>
            <a href="https://emranalbeik.odoo.com/" target="_blank"><i class="fas fa-globe"></i></a>
            <a href="mailto:emranalbiek@gmail.com"><i class="fas fa-envelope"></i></a>
        </div>
    """, unsafe_allow_html=True)

# Movie selection
movie_list = movies['title'].values
selected_movie = st.selectbox(
    "select a movie from the dropdown",
    movie_list
)

# Show selected movie info
if selected_movie:
    selected_info = movies[movies['title'] == selected_movie].iloc[0]
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Year", selected_info.get('year', 'N/A'))
    with col2:
        st.metric("Rating", f"{selected_info.get('avg_rating', 0):.1f}")

# Recommendation button
if st.button('Show Recommendation'):
    with st.spinner('Finding recommendations using k-NN...'):
        recommended_movie_names, recommended_movie_posters, recommended_movie_years, recommended_movie_ratings = recommend(selected_movie, metric_value, algorithm_value)
    
    if recommended_movie_names:
        st.markdown(f"### Because you watched **{selected_movie}**:")
        
        per_row = 6
        
        cols1 = st.columns(per_row)
        for i in range(min(per_row, len(recommended_movie_names))):
            with cols1[i]:
                st.text(recommended_movie_names[i])
                st.image(recommended_movie_posters[i], width=200)
                
                # Year
                year = recommended_movie_years[i]
                if pd.notna(year) and year != 'N/A':
                    try:
                        st.caption(f"Year: {int(float(year))}")
                    except:
                        st.caption("Year: N/A")
                else:
                    st.caption("Year: N/A")
                
                # Rating
                rating = recommended_movie_ratings[i]
                if pd.notna(rating) and rating > 0:
                    st.caption(f"Rating: {rating:.1f}")
                else:
                    st.caption("Rating: N/A")
        
        start = per_row
        cols2 = st.columns(per_row)
        for j in range(start, min(start + per_row, len(recommended_movie_names))):
            with cols2[j - start]:
                st.text(recommended_movie_names[j])
                st.image(recommended_movie_posters[j], width=150)
                
                # Year
                year = recommended_movie_years[j]
                if pd.notna(year) and year != 'N/A':
                    try:
                        st.caption(f"Year: {int(float(year))}")
                    except:
                        st.caption("Year: N/A")
                else:
                    st.caption("Year: N/A")
                
                # Rating
                rating = recommended_movie_ratings[j]
                if pd.notna(rating) and rating > 0:
                    st.caption(f"Rating: {rating:.1f}")
                else:
                    st.caption("Rating: N/A")
