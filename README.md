# FHIR Patient Summary Application

The live site is on Heroku at https://ddeveloper72-fhir-app-2d30b05e8d2c.herokuapp.com/

## Purpose

The FHIR Patient Summary Development Application is designed to create a FHIR patient document bundle, which is presented as a JSON file. This application also aims to convert the FHIR patient summary into an HL7 level 3 CDA document.

🚧 The conversion to HL7 CDA is currently a work in progress.

![Landing Page](https://github.com/ddeveloper72/fhir-patient-summary/blob/main/static/img/readme/landing_page.png 'Landing Page')

## CRUD Features

- Generate a sample patient document bundle as a FHIR bundle.
- Find HL7 FHIR Patient Information on the [FHIR HAPI test server](https://hapi.fhir.org/) using this app.
- View the FHIR Patient information as JSON and a portion of it rendered as a simple HTML list, created by other developers also working with the FHIR HAPI Server to develop their own CRUD functions/applications.
- Edit a portion of the patient information viewable from the list, in a form and then save those changes.
- View the new changes that were made, retrieved from the FHIR HAPI test server.
- **Note** The synthetic patient information from the FHIR HAPI server belongs to other fellow developers. It would be best practice to only carry out CRUD operations on ones own material.
- Convert the FHIR JSON bundle into an HL7 CDA document (work in progress).
- I will need to revisit application which creates the FHIR document bundle, to flesh it our further with additional synthetic clinical information that would be present in the original electronic health record.

### Picking a patient ID from a list

Note that this app returns a list of the last updated patient IDs, which can then be selected from a drop-down.
I have included an option to provide a specific ID, if known.

![Search for Patient ID](https://github.com/ddeveloper72/fhir-patient-summary/blob/main/static/img/readme/search_pid.png 'Patient ID')

### Viewing Patient Information

Note that the HAPI FHIR server serves the global public.  The patient IDs have been generated by developers in the global coding community.

![Patient Information](https://github.com/ddeveloper72/fhir-patient-summary/blob/main/static/img/readme/view_patient_info.png 'Patient Information')

### Editing Patient Information

A sample data-set is rendered by this application. In some instances, the data set may not comply to the FHIR guidelines for a patient summary, in which case, the app should fail gracefully with an error code of why the data set can not be opened in the editor.  When running the application locally with a .env file, I prefer to see more detailed information about these errors, so I allow jinja to render the error instead. 

![Edit Patient Information](https://github.com/ddeveloper72/fhir-patient-summary/blob/main/static/img/readme/edit_form_data.png 'Edit Patient Information')

### Creating a New Patient


![Create a New Patient](https://github.com/ddeveloper72/fhir-patient-summary/blob/main/static/img/readme/new_patient_form_data.png 'Add New Patient Information')

### 🚧 Deleting a Patient 🚧

I've not implemented this yet.  I want to only delete the Patients that I create and not those created by other developers.

### 🚧 Work in Progress

The application is currently being extended to convert the FHIR JSON bundle into an HL7 CDA-3 document. This feature is still under development and will be available in future updates.

### How to Run

1. Clone the repository
2. Install the required dependencies using pip install -r requirements.txt.
3. Run the application using python app.py.
4. Access the application in your web browser at http://localhost:5000.

### Resources

- Resource profile for HL7 FHIR Patient Summary [International Patient Summary Implementation Guide](https://build.fhir.org/ig/HL7/fhir-ips/StructureDefinition-Patient-uv-ips.html)
- Artifacts Summary for HL7 FHIR documents [Artifacts Summary](https://build.fhir.org/ig/HL7/fhir-ips/artifacts.html)
- [HAPI FHIR Bundle Builder (JavaDoc)](https://build.fhir.org/ig/HL7/fhir-ips/artifacts.html)
- HAPI FHIR [Test Server](https://hapi.fhir.org/)
- Python HL7 FHIR, [fhir.resources 7.1.0](https://pypi.org/project/fhir.resources/)