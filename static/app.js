// static/app.js

document.getElementById("configForm").addEventListener("submit", function(event) {
    event.preventDefault();  // Prevent the form from submitting traditionally

    // Collect selected genders for performers and studios separately
    const selectedPerformersGenders = [];
    const performerGenderCheckboxes = document.querySelectorAll('input[name="excludePerformerGender"]:checked');
    performerGenderCheckboxes.forEach(checkbox => selectedPerformersGenders.push(checkbox.value));

    const selectedStudiosGenders = [];
    const studioGenderCheckboxes = document.querySelectorAll('input[name="excludeStudioGender"]:checked');
    studioGenderCheckboxes.forEach(checkbox => selectedStudiosGenders.push(checkbox.value));


    // Get the cron expression
    const cronExpression = document.getElementById("cronExpression").value;

    // Validate the cron expression
    if (!isCronValid(cronExpression)) {
        document.getElementById("response").textContent = "Invalid cron expression. Please enter a valid cron expression.";
        document.getElementById("response").style.color = "red";
        return;
    }

    // Prepare form data
    const formData = {
        settings: {
            stashdbApiKey: document.getElementById("stashdbApiKey").value,
            whisparrApiKey: document.getElementById("whisparrApiKey").value,
            whisparrUrl: document.getElementById("whisparrUrl").value,
            rootFolderPath: document.getElementById("rootFolderPath").value,
            tagsToAdd: document.getElementById("tagsToAdd").value.split(',').map(tag => tag.trim()),
            cronExpression: cronExpression
        },

        performers: {
            excludeGender: selectedPerformersGenders,
            tagsInclude: document.getElementById("performerTagsInclude").value.split(',').map(tag => tag.trim()),
            tagsExclude: document.getElementById("performerTagsExclude").value.split(',').map(tag => tag.trim()),
            studiosInclude: document.getElementById("studiosInclude").value.split(',').map(tag => tag.trim()),
            studiosExclude: document.getElementById("studiosExclude").value.split(',').map(tag => tag.trim())
        },
        studios: {
            excludeGender: selectedStudiosGenders,
            tagsInclude: document.getElementById("studioTagsInclude").value.split(',').map(tag => tag.trim()),
            tagsExclude: document.getElementById("studioTagsExclude").value.split(',').map(tag => tag.trim())
        }
    };

    // Send data to the server
    fetch('/process', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("response").textContent = "Settings saved. Cron job scheduled.";
        document.getElementById("response").style.color = "green";
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById("response").textContent = "An error occurred. Please try again.";
        document.getElementById("response").style.color = "red";
    });
});

function isCronValid(freq) {
    var cronregex = new RegExp(/^(\*|([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])|\*\/([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])) (\*|([0-9]|1[0-9]|2[0-3])|\*\/([0-9]|1[0-9]|2[0-3])) (\*|([1-9]|1[0-9]|2[0-9]|3[0-1])|\*\/([1-9]|1[0-9]|2[0-9]|3[0-1])) (\*|([1-9]|1[0-2])|\*\/([1-9]|1[0-2])) (\*|([0-6])|\*\/([0-6]))$/);
    return cronregex.test(freq);
  }
