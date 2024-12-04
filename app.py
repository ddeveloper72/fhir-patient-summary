# import json
import os
import secrets
from pathlib import Path

from dotenv import load_dotenv

# from fhir.resources.patient import Patient
from fhirpy import SyncFHIRClient
from flask import Flask, flash, redirect, render_template, request, url_for

from create_patient_record import create_sample_patient_record

dotenv_path = Path(".env")
load_dotenv()

DEVELOPMENT = os.getenv("DEVELOPMENT")

app = Flask(__name__)

app.config["SECRET_KEY"] = secrets.token_hex(16)


# welcome page
@app.route("/", methods=["GET"])
def index():
    """Render the index page"""

    return render_template("index.html")


@app.route("/hl7/patient_summary/fhir/json", methods=["GET"])
def get_patient_summary():
    """Generate a sample patient record and return it as a JSON object"""

    try:
        patient_record = create_sample_patient_record()
        return render_template("fhir_template.html", patient_json=patient_record)

    except ValueError as e:
        flash("Error generating patient record: " + str(e), "alert-danger")
        return redirect(url_for("index"))


@app.route("/hl7/patient_summary/fhir/select", methods=["GET", "POST"])
def fhir_patient_list():
    """Get a list of patients from the HAPI FHIR server and display them to the user"""

    client = SyncFHIRClient(FHIR_SERVER_URL)
    try:
        patients = client.resources("Patient").sort("-_lastUpdated").limit(100).fetch()

        patient_list = []
        for patient in patients:
            patient_list.append(
                {
                    "id": patient.id,
                }
            )

        return render_template("fhir_patient_list.html", patients=patient_list)
    except (ConnectionError, TimeoutError, ValueError) as e:
        flash("Error fetching patient list: " + str(e), "alert-danger")
        return render_template("fhir_patient_list.html")


@app.route("/hl7/patient_summary/fhir/patient/search", methods=["GET", "POST"])
def fhir_patient_search():
    """Search for a patient record in the HAPI FHIR server"""
    if request.method == "POST":
        form_data = request.form
        resource_type = form_data.get("resource_type")
        search_detail = {
            "_id: Patient": form_data.get("id"),
            "given: Patient": form_data.get("given"),
            "family: Patient": form_data.get("family"),
            "birthdate: Patient": form_data.get("birthdate"),
            "_id: Practitioner": form_data.get("practitioner_id"),
            "given: Practitioner": form_data.get("practitioner_given"),
            "family: Practitioner": form_data.get("practitioner_family"),
            "address-city: Practitioner": form_data.get("practitioner_city"),
            "_id: Observation": form_data.get("observation_id"),
            "code: Observation": form_data.get("observation_code"),
            "performer: Observation": form_data.get("observation_performer"),
            "_id: Medication": form_data.get("medication_id"),
            "lot-number: Medication": form_data.get("lot_number"),
            "ingredient-code: Medication": form_data.get("ingredient_code"),
            "identifier: Medication": form_data.get("medication_name"),
            "form: Medication": form_data.get("dose_form"),
            "_id: MedicationRequest": form_data.get("medication_request_id"),
            "status: MedicationRequest": form_data.get("medication_request_status"),
            "medication: MedicationRequest": form_data.get("medication_request_medication"),
            "patient: MedicationRequest": form_data.get("medication_request_patient"),
            
        }

        client = SyncFHIRClient(FHIR_SERVER_URL)

        try:
            if resource_type == "Patient":
                search_params = filter_search_params(search_detail)
                resources = (
                    client.resources(resource_type).search(**search_params).fetch()
                )
            elif resource_type == "Practitioner":
                search_params = filter_search_params(search_detail)
                resources = (
                    client.resources(resource_type).search(**search_params).fetch()
                )
            elif resource_type == "Observation":
                search_params = filter_search_params(search_detail)
                resources = (
                    client.resources(resource_type).search(**search_params).fetch()
                )
            elif resource_type == "Medication":
                search_params = filter_search_params(search_detail)
                resources = (
                    client.resources(resource_type).search(**search_params).fetch()
                )
            elif resource_type == "MedicationRequest":
                search_params = filter_search_params(search_detail)
                resources = (
                    client.resources(resource_type).search(**search_params).fetch()
                )
            else:
                flash(f"Unsupported resource type: {resource_type}", "alert-danger")
                return redirect(url_for("fhir_patient_search"))

            bundle_json = [resource.serialize() for resource in resources[:1]]

            return render_template("fhir_patient_bundles.html", bundle_json=bundle_json)

        except (ConnectionError, TimeoutError, ValueError) as e:
            flash("Error fetching patient list: " + str(e), "alert-danger")
            return redirect(url_for("fhir_patient_list"))

    return render_template("fhir_patient_search.html")


