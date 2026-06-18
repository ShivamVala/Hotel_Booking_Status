import os
import pandas 
from src.logger import  get_logger
from src.custom_exception import CustomException
import sys
import yaml 
import pandas as pd 

logger = get_logger(__name__)

def read_yaml(file_path):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"YAML file not found at path: {file_path}")
        with open(file_path, 'r') as file:
            config = yaml.safe_load(file)   
        return config
    except Exception as e:
        logger.error(f"Error reading YAML file: {e}")
        raise CustomException("Not able to read YAML config file" , sys)
    

def load_data(path):
    try:
        logger.info("Loafing Data ")
        data = pd.read_csv(path)
        logger.info("Data Loafed Successfully")
        return data
    except CustomException as e:
        logger.error(f"Error loading data: {e}")
        raise CustomException("Not able to load data", sys)