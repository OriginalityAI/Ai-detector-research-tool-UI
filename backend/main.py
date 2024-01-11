from text_analyzer import text_analyzer_main
from analyze_output import csv_analyzer_main

from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['POST'])
def accept_post():
    data = request.get_json()
    return 'Success!', 200


output_csv = text_analyzer_main()
graphs = input("Would you like to generate a confusion matrix? (y/n): ")
if graphs.lower() == "y":
    try:
        csv_analyzer_main(output_csv)
        print("Done!")
    except Exception as e:
        print(f"An error occurred: {e}")
input("Press enter to exit...")
