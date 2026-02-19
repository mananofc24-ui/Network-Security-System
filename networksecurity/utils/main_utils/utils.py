import yaml 
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging 
import os
import sys 
import numpy as np 
import pickle
import tempfile


def read_yaml_file(file_path: str) -> dict:
    try:
        with open(file_path, 'rb') as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e


def write_yaml_file(file_path: str, content: dict):
    try:
        file_path = os.path.normpath(file_path)
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)

        with open(file_path, "w") as yaml_file:
            yaml.dump(content, yaml_file)

        logging.info(f"Successfully wrote YAML file at {file_path}")

    except Exception as e:
        raise NetworkSecurityException(e, sys)





def save_numpy_array_data(file_path: str, array: np.array):
    '''
    Save numpy array data to file
    file_path: str location of file to save
    array: np.array data to save
    '''
    try:
        # Normalize path
        file_path = os.path.normpath(file_path)
        dir_path = os.path.dirname(file_path)
        
        try:
            # Try to create directory and save
            os.makedirs(dir_path, exist_ok=True)
            with open(file_path, "wb") as file_obj:
                np.save(file_obj, array)
            logging.info(f"Successfully saved numpy array to {file_path}")
            
        except PermissionError:
            # FALLBACK: Use temp directory if permission denied
            logging.warning(f"Permission denied for {file_path}. Using temp directory instead.")
            
            # Create a temp file
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, os.path.basename(file_path))
            
            with open(temp_file, "wb") as file_obj:
                np.save(file_obj, array)
            
            # Try to copy to original location (may still fail, but we have backup)
            try:
                os.makedirs(dir_path, exist_ok=True)
                import shutil
                shutil.copy2(temp_file, file_path)
            except:
                logging.warning(f"Could not copy to {file_path}. File saved at: {temp_file}")
            
            logging.info(f"Successfully saved numpy array to {temp_file}")
            
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e

def save_object(file_path: str, obj: object) -> None:
    try:
        logging.info('Entered the save_object method of MainUtils class')
        
        # Normalize path
        file_path = os.path.normpath(file_path)
        dir_path = os.path.dirname(file_path)
        
        try:
            # Try to create directory and save
            os.makedirs(dir_path, exist_ok=True)
            with open(file_path, "wb") as file_obj:
                pickle.dump(obj, file_obj)
            logging.info(f'Successfully saved object to {file_path}')
            
        except PermissionError:
            # FALLBACK: Use temp directory if permission denied
            logging.warning(f"Permission denied for {file_path}. Using temp directory instead.")
            
            # Create a temp file
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, os.path.basename(file_path))
            
            with open(temp_file, "wb") as file_obj:
                pickle.dump(obj, file_obj)
            
            # Try to copy to original location
            try:
                os.makedirs(dir_path, exist_ok=True)
                import shutil
                shutil.copy2(temp_file, file_path)
            except:
                
                logging.warning(f"Could not copy to {file_path}. File saved at: {temp_file}")
            
            logging.info(f'Successfully saved object to {temp_file}')
            
    except Exception as e:
        raise NetworkSecurityException(e, sys)
    
    logging.info('Exited the save_object method of MainUtils class')