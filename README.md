# FHIR Patient Summary Application

The live site is on Heroku at https://ddeveloper72-fhir-app-2d30b05e8d2c.herokuapp.com/

## Purpose

The FHIR Patient Summary Development Application is designed to create a FHIR patient document bundle, which is presented as a JSON file. This application also aims to convert the FHIR patient summary into an HL7 level 3 CDA document.

🚧 The conversion to HL7 CDA is currently a work in progress.

## Features

- Generate a sample patient document bundle as a FHIR bundle.
- Find HL7 FHIR Patient Summary on the [FHIR HAPI test server](https://hapi.fhir.org/) using this app.
- Convert the FHIR JSON bundle into an HL7 CDA document (work in progress).
- I will need to revisit application which creates the FHIR document bundle, to flesh it our further with additional synthetic clinical information that would be present in the original electronic health record.

## Sample Code

Below is a sample code snippet that demonstrates how to create a sample patient record and generate a FHIR JSON bundle:

```python
def create_sample_patient_record():
    # Create a patient resource
    patient = Patient(
        id="12345",
        gender="female",
        birthDate="1980-05-12",
        name=[{
            "use": "official",
            "family": "Doe", 
            "given": ["Jane"] # list of given names
        }],
        address=[{
            "use": "home",
            "line": ["123 Main St"], # list of street addresses
            "city": "Springfield",
            "state": "IL",
            "postalCode": "62701"
        }],
        telecom=[{
            "system": "phone",
            "value": "555-555-5555",
            "use": "home"
        }]
    )
    # Allergies
    allergy = AllergyIntolerance(
        id="allergy1",
        patient={"reference": "Patient/12345"},
        clinicalStatus={
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical", 
                    "code": "active"
                }
            ]
        },
        verificationStatus={
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-verification", 
                    "code": "confirmed"
                }
            ]
        },
        code={
            "coding": [
                {
                    "system": "http://snomed.info/sct", 
                    "code": "227493005", 
                    "display": "Cashew nuts"
                }
            ]
        }
    )
    # Create a FHIR bundle
    bundle = Bundle(
        type="collection",
        entry=[
            {"resource": patient},
            {"resource": allergy}
        ]
    )
    return bundle

```

### FHIR document bundle

Below is the rendered FHIR JSON bundle.

``` JSON
{
    "entry": [
        {
            "resource": {
                "address": [
                    {
                        "city": "Springfield",
                        "line": [
                            "123 Main St"
                        ],
                        "postalCode": "62701",
                        "state": "IL",
                        "use": "home"
                    }
                ],
                "birthDate": "1980-05-12",
                "gender": "female",
                "id": "12345",
                "name": [
                    {
                        "family": "Doe",
                        "given": [
                            "Jane"
                        ],
                        "use": "official"
                    }
                ],
                "resourceType": "Patient",
                "telecom": [
                    {
                        "system": "phone",
                        "use": "home",
                        "value": "555-555-5555"
                    }
                ]
            }
        },
        {
            "resource": {
                "clinicalStatus": {
                    "coding": [
                        {
                            "code": "active",
                            "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical"
                        }
                    ]
                },
                "code": {
                    "coding": [
                        {
                            "code": "91936005",
                            "display": "Allergy to penicillin",
                            "system": "http://snomed.info/sct"
                        }
                    ],
                    "text": "🚧 Allergy to penicillin"
                },
                "id": "allergy1",
                "onsetDateTime": "2024-01-01",
                "patient": {
                    "reference": "Patient/12345"
                },
                "resourceType": "AllergyIntolerance",
                "verificationStatus": {
                    "coding": [
                        {
                            "code": "confirmed",
                            "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-verification"
                        }
                    ]
                }
            }
        },
        {
            "resource": {
                "dosage": [
                    {
                        "doseAndRate": [
                            {
                                "doseQuantity": {
                                    "code": "mg",
                                    "system": "http://unitsofmeasure.org",
                                    "unit": "mg",
                                    "value": 500
                                }
                            }
                        ],
                        "route": {
                            "text": "Oral"
                        },
                        "text": "500 mg/day Oral Tablet",
                        "timing": {
                            "repeat": {
                                "frequency": 1,
                                "period": 1,
                                "periodUnit": "d"
                            }
                        }
                    }
                ],
                "effectivePeriod": {
                    "start": "2024-01-01"
                },
                "id": "med1",
                "medication": {
                    "concept": {
                        "coding": [
                            {
                                "code": "313782",
                                "display": "Amoxicillin 500 MG Oral Tablet",
                                "system": "http://www.nlm.nih.gov/research/umls/rxnorm"
                            }
                        ],
                        "text": "Amoxicillin 500 MG Oral Tablet"
                    }
                },
                "resourceType": "MedicationStatement",
                "status": "active",
                "subject": {
                    "display": "Jane Doe",
                    "reference": "Patient/12345"
                }
            }
        },
        {
            "resource": {
                "category": [
                    {
                        "coding": [
                            {
                                "code": "problem-list-item",
                                "display": "Problem List Item",
                                "system": "http://terminology.hl7.org/CodeSystem/condition-category"
                            }
                        ]
                    }
                ],
                "clinicalStatus": {
                    "coding": [
                        {
                            "code": "active",
                            "display": "active",
                            "system": "http://terminology.hl7.org/CodeSystem/condition-clinical"
                        }
                    ]
                },
                "code": {
                    "coding": [
                        {
                            "code": "36971009",
                            "display": "Bacterial infection",
                            "system": "http://snomed.info/sct"
                        }
                    ],
                    "text": "Bacterial infection"
                },
                "id": "condition1",
                "onsetDateTime": "2024-01-01",
                "resourceType": "Condition",
                "subject": {
                    "reference": "Patient/12345"
                },
                "verificationStatus": {
                    "text": "confirmed"
                }
            }
        },
        {
            "resource": {
                "code": {
                    "coding": [
                        {
                            "code": "233258006",
                            "display": "Balloon angioplasty of artery",
                            "system": "http://snomed.info/sct"
                        },
                        {
                            "code": "233258006",
                            "display": "Balloon angioplasty of artery",
                            "system": "http://snomed.info/sct"
                        }
                    ],
                    "text": "Previous balloon angioplasty on mid-LAD stenosis with STENT Implantation"
                },
                "id": "procedure1",
                "resourceType": "Procedure",
                "status": "completed",
                "subject": {
                    "reference": "Patient/12345"
                }
            }
        }
    ],
    "id": "bundle1",
    "resourceType": "Bundle",
    "type": "collection"
}

```

### 🚧 Work in Progress

The application is currently being extended to convert the FHIR JSON bundle into an HL7 CDA-3 document. This feature is still under development and will be available in future updates.

### How to Run

1. Clone the repository
2. Install the required dependencies using pip install -r requirements.txt.
3. Run the application using python app.py.
4. Access the application in your web browser at http://localhost:5000.
