
import shutil
import time
from text_analyzer import text_analyzer_main
from analyze_output import csv_analyzer_main
from fastapi import FastAPI, UploadFile, Form, BackgroundTasks
from fastapi.responses import FileResponse
import zipfile 
import os
import io
import json


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/analyze/")
async def analyze_text(background_tasks: BackgroundTasks, api_keys: str = Form(...), csvFile: UploadFile = Form(...)):
    try:
        api_keys_dict = json.loads(api_keys)
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

        try:
            # set the csv file
            csv_file_path = await set_csv(csvFile)
        except Exception as e:
            return {"error": f"An error occurred when setting the csv file: {e}"}

        try:
            # run the text analyzer
            output_csv = text_analyzer_main( selected_endpoints=selected_endpoints, input_csv=csv_file_path)
        except Exception as e:
            return {"error": f"An error occurred when running the text analyzer: {e}"}
        try:
            # run the csv analyzer
            # TODO: change name "folder"
            folder =csv_analyzer_main(output_csv)
        except Exception as e:
            return {"error": f"An error occurred when running the csv analyzer: {e}"}
        

        try:
            # zip the output folder
            zip_file = zip_files(folder)
        except Exception as e:
            return {"error": f"An error occurred when zipping the output folder: {e}"}
        
        background_tasks.add_task(cleanup, [zip_file, folder, "./.env", csv_file_path, output_csv])
        
        return FileResponse(zip_file, media_type="application/octet-stream", filename="output.zip")
    except Exception as e:
        return {"error": f"An error occurred: {e}"}
    

def zip_files(folder: str):
    filenames = [os.path.join(root, file) for root, dirs, files in os.walk(folder) for file in files]
    zip_io = io.BytesIO()
    with zipfile.ZipFile(zip_io, mode='w', compression=zipfile.ZIP_DEFLATED) as backup_zip:
        for file in filenames:
            backup_zip.write(file, os.path.relpath(file, folder))
    zip_io.seek(0)

    zip_file_path = "./output.zip"
    with open(zip_file_path, "wb") as zip_file:
        zip_file.write(zip_io.getvalue())
    return zip_file_path

async def set_csv(csvFile: UploadFile = Form(...)):
    csv_file_path = "./csvFile.csv"
    with open(csv_file_path, "wb") as csv_file:
        csv_file.write(await csvFile.read())
    return csv_file_path
    
    
def set_env(selected_endpoints: dict):
    with open("./.env", "w") as env_file:
            for key, value in selected_endpoints.items():
                env_file.write(f"{key}='{value}'\n")
    env_file.close()
    return selected_endpoints

def cleanup(path:list):
    for file in path:
        time.sleep(2)
        if os.path.isdir(file):
            shutil.rmtree(file)
        elif os.path.exists(file):
            os.remove(file)
        else:
            print("The file does not exist")

    
