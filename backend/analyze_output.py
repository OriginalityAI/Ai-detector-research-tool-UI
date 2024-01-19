import os
import shutil
import matplotlib


import matplotlib.pyplot as plt
matplotlib.use('agg')
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
import uuid


class AnalyzeOutput:
    """
    A class to analyze the output CSV file from the text analysis tool.
    Generates confusion matrix and classification metrics for each API.

    Parameters
    ----------
    output_csv: the output csv file to analyze

    Returns
    -------
    None
    """

    THRESHOLD = 0.5

    def __init__(self, output_csv: str):
        self.output_csv = output_csv

    def _read_and_sanitize(self, csv_file: str):
        """
        Read and sanitize the data
        """
        try:
            df = pd.read_csv(csv_file)
            df = df[pd.isnull(df["Error_message"])]
            df = df[~(df["ai_score"] == "Error")]
            df = df.reset_index(drop=True)
            return df
        except KeyError as e:
            raise Exception(f"KKeyError: Missing expected column '{e}'. Please ensure your CSV file includes the necessary columns.")
        except Exception as e:
            raise Exception(f"Unexpected error occurred while reading CSV file: {e}. Please check the CSV file for correct formatting and data integrity.")

    def _calculate_labels(self, df: pd.DataFrame):
        """
        Calculate the labels for the confusion matrix

        Parameters
        ----------
        df: the dataframe to analyze

        Returns
        -------
        y_true: the true labels
        y_pred: the predicted labels
        """
        y_true = [1 if "ai" in tt.lower() else 0 for tt in df["Text Type"]]
        y_pred = [1 if float(score) > self.THRESHOLD else 0 for score in df["ai_score"]] # add or score == False for WINSTON

        return y_true, y_pred

    def confusion_matrix(self, csv_file: str):
        """
        Calculate the confusion matrix

        Parameters
        ----------
        csv_file: the csv file to analyze

        Returns
        -------
        None
        """
        df = self._read_and_sanitize(csv_file)
        API = df["API Name"]

        y_true, y_pred = self._calculate_labels(df)

        cm = confusion_matrix(y_true, y_pred, labels=[1, 0])

        self._visualize_confusion_matrix(cm, API[0], y_true)

    def _unique_apis(self):
        """
        Get the unique APIs from the output csv

        Returns
        -------
        unique_apis: a list of unique API names
        """
        df = self._read_and_sanitize(self.output_csv)

        grouped = df.groupby("API Name")
        unique_apis = grouped["API Name"].unique()
        for name, group in grouped:
            group.to_csv(f"{name}.csv", index=False)
        return unique_apis

    def _matrix_1x2(self, cm):
        try:
            if cm[0].sum() == 0:
                cm = np.delete(cm, 0, 0)
            elif cm[1].sum() == 0:
                cm = np.delete(cm, 1, 0)
            return cm
        except Exception as e:
            print(f"Error deleting rows from the confusion matrix to make it 1x2: {e}")
            return cm

    def _get_visual_labels(self, cm, y_true):
        """
        Get the labels for the confusion matrix based on the number of classes

        Parameters
        ----------
        cm: the confusion matrix
            y_true: the true labels

        Returns
        -------
        df_cm: the confusion matrix as a dataframe
        df_labels: the labels for the confusion matrix as a dataframe
        """
        # if the sum of the first row is 0, delete the first row to make the matrix 1x2
        cm = self._matrix_1x2(cm)
        # Recalculate the row-wise sum after deleting rows
        cm_sum = np.sum(cm, axis=1)

        #  Calculate the percentage of each cell + add a small number to avoid division by 0
        cm_perc = (cm / (cm_sum[:, None] + 1e-10)) * 100
        try:
            if cm.shape == (1, 2):
                # If there's only one class in the predictions, adjust labels and data accordingly
                single_class = "AI Generated" if y_true[0] == 1 else "Human Written"
                columns = ["AI Generated", "Human Written"] if y_true[0] == 1 else ["Human Written", "AI Generated"]
                labels = [f"{cm_perc[0, 0]:.1f}%", f"{cm_perc[0, 1]:.1f}%"]
                labels = np.asarray(labels).reshape(1, 2)
                if y_true[0] == 0:
                    labels = np.flip(labels, axis=1)

                df_cm = pd.DataFrame(cm, columns=columns, index=[single_class])
                df_labels = pd.DataFrame(
                    labels,
                    columns=columns,
                    index=[single_class],
                )
            else:
                # If there are two classes, the confusion matrix will be 2x2
                labels = [
                    f"{cm_perc[0, 0]:.1f}%",
                    f"{cm_perc[0, 1]:.1f}%",
                    f"{cm_perc[1, 0]:.1f}%",
                    f"{cm_perc[1, 1]:.1f}%",
                ]
                labels = np.asarray(labels).reshape(2, 2)
                df_cm = pd.DataFrame(
                    cm,
                    columns=["AI Generated", "Human Written"],
                    index=["AI Generated", "Human Written"],
                )
                df_labels = pd.DataFrame(
                    labels,
                    columns=["AI Generated", "Human Written"],
                    index=["AI Generated", "Human Written"],
                )
            return df_cm, df_labels
        except Exception as e:
            raise Exception(f"Error in calculating labels for the confusion matrix: {e}. Ensure the matrix dimensions are correct and data is valid.")

    def _visualize_confusion_matrix(self, cm, api_name: str, y_true):
        """
        Visualize the confusion matrix

        Parameters
        ----------
        cm: the confusion matrix
        api_name: the name of the API
        y_true: the true labels

        Returns
        -------
        df_cm: the confusion matrix as a dataframe
            df_labels: the labels for the confusion matrix as a dataframe
        """
        df_cm, df_labels = self._get_visual_labels(cm, y_true)
        try:
            # Visualize the confusion matrix
            plt.figure(figsize=(10, 7))
            plt.rcParams["font.size"] = 23
            sns.heatmap(
                df_cm,
                annot=df_labels,
                fmt="",
                annot_kws={"size": 23},
            )
            plt.xlabel("Predicted")
            plt.ylabel("Actual")
            plt.savefig(f"{api_name}_confusion_matrix.png")
            return df_cm, df_labels
        except:
            raise Exception(
                f"Failed to visualize confusion matrix due to incorrect dimensions (current shape: {cm.shape}). Matrix must be 2x2 or 1x2."
            )

    def generate_stats(self, csv_file: str):
        """
        Write the true positive rate, true negative rate, and F1 score to a text file

        Parameters
        ----------
        csv_file: the csv file to analyze

        Returns
        -------
        None

        Writes
        ------
        F1 score
        Precision
        Recall (True Positive Rate)
        Specificity (True Negative Rate)
        False Positive Rate
        Accuracy
        Classification Report
        """
        df = self._read_and_sanitize(csv_file)
        API = df["API Name"][0]

        y_true, y_pred = self._calculate_labels(df)
        cm = confusion_matrix(y_true, y_pred, labels=[1, 0])

        try:
            precision = precision_score(y_true, y_pred, zero_division=0)
            recall = recall_score(y_true, y_pred, zero_division=0)
            f1 = f1_score(y_true, y_pred, zero_division=0)
            accuracy = accuracy_score(y_true, y_pred)

            tnr = cm[1][1] / (cm[1][0] + cm[1][1] + 1e-10)
            fp_rate = cm[1][0] / (cm[1][0] + cm[1][1] + 1e-10)

            output_string = (
                f"F1 score: {f1}\n"
                f"Precision: {precision}\n"
                f"Recall: {recall}\n"
                f"Specificity: {tnr}\n"
                f"False Positive Rate: {fp_rate}\n"
                f"Accuracy: {accuracy}\n"
            )

            with open(f"{API}_true_rates.txt", "a") as f:
                f.write(output_string)
        except Exception as e:
            raise Exception(f"Failed to calculate performance metrics (precision, recall, F1, etc.). Ensure y_true and y_pred contain valid data: {e}")



