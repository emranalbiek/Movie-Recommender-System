import logging
import os
import pandas as pd
import numpy as np
import pickle
from typing import Tuple
from scipy.sparse import csr_matrix
import gc


# Setup logging Configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Create Class for Data Preprocessing
class DataPreprocessing():
    def clean(self, movies:pd.DataFrame, ratings:pd.DataFrame, links:pd.DataFrame) -> Tuple[
        pd.DataFrame, csr_matrix, dict, dict]:
        """Cleans and Format the data and saves the artifacts for model training.
        
        Args:
            movies: pandas dataframe containing movies data
            ratings: pandas dataframe containing ratings data
            links: pandas dataframe containing links data
        
        Returns:
            cleaned_data: pandas dataframe containing cleaned movies and ratings data
            X: sparse matrix
            movie_mapper: dict that maps movie id's to movie indices
            movie_inv_mapper: dict that maps movie indices to movie id's
        """
        try:
            # Step 1: Merge both dataframes on movieId
            movie_ratings = ratings.merge(movies, on='movieId')
            logging.info("Merged 'movies' and 'ratings' DataFrames Completed Successfully")
            
            del ratings
            gc.collect()
            
            # Step 2: Drop Duplicate Rows
            movie_ratings.drop_duplicates(inplace=True)
            movie_ratings.drop_duplicates(subset=['userId','title'], inplace=True)
            logging.info("Dropped Duplicate Rows Completed Successfully")
            
            # Step 3: Drop Missing Values
            movie_ratings.dropna(inplace=True)
            logging.info("Dropped Missing Values Completed Successfully")
            
            # Step 4: Drop Unnecessary Columns
            movie_ratings.drop(columns=['genres','timestamp'], inplace=True)
            movies.drop(columns=['genres'], inplace=True)
            logging.info("Dropped Unnecessary Columns Completed Successfully")
            
            # Step 5: Add year column
            movies['year'] = movies['title'].str.extract(r'\((\d{4})\)')[0]
            logging.info("Added Year Column Completed Successfully")
            
            # Step 6: Add Average Rating column
            average_ratings = movie_ratings.groupby('title')['rating'].mean().reset_index()
            average_ratings.rename(columns={'rating':'avg_rating'}, inplace=True)
            movies = movies.merge(average_ratings, on='title')
            logging.info("Added Average Rating Column Completed Successfully")
            
            # Step 7:Take those movies which got at least 50 rating of user
            number_rating = movie_ratings.groupby('title')['rating'].count().reset_index()
            number_rating.rename(columns={'rating':'num_of_rating'},inplace=True)
            
            # Filter movies dataframe
            movies = movies.merge(number_rating, on='title')
            movies = movies[movies['num_of_rating'] >= 50]
            movies.drop(columns=['num_of_rating'], inplace=True)
            
            # Filter movie_ratings dataframe
            final_ratings = movie_ratings.merge(number_rating, on='title')
            final_ratings = final_ratings[final_ratings['num_of_rating'] >= 50]
            final_ratings.drop(columns=['num_of_rating'], inplace=True)
            logging.info("Filtered Movies with at least 50 Ratings Completed Successfully")
            
            del number_rating, movie_ratings, average_ratings
            gc.collect()
            # Step 8: Add TMDB movie_id (from links.csv)
            movies = movies.merge(links[['movieId', 'tmdbId']], on='movieId', how='left')
            movies.rename(columns={'tmdbId': 'movie_id'}, inplace=True)
            logging.info("Merged 'links' DataFrame to add TMDB movie_id Completed Successfully")
            
            # Step 9: Transform our dataframe into a user-item matrix, also known as a "utility" matrix.
            # We will use a crs matrix from scipy for this transformation.
            def create_X(df):
                """
                Generates a sparse matrix from ratings dataframe.
                
                Args:
                    df: pandas dataframe containing 3 columns (userId, movieId, rating)
                
                Returns:
                    X: sparse matrix
                    movie_mapper: dict that maps movie id's to movie indices
                    movie_inv_mapper: dict that maps movie indices to movie id's
                """
                M = df['userId'].nunique()
                N = df['movieId'].nunique()
                
                user_mapper = dict(zip(np.unique(df["userId"]), list(range(M))))
                movie_mapper = dict(zip(np.unique(df["movieId"]), list(range(N))))
                
                movie_inv_mapper = dict(zip(list(range(N)), np.unique(df["movieId"])))
                
                user_index = [user_mapper[i] for i in df['userId']]
                item_index = [movie_mapper[i] for i in df['movieId']]
                
                X = csr_matrix((df["rating"], (user_index,item_index)), shape=(M,N))
                
                return X, movie_mapper, movie_inv_mapper
            
            X, movie_mapper,  movie_inv_mapper = create_X(final_ratings)
            logging.info("Created User-Item Matrix Completed Successfully")
            
            # Step 10: Evaluate sparsity of the matrix
            n_total = X.shape[0]*X.shape[1]
            n_ratings = X.nnz
            sparsity = n_ratings/n_total
            logging.info(f'Sparsity of the User-Item Matrix: {round(sparsity*100,2)}')
            
            # Final Step: Save The Artifacts
            logging.info("Saving artifacts...")
            
            # Create artifacts directory if it doesn't exist
            os.makedirs('artifacts', exist_ok=True)
            logging.info("Artifacts directory created/verified")
            
            # Save movies dataframe
            movies.to_pickle('artifacts/movies_processed.pkl')
            logging.info("Saved: movies_processed.pkl")
            
            # Save X matrix
            with open('artifacts/X_matrix.pkl', 'wb') as f:
                pickle.dump(X, f)
            logging.info("Saved: X_matrix.pkl")
            
            # Save movie_mapper
            with open('artifacts/movie_mapper.pkl', 'wb') as f:
                pickle.dump(movie_mapper, f)
            logging.info("Saved: movie_mapper.pkl")
            
            # Save movie_inv_mapper
            with open('artifacts/movie_inv_mapper.pkl', 'wb') as f:
                pickle.dump(movie_inv_mapper, f)
            logging.info("Saved: movie_inv_mapper.pkl")
            
            del links, movies
            gc.collect()
            
            logging.info("Data Preprocessing Completed Successfully")
            return final_ratings, X, movie_mapper, movie_inv_mapper
        except Exception as e:
            logging.error(f'Error in Data Preprocessing: {e}')
            raise e