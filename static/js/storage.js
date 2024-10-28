// Constants
const STORAGE_KEYS = {
    THUMBNAILS: 'saved_thumbnails',
    API_REQUESTS: 'api_request_count'
};
const MAX_API_REQUESTS = 10;

// Request counting functions
export function getRequestCount() {
    return parseInt(localStorage.getItem(STORAGE_KEYS.API_REQUESTS) || '0');
}

export function incrementRequestCount() {
    const currentCount = getRequestCount();
    localStorage.setItem(STORAGE_KEYS.API_REQUESTS, (currentCount + 1).toString());
}

export function checkRequestLimit() {
    const currentCount = getRequestCount();
    console.log('checkRequestLimit', currentCount);
    if (currentCount >= MAX_API_REQUESTS) {
        alert(`This is a demo version limited to ${MAX_API_REQUESTS} requests. Thank you for trying it out!`);
        return false;
    }
    return true;
}

// Thumbnail storage functions
export function saveThumbnail(thumbnailData) {
    const savedThumbnails = JSON.parse(localStorage.getItem(STORAGE_KEYS.THUMBNAILS) || '[]');
    savedThumbnails.push(thumbnailData);
    localStorage.setItem(STORAGE_KEYS.THUMBNAILS, JSON.stringify(savedThumbnails));
}

export function deleteThumbnail(thumbnailId) {
    const savedThumbnails = JSON.parse(localStorage.getItem(STORAGE_KEYS.THUMBNAILS) || '[]');
    const updatedThumbnails = savedThumbnails.filter(t => t.id !== thumbnailId);
    localStorage.setItem(STORAGE_KEYS.THUMBNAILS, JSON.stringify(updatedThumbnails));
}

export function getSavedThumbnails() {
    return JSON.parse(localStorage.getItem(STORAGE_KEYS.THUMBNAILS) || '[]');
}