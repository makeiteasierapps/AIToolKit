// Function to handle submitting the description
function showProgressOverlay() {
    document.getElementById('progress-overlay').classList.remove('d-none');
}

function hideProgressOverlay() {
    document.getElementById('progress-overlay').classList.add('d-none');
}

function addProgressMessage(message) {
    const messagesContainer = document.getElementById('progress-messages');
    const messageElement = document.createElement('div');
    messageElement.className = 'mb-2';
    messageElement.textContent = message;
    messagesContainer.appendChild(messageElement);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function addProgressImage(url, description) {
    const imagesContainer = document.getElementById('progress-images');
    const imageWrapper = document.createElement('div');
    imageWrapper.className = 'progress-image';
    imageWrapper.style.width = '150px';

    const img = document.createElement('img');
    img.src = url;
    img.alt = description;
    img.style.width = '100%';
    img.style.height = '100px';
    img.style.objectFit = 'cover';
    img.style.borderRadius = '4px';

    imageWrapper.appendChild(img);
    imagesContainer.appendChild(imageWrapper);
}

async function handleSubmitDescription() {
    const description = document.getElementById('website-description').value;

    if (!description) {
        alert('Please enter a description.');
        return;
    }

    try {
        // Reset progress containers
        document.getElementById('progress-messages').innerHTML = '';
        document.getElementById('progress-images').innerHTML = '';
        showProgressOverlay();

        const response = await fetch(
            'http://localhost:5000/run_site_prompting',
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    'website-description': description,
                }),
            }
        );

        if (response.ok) {
            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                // Split the chunk into individual SSE messages
                const messages = chunk
                    .split('data: ')
                    .filter((msg) => msg.trim());

                for (const msg of messages) {
                    try {
                        const jsonData = JSON.parse(msg.trim());
                        if (jsonData.type === 'progress') {
                            addProgressMessage(jsonData.message);
                        } else if (jsonData.type === 'image') {
                            addProgressImage(
                                jsonData.url,
                                jsonData.description
                            );
                        } else if (jsonData.type === 'html') {
                            updatePreviewIframe(jsonData.content);
                        }
                    } catch (e) {
                        // If not JSON, treat as HTML
                        updatePreviewIframe(msg.trim());
                    }
                }
            }
        } else {
            throw new Error('Error submitting description.');
        }
    } catch (error) {
        alert('Error submitting description. Please try again.');
    } finally {
        hideProgressOverlay();
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
