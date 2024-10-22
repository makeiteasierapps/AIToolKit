// Function to handle submitting the description
async function handleSubmitDescription() {
    // Get the value of the 'website-description' input field
    const description = document.getElementById('website-description').value;

    // Check if the description is empty, show an alert if it is
    if (!description) {
        alert('Please enter a description.');
        return;
    }

    // Send a POST request with the description to the server
    try {
        const response = await fetch('http://localhost:5000/run_site_prompting', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                'website-description': description,
            }),
        });

        // If the response is OK, update the 'preview' iframe with the generated HTML content
        if (response.ok) {
            const htmlContent = await response.text();
            updatePreviewIframe(htmlContent);
        } else {
            throw new Error('Error submitting description.');
        }
    } catch (error) {
        alert('Error submitting description. Please try again.');
    }
}

// Function to update the 'preview' iframe with given HTML content
function updatePreviewIframe(htmlContent) {
    const iframe = document.getElementById('preview');
    iframe.contentWindow.document.open();
    iframe.contentWindow.document.write(htmlContent);
    iframe.contentWindow.document.close();
}

// Function to download the generated HTML content as a file
function download(filename, text) {
    const element = document.createElement('a');
    element.setAttribute(
        'href',
        'data:text/html;charset=utf-8,' + encodeURIComponent(text)
    );
    element.setAttribute('download', filename);

    element.style.display = 'none';
    document.body.appendChild(element);

    element.click();

    document.body.removeChild(element);
}

// Function to save the generated HTML content as a file
function handleSaveHtml() {
    const iframe = document.getElementById('preview');
    const htmlContent = iframe.contentWindow.document.documentElement.outerHTML;
    download('website-description.html', htmlContent);
}

// Function to create a thumbnail of the current page
async function createThumbnail(iframe, htmlContent) {
    const title = prompt('Enter title for the current page: ');
    if (title === null) {
        return;
    }

    const thumbnailWrapper = document.createElement('div');
    const thumbnail = document.createElement('div');
    const thumbnailImg = document.createElement('img');
    const thumbnailTitle = document.createElement('p');

    thumbnail.classList.add('thumbnail');
    thumbnailImg.classList.add('thumbnail-img');

    // Add the title and style it
    thumbnailTitle.innerText = title;
    thumbnailTitle.style.textAlign = 'center';
    thumbnailTitle.style.marginTop = '5px';
    thumbnailTitle.style.fontSize = '14px';
    thumbnailTitle.style.color = '#fff';

    thumbnailWrapper.appendChild(thumbnailTitle);
    thumbnail.appendChild(thumbnailImg);
    thumbnailWrapper.appendChild(thumbnail);

    thumbnail.addEventListener('click', () => {
        const mainIframe = document.getElementById('preview');
        mainIframe.contentWindow.document.open();
        mainIframe.contentWindow.document.write(htmlContent);
        mainIframe.contentWindow.document.close();
    });

    const iframeDocument = iframe.contentWindow.document;
    const canvas = await html2canvas(iframeDocument.documentElement, {
        scale: 0.25,
    });
    const dataURL = canvas.toDataURL();

    thumbnailImg.width = 180;
    thumbnailImg.height = 135;
    thumbnailImg.src = dataURL;

    return thumbnailWrapper;
}

// Function to save the current page and create a thumbnail
async function handleSavePage() {
    const iframe = document.getElementById('preview');
    const htmlContent = iframe.contentWindow.document.documentElement.outerHTML;
    const thumbnail = await createThumbnail(iframe, htmlContent);
    document.getElementById('thumbnails-container').appendChild(thumbnail);

    // Clear the description input field and iframe
    document.getElementById('website-description').value = 'Go Again?';
    iframe.contentWindow.document.open();
    iframe.contentWindow.document.write(
        `<html><head></head><body style="display: flex; align-items: center; justify-content: center; font-family: Arial, sans-serif; font-size: 24px; color: #fff;">Let's Create Your Next Page</body></html>`
    );
    iframe.contentWindow.document.close();
}

// Add event listeners to the respective buttons
document
    .getElementById('submit-description')
    .addEventListener('click', handleSubmitDescription);
document.getElementById('save-html').addEventListener('click', handleSaveHtml);
document.getElementById('save-page').addEventListener('click', handleSavePage);
