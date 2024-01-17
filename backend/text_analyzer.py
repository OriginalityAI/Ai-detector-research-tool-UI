import csv
import math
import os
import traceback
import pandas as pd
import requests
from typing import Any, Dict, List
from api_endpoints import API_ENDPOINTS
from dotenv import load_dotenv
import concurrent.futures
from task_status import shared_data
task_status = shared_data.task_status

api_progress = {}

load_dotenv()


"""
This program takes in a directory of text files and runs them through the selected APIs to determine if the text is human or AI generated.
"""


class TextAnalyzer:
    """
    class that handles the text analysis

    Parameters
    ----------
    output_csv: the output csv file to write the results to
    api_info: the API settings
    api_name: the name of the API
    writer_organization_id: the writer organization ID for the Writer.com API
    copyleaks_scan_id: the Copyleaks scan ID for the Copyleaks API

    Returns
    -------
    None
    """

    def __init__(
        self,
        output_csv: str,
        api_info: Dict[str, Dict[str, Any]],
        api_name: str,
        task_id: str,
        writer_organization_id: str = None,
        copyleaks_scan_id: str = None,
    ) -> None:
        self.output_csv = output_csv
        self.api_info = api_info
        self.api_name = api_name
        self.task_id = task_id
        self.writer_organization_id = writer_organization_id
        self.copyleaks_scan_id = copyleaks_scan_id

    def _get_endpoint(self, endpoint):
        """
        Replace the writer_organization_id and copyleaks_scan_id in the endpoint with the actual values

        Parameters
        ----------
        endpoint: the endpoint to replace the values in

        Returns
        -------
        endpoint: The endpoint with the values replaced
        """
        if "{writer_organization_id}" in endpoint:
            return endpoint.format(writer_organization_id=self.writer_organization_id)
        if "{copyleaks_scan_id}" in endpoint:
            return endpoint.format(copyleaks_scan_id=self.copyleaks_scan_id)

        return endpoint

    def _handle_data(self, data, keys):
        """
        Extract the values from the data that correspond to the keys provided

        Parameters
        ----------
        data: the data to extract the values from
        keys: the keys to extract the values for

        Returns
        -------
        row: the values extracted from the data
        """
        row = []
        try:
            # if the keys are a list, then loop through the data and extract the values that correspond to the keys
            if isinstance(keys, list):
                for item in data:
                    for key, value in item.items():
                        if key in keys:
                            row.append(value)
            else:
                # if the keys are a dictionary, then loop through the data and extract the values that correspond to the keys
                for key, value in keys.items():
                    if isinstance(data.get(key), dict):
                        row.extend(self._handle_data(data[key], value))
                    elif isinstance(data.get(key), list):
                        for sub_dict in data[key]:
                            for sub_key, sub_value in sub_dict.items():
                                if sub_key in value:
                                    row.append(sub_value)
                    else:
                        row.append(data.get(key))
            return row
        except Exception as e:
            raise Exception(f"An error occurred: {e} check the API response format in api_endpoints.py")

    def _extract_values(
        self,
        data: Dict[str, Dict[str, Any]],
        keys: Dict[str, List[str]],
    ) -> List[Any]:
        """
        Extract the values from the data that correspond to the keys provided needed to do it this way to avoid type errors
        """
        return self._handle_data(data, keys)

    def _write_error(self, text_type, row, index, response, output_csv, api_name):
        with open(output_csv, "a", newline="", encoding="UTF-8") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    text_type,
                    api_name,
                    f"{row['dataset']}-{index}",
                    "Error",
                    "Error",
                    f"Error: {response.text}",
                ]
            )

    def process_files(self, input_path, text_type, is_csv=False, selected_endpoints=None):
        """
        Main function that processes the files in the directory using the API and writes the results to the CSV file

        Parameters
        ----------
        directory: the directory to process the files in
        text_type: the type of text to process (AI or Human)

        Returns
        -------
        None
        """
        api_post = self.api_info["post_parameters"]
        api_response = self.api_info["response"]["200"]
        api_name = self.api_name
        text_key = api_post.get("text_key", "content")
        output_csv = self.output_csv
        endpoint = self._get_endpoint(api_post["endpoint"])

        if "headers" in api_post:
            headers = api_post["headers"]
        else:
            headers = {}

        body = api_post["body"]

        try:
            if is_csv:
                df = pd.read_csv(input_path)
                with open(output_csv, "a", newline="", encoding="UTF-8") as file:
                    writer = csv.writer(file)
                    writer.writerow(
                        [
                            "Text Type",
                            "API Name",
                            'id',
                            "dataset",
                            "ai_score",
                            "human_score",
                            "Error_message",
                        ]
                    )
                for index, row in df.iterrows():
                    text_type = "Human" if "human" in row["dataset"].lower() else "AI"
                    text = row["text"]
                    body[text_key] = text
                    parameters = body.copy()


                    for key, value in parameters.items():
                        if isinstance(value, float):
                            if math.isinf(value) or math.isnan(value) or value > 1.7e308:
                                print(
                                    f"⚠️  Warning: The value for {key} is not JSON compliant. Replacing with a default value."
                                )
                                parameters[key] = 0.0

                    try:
                        response = requests.post(endpoint, headers=headers, json=parameters, timeout=60)
                    except ValueError as e:
                        print(f"ValueError in API request: {e}. This could be due to invalid data types in the request body. Check the format of the data being sent.")
                        self._write_error(text_type, row, index, e, output_csv, api_name)
                        continue

                    if response.status_code != 200:
                        print(f"API request failed with status code {response.status_code}: {response.text}. Check the API endpoint, request body, and headers.")
                        self._write_error(text_type, row, index, response, output_csv, api_name)
                        continue

                    data = response.json()

                    row = [text_type, api_name, f"{row['dataset']}-{index}", row["dataset"]] + self._extract_values(
                        data, api_response
                    )

                    with open(output_csv, "a", newline="", encoding="UTF-8") as file:
                        writer = csv.writer(file)
                        writer.writerow(row)
                    with shared_data.lock:
                        api_progress[api_name] = index/len(df)*100
                    overall_progress = sum(api_progress.values())/len(api_progress)
                    task_status[self.task_id] = {**task_status[self.task_id], "progress": overall_progress}
                    print(f"Progress: {overall_progress}%")
                return output_csv
            else:
                raise Exception("Only CSV files are supported")

        except KeyError as e:
            raise KeyError(f"KeyError: '{e}' not found. Ensure the key exists in the response data or the input CSV. Check 'api_endpoints.py' for expected keys.")

    def _get_nested_value(self, dictionary, keys):
        """
        Retrieve the value from a nested dictionary using the keys provided

        Parameters
        ----------
        dictionary: the dictionary to retrieve the value from
        keys: the keys to retrieve the value for

        Returns
        -------
        dictionary: A dictionary containing the value retrieved from the nested dictionary
        """
        for key in keys:
            if isinstance(dictionary, list):
                dictionary = [
                    sub_dict.get(key, None) if isinstance(sub_dict, dict) else None for sub_dict in dictionary
                ]
            else:
                dictionary = dictionary.get(key, None)
        return dictionary