@app.route(
    "/hl7/patient_summary/fhir/patient",
    defaults={"patient_id": None},
    methods=["GET", "POST"],
)
@app.route("/hl7/patient_summary/fhir/<patient_id>", methods=["GET", "POST"])
def fhir_patient_summary(patient_id):
    """Get the patient id from the user selection and display a detailed patient summary"""

    if request.method == "POST":
        patient_id = request.form.get("patient_id")
        return redirect(url_for("fhir_patient_summary", patient_id=patient_id))

    client = SyncFHIRClient(FHIR_SERVER_URL)

    try:
        patient = client.resources("Patient").search(_id=patient_id).get()
        patient_json = patient.serialize()

        # Convert FHIR resources to JSON
        patient_info = []
        for key, value in patient_json.items():
            patient_info.append({"key": key, "value": value})

    except (ConnectionError, TimeoutError, ValueError) as e:
        flash("The patient ID was not found: " + str(e), "alert-danger")
        return redirect(url_for("fhir_patient_list"))

    # Extract common patient information with fault tolerance
    profile_urls = patient_json.get("meta", {}).get("profile", [])
    profile_links = " ".join(
        [f'<a href="{url}" target="_blank">{url}</a>' for url in profile_urls]
    )

    patient_data = {
        "id": patient_id,
        "name": extract_patient_name(patient_json),
        "identifier": extract_patient_identifier(patient_json),
        "birth_date": patient_json.get("birthDate", "N/A"),
        "gender": patient_json.get("gender", "N/A"),
        "address": extract_patient_address(patient_json),
        "phone": extract_patient_telecom(patient_json, "phone"),
        "email": extract_patient_telecom(patient_json, "email"),
        "source": patient_json.get("meta", {}).get("source", "N/A"),
        "versionId": patient_json.get("meta", {}).get("versionId", "N/A"),
        "last_updated": patient_json.get("meta", {}).get("lastUpdated", "N/A"),
        "profile": profile_links,
        "active": patient_json.get("active", "N/A"),
        "marital_status": extract_patient_marital_status(patient_json, "maritalStatus"),
        "deceased": patient_json.get("deceasedDateTime", "N/A"),
        "deceased_age": patient_json.get("deceasedAge", "N/A"),
        "multiple_birth": patient_json.get("multipleBirthBoolean", "N/A"),
        "multiple_birth_integer": patient_json.get("multipleBirthInteger", "N/A"),
        "communication": extract_patient_languages(patient_json, "language"),
        "contact": extract_patient_contact(patient_json, "contact"),
        "contact_relationship": extract_patient_contact_relationship(
            patient_json, "relationship"
        ),
        "contact_address": extract_patient_contact_address(
            patient_json, "contact_address"
        ),
        "contact_phone": extract_patient_contact_phone(patient_json, "contact_phone"),
        "contact_email": extract_patient_contact_email(patient_json, "contact_email"),
        "general_practitioner": extract_general_practitioner(
            patient_json, "generalPractitioner"
        ),
        "managing_organization": extract_managing_organization(
            patient_json,
            "managingOrganization",
        ),
        "link": patient_json.get("link", "N/A"),
        "photo": patient_json.get("photo", "N/A"),
        "text": extract_patient_text(patient_json, "text"),
    }

    return render_template(
        "fhir_patient_summary.html", patient=patient_data, patient_json=patient_info
    )


# Helper functions to extract information with fault tolerance
def extract_patient_name(patient_json):
    """Extracts a readable name from patient data"""
    names = patient_json.get("name", [])
    if names:
        first_name = names[0].get("given", [""])[0]
        last_name = names[0].get("family", "")
        official_name = names[0].get("use", "")
        if official_name:
            return f"{first_name} {last_name} ({official_name})".strip()
        return f"{first_name} {last_name}".strip()