def csv_analyzer_main(csv_file: str, task_id: str):
    """
    Main function and entry point for the csv analyzer

    Parameters
    ----------
    csv_file: the csv file to analyze

    Returns
    -------
    None

    Raises
    ------
    FileNotFoundError: if the file is not found
    ValueError: if the file is empty or not a csv file
    """
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"FileNotFoundError: The file '{csv_file}' does not exist. Please provide a valid file path.")
    if not csv_file.endswith(".csv"):
        raise ValueError(f"ValueError: The file '{csv_file}' is not a CSV file. Please provide a file with the .csv extension.")
    if os.stat(csv_file).st_size == 0:
        raise ValueError(f"ValueError: The file '{csv_file}' is empty. Please provide a CSV file with data.")

    output_analyzer = AnalyzeOutput(csv_file)
    unique_apis = output_analyzer._unique_apis()
    folder = f"output_{task_id}/"
    for API in unique_apis:
        api_with_filetype = API[0] + ".csv"
        output_analyzer.confusion_matrix(api_with_filetype)
        output_analyzer.generate_stats(api_with_filetype)
        folder = file_cleanup(API[0], folder)
    return folder


def file_cleanup(api_name: str, folder: str):
    """
    Move the csv files into a folder called output, one for each API

    Parameters
    ----------
    api_name: the name of the API

    Returns
    -------
    None

    """
    api_folder = os.path.join(folder, api_name)
    os.makedirs(api_folder, exist_ok=True)
    for filename in os.listdir():
        if api_name in filename:
            shutil.move(filename, os.path.join(api_folder, filename))
    return folder
