from fhir.resources.patient import Patient
from fhir.resources.allergyintolerance import AllergyIntolerance
from fhir.resources.condition import Condition
from fhir.resources.medicationstatement import MedicationStatement
from fhir.resources.procedure import Procedure
from fhir.resources.bundle import Bundle
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.reference import Reference
from fhir.resources.codeablereference import CodeableReference
from fhir.resources.coding import Coding
from fhir.resources.dosage import Dosage
from fhir.resources.timing import Timing
# from fhir.resources.fhirdate import FHIRDate


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
        code=CodeableConcept(
            coding=[
                Coding(
                    system="http://snomed.info/sct",
                    code="91936005",
                    display="Allergy to penicillin"
                )
            ],
            text="Allergy to penicillin"
        ),
        onsetDateTime="2024-01-01"
    )

   # Medications
    medication = MedicationStatement(
    id="med1",
    subject=Reference(
        reference="Patient/12345",
        display="Jane Doe"),
    medication=CodeableReference( # medication reference
        concept=CodeableConcept( # medication concept
            coding=[
                Coding(
                    system="http://www.nlm.nih.gov/research/umls/rxnorm",
                    code="313782",
                    display="Amoxicillin 500 MG Oral Tablet"
                )
            ],
            text="Amoxicillin 500 MG Oral Tablet"
        )        
    ),
    dosage=[
        Dosage(
            text="500 mg/day Oral Tablet",
            timing=Timing(
                repeat={
                    "frequency": 1,
                    "period": 1,
                    "periodUnit": "d"
                }
            ),
            route={"text": "Oral"},
            doseAndRate=[{
                "doseQuantity": {
                    "value": 500,
                    "unit": "mg",
                    "system": "http://unitsofmeasure.org",
                    "code": "mg"
                }
            }]
        )
    ],
    status="active",  # active | completed | entered-in-error | intended | stopped | on-hold | unknown | not-taken
    effectivePeriod={
        "start": "2024-01-01"
    }
)

    # Conditions (Medical History)
    condition = Condition(
        id="condition1",
        subject=Reference(reference="Patient/12345"),
        clinicalStatus=CodeableConcept(
            coding=[
                Coding(
                    system="http://terminology.hl7.org/CodeSystem/condition-clinical",
                    code="active",
                    display="active"
                )
            ],
        ),
        verificationStatus=CodeableConcept(
            text="confirmed"
        ),
        category=[
            CodeableConcept(
                coding=[
                    Coding(
                        system="http://terminology.hl7.org/CodeSystem/condition-category",
                        code="problem-list-item",
                        display="Problem List Item"
                    )
                ],
                )
                ],
        code=CodeableConcept(
            coding=[
                Coding(
                    system="http://snomed.info/sct",
                    code="36971009",
                    display="Bacterial infection"
                )
            ],
            text="Bacterial infection"
            ),
        onsetDateTime="2024-01-01"
    )

    # Procedures 
    procedure = Procedure(
        id="procedure1",
        subject=Reference(reference="Patient/12345"),
        status="completed",  # required field
        code=CodeableConcept(
            coding=[
                Coding(
                    system="http://snomed.info/sct",
                    code="233258006",
                    display="Balloon angioplasty of artery"
                ),
                Coding(
                    system="http://snomed.info/sct",
                    code="233258006",
                    display="Balloon angioplasty of artery"
                )
            ],
            text="Previous balloon angioplasty on mid-LAD stenosis with STENT Implantation"
        )
    )


    # Bundle all resources together
    bundle = Bundle(
        id="bundle1",
        type="collection",
        entry=[
            {"resource": patient},
            {"resource": allergy},
            {"resource": medication},
            {"resource": condition},
            {"resource": procedure}
        ]
    )
    
    return bundle
