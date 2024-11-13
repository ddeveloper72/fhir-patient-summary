import json
import os
import secrets
from pathlib import Path

from dotenv import load_dotenv
from fhir.resources.patient import Patient
from fhirpy import SyncFHIRClient
from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   url_for)

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

    except Exception as e:
        flash("Error generating patient record: " + str(e), "alert-danger")
        return redirect(url_for("index"))


@app.route("/hl7/patient_summary/fhir/select", methods=["GET", "POST"])
def fhir_patient_list():
    """Get a list of patients from the HAPI server and display them to the user"""

    client = SyncFHIRClient("http://hapi.fhir.org/baseR4")
    patients = client.resources("Patient").sort("-_lastUpdated").limit(100).fetch()

    patient_list = []
    for patient in patients:
        patient_list.append(
            {
                "id": patient.id,
            }
        )
        # print(patient_list)

    return render_template("fhir_patient_list.html", patients=patient_list)


#


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

    client = SyncFHIRClient("http://hapi.fhir.org/baseR4")

    try:
        patient = client.resources("Patient").get(id=patient_id)
        patient_json = patient.serialize()

        # Convert FHIR resources to JSON
        patient_info = []
        for key, value in patient_json.items():
            patient_info.append({"key": key, "value": value})

    except Exception as e:
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


@app.route("/hl7/patient_summary/fhir/patient/edit", methods=["GET", "POST"])
def edit_fhir_patient():
    """Edit a patient record in the HAPI FHIR server."""

    client = SyncFHIRClient("http://hapi.fhir.org/baseR4")
    patient_id = request.args.get("patient_id")

    if request.method == "POST":
        # Update patient data with submitted form data
        form_data = request.form
        updated_patient = {
            "id": patient_id,
            "name": [
                {
                    "family": form_data.get("family_name", ""),
                    "given": [form_data.get("given_name", "")],
                    "use": form_data.get("official_name", ""),
                }
            ],
            "birthDate": form_data.get("birth_date", ""),
            "gender": form_data.get("gender", ""),
            "address": [
                {
                    "line": [form_data.get("address_line", "")],
                    "city": form_data.get("city", ""),
                    "state": form_data.get("state", ""),
                    "postalCode": form_data.get("postal_code", ""),
                    "use": form_data.get("address_use", ""),
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
        }

        try:
            # Update patient on the HAPI FHIR server
            patient_resource = client.resource("Patient", **updated_patient)
            patient_resource.id = patient_id  # Set ID for updating
            patient_resource.save()
            flash("Patient information updated successfully.", "alert-success")
            return redirect(url_for("fhir_patient_summary", patient_id=patient_id))
        except Exception as e:
            flash("Error updating patient: " + str(e), "alert-danger")
            return redirect(url_for("fhir_patient_summary", patient_id=patient_id))

    # If GET, render edit form with existing patient data
    try:
        patient = client.resources("Patient").get(id=patient_id)
        patient_json = patient.serialize()
    except Exception as e:
        flash("The patient ID was not found: " + str(e), "alert-danger")
        return redirect(url_for("fhir_patient_list"))

    try:
        return render_template("edit_fhir_patient.html", patient=patient_json)
    except Exception as e:
        flash("Error rendering edit form: " + str(e), "alert-danger")
        return redirect(url_for("fhir_patient_list"))


# # Helper function to compile infomation from the form
# def compile_patient_name(form_data):
#     """Compile patient name from form data"""
#     return [
#         {
#             "use": form_data.get("official_name", ""),
#             "family": form_data.get("family_name", ""),
#             "given": [form_data.get("given_name", "")],
#         }
#     ]


# New patient record
@app.route("/hl7/patient_summary/fhir/patient/new", methods=["GET", "POST"])
def new_fhir_patient():
    """Create a new patient record in the HAPI FHIR server."""

    if request.method == "POST":
        # Create a new patient record with submitted form data
        form_data = request.form
        new_patient = {
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
        }

        client = SyncFHIRClient("http://hapi.fhir.org/baseR4")
        try:
            # Create a new patient on the HAPI FHIR server
            patient_resource = client.resource("Patient", **new_patient)
            patient_resource.save()
            flash("New patient record created successfully.", "alert-success")
            return redirect(url_for("fhir_patient_list"))
        except Exception as e:
            flash("Error creating new patient: " + str(e), "alert-danger")
            return redirect(url_for("fhir_patient_list"))

    return render_template("new_fhir_patient.html")


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


if __name__ == "__main__":
    if DEVELOPMENT:
        app.run(host=os.getenv("IP"), port=os.getenv("PORT"), debug=True)
    else:
        app.run(host=os.getenv("IP"), port=os.getenv("PORT"), debug=False)
