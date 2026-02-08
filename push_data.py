#ETL pipeline 
import os 
import sys 
import json 

from dotenv import load_dotenv #used for calling environment variables
load_dotenv()

#Get the environment variable
MONGO_DB_URL = os.getenv("MONGO_DB_URL")
print(MONGO_DB_URL)

#For estabilishing a trustified connection
import certifi 
ca = certifi.where() 

import numpy as np 
import pandas as pd 
import pymongo 

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging 

class NetworkDataExtract():
    def __init__(self):
        try:
            pass
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
    def csv_to_json_converter(self , file_path):
        try:
            data = pd.read_csv(file_path)
            data.reset_index(drop=True , inplace=True)
            records = list(json.loads(data.T.to_json()).values()) 
            return records
        
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def insert_data_into_mongodb(self , records , database_name , collection_name):
        try:
            #Creates a gateway to MongoDB server
            mongo_client = pymongo.MongoClient(MONGO_DB_URL)
            
            #Gives access from MongoDB server to this database
            database = mongo_client[database_name]
            
            #Gives access from database to this collection
            collection = database[collection_name]
            
            #Send these python dictionaries to MongoDB and store them
            collection.insert_many(records)
            
            return len(records)
        
        except Exception as e:
            raise NetworkSecurityException(e,sys)

if __name__ == "__main__":
    FILE_PATH = 'Network_Data\phisingData.csv'
    DATABASE = 'MANAN'
    Collection = 'NetworkData'
    networkobj = NetworkDataExtract()
    records = networkobj.csv_to_json_converter(file_path = FILE_PATH)
    print(records)
    
    no_of_records = networkobj.insert_data_into_mongodb(records , DATABASE , Collection)
    print(no_of_records)
    
    
                              