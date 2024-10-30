import { deleteThumbnail, getSavedThumbnails } from './storage.js';

export async function createThumbnail(
    iframe,
    htmlContent,
    title,
    thumbnailId = 'thumbnail-' + Date.now()
) {
    const fragment = document.createDocumentFragment();

    const thumbnailWrapper = document.createElement('div');
    thumbnailWrapper.id = thumbnailId;

    const thumbnail = document.createElement('div');
    thumbnail.classList.add('thumbnail');

    const thumbnailImg = document.createElement('img');
    thumbnailImg.classList.add('thumbnail-img');
    thumbnailImg.width = 180;
    thumbnailImg.height = 135;

    const thumbnailTitle = document.createElement('p');
    thumbnailTitle.classList.add('thumbnail-title');
    thumbnailTitle.innerText = title;

    const deleteButton = document.createElement('button');
    deleteButton.classList.add('delete-button');
    deleteButton.innerHTML = '×';
    deleteButton.title = 'Delete thumbnail';
    deleteButton.onclick = (e) => {
        e.stopPropagation();
        if (confirm('Are you sure you want to delete this thumbnail?')) {
            thumbnailWrapper.remove();
            deleteThumbnail(thumbnailId);
        }
    };

    thumbnail.append(thumbnailImg, deleteButton);
    thumbnailWrapper.append(thumbnail, thumbnailTitle);
    fragment.appendChild(thumbnailWrapper);

    // Thumbnail click to update iframe
    thumbnail.addEventListener('click', () => {
        const mainIframe = document.getElementById('preview');
        mainIframe.contentWindow.document.open();
        mainIframe.contentWindow.document.write(htmlContent);
        mainIframe.contentWindow.document.close();
    });

    // Add to DOM all at once
    document.getElementById('thumbnails-container').appendChild(fragment);

    // Capture thumbnail image from iframe
    const iframeDocument = iframe.contentWindow.document;
    iframe.style.width = '1024px';
    iframe.style.height = '768px';
    const canvas = await html2canvas(iframeDocument.documentElement, {
        scale: 0.25,
    });
    thumbnailImg.src = canvas.toDataURL();

    return thumbnailWrapper;
}

// Add this function to load saved thumbnails
export async function loadSavedThumbnails() {
    const savedThumbnails = getSavedThumbnails();
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
            thumbnailData.id
        );

        iframe.contentWindow.document.close();
        thumbnail.id = thumbnailData.id;
        container.appendChild(thumbnail);
        document.body.removeChild(iframe);
    }
}
