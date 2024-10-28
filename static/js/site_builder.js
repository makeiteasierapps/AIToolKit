// Function to handle submitting the description
function showProgressOverlay() {
    document.getElementById('progress-overlay').classList.remove('d-none');
}

function hideProgressOverlay() {
    document.getElementById('progress-overlay').classList.add('d-none');
}

let pendingImageLoads = Promise.resolve();

async function addProgressItem(type, content, imageUrl = null) {
    const streamContainer = document.getElementById('progress-stream');

    if (type === 'message') {
        if (!currentMessageGroup) {
            currentMessageGroup = document.createElement('div');
            currentMessageGroup.className = 'progress-item mb-3';
            streamContainer.appendChild(currentMessageGroup);
        }

        const messageDiv = document.createElement('div');
        messageDiv.textContent = content;
        currentMessageGroup.appendChild(messageDiv);
    } else if (type === 'image') {
        if (!currentMessageGroup.imageContainer) {
            currentMessageGroup.imageContainer = document.createElement('div');
            currentMessageGroup.imageContainer.className = 'image-grid mt-2';
            currentMessageGroup.imageContainer.style.display = 'grid';
            currentMessageGroup.imageContainer.style.gridTemplateColumns =
                'repeat(auto-fill, minmax(150px, 1fr))';
            currentMessageGroup.imageContainer.style.gap = '8px';
            currentMessageGroup.appendChild(currentMessageGroup.imageContainer);
        }

        const imageLoadPromise = new Promise((resolve, reject) => {
            const img = document.createElement('img');
            img.src = imageUrl;
            img.alt = content;
            img.style.width = '100%';
            img.style.height = '100px';
            img.style.objectFit = 'cover';
            img.style.borderRadius = '4px';

            img.onload = () => {
                currentMessageGroup.imageContainer.appendChild(img);
                resolve();
            };
            img.onerror = reject;
        });

        pendingImageLoads = pendingImageLoads.then(() => imageLoadPromise);
        return pendingImageLoads;
    }

    // Auto-scroll to the bottom
    streamContainer.scrollTop = streamContainer.scrollHeight;
}

function startNewMessageGroup() {
    currentMessageGroup = null;
}

async function handleSubmitDescription() {
    const description = document.getElementById('website-description').value;

    if (!description) {
        alert('Please enter a description.');
        return;
    }

    try {
        // Reset progress containers
        document.getElementById('progress-stream').innerHTML = '';
        startNewMessageGroup();
        showProgressOverlay();

        const response = await fetch(
            'http://127.0.0.1:5000/run_site_prompting',
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
                        console.log(jsonData);
                        if (jsonData.type === 'progress') {
                            await pendingImageLoads; // Wait for any pending images
                            await addProgressItem('message', jsonData.message);
                        } else if (jsonData.type === 'image') {
                            await addProgressItem(
                                'image',
                                jsonData.description,
                                jsonData.url
                            );
                        } else if (jsonData.type === 'html') {
                            await pendingImageLoads;
                            updatePreviewIframe(jsonData.content);
                        }
                    } catch (e) {
                        // If not JSON, treat as HTML
                        await pendingImageLoads;
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
    thumbnailTitle.classList.add('thumbnail-title');

    // Add the title and style it
    thumbnailTitle.innerText = title;

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
