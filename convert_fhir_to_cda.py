import json
from lxml import etree
import xml.etree.ElementTree as ET
from datetime import datetime
from create_patient_record import create_sample_patient_record
from flask import render_template


def read_fhir_bundle():

    # Create the sample patient record as a FHIR bundle
    patient_record = create_sample_patient_record()
    patient_record_json = patient_record.json(indent=4)
    fhir_bundle = json.loads(patient_record_json)
    return fhir_bundle

# Helper function to add sub-elements with text and attributes
def add_sub_element(parent, tag, text=None, attrib={}):
    elem = etree.SubElement(parent, tag, attrib)
    if text is not None:
        elem.text = text


class CDAData:
    def __init__(self):
        with open('static/codes/ehdsi.json', encoding='utf-8') as json_file:
            data = json.load(json_file)
            self.head = [
                (
                    p['codeElement'][0]['displayName'],
                    p['codeElement'][0]['code'],
                    p['codeElement'][0]['codeSystem'],
                    p['codeElement'][0]['codeSystemName']
                )
                for p in data[('rootDirectory')]]
            
            self.head_type_id = [
                (
                    p['typeId'][0]['extension'],
                    p['typeId'][0]['root']
                )
                for p in data['rootDirectory']]
            
            self.conf = [
                (
                    p['confidentiality'], 
                    p['codeSystem'], 
                    p['displayName']
                    ) 
                    for p in data['confidentialityCode']]

            self.custodian = [
                (
                    p['title'], 
                    p['oid'], 
                    p['address'], 
                    p['city'], 
                    p['county'], 
                    p['postalCode'], 
                    p['country'], 
                    p['phone'], 
                    p['use'], 
                    p['email'], 
                    p['website']
                    ) 
                    for p in data['custodian']]

    def get_headers(self):
        return self.head
    
    def get_header_type_id(self):
        return self.head_type_id

    def get_confidentiality(self):
        return self.conf
    
    def get_custodian(self):
        return self.custodian

cda_data = CDAData()


# Create the root element for the CDA document
def create_root_element():
    root = etree.Element('ClinicalDocument', xmlns="urn:hl7-org:v3", xsi="schemaLocation=http://www.w3.org/2001/XMLSchema-instance")
    add_header_elements(root)
    return root

# Add header elements required for CDA
def add_header_elements(root):

    head = cda_data.get_headers()
    head_type_id = cda_data.get_header_type_id()
    conf = cda_data.get_confidentiality()

    for extension, root_element in head_type_id:
        add_sub_element(root, 'typeId', attrib={'extension': extension, 'root': root_element})

    for displayName, code, codeSystem, codeSystemName in head:        
        add_sub_element(root, 'id', attrib={'root': '2.16.840.1.113883.19.5.99999.1'})
        add_sub_element(root, 'code', attrib={'code': code, 'codeSystem': codeSystem, 'codeSystemName': codeSystemName})
        add_sub_element(root, 'title', text=displayName)
        add_sub_element(root, 'effectiveTime', attrib={'value': datetime.now().strftime('%Y%m%d%H%M%S')})
        
    for confidentiality, codeSystem, displayName in conf:  
        add_sub_element(root, 'confidentialityCode', attrib={'code': confidentiality, 'codeSystem': codeSystem, 'displayName': displayName})



def fhir_to_cda(fhir_bundle):
    # Create CDA root element
    cda_root = create_root_element()

    # Add header information
    add_header_information(cda_root, fhir_bundle)

    # Add Allergies
    add_allergies(cda_root, fhir_bundle)

    # Add Medications
    add_medications(cda_root, fhir_bundle)

    # Add Conditions
    add_conditions(cda_root, fhir_bundle)

    # Add Procedures
    add_procedures(cda_root, fhir_bundle)

    # print(etree.tostring(cda_root, pretty_print=True, xml_declaration=True, encoding="UTF-8"))
    
    return etree.ElementTree(cda_root)


def add_header_information(cda_root, fhir_bundle):
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


def add_allergies(cda_root, fhir_bundle):
    allergies = etree.SubElement(cda_root, "allergies")
    for entry in fhir_bundle['entry']:
        if entry['resource']['resourceType'] == "AllergyIntolerance":
            allergy = etree.SubElement(allergies, "allergy")
            allergy.text = entry['resource']['code'].get('text', 'Unknown')


def add_medications(cda_root, fhir_bundle):
    medications = etree.SubElement(cda_root, "medications")
    for entry in fhir_bundle['entry']:
        if entry['resource']['resourceType'] == "MedicationStatement":
            medication = etree.SubElement(medications, "medication")
            medication.text = entry['resource']['medication'].get('code', {}).get('text', 'Unknown')


def add_conditions(cda_root, fhir_bundle):
    conditions = etree.SubElement(cda_root, "conditions")
    for entry in fhir_bundle['entry']:
        if entry['resource']['resourceType'] == "Condition":
            condition = etree.SubElement(conditions, "condition")
            condition.text = entry['resource']['code'].get('text', 'Unknown')
            
            
def add_procedures(cda_root, fhir_bundle):
    procedures = etree.SubElement(cda_root, "procedures")
    for entry in fhir_bundle['entry']:
        if entry['resource']['resourceType'] == "Procedure":
            procedure = etree.SubElement(procedures, "procedure")
            procedure.text = entry['resource']['code'].get('text', 'Unknown')


# Add different sections
# IHE Resource https://wiki.ihe.net/index.php/
# Add clinical sections filtered by patient ID with table rendering
def add_clinical_sections(cda_root, fhir_bundle):
    clinical_sections = etree.SubElement(cda_root, "clinicalSections")
    resource_types = [
        "Observation",
        "DiagnosticReport",
        "Immunization",
        "Procedure",
        "MedicationStatement",
        "Condition",
        "AllergyIntolerance"
    ]
    
    found_types = set()

    for entry in fhir_bundle['entry']:
        resource_type = entry['resource']['resourceType']
        if resource_type in resource_types:
            found_types.add(resource_type)
            clinical_section = etree.SubElement(clinical_sections, "clinicalSection")
            clinical_section.text = entry['resource']['code'].get('text', 'Unknown')

    for resource_type in resource_types:
        if resource_type not in found_types:
            clinical_section = etree.SubElement(clinical_sections, "clinicalSection")
            clinical_section.text = f"No information provided for {resource_type}"

    return etree.tostring(clinical_sections, encoding='unicode')





# Save the CDA document as an XML file
def save_cda_document(fhir_bundle):
    cda_tree = fhir_to_cda(fhir_bundle)
    file_name = "output.xml"
    cda_tree.write(file_name, pretty_print=True, xml_declaration=True, encoding='UTF-8')
    print("File saved as output.xml")

if __name__ == "__main__":
    fhir_bundle = read_fhir_bundle()
    save_cda_document(fhir_bundle)