def extract_patient_identifier(patient_json):
    """Extracts identifier information based on type"""
    identifiers = patient_json.get("identifier", [])
    identifier_list = []
    for identifier in identifiers:
        identifier_system = identifier.get("system", "")
        identifier_value = identifier.get("value", "")
        identifier_list.append(f"{identifier_system} - {identifier_value}")
    return ", ".join(identifier_list) if identifier_list else "N/A"


def extract_patient_address(patient_json):
    """Extracts the first line of address information if available"""
    addresses = patient_json.get("address", [])
    if addresses:
        line = addresses[0].get("line", [""])[0]
        city = addresses[0].get("city", "")
        state = addresses[0].get("state", "")
        postal = addresses[0].get("postalCode", "")
        address_use = addresses[0].get("use", "")
        if address_use:
            return f"{line}, {city}, {state} {postal} ({address_use})".strip(", ")
        return f"{line}, {city}, {state} {postal}".strip(", ")
    return "N/A"


def extract_patient_telecom(patient_json, telecom_type):
    """Extracts telecom information based on type"""
    telecoms = patient_json.get("telecom", [])
    if telecoms:
        phone_type = telecoms[0].get("use", "")
        email_type = telecoms[1].get("use", "") if len(telecoms) > 1 else "N/A"
        if telecom_type == "phone":
            return telecoms[0].get("value", "N/A") + f" ({phone_type})"
        if telecom_type == "email" and len(telecoms) > 1:
            return telecoms[1].get("value", "N/A") + f" ({email_type})"
    return "N/A"


def extract_patient_marital_status(patient_json, marital_status_type):
    """Extracts marital status information based on type"""
    marital_status = patient_json.get("maritalStatus", {})
    if marital_status_type == "maritalStatus":
        return marital_status.get("coding", [{}])[0].get("display", "N/A")
    return "N/A"


def extract_patient_contact(patient_json, contact_type):
    """Extracts contact information based on type"""
    contact = patient_json.get("contact", [])
    if contact:
        contact_name = contact[0].get("name", {})
        family_name = contact_name.get("family", "")
        given_name = contact_name.get("given", [""])[0]
        prefix_extension = contact_name.get("_family", {}).get("extension", [])
        value_string = next(
            (
                ext.get("valueString", "")
                for ext in prefix_extension
                if ext.get("url")
                == "http://hl7.org/fhir/StructureDefinition/humanname-own-prefix"
            ),
            "",
        )
        return f"{value_string} {given_name} {family_name}".strip()
    return "N/A"


def extract_patient_contact_relationship(patient_json, contact_relationship_type):
    """Extracts contact relationship information based on type"""
    contact = patient_json.get("contact", [])
    if contact:
        contact_relationship = (
            contact[0]
            .get("relationship", [{}])[0]
            .get("coding", [{}])[0]
            .get("display", "N/A")
        )
        return contact_relationship
    return "N/A"


def extract_patient_contact_address(patient_json, contact_address_type):
    """Extracts contact address information based on type"""
    contact = patient_json.get("contact", [])
    if contact:
        contact_address = contact[0].get("address", {})
        contact_address_use = contact_address.get("use", "")
        contact_address_line = contact_address.get("line", [""])[0]
        contact_city = contact_address.get("city", "")
        contact_state = contact_address.get("state", "")
        contact_postal_code = contact_address.get("postalCode", "")
        return f"{contact_address_line}, {contact_city}, {contact_state} {contact_postal_code} ({contact_address_use})".strip(
            ", "
        )
    return "N/A"


def extract_patient_contact_phone(patient_json, contact_phone_type):
    """Extracts contact phone information based on type"""
    contact = patient_json.get("contact", [])
    if contact:
        contact_phone = contact[0].get("telecom", [])
        contact_phone_use = contact_phone[0].get("use", "")
        contact_phone_value = contact_phone[0].get("value", "")
        return f"{contact_phone_value} ({contact_phone_use})"
    return "N/A"


def extract_patient_contact_email(patient_json, contact_email_type):
    """Extracts contact email information based on type"""
    contact = patient_json.get("contact", [])
    if contact:
        contact_email = contact[0].get("telecom", [])
        contact_email_use = contact_email[1].get("use", "")
        contact_email_value = contact_email[1].get("value", "")
        return f"{contact_email_value} ({contact_email_use})"
    return "N/A"


