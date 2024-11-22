// Replace with your API Gateway endpoint
const apiGatewayUrl = "https://vfb11tukva.execute-api.us-east-1.amazonaws.com/dev";

// Function to handle search
$('#searchBtn').on('click', function() {
    const query = $('#searchQuery').val();
    
    if (!query) {
        alert('Please enter a search query.');
        return;
    }

    // Fetch photos based on search query
    $.ajax({
        url: `${apiGatewayUrl}/search?q=${encodeURIComponent(query)}`,
        method: 'GET',
        success: function(data) {
            console.log('Raw data received:', data);
            console.log('Data type:', typeof data);
            console.log('Data stringified:', JSON.stringify(data));
            displayResults(data);
        },
        error: function(error) {
            console.error(error);
            alert('Error fetching results.');
        }
    });
});

// Function to display results
function displayResults(data) {
    const resultsDiv = $('#results');
    resultsDiv.empty(); // Clear any previous results

    console.log('Displaying results for:', data);

    if (data && data.results && Array.isArray(data.results)) {
        data.results.forEach(photoUrl => {
            console.log('Adding image:', photoUrl);
            resultsDiv.append(`
                <div class="photo">
                    <img src="${photoUrl}" alt="Search result" onerror="this.onerror=null; this.style.display='none'; this.parentNode.innerHTML='Image could not be loaded';">
                </div>
            `);
        });

        if (data.results.length === 0) {
            resultsDiv.append('<p>No results found.</p>');
        }
    } else {
        resultsDiv.append('<p>Invalid data format received.</p>');
        console.error('Invalid data format:', data);
    }
}

// Function to handle photo upload
$('#uploadBtn').on('click', async function () {
    const fileInput = $('#photoUpload')[0];
    const labelsInput = $('#customLabels').val();
    const customLabels = labelsInput.split(',').map(label => label.trim()); // Convert to an array

    if (!fileInput.files.length) {
        alert('Please select a photo to upload.');
        return;
    }

    const file = fileInput.files[0];

    try {
        // Convert the image file to a Base64 string
        const base64Image = await convertToBase64(file);

        // Send the PUT request with customLabels in the header
        $.ajax({
            url: `${apiGatewayUrl}/upload`, // Your actual API Gateway endpoint
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json', // Set the content type
                'x-amz-meta-customLabels': customLabels.join(',') // Add custom labels as a header
            },
            data: JSON.stringify({
                filename: file.name, // Optional: include the filename
                imageData: base64Image // Base64-encoded image string
            }),
            success: function (response) {
                console.log('Custom Labels sent as header:', customLabels);
                alert('Photo uploaded successfully!');
            },
            error: function (error) {
                console.error(error);
                alert('Error uploading photo.');
            }
        });
    } catch (error) {
        console.error('Error converting file to Base64:', error);
        alert('Failed to process the photo.');
    }
});
// Function to convert a file to a Base64 string
function convertToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result.split(',')[1]); // Extract Base64 part
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}