def set_headers(output_csv: str, file_type: str) -> None:
    """
    Set the initial headers for the CSV file

    Parameters
    ----------
    output_csv: the output CSV file to write the headers to

    Returns
    -------
    None
    """
    try:
        if file_type == "csv":
            init_row = [
                "Text Type",
                "API Name",
                "File Name",
                "Dataset",
                "ai_score",
                "human_score",
                "Error_message",
            ]
        else:
            init_row = [
                "Text Type",
                "API Name",
                "File Name",
                "ai_score",
                "human_score",
                "Error_message",
            ]

        with open(output_csv, "a", newline="", encoding="UTF-8") as file:
            writer = csv.writer(file)
            writer.writerow(init_row)
    except Exception as e:
        raise Exception(f"Error: Invalid output CSV file path provided. Please specify a valid file path ending in '.csv'.")


class HandleInput:
    def api_constructor(self, selected_endpoints):
        """
        Construct the API settings dictionary using the selected endpoints and API keys

        Parameters
        ----------
        selected_endpoints: the selected endpoints to use

        Returns
        -------
        api_settings: the API settings dictionary
        """
        # Initialize an empty dictionary to hold API settings
        api_settings = {}

        # Iterate over the selected endpoints
        for api_name, api_key in selected_endpoints.items():
            # Get the API's settings from the master dictionary
            api_info = API_ENDPOINTS[api_name]

            # Update the API key in the post_parameters dictionary
            key_location = api_info["post_parameters"]["API_KEY_POINTER"]["location"]
            if key_location == "headers":
                api_info["post_parameters"]["headers"][api_info["post_parameters"]["API_KEY_POINTER"]["key_name"]] = (
                    api_info["post_parameters"]["API_KEY_POINTER"]["value"] + api_key
                )
            elif key_location == "body":
                api_info["post_parameters"]["body"][api_info["post_parameters"]["API_KEY_POINTER"]["key_name"]] = (
                    api_info["post_parameters"]["API_KEY_POINTER"]["value"] + api_key
                )
            # Add the modified API info to the api_settings dictionary
            api_settings[api_name] = api_info
        return api_settings

    def handle_csv(self, input_csv, output_csv=None):
        """Handle CSV input and output.

        Validates output CSV path and sets appropriate headers
        based on input CSV.

        Parameters
        ----------
            input_csv: Path to input CSV file

        Returns
        -------
            output_csv: Path to validated output CSV
        """
        if output_csv is None:
            print("Invalid output CSV file path")
            exit(1)
        if output_csv.endswith(".csv"):
            if input_csv.endswith(".csv"):
                set_headers(output_csv, "csv")
            else:
                set_headers(output_csv, "txt")

        return output_csv, input_csv

   


def text_analyzer_main(task_id: str, selected_endpoints: list, input_csv: str = "") -> str:
    """
    main function that runs the text analyzer

    Parameters
    ----------
    None

    Returns
    -------
    output_csv: the output CSV file path
    """
    
    
    output_csv = "output.csv"
    copyleaks_scan_id = os.getenv('COPYLEAKS_SCAN_ID')
    api_settings = HandleInput().api_constructor(selected_endpoints)
    for api_name, api in api_settings.items():
        api_progress[api_name] = 0
    

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for api_name, api in api_settings.items():
            text_analyzer = TextAnalyzer(output_csv, api, api_name, task_id, copyleaks_scan_id)
            if input_csv != "":
                future = (executor.submit(text_analyzer.process_files, input_csv, "", True, selected_endpoints))
                futures.append(future)
    for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                raise Exception(f"Exception in processing: {e}. Check for issues in 'text_analyzer.process_files' method. Ensure the input data and API settings are correct.")
    
    return output_csv