def extract_general_practitioner(patient_json, general_practitioner_type):
    """Extracts general practitioner information based on type"""
    general_practitioner = patient_json.get("generalPractitioner", {})
    if general_practitioner_type == "generalPractitioner":
        return (
            general_practitioner[0].get("reference", "N/A")
            if general_practitioner
            else "N/A"
        )
    return "N/A"


def extract_managing_organization(patient_json, managing_organization_type):
    """Extracts managing organization information based on type"""
    managing_organization = patient_json.get("managingOrganization", {})
    if managing_organization_type == "managingOrganization":
        return (
            managing_organization.get("reference", "N/A")
            if managing_organization
            else "N/A"
        )
    return "N/A"


def extract_patient_languages(patient_json, language_type):
    """Extracts language information based on type"""
    languages = patient_json.get("communication", [])
    language_list = []
    for language in languages:
        language_code = (
            language.get("language", {}).get("coding", [{}])[0].get("display", "N/A")
        )
        preferred = language.get("preferred", False)
        preferred_text = " (preferred)" if preferred else ""
        language_list.append(f"{language_code}{preferred_text}")
    return ", ".join(language_list) if language_list else "N/A"


def extract_patient_text(patient_json, text_type):
    """Extracts text information based on type"""
    text = patient_json.get("text", {})
    if text_type == "text":
        return text.get("div", "N/A")
    return "N/A"


