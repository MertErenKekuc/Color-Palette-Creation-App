// script.js

document.addEventListener('DOMContentLoaded', function () {
    console.log('JavaScript loaded successfully.');

    // Add custom interactivity if needed
    const alertButtons = document.querySelectorAll('.alert-button');
    alertButtons.forEach(button => {
        button.addEventListener('click', function () {
            alert('Button clicked!');
        });
    });

    const fileInput = document.querySelector('#image');
    if (fileInput) {
        fileInput.addEventListener('change', function () {
            const fileName = fileInput.files[0].name;
            alert('File selected: ' + fileName);
        });
    }
});