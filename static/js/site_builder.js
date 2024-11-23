import {
    checkRequestLimit,
    incrementRequestCount,
    saveThumbnail,
} from './storage.js';

import { createThumbnail, loadSavedThumbnails } from './thumbnailManager.js';

let currentMessageGroup = null;

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
    const submitButton = document.getElementById('submit-description');
    submitButton.disabled = true;
    hideError();
    try {
        const description = document.getElementById(
            'website-description'
        ).value;

        if (!description) {
            showError('Please enter a description.');
            return;
        }

        if (!checkRequestLimit()) {
            showError(
                'You have reached the maximum number of requests. Thank you for trying it out!'
            );
            return;
        }

        incrementRequestCount();
        // Reset progress containers
        document.getElementById('progress-stream').innerHTML = '';
        startNewMessageGroup();
        const response = await fetch('/test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                website_description: description,
            }),
        });

        if (!response.ok) {
            throw new Error(
                `Server returned ${response.status}: ${response.statusText}`
            );
        }

        showProgressOverlay();
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            // Split the chunk into individual SSE messages
            const messages = chunk.split('data: ').filter((msg) => msg.trim());

            for (const msg of messages) {
                try {
                    const jsonData = JSON.parse(msg.trim());
                    switch (jsonData.type) {
                        case 'error':
                            showError(jsonData.message);
                            return;

                        case 'progress':
                            await pendingImageLoads;
                            await addProgressItem('message', jsonData.message);
                            break;

                        case 'section_complete':
                            console.log('Section Complete:', jsonData.content);
                            await pendingImageLoads;
                            // Update the preview with the intermediate component
                            updatePreviewIframe(jsonData.content);
                            break;

                        case 'component_complete':
                            console.log('Component Complete', jsonData.content);
                            await pendingImageLoads;
                            updatePreviewIframe(jsonData.content);
                            await addProgressItem(
                                'message',
                                'Component build complete!'
                            );
                            break;

                        case 'image':
                            await addProgressItem(
                                'image',
                                jsonData.description,
                                jsonData.url
                            );
                            break;
                    }
                } catch (e) {
                    console.error(
                        'Error processing message:',
                        e,
                        '\nMessage was:',
                        msg
                    );
                    showError('Error processing server response');
                }
            }
        }
    } catch (error) {
        console.error('Error submitting description:', error);
        showError(`Failed to generate website: ${error.message}`);
    } finally {
        submitButton.disabled = false;
        document.getElementById('website-description').value = '';
        hideProgressOverlay();
    }
}

function updatePreviewIframe(htmlContent) {
    const iframe = document.getElementById('preview');
    iframe.contentWindow.document.open();
    iframe.contentWindow.document.write(htmlContent);
    iframe.contentWindow.document.close();
}

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

function handleSaveHtml() {
    const iframe = document.getElementById('preview');
    const htmlContent = iframe.contentWindow.document.documentElement.outerHTML;
    download('website-description.html', htmlContent);
}

async function handleSavePage() {
    const title = prompt('Enter title for the current page: ');
    if (title === null) {
        return;
    }

    const saveOverlay = document.getElementById('save-overlay');
    saveOverlay.classList.remove('d-none');

    try {
        const iframe = document.getElementById('preview');
        const htmlContent =
            iframe.contentWindow.document.documentElement.outerHTML;
        const thumbnail = await createThumbnail(iframe, htmlContent, title);
        document.getElementById('thumbnails-container').appendChild(thumbnail);

        saveThumbnail({
            id: thumbnail.id,
            title: title,
            html: htmlContent,
            timestamp: Date.now(),
        });

        updatePreviewIframe('');
    } finally {
        saveOverlay.classList.add('d-none');
    }
}

function handleDescriptionInput() {
    const description = document.getElementById('website-description').value;
    const submitButton = document.getElementById('submit-description');
    const shouldBeDisabled = !description.trim();
    submitButton.disabled = shouldBeDisabled;
}

function initializeEventListeners() {
    const textarea = document.getElementById('website-description');
    if (textarea) {
        textarea.addEventListener('input', handleDescriptionInput);
        handleDescriptionInput();
    } else {
        console.error('Textarea not found!');
    }

    document
        .getElementById('submit-description')
        .addEventListener('click', handleSubmitDescription);
    document
        .getElementById('save-html')
        .addEventListener('click', handleSaveHtml);
    document
        .getElementById('save-page')
        .addEventListener('click', handleSavePage);
    document
        .querySelector('.thumbnails-toggle')
        .addEventListener('click', function () {
            const wrapper = this.closest('.thumbnails-wrapper');
            wrapper.classList.toggle('collapsed');
        });
    document
        .querySelector('.error-container .btn-close')
        .addEventListener('click', hideError);
}

document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    loadSavedThumbnails();
});
