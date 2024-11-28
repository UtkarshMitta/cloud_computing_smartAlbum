$(document).ready(function () {
    // Create a new API Gateway client instance
    var apigClient = apigClientFactory.newClient();

    // Search button click handler
    $('#searchBtn').click(function () {
        var query = $('#searchQuery').val();

        if (!query) {
            alert('Please enter a search query.');
            return;
        }

        // API parameters for the search endpoint
        var params = {
            q: query // Pass the query as a parameter
        };
        var body = {};
        var additionalParams = {
            headers: {
                'Content-Type': 'application/json'
            }
        };

        // Call the searchGet method
        apigClient.searchGet(params, body, additionalParams)
            .then(function (result) {
                console.log('Search response:', result.data.results);
                displayResults(result.data.results);
            })
            .catch(function (error) {
                console.error('Error during search:', error);
                alert('Error during search. Check the console for details.');
            });
    });

    $('#uploadBtn').click(function () {
        const fileInput = $('#photoUpload')[0];
        const customLabels = $('#customLabels').val();
    
        if (!fileInput.files.length) {
            alert('Please select a photo to upload.');
            return;
        }
    
        const file = fileInput.files[0];
        const reader = new FileReader();
    
        // Read the file as Base64
        reader.onload = function (event) {
            const base64Data = event.target.result.split(',')[1]; // Remove the "data:*/*;base64," prefix
            const fileName = file.name;
    
            const body = {
                imageData: base64Data,
                filename: fileName,
                'customLabels': customLabels,
            };
    
            const params = {
                
            };
    
            const additionalParams = {
                headers: {
                    'x-amz-meta-customlabels': customLabels || '',
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type, x-amz-meta-customLabels',
                    'Access-Control-Allow-Methods': '*',
                },
            };
    
            // Call the uploadPost method (or adjust to your API Gateway endpoint)
            apigClient.uploadPut(params, body, additionalParams)
                .then(function (result) {
                    console.log('Upload response:', result);
                    alert('Photo uploaded successfully!');
                })
                .catch(function (error) {
                    console.error('Error during upload:', error);
                    alert('Error during upload. Check the console for details.');
                });
        };
    
        // Read the file as a data URL (Base64)
        reader.readAsDataURL(file);
    });

    // Function to display search results
    function displayResults(photos) {
        const resultsDiv = $('#results');
        resultsDiv.empty(); // Clear previous results
    
        // Check if photos is an array
        if (Array.isArray(photos)) {
            photos.forEach((photo) => {
                const photoDiv = $('<div class="photo"></div>'); // Create a container div for each photo
            
                // Create an image element
                const img = $('<img>')
                    .attr('src', photo.URL) // Set the image source to photo.URL
                    .attr('alt', photo.Title || 'Photo'); // Use photo.Title for the alt attribute or a default value
            
                // Create a title element for the photo
                const title = $('<h4>')
                    .text(photo.Title || 'Untitled'); // Set the title text or use a default value
            
                // Create a labels element and format the labels as a comma-separated string
                const labels = $('<p>')
                    .text(photo.Labels ? `Labels: ${photo.Labels.join(', ')}` : 'No labels available'); // Format labels
            
                // Append the title, image, and labels to the photoDiv
                photoDiv.append(title);
                photoDiv.append(img);
                photoDiv.append(labels);
            
                // Append the photoDiv to the results container
                resultsDiv.append(photoDiv);
            });
            if (photos.length === 0) {
                resultsDiv.append('<p>No photos found.</p>');
            }
        } else {
            console.error('Invalid photos data:', photos);
            resultsDiv.append('<p>Unexpected response format.</p>');
        }
    }
});