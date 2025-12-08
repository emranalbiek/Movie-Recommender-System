import logging
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors

# Setup logging Configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Create Class for Model Training
class ModelTraining:
    def __init__(self, movie_id, X, movie_mapper, movie_inv_mapper, k, metric, algorithm):
        """
        Finds k-nearest neighbours for a given movie id.
        
        Args:
            movie_id: id of the movie of interest
            X: user-item utility matrix
            movie_mapper: dict that maps movie id's to movie indices
            movie_inv_mapper: dict that maps movie indices to movie id's
            k: number of similar movies to retrieve
            metric: distance metric for kNN calculations
        
        Output: returns list of k similar movie ID's
        """
        self.movie_id = movie_id
        self.X = X
        self.movie_mapper = movie_mapper
        self.movie_inv_mapper = movie_inv_mapper
        self.k = k
        self.metric = metric
        self.algorithm = algorithm
    
    def find_similar_movies(self):
        try:
            X = self.X.T
            neighbour_ids = []
            
            movie_ind = self.movie_mapper[self.movie_id]
            movie_vec = X[movie_ind]
            if isinstance(movie_vec, (np.ndarray)):
                movie_vec = movie_vec.reshape(1,-1)
            # use k+1 since kNN output includes the movieId of interest
            kNN = NearestNeighbors(n_neighbors=self.k+1, algorithm=self.algorithm, metric=self.metric)
            kNN.fit(X)
            neighbour = kNN.kneighbors(movie_vec, return_distance=False)
            for i in range(0,self.k):
                n = neighbour.item(i)
                neighbour_ids.append(self.movie_inv_mapper[n])
            neighbour_ids.pop(0)
            logging.info('Item-Item Collaborative Filtering Model Training Completed Successfully')
            logging.info(f'Params: k:{self.k}, metric:{self.metric}, algorithm:{self.algorithm}')
            return neighbour_ids
        except Exception as e:
            logging.error(f'Error in Model Training: {e}')
            raise e
    
    def recommend(self, movie_titles):
        try:
            similar_movie_ids = self.find_similar_movies()
            similar_movies = [movie_titles[i] for i in similar_movie_ids]
            logging.info(f'Similar Movies to {movie_titles[self.movie_id]}: {similar_movies}')
            return similar_movies
        except Exception as e:
            logging.error(f'Error in Generating Recommendations: {e}')
            raise e
