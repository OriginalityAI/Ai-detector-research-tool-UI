
import asyncio
import shutil
import time
import uuid
from text_analyzer import text_analyzer_main, task_status
from analyze_output import csv_analyzer_main
from fastapi import FastAPI, UploadFile, Form, BackgroundTasks
from fastapi.responses import FileResponse
import zipfile 
import os
import io
import json
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

task_status = {}

@app.get("/results/{task_id}")
async def get_results(task_id: str, background_tasks: BackgroundTasks):
    if task_status[task_id] == "failed" or (task_id not in task_status):
        if os.path.exists(f"./log/error_log_{task_id}.txt"):
            with open(f"./log/error_log_{task_id}.txt", "r") as f:
                return {"task_id": task_id, "status": "failed", "error": f.read(), "message": f"for a full log go to ./log/error_log_{task_id}.txt"}
        else:
            return {"task_id": task_id, "status": "failed", "error": "No error log found", "message": "No error log found"}
            
    if (task_status[task_id] == "running"):
        return {**task_status}

    if os.path.exists(f"./output_{task_id}.zip"):
        # uncommenting this deletes the zip file after it is downloaded
        # background_tasks.add_task(cleanup, [f"./output_{task_id}.zip"])
        return FileResponse(f"./output_{task_id}.zip", media_type="application/octet-stream", filename=f"output_{task_id}.zip")
    elif os.path.exists(f"./log/error_log_{task_id}.txt"):
        with open("./log/error_log.txt", "r") as f:
            return {"error": f.read()}
    else:
        return {"error": "No results found"}

@app.post("/analyze/")
async def analyze_text(background_tasks: BackgroundTasks, api_keys: str = Form(...), csvFile: UploadFile = Form(...)):
    try:
        task_id = str(uuid.uuid4())
        api_keys_dict = json.loads(api_keys)
        task_status[task_id] = "running"
        background_tasks.add_task(process_file, api_keys_dict, csvFile, task_id)

        return {"message": "Analysis started", "task_id": task_id} 
    except Exception as e:
        return {"error": f"An error occurred: {e}"}
    
async def process_file(api_keys_dict: dict, csvFile: UploadFile, task_id: str):
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
            return {"error": f"An error occurred when setting the api keys in the .env file: {e}"}
        
        # now we have the api keys in the .env file remove the api keys from the selected_endpoints dict
        selected_endpoints = {key.split('_')[0]: value for key, value in selected_endpoints.items() if value}
        time.sleep(2)
        try:
            # set the csv file
            csv_file_path = await set_csv(csvFile)
        except Exception as e:
            create_failed_folder([], "setting csv", e, task_id, "Check the csv file is properly formatted and exists")
            task_status[task_id] = "failed"
            return {"error": f"An error occurred when setting the csv file: {e}"}
        time.sleep(2)


        try:
            # run the text analyzer
            output_csv = await asyncio.to_thread(text_analyzer_main, task_id,selected_endpoints=selected_endpoints, input_csv=csv_file_path)

        except Exception as e:
            create_failed_folder([csv_file_path], "text analyzer", e, task_id)
            task_status[task_id] = "failed"
            return {"error": f"An error occurred when running the text analyzer: {e}"}
        

        try:
            # run the csv analyzer
            output_folder = await asyncio.to_thread(csv_analyzer_main, output_csv, task_id)
        except Exception as e:

            create_failed_folder([csv_file_path, output_csv], "csv analyzer", e, task_id)
            task_status[task_id] = "failed"
            return {"error": f"An error occurred when running the csv analyzer: {e}"}
        

        try:
            # zip the output folder
            zip_files(output_folder, task_id)
        except Exception as e:
            create_failed_folder([output_folder,csv_file_path, output_csv], "zipping", e, task_id)
            task_status[task_id] = "failed"
            return {"error": f"An error occurred when zipping the output folder: {e}"}
        

        task_status[task_id] = "complete"
        cleanup([output_folder, "./.env", csv_file_path, output_csv])
    except Exception as e:
        create_failed_folder([csv_file_path, output_csv], "failed", e, task_id)
        task_status[task_id] = "failed"
        return {"error": f"An error occurred: {e}"}
    
        

    

def zip_files(folder: str, task_id: str):
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
    csv_file_path = "./csvFile.csv"
    try:
        with open(csv_file_path, "wb") as csv_file:
            csv_file.write(await csvFile.read())
        return csv_file_path
    except Exception as e:
        raise Exception(f"An error occurred when setting the csv file: {e}")

def create_failed_folder(files: list, location: str, e: Exception, task_id: str, custom_message: str = None):
    try:
        os.makedirs("log", exist_ok=True)
        os.makedirs(f"./log/{task_id}", exist_ok=True)
        with open(f"./log/{task_id}/error_log_{task_id}.txt", "w") as f:
            f.write(f"An error occurred at the following location: {location}\nerror: {e}\nmessage: {custom_message}")
        for file in files:
            shutil.move(file, f"./log/{task_id}")
        f.close()
    except Exception as e:
        raise Exception(f"An error occurred when creating the failed folder: {e}")
    
    
def set_env(selected_endpoints: dict):
    try:
        with open("./.env", "w") as env_file:
                for key, value in selected_endpoints.items():
                    env_file.write(f"{key}='{value}'\n")
        env_file.close()
        return selected_endpoints
    except Exception as e:
        raise Exception(f"An error occurred when setting the api keys in the .env file: {e}")

def cleanup(path:list):
    for file in path:
        time.sleep(2)
        if os.path.isdir(file):
            shutil.rmtree(file)
        elif os.path.exists(file):
            os.remove(file)
        else:
            print("The file does not exist")

    