@app.route("/hl7/patient_summary/fhir/patient/edit", methods=["GET", "POST"])
def edit_fhir_patient():
    """Edit a patient record in the HAPI FHIR server."""

    client = SyncFHIRClient(FHIR_SERVER_URL)
    patient_id = request.args.get("patient_id")

    if request.method == "POST":
        # Update patient data with submitted form data
        form_data = request.form
        updated_patient = {
            "id": patient_id,
            "birthDate": form_data.get("birth_date", ""),
            "gender": form_data.get("gender", ""),
            "name": [
                {
                    "use": form_data.get("official_name", ""),
                    "family": form_data.get("family_name", ""),
                    "given": [form_data.get("given_name", "")],
                }
            ],
            "address": [
                {
                    "use": form_data.get("address_use", ""),
                    "line": [form_data.get("address_line", "")],
                    "city": form_data.get("city", ""),
                    "state": form_data.get("state", ""),
                    "postalCode": form_data.get("postal_code", ""),
                }
            ],
            "telecom": [
                {
                    "system": "phone",
                    "value": form_data.get("phone", ""),
                    "use": form_data.get("phone_use", ""),
                },
                {
                    "system": "email",
                    "value": form_data.get("email", ""),
                    "use": form_data.get("email_use", ""),
                },
            ],
            "profile": [
                "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"
            ],
            "active": form_data.get("active", "") == "True",
            "maritalStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus",
                        "code": form_data.get("marital_status", ""),
                        "display": form_data.get("marital_status", ""),
                    }
                ]
            },
            "deceased": [
                {
                    "deceasedDateTime": form_data.get("deceased", ""),
                    "deceasedBoolean": form_data.get("deceased_boolean", ""),
                },
            ],
            "multipleBirthBoolean": form_data.get("multiple_birth", ""),
            "multipleBirthInteger": form_data.get("multiple_birth_integer", ""),
            "communication": [
                {
                    "language": {
                        "coding": [
                            {
                                "system": "urn:ietf:bcp:47",
                                "code": get_language_code(language),
                                "display": language,
                            }
                        ]
                    },
                    "preferred": language == form_data.get("preferred_language", ""),
                }
                for language in form_data.getlist("languages")
            ],
            "contact": [
                {
                    "relationship": [
                        {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/v2-0131",
                                    "code": get_relationship_code(
                                        form_data.get("contact_relationship", "")
                                    ),
                                    "display": form_data.get(
                                        "contact_relationship", ""
                                    ),
                                }
                            ]
                        }
                    ],
                    "name": {
                        "family": form_data.get("contact_family_name", ""),
                        "_family": {
                            "extension": [
                                {
                                    "url": "http://hl7.org/fhir/StructureDefinition/humanname-own-prefix",
                                    "valueString": form_data.get(
                                        "contact_family_name_prefix", ""
                                    ),
                                }
                            ]
                        },
                        "given": [form_data.get("contact_given_name", "")],
                    },
                    "telecom": [
                        {
                            "system": "phone",
                            "value": form_data.get("contact_phone", ""),
                            "use": form_data.get("contact_phone_use", ""),
                        },
                        {
                            "system": "email",
                            "value": form_data.get("contact_email", ""),
                            "use": form_data.get("contact_email_use", ""),
                        },
                    ],
                    "address": [
                        {
                            "use": form_data.get("contact_address_use", ""),
                            "line": [form_data.get("contact_address_line", "")],
                            "city": form_data.get("contact_city", ""),
                            "state": form_data.get("contact_state", ""),
                            "postalCode": form_data.get("contact_postal_code", ""),
                            "period": {
                                "start": form_data.get("contact_start", ""),
                            },
                        }
                    ],
                }
            ],
            "generalPractitioner": {
                "reference": [
                    {
                        "reference": form_data.get("general_practitioner", ""),
                        "type": "Practitioner",
                        "identifier": [
                            {
                                "system": "http://hl7.org/fhir/sid/us-npi",
                                "value": form_data.get("general_practitioner", ""),
                            },
                        ],
                        "display": form_data.get("general_practitioner", ""),
                    }
                ]
            },
            "managingOrganization": {
                "reference": [
                    {
                        "reference": form_data.get("managing_organization", ""),
                        "type": "Organization",
                        "identifier": [
                            {
                                "system": "http://hl7.org/fhir/sid/us-npi",
                                "value": form_data.get("managing_organization", ""),
                            },
                        ],
                        "display": form_data.get("managing_organization", ""),
                    }
                ]
            },
            "link": {
                "reference": [
                    {
                        "reference": form_data.get("link", ""),
                        "type": "Patient",
                        "identifier": [
                            {
                                "system": "http://hl7.org/fhir/sid/us-npi",
                                "value": form_data.get("link", ""),
                            },
                        ],
                        "display": form_data.get("link", ""),
                    }
                ],
            },
            "photo": {
                "reference": [
                    {
                        "reference": form_data.get("photo", ""),
                        "type": "Photo",
                        "identifier": [
                            {
                                "system": "http://hl7.org/fhir/sid/us-npi",
                                "value": form_data.get("photo", ""),
                            },
                        ],
                        "display": form_data.get("photo", ""),
                    }
                ],
            },
        }

        try:
            # Update patient on the HAPI FHIR server
            patient_resource = client.resource("Patient", **updated_patient)
            patient_resource.id = patient_id  # Set ID for updating
            patient_resource.save()
            flash("Patient information updated successfully.", "alert-success")
            return redirect(url_for("fhir_patient_summary", patient_id=patient_id))
        except (ConnectionError, TimeoutError, ValueError) as e:
            flash("Error updating patient: " + str(e), "alert-danger")
            return redirect(url_for("fhir_patient_summary", patient_id=patient_id))

    # If GET, render edit form with existing patient data
    try:
        patient = client.resources("Patient").get(id=patient_id)
        patient_json = patient.serialize()
    except Exception as e:
        flash("The patient ID was not found: " + str(e), "alert-danger")
        return redirect(url_for("fhir_patient_list"))

    if DEVELOPMENT:  # Debugging
        return render_template("edit_fhir_patient.html", patient=patient_json)

    else:  # Production
        try:
            return render_template("edit_fhir_patient.html", patient=patient_json)
        except Exception as e:
            flash("Error rendering edit form: " + str(e), "alert-danger")
            return redirect(url_for("fhir_patient_list"))


