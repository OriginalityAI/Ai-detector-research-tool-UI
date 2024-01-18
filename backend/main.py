
import asyncio
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
from task_status import shared_data
task_status = shared_data.task_status


app = FastAPI()
router = APIRouter(prefix='/api')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", 'http://localhost:5173'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




@router.get("/")
async def root():
    return {"message": "Hello World"}

@router.get("/download/default_csv")
async def get_default_csv():
    return FileResponse("./default_csv.csv", media_type="text/csv", filename="default_csv.csv")

@router.get("/results/{task_id}")
async def get_results(task_id: str, background_tasks: BackgroundTasks):
    if task_status[task_id]["status"] == "failed" or (task_id not in task_status):
        if os.path.exists(f"./log/{task_id}/error_log_{task_id}.txt"):
            zipped_error_log = zip_files(f"./log/{task_id}", task_id)
            return FileResponse(zipped_error_log, headers={"Access-Control-Expose-Headers": "Content-Disposition","Content-Disposition": f"attachment; filename=error_log_{task_id}.zip"}, media_type="application/octet-stream", filename=f"error_log_{task_id}.zip")
        else:
            return {"task_id": task_status[task_id], "error": "No error log found", "message": "No error log found"}
            
    if (task_status[task_id]["status"] == "running"):
        return {**task_status}

    if os.path.exists(f"./output_{task_id}.zip"):
        # uncommenting this deletes the zip file after it is downloaded
        # background_tasks.add_task(cleanup, [f"./output_{task_id}.zip"])
        return FileResponse(f"./output_{task_id}.zip", headers={"Access-Control-Expose-Headers": "Content-Disposition", "Content-Disposition": f"attachment; filename=output_{task_id}.zip"}, media_type="application/octet-stream", filename=f"output_{task_id}.zip")
    elif os.path.exists(f"./log/error_log_{task_id}.txt"):
        with open("./log/error_log.txt", "r") as f:
            return {"error": f.read()}
    else:
        return {"error": "No results found"}

@router.post("/analyze/")
async def analyze_text(background_tasks: BackgroundTasks, api_keys: str = Form(...), csvFile: UploadFile = Form(...)):
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
        raise Exception(f"Error creating log folder for failed task: {e}. Check file system permissions and available storage.")
    
    
def set_env(selected_endpoints: dict):
    try:
        with open("./.env", "w") as env_file:
                for key, value in selected_endpoints.items():
                    env_file.write(f"{key}='{value}'\n")
        return selected_endpoints
    except Exception as e:
        raise Exception(f"AFailed to write API keys to the .env file: {e}. Ensure the file path is correct and writable.")

def cleanup(path:list):
    for file in path:
        time.sleep(2)
        if os.path.isdir(file):
            shutil.rmtree(file)
        elif os.path.exists(file):
            os.remove(file)
        else:
            print("The file does not exist")

    
