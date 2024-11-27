
// Initialize the patient ID toggle

const initializePatientIdToggle = () => {
    document.getElementById('patient_list').addEventListener('change', function () {
        const customPatientIdContainer = document.getElementById('custom-patient-id-container');
        // Check if the selected value is 'custom'
        if (this.value === 'custom') {
            customPatientIdContainer.style.display = 'block';
        } else {
            customPatientIdContainer.style.display = 'none';
        }
    });

    document.getElementById('patient-form').addEventListener('submit', function (event) {
        const patientList = document.getElementById('patient_list');
        const customPatientId = document.getElementById('custom_patient_id');
        if (patientList.value === 'custom' && customPatientId.value.trim() !== '') {
            patientList.value = customPatientId.value.trim();
        }
    });
};


// render json data

const renderJson = () => {
    fetch('/hl7/patient_summary/fhir/json')
        .then(response => response.json())
        .then(data => {
            document.getElementById("json").innerHTML = JSON.stringify(data, null, 2);
        })
        .catch(error => console.error('Error fetching patient JSON:', error));
};


// toggle birth order

const toggleBirthOrder = (select) => {
    const birthOrderGroup = document.getElementById('birth_order_group');
    if (select.value === 'True') {
        birthOrderGroup.style.display = 'block';
    } else {
        birthOrderGroup.style.display = 'none';
    }
};

// Determine if date of death field is required

const showRelevantFormSection = () => {
    const resourceType = document.getElementById('resource_type').value;
    const formSections = document.getElementsByClassName('form-section');
    for (let i = 0; i < formSections.length; i++) {
        formSections[i].style.display = 'none';
    }
    if (resourceType) {
        document.getElementById(resourceType.toLowerCase() + '-form').style.display = 'block';
    }
};

// Display toggle date of death

const toggleDateOfDeath = (select) => {
    const dateOfDeathGroup = document.getElementById('date_of_death_group');
    if (select.value === 'True') {
        dateOfDeathGroup.style.display = 'block';
    } else {
        dateOfDeathGroup.style.display = 'none';
    }
};

// Display a list of languages selected for the preferred language

const updatePreferredLanguageOptions = () => {
    const checkboxes = document.querySelectorAll('input[name="languages"]:checked'); // Get all checked checkboxes
    const preferredLanguageSelect = document.getElementById('preferred_language'); // Get the preferred language select element
    preferredLanguageSelect.innerHTML = '<option value="" disabled selected>Select</option>'; // Clear the preferred language select element

    checkboxes.forEach((checkbox) => {
        const option = document.createElement('option'); // Create a new option element
        option.value = checkbox.value; // Set the option value to the checkbox value
        option.text = checkbox.nextElementSibling.textContent; // Set the option text to the checkbox label text
        preferredLanguageSelect.appendChild(option); // Append the option to the preferred language select element
    });
};

document.querySelectorAll('input[name="languages"]').forEach((checkbox) => {
    checkbox.addEventListener('change', updatePreferredLanguageOptions);
});