# New patient record
@app.route("/hl7/patient_summary/fhir/patient/new", methods=["GET", "POST"])
def new_fhir_patient():
    """Create a new patient record in the HAPI FHIR server."""

    if request.method == "POST":
        # Create a new patient record with submitted form data
        form_data = request.form
        new_patient = {
            "id": secrets.token_hex(16),
            "resourceType": "Patient",
            "gender": form_data.get("gender", ""),
            "birthDate": form_data.get("birth_date", ""),
            "name": [
                {
                    "use": form_data.get("official_name", ""),
                    "family": form_data.get("family_name", ""),
                    "given": [form_data.get("given_name", "")],
                }
            ],
            "address": [
                {
                    "use": form_data.get("address_use", ""),
                    "line": [form_data.get("address_line", "")],
                    "city": form_data.get("city", ""),
                    "state": form_data.get("state", ""),
                    "postalCode": form_data.get("postal_code", ""),
                }
            ],
            "telecom": [
                {
                    "system": "phone",
                    "value": form_data.get("phone", ""),
                    "use": form_data.get("phone_use", ""),
                },
                {
                    "system": "email",
                    "value": form_data.get("email", ""),
                    "use": form_data.get("email_use", ""),
                },
            ],
            "profile": [
                "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"
            ],
            "active": form_data.get("active", "") == "True",
            "maritalStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus",
                        "code": form_data.get("marital_status", ""),
                        "display": form_data.get("marital_status", ""),
                    }
                ]
            },
            "deceasedDateTime": form_data.get("deceased", ""),
            "deceasedBoolean": form_data.get("deceased_boolean", "") == "True",
            "multipleBirthBoolean": form_data.get("multiple_birth", "") == "True",
            "multipleBirthInteger": form_data.get("multiple_birth_integer", ""),
            "communication": [
                {
                    "language": {
                        "coding": [
                            {
                                "system": "urn:ietf:bcp:47",
                                "code": get_language_code(language),
                                "display": language,
                            }
                        ]
                    },
                    "preferred": language == form_data.get("preferred_language", ""),
                }
                for language in form_data.getlist("languages")
            ],
            "contact": [
                {
                    "relationship": [
                        {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/v2-0131",
                                    "code": get_relationship_code(
                                        form_data.get("contact_relationship", "")
                                    ),
                                    "display": form_data.get(
                                        "contact_relationship", ""
                                    ),
                                }
                            ]
                        }
                    ],
                    "name": {
                        "family": form_data.get("contact_family_name", ""),
                        "_family": {
                            "extension": [
                                {
                                    "url": "http://hl7.org/fhir/StructureDefinition/humanname-own-prefix",
                                    "valueString": form_data.get(
                                        "contact_family_name_prefix", ""
                                    ),
                                }
                            ]
                        },
                        "given": [form_data.get("contact_given_name", "")],
                    },
                    "telecom": [
                        {
                            "system": "phone",
                            "value": form_data.get("contact_phone", ""),
                            "use": form_data.get("contact_phone_use", ""),
                        },
                        {
                            "system": "email",
                            "value": form_data.get("contact_email", ""),
                            "use": form_data.get("contact_email_use", ""),
                        },
                    ],
                    "address": [
                        {
                            "use": form_data.get("contact_address_use", ""),
                            "line": [form_data.get("contact_address_line", "")],
                            "city": form_data.get("contact_city", ""),
                            "state": form_data.get("contact_state", ""),
                            "postalCode": form_data.get("contact_postal_code", ""),
                            "period": {
                                "start": form_data.get("contact_start", ""),
                            },
                        }
                    ],
                }
            ],
            "generalPractitioner": [
                {
                    "resource_type": "GeneralPractitioner",
                    "id": form_data.get("general_practitioner_id", ""),
                    "reference": form_data.get("general_practitioner", ""),
                    "type": "Practitioner",
                    "identifier": [
                        {
                            "system": "http://hl7.org/fhir/sid/us-npi",
                            "value": form_data.get("general_practitioner", ""),
                        },
                    ],
                    "display": form_data.get("general_practitioner_display", ""),
                }
            ],
            "managingOrganization": [
                {
                    "resource_type": "managingOrganization",
                    "id": form_data.get("managing_organization_id", ""),
                    "reference": form_data.get("managing_organization", ""),
                    "type": "Organization",
                    "identifier": [
                        {
                            "system": "http://hl7.org/fhir/sid/us-npi",
                            "value": form_data.get("managing_organization", ""),
                        },
                    ],
                    "display": form_data.get("managing_organization_display", ""),
                },
            ],
            "link": [
                {
                    "resource_type": "Link",
                    "id": form_data.get("link_id", ""),
                    "reference": form_data.get("link", ""),
                    "identifier": [
                        {
                            "system": "http://hl7.org/fhir/sid/us-npi",
                            "value": form_data.get("link", ""),
                        },
                    ],
                    "display": form_data.get("link_display", ""),
                }
            ],
            "photo": [
                {
                    "resource_type": "Photo",
                    "id": form_data.get("photo_id", ""),
                    "reference": form_data.get("photo", ""),
                    "type": "Photo",
                    "identifier": [
                        {
                            "system": "http://hl7.org/fhir/sid/us-npi",
                            "value": form_data.get("photo", ""),
                        },
                    ],
                    "display": form_data.get("photo_display", ""),
                }
            ],
        }

        print("New Patient Data:", new_patient)
        client = SyncFHIRClient(FHIR_SERVER_URL)
        try:
            # Create a new patient on the HAPI FHIR server
            patient_resource = client.resource("Patient", **new_patient)
            patient_resource.save()
            flash("New patient record created successfully.", "alert-success")
            # print("Form data: ", form_data)
            return redirect(url_for("fhir_patient_list"))
        except (ConnectionError, TimeoutError, ValueError) as e:
            flash("Error creating new patient: " + str(e), "alert-danger")
            return redirect(url_for("fhir_patient_list"))

    return render_template("new_fhir_patient.html")


