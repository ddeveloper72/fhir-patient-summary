import os
import requests

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

FHIR_SERVER_URL = os.getenv("FHIR_SERVER_URL")
FHIR_FILE_OUTPUT_PATH = os.getenv("FHIR_FILE_OUTPUT_PATH")


# FHIR server endpoint
URL = FHIR_SERVER_URL

# FHIR server JSON header content
headers = {"Content-Type": "application/fhir+json;charset=utf-8"}

# Loop over all files in the output folder to upload each JSON file for each patient.
for dirpath, dirnames, files in os.walk(FHIR_FILE_OUTPUT_PATH):
    for file_name in files:
        file_path = os.path.join(dirpath, file_name)
        with open(file_path, "r", encoding="utf-8") as bundle_file:
            data = bundle_file.read()

        try:
            response = requests.post(url=URL, data=data, headers=headers, timeout=10)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

            # Confirm server receipt of the new data
            if response.status_code == 200:
                print(f"Successfully uploaded {file_name}")
            else:
                print(
                    f"Unexpected status code {response.status_code} for file {file_name}"
                )

        except requests.exceptions.RequestException as e:
            print(f"Failed to upload {file_name}: {e}")
