export const SPINNER_TEMPLATE = `
    <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
    </div>
`;

// Thumbnail storage functions
export async function saveThumbnail(thumbnailData) {
    const response = await fetch('/thumbnails', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(thumbnailData),
    });
    return response.json();
}

export async function deleteThumbnail(thumbnailId) {
    await fetch(`/thumbnails/${thumbnailId}`, {
        method: 'DELETE',
    });
}

async function getSavedThumbnails() {
    const response = await fetch('/thumbnails');
    const data = await response.json();
    return data;
}

export async function createThumbnail(iframe, htmlContent, title) {
    const thumbnailId = Array.from({ length: 24 }, () =>
        Math.floor(Math.random() * 16).toString(16)
    ).join('');
    // Clone the template
    const template = document.getElementById('thumbnail-template');
    const thumbnailWrapper = template.content
        .cloneNode(true)
        .querySelector('.thumbnail-wrapper');
    thumbnailWrapper.id = thumbnailId;

    // Get elements
    const thumbnailImg = thumbnailWrapper.querySelector('.thumbnail-img');
    const spinner = thumbnailWrapper.querySelector('.spinner-border');
    const deleteButton = thumbnailWrapper.querySelector('.delete-button');
    const thumbnailTitle = thumbnailWrapper.querySelector('.thumbnail-title');

    // Set up image load handler
    thumbnailImg.onload = () => {
        spinner.remove();
        thumbnailImg.style.display = 'block';
    };

    // Set up delete handler
    deleteButton.onclick = (e) => {
        e.stopPropagation();
        if (confirm('Are you sure you want to delete this thumbnail?')) {
            thumbnailWrapper.remove();
            deleteThumbnail(thumbnailId);
        }
    };

    // Set title
    thumbnailTitle.innerText = title;

    // Set up click handler
    thumbnailWrapper
        .querySelector('.thumbnail')
        .addEventListener('click', () => {
            const mainIframe = document.getElementById('preview');
            mainIframe.contentWindow.document.open();
            mainIframe.contentWindow.document.write(htmlContent);
            mainIframe.contentWindow.document.close();
        });

    // Add to DOM
    document
        .getElementById('thumbnails-container')
        .appendChild(thumbnailWrapper);

    // Capture thumbnail image from iframe
    const iframeDocument = iframe.contentWindow.document;
    iframe.style.width = '1920px';
    iframe.style.height = '1080px';

    // Wait for iframe content to fully load
    await new Promise((resolve) => {
        iframe.onload = resolve;
        // Also wait for all images to load
        Promise.all(
            Array.from(iframeDocument.images).map((img) => {
                if (img.complete) return Promise.resolve();
                return new Promise((resolve) => {
                    img.onload = resolve;
                    img.onerror = resolve; // Handle failed image loads
                });
            })
        ).then(resolve);
    });

    // Add a small delay to ensure everything is rendered
    await new Promise((resolve) => setTimeout(resolve, 500));

    const canvas = await html2canvas(iframeDocument.documentElement, {
        scale: 0.25,
        windowWidth: 1920,
        windowHeight: 1080,
        useCORS: true, // Allow cross-origin images
        allowTaint: true, // Allow cross-origin images to taint canvas
    });
    thumbnailImg.src = canvas.toDataURL();

    return thumbnailWrapper;
}

export async function loadSavedThumbnails() {
    const savedThumbnails = await getSavedThumbnails();
    const container = document.getElementById('thumbnails-container');

    for (const thumbnailData of savedThumbnails) {
        // Create a temporary iframe to generate the thumbnail
        const iframe = document.createElement('iframe');
        document.body.appendChild(iframe);
        iframe.contentWindow.document.open();
        iframe.contentWindow.document.write(thumbnailData.html);
        const thumbnail = await createThumbnail(
            iframe,
            thumbnailData.html,
            thumbnailData.title,
            thumbnailData._id
        );

        iframe.contentWindow.document.close();
        thumbnail.id = thumbnailData.id;
        container.appendChild(thumbnail);
        document.body.removeChild(iframe);
    }
}