def get_language_code(language_display):
    """Returns the language code for a given language display name"""
    language_map = {
        "english": "en",
        "french": "fr",
        "german": "de",
        "spanish": "es",
        "italian": "it",
        "portuguese": "pt",
        "romanian": "ro",
        "dutch": "nl",
        "swedish": "sv",
        "danish": "da",
        "norwegian": "no",
        "russian": "ru",
        "polish": "pl",
        "czech": "cs",
        "slovak": "sk",
        "bulgarian": "bg",
        "serbian": "sr",
        "croatian": "hr",
        "slovenian": "sl",
        "latvian": "lv",
        "lithuanian": "lt",
        "greek": "el",
        "finnish": "fi",
        "hungarian": "hu",
        "estonian": "et",
    }
    return language_map.get(language_display.lower(), "en")


def get_relationship_code(contact_relationship):
    """Returns the relationship code for a given relationship display name"""
    relationship_map = {
        "Billing contact person": "BP",
        "Contact person": "CP",
        "Emergency contact person": "EP",
        "Person preparing referral": "PR",
        "Employer": "E",
        "Emergency Contact": "C",
        "Federal Agency": "F",
        "Insurance Company": "I",
        "Next-of-Kin": "N",
        "State Agency": "S",
        "Unknown": "U",
    }
    return relationship_map.get(contact_relationship, "U")


# Delete patient record
@app.route("/hl7/patient_summary/fhir/patient/delete", methods=["GET", "POST"])
def delete_fhir_patient():
    """Delete a patient record from the HAPI FHIR server."""

    client = SyncFHIRClient(os.getenv("FHIR_SERVER_URL"))
    patient_id = request.args.get("patient_id")

    if request.method == "POST":
        try:
            # Delete patient record from the HAPI FHIR server
            patient = client.resources("Patient").get(id=patient_id)
            patient.delete()
            flash("Patient record deleted successfully.", "alert-success")
            return redirect(url_for("fhir_patient_list"))
        except (ConnectionError, TimeoutError, ValueError) as e:
            flash("Error deleting patient record: " + str(e), "alert-danger")
            return redirect(url_for("fhir_patient_list"))

    try:
        patient = client.resources("Patient").get(id=patient_id)
        return render_template("delete_fhir_patient.html", patient=patient)
    except (ConnectionError, TimeoutError, ValueError) as e:
        flash("Error fetching patient record: " + str(e), "alert-danger")
        return redirect(url_for("fhir_patient_list"))


@app.errorhandler(404)
def page_not_found(e):
    """Page not found error handler"""

    flash(e, "alert-danger")
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    """Internal server error handler"""

    flash(e, "alert-danger")
    return render_template("500.html"), 500


if DEVELOPMENT:
    FHIR_SERVER_URL = os.getenv("FHIR_SERVER_URL")
else:
    FHIR_SERVER_URL = "https://hapi.fhir.org/baseR4"

def filter_search_params(search_detail):
    """Filter search parameters to remove empty values"""
    return {k: v for k, v in search_detail.items() if v}


if __name__ == "__main__":
    if DEVELOPMENT:
        app.run(
            host=os.getenv("IP"),
            port=os.getenv("PORT"),
            debug=True,
        )
    else:
        app.run(host=os.getenv("IP"), port=os.getenv("PORT"), debug=False)
