import secrets
import json
from flask import Flask, jsonify
from fhir.resources.bundle import Bundle
from fhir.resources.patient import Patient
from jinja2 import Environment, FileSystemLoader

# Import the function that creates the sample patient record
from create_patient_record import create_sample_patient_record
from flask import render_template
from convert_fhir_to_cda import fhir_to_cda


app = Flask(__name__)

app.config['SECRET_KEY'] = secrets.token_hex(16)


@app.route("/fhir/patient_summary", methods=["GET"])
def get_patient_summary():
    # Create the sample patient record as a FHIR bundle
    patient_record = create_sample_patient_record()

    # Convert FHIR resources to JSON
    patient_record_json = patient_record.json(indent=4)

    return jsonify(json.loads(patient_record_json))

# # HL7 Summary endpoint (placeholder)
# @app.route("/hl7/patient_summary", methods=["GET"])
# def get_hl7_patient_summary():
#     # generate a CDA document from the FHIR patient record
#     return "HL7 Patient Summary"
#     # Assuming you have a function to convert FHIR to CDA

# HL7 Summary endpoint (placeholder)

@app.route("/hl7/patient_summary", methods=["GET"])
def get_hl7_patient_summary():
    # Create the sample patient record as a FHIR bundle
    patient_record = create_sample_patient_record()

    # Convert FHIR resources to JSON
    patient_record_json = patient_record.json(indent=4)

    return jsonify(json.loads(patient_record_json))

@app.route("/hl7/patient_summary/cda", methods=["GET"])
def get_hl7_patient_summary_html():
    # Create the sample patient record as a FHIR bundle
    cda_root = fhir_to_cda(create_sample_patient_record())
    return render_template("cda_template.html", cda_root=cda_root)

    
@app.route("/fhir/patient_summary/html", methods=["GET"])
def get_patient_summary_html():
    # render the FHIR patient record as HTML
    patient_record = fhir_to_cda(create_sample_patient_record())
    return render_template("fhir_template.html", patient_record=patient_record)

if __name__ == "__main__":
    app.run(debug=True)
