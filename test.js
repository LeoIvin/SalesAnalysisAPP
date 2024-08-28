document.getElementById('uploadForm').addEventListener('submit', function(event) {
    var fileInput = document.getElementById('fileInput');
    var errorMessage = document.getElementById('error-message');
    

    // Clear previous error message
    errorMessage.textContent = '';


    if (fileInput.files.length < 1) {
        event.preventDefault(); // Prevent form submission
        console.log("Nothing was uploaded");
        errorMessage.textContent = "You have not selected any file!";
    } else {
        console.log('File uploaded');
        fileName.textContent = fileInput.files.name;
    }
});

function getFileName() {
    var fileNameDisplay = document.getElementById('file-name');
    var fileInput = document.getElementById('fileInput');

    // Clear previous file name
    fileNameDisplay.textContent = '';

    if (fileInput.files.length >= 1) {
        var fileName = fileInput.files[0].name; // Access the name of the first file
        //var fileSize = fileInput.files[0].size;
        console.log('File uploaded' + fileName);
        fileNameDisplay.textContent = "Selected File: " + fileName;
    }

}