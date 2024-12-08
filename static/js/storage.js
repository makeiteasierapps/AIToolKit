export async function buildPage(description) {
    const response = await fetch('/page_builder', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ website_description: description }),
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const messages = decoder.decode(value).split('\n\n');
        for (const message of messages) {
            if (!message.trim()) continue;

            const jsonData = JSON.parse(message.replace('data: ', ''));

            switch (jsonData.type) {
                case 'error':
                    showError(jsonData.message);
                    return;

                case 'info':
                    // Handle remaining requests info
                    await addProgressItem(
                        'message',
                        `You have ${jsonData.remaining_requests} requests remaining`
                    );
                    break;

                case 'progress':
                    await pendingImageLoads;
                    await addProgressItem('message', jsonData.message);
                    break;

                case 'section_complete':
                    console.log('Section Complete:', jsonData.content);
                    await pendingImageLoads;
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

                default:
                    console.log('Unknown message type:', jsonData);
                    break;
            }
        }
    }
}

// Thumbnail storage functions
export async function saveThumbnail(thumbnailData) {
    const response = await fetch('/api/thumbnails', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(thumbnailData),
    });
    return response.json();
}

export async function deleteThumbnail(thumbnailId) {
    await fetch(`/api/thumbnails/${thumbnailId}`, {
        method: 'DELETE',
    });
}

export async function getSavedThumbnails() {
    const response = await fetch('/api/thumbnails');
    return response.json();
}

let pendingImageLoads = Promise.resolve();
let currentMessageGroup = null;

// Function to handle submitting the description
export function showProgressOverlay() {
    document.getElementById('progress-overlay').classList.remove('d-none');
}

export function hideProgressOverlay() {
    document.getElementById('progress-overlay').classList.add('d-none');
}

export function startNewMessageGroup() {
    currentMessageGroup = null;
}

export async function addProgressItem(type, content, imageUrl = null) {
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
