import os , sys 
import numpy as np 

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.entity.config_entity import ModelTrainerConfig
from networksecurity.entity.artifact_entity import ModelTrainerArtifact 
from networksecurity.entity.artifact_entity import DataTransformationArtifact

from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.utils.main_utils.utils import save_object , load_object , load_numpy_array_data

from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_score

from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier , GradientBoostingClassifier , RandomForestClassifier
import mlflow 


class ModelTrainer:
    def __init__(self , data_transformation_artifact : DataTransformationArtifact , model_trainer_config : ModelTrainerConfig):
        
        try: 
            self.data_transformation_artifact = data_transformation_artifact 
            self.model_trainer_config = model_trainer_config 
        
        except Exception as e:
            raise NetworkSecurityException(e,sys) 
    
    def track_mlflow(self , best_model , classificationmetric):
        with mlflow.start_run():
            f1_score = classificationmetric.f1_score 
            precision_score = classificationmetric.precision_score 
            recall_score = classificationmetric.recall_score 
            
            mlflow.log_metric("f1_score" , f1_score)
            mlflow.log_metric("precision_score" , precision_score)
            mlflow.log_metric("recall_score" , recall_score)
            mlflow.sklearn.log_model(best_model , "model")        
    
    
    def train_model(self , X_train , y_train , X_test , y_test):
        try: 
            models = {
                "RandomForest" : RandomForestClassifier() , 
                "DecisionTree" : DecisionTreeClassifier() , 
                "GradientBoosting" : GradientBoostingClassifier() , 
                "LogisticRegression" : LogisticRegression(max_iter = 1000) , 
                "AdaBoost" : AdaBoostClassifier()
            }        
            
            params = {
                "DecisionTree" : {
                    'criterion' : ['gini' , 'entropy'] , 
                    'max_features' : ['sqrt' , 'log2']
                } , 
                
                "RandomForest" : {
                    'n_estimators' : [100,200] , 
                    'max_features' : ['sqrt' , 'log2']
                } , 
                
                "GradientBoosting" : {
                    'learning_rate' : [0.1 , 0.01] , 
                    'n_estimators' : [100,200]
                } , 
                
                "LogisticRegression" : {} , 
                
                "AdaBoost" : {
                    'n_estimators' : [50,100] , 
                    'learning_rate' : [0.1 , 0.01]
                }
            } 
            
            best_model = None 
            best_score = -1 
            model_report = {}
            
            #Train & Select Best Model 
            for model_name , model in models.items():
                logging.info(f"Training model : {model_name}") 
                
                param_grid = params[model_name] 
                
                grid_search = GridSearchCV(
                    model , 
                    param_grid , 
                    cv = 3 , 
                    scoring = 'accuracy'
                ) 
                
                grid_search.fit(X_train , y_train) 
                
                best_estimator = grid_search.best_estimator_ 
                
                y_test_pred = best_estimator.predict(X_test) 
                test_score = accuracy_score(y_test , y_test_pred) 
                
                model_report[model_name] = test_score 
                
                if test_score > best_score:
                    best_score = test_score 
                    best_model = best_estimator 
                    
            logging.info(f"Model Report : {model_report}") 
            logging.info(f"Best Model Score : {best_score}") 
            
            
            #Final metrics 
            y_train_pred = best_model.predict(X_train) 
            y_test_pred = best_model.predict(X_test) 
            
            classification_train_metric = get_classification_score(
                y_true = y_train , 
                y_pred = y_train_pred
            )       
            
            classification_test_metric = get_classification_score(
                y_true = y_test , 
                y_pred = y_test_pred
            ) 
            
            #Track the experiments with mlflow 
            self.track_mlflow(best_model , classification_train_metric) 
            self.track_mlflow(best_model , classification_test_metric) 
            
            
            
            #Load Preprocessor 
            preprocessor = load_object(
                self.data_transformation_artifact.transformed_object_file_path
            ) 
            
            #Wrap preprocessor + trained model 
            trained_network_model = NetworkModel(
                preprocessor = preprocessor , 
                model = best_model 
            ) 
            
            #Save Model 
            model_dir_path = os.path.dirname(
                self.model_trainer_config.trained_model_file_path
            ) 
            
            os.makedirs(model_dir_path , exist_ok=True) 
            
            save_object(
                self.model_trainer_config.trained_model_file_path , trained_network_model
            ) 
            
            #Create Artifact 
            model_trainer_artifact = ModelTrainerArtifact(
                trained_model_file_path = self.model_trainer_config.trained_model_file_path , 
                train_metric_artifact = classification_train_metric , 
                test_metric_artifact = classification_test_metric
            ) 
            
            logging.info(f"Model trainer artifact : {model_trainer_artifact}") 
            
            return model_trainer_artifact 
        
        except Exception as e:
            raise NetworkSecurityException(e,sys) 
        
    
    def initiate_model_trainer(self) -> ModelTrainerArtifact:
        
        try: 
            logging.info('Starting model training process') 
            
            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path = self.data_transformation_artifact.transformed_test_file_path
            
            train_arr = load_numpy_array_data(train_file_path)
            test_arr = load_numpy_array_data(test_file_path) 
            
            X_train , y_train = train_arr[: , :-1] , train_arr[: , -1] 
            X_test , y_test = test_arr[: , :-1] , test_arr[: , -1] 
            
            model_trainer_artifact = self.train_model(
                X_train , y_train , X_test , y_test
            )  
            
            return model_trainer_artifact 
        
        except Exception as e:
            raise NetworkSecurityException(e,sys)