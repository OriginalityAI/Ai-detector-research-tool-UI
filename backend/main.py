from text_analyzer import text_analyzer_main
from analyze_output import csv_analyzer_main
from typing import Union
from fastapi import FastAPI, UploadFile, Form, Request
from pydantic import BaseModel
from fastapi.responses import FileResponse
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
        
        csv_file_path = "./csvFile.csv"
        with open(csv_file_path, "wb") as csv_file:
            csv_file.write(await csvFile.read())

        # now we have the api keys in the .env file remove the api keys from the selected_endpoints dict
        selected_endpoints = {key.split('_')[0]: value for key, value in selected_endpoints.items() if value}

        output_csv = text_analyzer_main( selected_endpoints=selected_endpoints, input_csv=csv_file_path)
            
        return {"status": "success", "file": csvFile.filename, "output_csv": output_csv}
    except Exception as e:
        return {"error": f"An error occurred: {e}"}
    
@app.get("/image/")
async def get_image():
    return FileResponse("/Users/jamie/Documents/Code/Originality_code/tools/Ai-detector-research-tool-Vue/backend/test.png")



# output_csv = text_analyzer_main()
# graphs = input("Would you like to generate a confusion matrix? (y/n): ")
# if graphs.lower() == "y":
#     try:
#         csv_analyzer_main(output_csv)
#         print("Done!")
#     except Exception as e:
#         print(f"An error occurred: {e}")
# input("Press enter to exit...")
