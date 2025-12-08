# Import Dependencies
import logging
import os
from zipfile import ZipFile
import pandas as pd
import gc

# Setup logging Configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Create Class for ZIP Ingestion
class ZipDataIngestor():
    def ingest(self, file_path:str) -> pd.DataFrame:
        """Extracts a zip file and returns the content as a pandas DataFrame"""
        try:
            # Ensure the file is a zip file
            if not file_path.endswith('.zip'):
                raise ValueError("The provided file is not a zip file")
            
            # Extract zip file
            with ZipFile(file_path, "r") as zip_ref:
                zip_ref.extractall("extracted_data")
            
            # Find extracted CSV file
            extracted_files = os.listdir(r"extracted_data\ml-latest")
            csv_files = [f for f in extracted_files if f.endswith('.csv')]
            
            # Ensure the csv_files is not empty
            if len(csv_files) == 0:
                raise FileNotFoundError("No CSV file is found in the extracted data.")
            
            links_index = csv_files.index('links.csv')
            movies_index = csv_files.index('movies.csv')
            ratings_index = csv_files.index('ratings.csv')
            
            # Read the CSV files into DataFrame
            csv_file1_path = os.path.join(r"extracted_data\ml-latest", csv_files[links_index])
            csv_file2_path = os.path.join(r"extracted_data\ml-latest", csv_files[movies_index])
            csv_file3_path = os.path.join(r"extracted_data\ml-latest", csv_files[ratings_index])
            
            links = pd.read_csv(csv_file1_path)
            movies = pd.read_csv(csv_file2_path)
            ratings = pd.read_csv(csv_file3_path)
            
            del extracted_files, csv_files, csv_file1_path, csv_file2_path, csv_file3_path, 
            links_index, movies_index, ratings_index
            gc.collect()
            
            logging.info("Data Ingestion Completed Successfully")
            # Return the dataframes
            return links, movies, ratings
        except Exception as e:
            logging.error(f"Error in Data Ingestion: {e}")
            raise e
