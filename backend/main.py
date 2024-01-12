
from text_analyzer import text_analyzer_main
from analyze_output import csv_analyzer_main
from typing import Union
from fastapi import FastAPI, UploadFile, Form, Request
from pydantic import BaseModel
from fastapi.responses import FileResponse
import zipfile 
import os
import io
from pathlib import Path
import json

app = FastAPI()

@app.post("/analyze/")
async def analyze_text(api_keys: str = Form(...), csvFile: UploadFile = Form(...)):
    try:
        api_keys_dict = json.loads(api_keys)
        selected_endpoints = {}

        for key, value in api_keys_dict.items():
            if value[0]:  # Check if the endpoint is selected (boolean is True)
                selected_endpoints[key] = value[1]  # Store the API key

        with open("./.env", "w") as env_file:
            for key, value in selected_endpoints.items():
                env_file.write(f"{key}='{value}'\n")
        env_file.close()

        csv_file_path = "./csvFile.csv"
        with open(csv_file_path, "wb") as csv_file:
            csv_file.write(await csvFile.read())

        # now we have the api keys in the .env file remove the api keys from the selected_endpoints dict
        selected_endpoints = {key.split('_')[0]: value for key, value in selected_endpoints.items() if value}
        output_csv = text_analyzer_main( selected_endpoints=selected_endpoints, input_csv=csv_file_path)
        csv_analyzer_main(output_csv)


        zip_file = zip_files()
        return FileResponse(zip_file, media_type="application/octet-stream", filename="output.zip")
        # return {"status": "success", "file": csvFile.filename, "output_csv": output_csv}
    except Exception as e:
        return {"error": f"An error occurred: {e}"}
    

def zip_files():
    zip_sub_dir = 'output/'
    filenames = [os.path.join(root, file) for root, dirs, files in os.walk(zip_sub_dir) for file in files]
    zip_io = io.BytesIO()
    with zipfile.ZipFile(zip_io, mode='w', compression=zipfile.ZIP_DEFLATED) as backup_zip:
        for file in filenames:
            print(file)
            backup_zip.write(file, os.path.relpath(file, zip_sub_dir))
    zip_io.seek(0)

    zip_file_path = "./output.zip"
    with open(zip_file_path, "wb") as zip_file:
        zip_file.write(zip_io.getvalue())
    return zip_file_path
    


# output_csv = text_analyzer_main()
# graphs = input("Would you like to generate a confusion matrix? (y/n): ")
# if graphs.lower() == "y":
#     try:
#         csv_analyzer_main(output_csv)
#         print("Done!")
#     except Exception as e:
#         print(f"An error occurred: {e}")
# input("Press enter to exit...")
