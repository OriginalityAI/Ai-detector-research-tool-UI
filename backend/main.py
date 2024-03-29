import asyncio
import io
import json
import os
import shutil
import time
import uuid
from text_analyzer import text_analyzer_main
from analyze_output import csv_analyzer_main
from fastapi import FastAPI, UploadFile, Form, BackgroundTasks, APIRouter
from fastapi.responses import FileResponse
import zipfile 
import os
import io
import json
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from analyze_output import csv_analyzer_main
from task_status import shared_data
from text_analyzer import text_analyzer_main

task_status = shared_data.task_status


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", 'http://localhost:5173'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """
    This function is the root endpoint of the API. 
    When accessed, it returns a simple greeting message.
    Used for testing that the API is running.

    Returns
    -------
    JSON
        A JSON object containing a greeting message.
    """
    return {"message": "Hello World"}

@app.get("/api/download/default_csv")
async def get_default_csv():
    return FileResponse("./default_csv.csv", media_type="text/csv", filename="default_csv.csv")

@app.get("/api/results/{task_id}")
async def get_results(task_id: str, background_tasks: BackgroundTasks):
    """
    This function retrieves the results of a task given its ID. If the task has failed, it returns the error log.
    If the task is still running, it returns the current status of the task.
    If the task has completed, it returns the output file and adds a cleanup task to delete the output file after it is downloaded.

    Parameters
    ----------
    task_id : str
        The ID of the task.
    background_tasks : BackgroundTasks
        The background tasks where the cleanup task will be added.

    Returns
    -------
    dict or FileResponse
        A dictionary containing the task status or an error message, or a FileResponse containing the output file or error log.
    """
    if task_status[task_id]["status"] == "failed" or (task_id not in task_status):
        if os.path.exists(f"./log/{task_id}/error_log_{task_id}.txt"):
            zipped_error_log = zip_files(f"./log/{task_id}", task_id)

            background_tasks.add_task(cleanup, [f"./log/{task_id}"])
            return FileResponse(zipped_error_log, headers={"Access-Control-Expose-Headers": "Content-Disposition","Content-Disposition": f"attachment; filename=error_log_{task_id}.zip"}, media_type="application/octet-stream", filename=f"error_log_{task_id}.zip")
        else:
            return {"task_id": task_status[task_id], "error": "No error log found", "message": "No error log found"}
            
    if (task_status[task_id]["status"] == "running"):
        return task_status[task_id]

    if os.path.exists(f"./output_{task_id}.zip"):
        background_tasks.add_task(cleanup, [f"./output_{task_id}.zip"]) # uncommenting this deletes the zip file after it is downloaded
        # uncommenting this deletes the zip file after it is downloaded
        # background_tasks.add_task(cleanup, [f"./output_{task_id}.zip"])
        return FileResponse(f"./output_{task_id}.zip", headers={"Access-Control-Expose-Headers": "Content-Disposition", "Content-Disposition": f"attachment; filename=output_{task_id}.zip"}, media_type="application/octet-stream", filename=f"output_{task_id}.zip")
    elif os.path.exists(f"./log/error_log_{task_id}.txt"):
        with open("./log/error_log.txt", "r") as f:
            return {"error": f.read()}
    else:
        return {"error": "No results found"}

@app.post("/api/analyze/")
async def analyze_text(background_tasks: BackgroundTasks, api_keys: str = Form(...), csvFile: UploadFile = Form(...)):
    """
    This function initiates the text analysis process. It first sets the CSV file to be used for the analysis,
    generates a unique task ID, and then adds the task of processing the file to the background tasks.

    Parameters
    ----------
    background_tasks : BackgroundTasks
        The background tasks where the file processing task will be added.
    api_keys : str
        The API keys in a JSON format.
    csvFile : UploadFile
        The CSV file to be used for the analysis.

    Returns
    -------
    dict
        A dictionary containing a message indicating that the analysis has started and the task ID.
    """
    try: 
        csv_file_path = await set_csv(csvFile)
    except Exception as e:
        create_failed_folder([], "setting csv", e, task_id, "Check the csv file is properly formatted and exists")
        task_status[task_id] = {"status": "failed"}
        return {"error": f"Failed to process the uploaded CSV file: {e}. Please ensure the file is correctly formatted and try uploading again."}
    try:
        task_id = str(uuid.uuid4())
        api_keys_dict = json.loads(api_keys)
        task_status[task_id] = {"status": "running", "progress": 0}
        print(task_status)
        background_tasks.add_task(process_file, api_keys_dict, csv_file_path, task_id)

        return {"message": "Analysis started", "task_id": task_id} 
    except Exception as e:
        return {"error": f"An error occurred: {e}"}
    
async def process_file(api_keys_dict: dict, csv_file_path: str, task_id: str):
    """
    This function processes the given CSV file and runs the text and CSV analyzers.

    Parameters
    ----------
    api_keys_dict : dict
        A dictionary containing the API keys.
    csv_file_path : str
        The path to the CSV file to be processed.
    task_id : str
        The ID of the task.

    Returns
    -------
    dict
        A dictionary containing the status of the task and any error messages if an error occurred.
    """
    try:
        # set the api keys in the .env file
        selected_endpoints = {}

        for key, value in api_keys_dict.items():
            if value[0]:  # Check if the endpoint is selected (boolean is True)
                selected_endpoints[key] = value[1]  # Store the API key

        try:
            # set the api keys in the .env file
            selected_endpoints = set_env(selected_endpoints)
        except Exception as e:
            return {"error": f"Error setting API keys in the environment: {e}. Please check the API key format and ensure they are valid."}
        
        # now we have the api keys in the .env file remove the api keys from the selected_endpoints dict
        if "COPYLEAKS_SCAN_ID" in selected_endpoints:
            del selected_endpoints["COPYLEAKS_SCAN_ID"]

        selected_endpoints = {key.split('_')[0]: value for key, value in selected_endpoints.items() if value}


        try:
            # run the text analyzer
            output_csv = await asyncio.to_thread(text_analyzer_main, task_id,selected_endpoints=selected_endpoints, input_csv=csv_file_path)
        except Exception as e:
            create_failed_folder([csv_file_path], "text analyzer", e, task_id)
            task_status[task_id]["status"] = "failed"
            return {"error": f"Failed to execute text analysis: {e}. Ensure the text analyzer is correctly configured and the input CSV is properly formatted."}
        

        try:
            # run the csv analyzer
            output_folder = csv_analyzer_main(output_csv, task_id)
        except Exception as e:
            create_failed_folder([csv_file_path, output_csv], "csv analyzer", e, task_id)
            task_status[task_id]["status"] = "failed"
            return {"error": f"Error during CSV analysis: {e}. Check the CSV analyzer's configuration and input data."}
        

        try:
            # zip the output folder
            zip_files(output_folder, task_id)
        except Exception as e:
            create_failed_folder([output_folder,csv_file_path, output_csv], "zipping", e, task_id)
            task_status[task_id]["status"] = "failed"
            return {"error": f"Failed to zip output folder: {e}. Ensure the folder exists and has accessible content."}
        

        task_status[task_id]["status"] = "complete"
        cleanup([output_folder, "./.env", csv_file_path, output_csv]) 
    except Exception as e:
        create_failed_folder([csv_file_path, output_csv], "failed", e, task_id)
        task_status[task_id]["status"] = "failed"
        return {"error": f"An error occurred: {e}"}
    
        

    

def zip_files(folder: str, task_id: str):
    """
    Create a zip file from the contents of a folder.

    Parameters
    ----------
    folder : str
        The path to the folder that needs to be zipped.
    task_id : str
        The id of the task for which the folder is being zipped.

    Returns
    -------
    None
    """
    filenames = [os.path.join(root, file) for root, dirs, files in os.walk(folder) for file in files]
    zip_io = io.BytesIO()
    with zipfile.ZipFile(zip_io, mode='w', compression=zipfile.ZIP_DEFLATED) as backup_zip:
        for file in filenames:
            backup_zip.write(file, os.path.relpath(file, folder))
    zip_io.seek(0)

    zip_file_path = f"./output_{task_id}.zip"
    with open(zip_file_path, "wb") as zip_file:
        zip_file.write(zip_io.getvalue())
    return zip_file_path

async def set_csv(csvFile: UploadFile = Form(...)):
    """
    Set the csv file to be used for the analysis.

    Parameters
    ----------
    csvFile : UploadFile
        The csv file to be used for the analysis.

    Returns
    -------
    csv_file_path : str
        The path to the csv file that has been set for the analysis.
    """
    csv_file_path = "./csvFile.csv"
    try:
        with open(csv_file_path, "wb") as csv_file:
            csv_file.write(await csvFile.read())
        return csv_file_path
    except Exception as e:
        raise Exception(f"An error occurred when setting the csv file: {e}")

def create_failed_folder(files: list, location: str, e: Exception, task_id: str, custom_message: str = None):
    """
    Create a folder to store the files from a failed task.

    Parameters
    ----------
    files : list
        The list of files to be moved to the log folder.
    location : str
        The location where the error occurred.
    e : Exception
        The exception that was raised.
    task_id : str
        The id of the task that failed.
    custom_message : str, optional
        A custom message to be written to the error log, by default None

    Raises
    ------
    Exception
        If an error occurs while creating the log folder.
    """
    try:
        os.makedirs("log", exist_ok=True)
        os.makedirs(f"./log/{task_id}", exist_ok=True)
        with open(f"./log/{task_id}/error_log_{task_id}.txt", "w") as f:
            f.write(f"An error occurred at the following location: {location}\nerror: {e}\nmessage: {custom_message}")
        for file in files:
            shutil.move(file, f"./log/{task_id}")
        f.close()
    except Exception as e:
        raise Exception(f"Error creating log folder for failed task: {e}. Check file system permissions and available storage.")
    
    
def set_env(selected_endpoints: dict):
    """
    Set the API keys in the .env file.

    This function takes a dictionary of selected endpoints and writes them to the .env file.
    Each key-value pair in the dictionary is written as a separate line in the .env file.

    Parameters
    ----------
    selected_endpoints : dict
        A dictionary where the keys are the names of the endpoints and the values are the corresponding API keys.

    Returns
    -------
    selected_endpoints : dict
        The same dictionary that was passed as an argument.

    Raises
    ------
    Exception
        If there was an error writing to the .env file, an exception is raised with a message indicating the error.
    """
    try:
        with open("./.env", "w") as env_file:
            for key, value in selected_endpoints.items():
                env_file.write(f"{key}='{value}'\n")
        return selected_endpoints
    except Exception as e:
        raise Exception(f"Failed to write API keys to the .env file: {e}. Ensure the file path is correct and writable.")

def cleanup(path:list):
    """
    Cleans up the specified files or directories.

    Parameters
    ----------
    path : list
        The list of file or directory paths to be cleaned up.

    This function will wait for 2 seconds before attempting to delete each file or directory.
    If the path is a directory, it will be removed along with all its contents.
    If the path is a file, the file will be removed.
    If the path does not exist, a message will be printed to the console.
    """
    for file in path:
        time.sleep(2)
        if os.path.isdir(file):
            shutil.rmtree(file)
        elif os.path.exists(file):
            os.remove(file)
        else:
            print("The file does not exist")

    
