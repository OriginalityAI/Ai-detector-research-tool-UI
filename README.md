# AI Detector Research Tool

This tool allows you to test the accuracy of various AI detectors. It is a tool designed to make it easy to test a large number of detectors at the same time using the same data. - It is a GUI version of the [AI-detector-research-tool](https://github.com/OriginalityAI/AI-detector-research-tool)

## Requirements

- Docker - [Installation instructions](https://docs.docker.com/get-docker/)

## Installation

1. Clone this repository or download the zip file.

## Usage

### [Video tutorial](https://youtu.be/fUsAbRwc9Uo)

1. Navigate to the project directory in your terminal, e.g `cd user/documents/ai-detector-research-tool-UI`

2. Build the Docker images:
   `docker-compose build`

3. Start the Docker containers:
   `docker-compose up`

4. To close the tool, press `Ctrl+C` in the terminal window running the Docker container and then run the following command:
   `docker-compose down`

The tool by default will be running at `http://localhost:8080`.

## API Endpoints

- `GET /`: Returns a greeting message. - for testing purposes
- `GET /results/{task_id}`: Fetches the results of a previously submitted task.
- `POST /analyze`: Submits a new task for analysis.

## Adding detectors

To add a detector you need to do the following:

1. Find the detectors API documentation
2. Find the endpoint for the detector
3. Find the parameters required for the endpoint
4. Add the detector to the `api_endpoints.py` file in the following format:

```python
"YOUR_DETECTOR_NAME": {
    "post_parameters": {
        # The endpoint URL for the API.
        "endpoint": "YOUR_API_ENDPOINT_URL",

        # The body of the POST request. This usually contains the text to be analyzed.
        # The actual contents will depend on what the API expects.
        # Add or remove parameters as needed depending on the API requirements.
        "body": {"PARAMETER_NAME": "PARAMETER_VALUE"},

        # The headers for the POST request. This usually includes the API key and content type.
        # Add or remove headers as needed depending on the API requirements.
        "headers": {"HEADER_NAME": "HEADER_VALUE"},

        # Information about where the API key is included in the request.
        "API_KEY_POINTER": {
            # The location that the API key will end up (usually 'headers' or 'body').
            "location": "headers_or_body",

            # The actual API key. This is usually read from an environment variable or input by the user.
            "value": "LEAVE_BLANK",

            # The name of the key or field where the API key is included. e.g 'x-api-key' or 'api_key'.
            "key_name": "API_KEY_HEADER_OR_PARAMETER_NAME",
        },

        # The key in the body of the POST request where the text to be analyzed is included. e.g 'text' or 'content'.
        "text_key": "KEY_NAME_FOR_TEXT",
    },

    "response": {
        # The expected response from the API. The actual structure will depend on what the API returns.
        # This should include mappings for how to interpret the API's response.
        # Add or remove mappings as needed.
        # e.g if the API returns a JSON object with a key called 'result' and the value of 'result' is a list of objects
        # with a key called 'score' then the mapping would be:
        # "result": {
        #     "score": "score"
        # }
        "200": {
            "result": {
                "MAPPING_FOR_DESIRED_OUTPUT": "RESPONSE_KEY_PATH",
            }
        }
    },
}
```

## Links to api docs for detectors

- Originality.ai [DOCS](https://docs.originality.ai/) - to specify a particular version please check the docs and add it to the appropriate place in the `api_endpoints.py` file
- Sapling.ai [DOCS](https://sapling.ai/docs/api/detector)
- GPTZero [DOCS](https://gptzero.stoplight.io/docs/gptzero-api/d2144a785776b-ai-detection-on-single-string) - to specify a particular version please check the docs and add it to the appropriate place in the `api_endpoints.py` file
- Copyleaks [DOCS](https://api.copyleaks.com/documentation/v3) - Please follow Copyleaks instructions for setting up the API key as it is a bit more complicated than the other detectors
- Winston [DOCS](https://docs.gowinston.ai/api-reference/introduction)

## Error Handling

The tool has robust error handling. If an error occurs during the processing of a file, the tool creates a folder, writes an error log, and moves the file to the folder. The error log can be retrieved using the `/results/{task_id}` endpoint.

## License

This project is licensed under the MIT License. For more details, refer to the `LICENSE` file in the project root directory.

## Contributing

We welcome contributions! Please submit a pull request or open an issue to make improvements or fix bugs.
