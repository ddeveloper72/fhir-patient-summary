import os
import json
import secrets

from fhirpy import SyncFHIRClient
from flask import Flask, flash, jsonify, render_template, request, redirect, url_for
from create_patient_record import create_sample_patient_record

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

    patient_record = create_sample_patient_record()
    patient_record_json = patient_record.json(indent=4)

    return jsonify(json.loads(patient_record_json))


# @app.route("/generate_cda", methods=["POST"])
# def generate_cda():
#     '''Generate a CDA document from the FHIR patient record and return it as a file'''

#     patient_id = request.form.get("patient_id")

#     if not patient_id:
#         return redirect(url_for("index"))
#     if patient_id:
#         patient_record = create_sample_patient_record()
#         fhir_to_cda(fhir_data=patient_record, patient_identifier=patient_id)

#         return redirect(url_for("download_cda", patient_id=patient_id))

#     return redirect(url_for("index"))


# @app.route("/hl7/patient_summary/download_cda", methods=["GET"])
# def get_hl7_patient_summary_cda(patient_identifier):
#     """Generate a CDA document from the FHIR patient record and return it as a file"""

#     patient_record = create_sample_patient_record()
#     fhir_to_cda(fhir_data=patient_record, patient_identifier=patient_identifier)

#     directory = os.path.join(app.root_path, "static/out")
#     file_name = f"{patient_identifier}_ps_sample_cda.xml"

#     return send_from_directory(directory, file_name, as_attachment=True)


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


@app.route("/hl7/patient_summary/fhir/patient", methods=["GET", "POST"])
def fhir_patient_summary():
    """Get the patient id from the user selection and display the patient summary"""

    patient_id = request.form.get("patient_id")
    client = SyncFHIRClient("http://hapi.fhir.org/baseR4")

    try:
        patient = client.resources("Patient").get(id=patient_id)
    except Exception as e:
        flash("The patient id is not found: " + str(e), "alert-danger")
        return redirect(url_for("fhir_patient_list"))

    # Convert FHIR resources to JSON
    patient_json = patient.serialize()
    patient_info = []
    for key, value in patient_json.items():
        patient_info.append({"key": key, "value": value})

    return render_template("fhir_patient_summary.html", patient=patient_info)


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
    app.run(host=os.getenv("IP"), 
            port=os.getenv("PORT"), 
            debug=False)
