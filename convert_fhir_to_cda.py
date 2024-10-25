import json
from lxml import etree
from create_patient_record import create_sample_patient_record
from jinja2 import Environment, FileSystemLoader


def read_fhir_bundle():

    # Create the sample patient record as a FHIR bundle
    patient_record = create_sample_patient_record()
    patient_record_json = patient_record.json(indent=4)
    fhir_bundle = json.loads(patient_record_json)
    return fhir_bundle

def fhir_to_cda(fhir_bundle):
    # Create CDA root element
    cda_root = etree.Element("ClinicalDocument", xmlns="urn:hl7-org:v3")

    # Add header information
    header = etree.SubElement(cda_root, "header")
    patient_info = etree.SubElement(header, "patient")
    patient_name = etree.SubElement(patient_info, "name")
    patient_name.text = fhir_bundle['entry'][0]['resource']['name'][0]['given'][0] + " " + fhir_bundle['entry'][0]['resource']['name'][0]['family']

    # Add more elements as needed from the FHIR bundle to the CDA document
    # For example, patient ID, birth date, etc.
    patient_id = etree.SubElement(patient_info, "id")
    patient_id.text = fhir_bundle['entry'][0]['resource']['id']

    birth_date = etree.SubElement(patient_info, "birthDate")
    birth_date.text = fhir_bundle['entry'][0]['resource']['birthDate']   

    # Add Allergies
    allergies = etree.SubElement(cda_root, "allergies")
    for entry in fhir_bundle['entry']:
        if entry['resource']['resourceType'] == "AllergyIntolerance":
            allergy = etree.SubElement(allergies, "allergy")
            allergy.text = entry['resource']['code'].get('text', 'Unknown')

    # Add Medications
    medications = etree.SubElement(cda_root, "medications")
    for entry in fhir_bundle['entry']:
        if entry['resource']['resourceType'] == "MedicationStatement":
            medication = etree.SubElement(medications, "medication")
            medication.text = entry['resource']['medication'].get('code', {}).get('text', 'Unknown')

    # Add Condition
    conditions = etree.SubElement(cda_root, "conditions")
    for entry in fhir_bundle['entry']:
        if entry['resource']['resourceType'] == "Condition":
            condition = etree.SubElement(conditions, "condition")
            condition.text = entry['resource']['code'].get('text', 'Unknown')

    # Add Procedures
    procedures = etree.SubElement(cda_root, "procedures")
    for entry in fhir_bundle['entry']:
        if entry['resource']['resourceType'] == "Procedure":
            procedure = etree.SubElement(procedures, "procedure")
            procedure.text = entry['resource']['code'].get('text', 'Unknown')



    
    return etree.tostring(cda_root, pretty_print=True, xml_declaration=True, encoding="UTF-8")

def render_html(cda_xml, template_path):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(template_path)
    return template.render(cda=cda_xml.decode('utf-8'))

def main():
    fhir_bundle = read_fhir_bundle()
    cda_xml = fhir_to_cda(fhir_bundle)
    html_output = render_html(cda_xml, 'cda_template.html')
    
    with open('output.html', 'w') as file:
        file.write(html_output)

if __name__ == "__main__":
    main()