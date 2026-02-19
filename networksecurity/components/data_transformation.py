import sys , os 
import numpy as np 
import pandas as pd 
from sklearn.pipeline import Pipeline
from sklearn.impute import KNNImputer

from networksecurity.constant.training_pipeline import TARGET_COLUMN
from networksecurity.constant.training_pipeline import DATA_TRANSFORMATION_INMPUTER_PARAMS

from networksecurity.entity.artifact_entity import DataValidationArtifact , DataTransformationArtifact
from networksecurity.entity.config_entity import DataTransformationConfig

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.utils.main_utils.utils import save_numpy_array_data , save_object , read_yaml_file


class DataTransformation:
    def __init__(self , data_validation_artifact : DataValidationArtifact , 
                 data_transformation_config : DataTransformationConfig):
        
        try:
            self.data_validation_artifact = data_validation_artifact
            self.data_transformation_config = data_transformation_config
            
        except Exception as e:
            raise NetworkSecurityException(e,sys) 
        
    
    @staticmethod
    def read_data(file_path)-> pd.DataFrame:
        try:
            return pd.read_csv(file_path) 
        except Exception as e:
            raise NetworkSecurityException(e,sys) 
        
    
    def get_data_transformer_object(cls)->Pipeline:
        '''
        It initialises a KNNImputer object with the parameters specified in the training_pipeline.py
        and returns a Pipeline object with the KNNImputer object as the first step . 
        '''
        logging.info('Entered data_transformer_object method of Transformation class')
        
        try:
            imputer = KNNImputer(**DATA_TRANSFORMATION_INMPUTER_PARAMS)
            logging.info(f"Initialise KNNImputer with {DATA_TRANSFORMATION_INMPUTER_PARAMS}")
            
            preprocessor = Pipeline([
                ('imputer' , imputer)
            ])
            
            return preprocessor 
        
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
    
    
    def initiate_data_transformation(self)->DataTransformationArtifact:
        logging.info('Entered initiate_data_transformation method of DataTransformation')
        
        try:
            logging.info('Starting data transformation')
            
            train_df = DataTransformation.read_data(self.data_validation_artifact.valid_train_file_path)
            test_df = DataTransformation.read_data(self.data_validation_artifact.valid_test_file_path)
            
            
            #Training data independent & dependent features
            input_feature_train_df = train_df.drop(columns = [TARGET_COLUMN])
            output_feature_train_df = train_df[TARGET_COLUMN] 
            output_feature_train_df = output_feature_train_df.replace(-1 , 0) #we need 0 and 1 as output 
            
            #Testing data independent & dependent features
            input_feature_test_df = test_df.drop(columns = [TARGET_COLUMN])
            output_feature_test_df = test_df[TARGET_COLUMN]
            output_feature_test_df = output_feature_test_df.replace(-1 , 0)
            
            
            #KNN Imputer 
            preprocessor = self.get_data_transformer_object() 
            
            preprocessor_object = preprocessor.fit(input_feature_train_df)
            transformed_input_train_feature = preprocessor_object.transform(input_feature_train_df) #array
            transformed_input_test_feature = preprocessor_object.transform(input_feature_test_df)   #array
           
           #Combine transformed input array with target column 
            train_arr = np.c_[transformed_input_train_feature , np.array(output_feature_train_df)]
            test_arr = np.c_[transformed_input_test_feature , np.array(output_feature_test_df)]
            
            #Save numpy array data 
            save_numpy_array_data(self.data_transformation_config.transformed_train_file_path , train_arr)
            save_numpy_array_data(self.data_transformation_config.transformed_test_file_path , test_arr)
            
            save_object(self.data_transformation_config.transformed_object_file_path , preprocessor_object)
            
            
            data_transformation_artifact = DataTransformationArtifact(
                transformed_object_file_path = self.data_transformation_config.transformed_object_file_path , 
                transformed_train_file_path = self.data_transformation_config.transformed_train_file_path , 
                transformed_test_file_path = self.data_transformation_config.transformed_test_file_path
            )
            
            return data_transformation_artifact
        
        except Exception as e:
            raise NetworkSecurityException(e,sys)        
    
