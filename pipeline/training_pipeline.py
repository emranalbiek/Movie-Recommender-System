import logging
import gc

from src.data_ingestion import ZipDataIngestor
from src.data_preprocessing import DataPreprocessing
from src.model_training import ModelTraining

# Setup logging Configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def training_pipeline(movie_id:int, k=10, metric='cosine', algorithm='brute'):
    try:
        # Ingest the data
        logging.info('[Ingest the data]')
        data_ingestor = ZipDataIngestor()
        file_path = r'.\data\ml-latest.zip'
        links, movies, ratings = data_ingestor.ingest(file_path)
        # Clean the data
        logging.info('[Clean the data]')
        data_preprocessor = DataPreprocessing()
        cleaned_data, X, movie_mapper, movie_inv_mapper = data_preprocessor.clean(movies, ratings, links)
        
        del movies, ratings, links, data_ingestor, data_preprocessor
        gc.collect()
        
        # Train the model
        logging.info('[Train the model]')
        model_trainer = ModelTraining(
            movie_id=movie_id,
            X=X,
            movie_mapper=movie_mapper,
            movie_inv_mapper=movie_inv_mapper,
            k=k,
            metric=metric,
            algorithm=algorithm
        )
        
        # movie_titles mapping
        movie_titles = dict(zip(cleaned_data['movieId'], cleaned_data['title']))
        
        # Get the recommendations
        recommendations = model_trainer.recommend(movie_titles)
        
        del cleaned_data, X, movie_mapper, movie_inv_mapper, movie_titles, model_trainer
        gc.collect()
        
        logging.info('Training Pipeline Completed Successfully')
        return recommendations
    except Exception as e:
        logging.error(f'Error in Training Pipeline: {e}')
        raise e