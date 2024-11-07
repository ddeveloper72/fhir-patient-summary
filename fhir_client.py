import requests
from fhirpy import SyncFHIRClient
import json
from create_patient_record import create_sample_patient_record


def upload_patient_summary():
    """Uploads a patient summary bundle to a FHIR server."""
    # patient_summary = create_sample_patient_record()

    with open('templates/sample.json', 'r') as file:
        patient_summary = file.read()

    client = SyncFHIRClient("https://hapi.fhir.org/baseR4")
    patient = client.resource("Patient", **json.loads(patient_summary))
    patient.save()





    # response = requests.post(
    #     url, headers=headers, data=patient_summary, timeout=10
    # )

    # if response.status_code == 201:
    #     print("Patient summary uploaded successfully.")
    # else:
    #     print(f"Failed to upload patient summary. Status code: {response.status_code}")
    #     print(response.text)

# search for bundle

def search_bundle():
    """Searches for a bundle with the given ID."""
    url = f"https://hapi.fhir.org/baseR4/Bundle/{bundle_id}"
    headers = {"Content-Type": "application/fhir+json"}

    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code == 200:
        print("Bundle found.")
        print(response.json())
    else:
        print(f"Bundle not found. Status code: {response.status_code}")
        print(response.text)

# search for patient
def search_patient():
    """Searches for a patient with the given ID."""
    url = f"https://hapi.fhir.org/baseR4/Parameters/{patient_id}"
    headers = {"Content-Type": "application/fhir+json"}

    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code == 200:
        print("Patient found.")
        print(response.json())
    else:
        print(f"Patient not found. Status code: {response.status_code}")
        print(response.text)


# Example usage
if __name__ == "__main__":
    # patient_id = "45107122"
    # bundle_id = "45107028"
    upload_patient_summary()
    # search_bundle()
    # search_patient()
