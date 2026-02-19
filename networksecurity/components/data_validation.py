from networksecurity.logging.logger import logging
from networksecurity.exception.exception import NetworkSecurityException

from networksecurity.entity.artifact_entity import (
    DataIngestionArtifact,
    DataValidationArtifact
)
from networksecurity.entity.config_entity import DataValidationConfig
from networksecurity.constant.training_pipeline import SCHEMA_FILE_PATH
from networksecurity.utils.main_utils.utils import read_yaml_file, write_yaml_file

import os
import sys
from scipy.stats import ks_2samp
import pandas as pd


class DataValidation:

    def __init__(
        self,
        data_ingestion_artifact: DataIngestionArtifact,
        data_validation_config: DataValidationConfig
    ):
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self.schema_config = read_yaml_file(SCHEMA_FILE_PATH)

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    # ---------------------------------------------------
    # Read CSV
    # ---------------------------------------------------
    @staticmethod
    def read_data(file_path) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    # ---------------------------------------------------
    # Validate Column Count
    # ---------------------------------------------------
    def validate_number_of_columns(self, dataframe: pd.DataFrame) -> bool:
        try:
            expected_columns = len(self.schema_config['columns'])
            actual_columns = len(dataframe.columns)

            logging.info(f"Expected columns: {expected_columns}")
            logging.info(f"Actual columns: {actual_columns}")

            return expected_columns == actual_columns

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    # ---------------------------------------------------
    # Validate Numerical Columns Exist
    # ---------------------------------------------------
    def validate_numerical_columns_exist(self, dataframe: pd.DataFrame) -> bool:
        try:
            numerical_columns = self.schema_config['numerical_columns']

            missing_columns = [
                col for col in numerical_columns
                if col not in dataframe.columns
            ]

            if missing_columns:
                logging.error(f"Missing numerical columns: {missing_columns}")
                return False

            return True

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    # ---------------------------------------------------
    # Detect Data Drift
    # ---------------------------------------------------
    def detect_dataset_drift(
        self,
        base_df: pd.DataFrame,
        current_df: pd.DataFrame,
        threshold: float = 0.05
    ) -> bool:
        try:
            status = True
            report = {}

            for column in base_df.columns:

                d1 = base_df[column]
                d2 = current_df[column]

                ks_test = ks_2samp(d1, d2)

                drift_found = ks_test.pvalue < threshold

                if drift_found:
                    status = False

                report[column] = {
                    "p_value": float(ks_test.pvalue),
                    "drift_status": drift_found
                }

            drift_report_path = self.data_validation_config.drift_report_file_path
            write_yaml_file(drift_report_path, report)

            return status

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    # ---------------------------------------------------
    # Main Entry Point
    # ---------------------------------------------------
    def initiate_data_validation(self) -> DataValidationArtifact:
        try:
            # Get file paths
            train_path = self.data_ingestion_artifact.trained_file_path
            test_path = self.data_ingestion_artifact.test_file_path

            # Read data
            train_df = self.read_data(train_path)
            test_df = self.read_data(test_path)

            # Validate number of columns
            if not self.validate_number_of_columns(train_df):
                raise Exception("Train dataframe has incorrect number of columns.")

            if not self.validate_number_of_columns(test_df):
                raise Exception("Test dataframe has incorrect number of columns.")

            # Validate numerical columns
            if not self.validate_numerical_columns_exist(train_df):
                raise Exception("Train dataframe missing numerical columns.")

            if not self.validate_numerical_columns_exist(test_df):
                raise Exception("Test dataframe missing numerical columns.")

            # Detect drift
            drift_status = self.detect_dataset_drift(train_df, test_df)

            # Create validated directory
            os.makedirs(
                os.path.dirname(self.data_validation_config.valid_train_file_path),
                exist_ok=True
            )

            # Save validated files
            train_df.to_csv(
                self.data_validation_config.valid_train_file_path,
                index=False
            )

            test_df.to_csv(
                self.data_validation_config.valid_test_file_path,
                index=False
            )

            # Create artifact
            data_validation_artifact = DataValidationArtifact(
                validation_status=drift_status,
                valid_train_file_path=self.data_validation_config.valid_train_file_path,
                valid_test_file_path=self.data_validation_config.valid_test_file_path,
                invalid_train_file_path=None,
                invalid_test_file_path=None,
                drift_report_file_path=self.data_validation_config.drift_report_file_path
            )

            return data_validation_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)
