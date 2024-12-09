import { showError } from './utils.js';
class PageBuilder {
    constructor() {
        this.pendingImageLoads = Promise.resolve();
        this.currentMessageGroup = null;
        this.iframe = document.getElementById('preview');
        this.streamContainer = document.getElementById('progress-stream');
    }

    updatePreviewIframe(htmlContent) {
        this.iframe.contentWindow.document.open();
        this.iframe.contentWindow.document.write(htmlContent);
        this.iframe.contentWindow.document.close();
    }

    async buildPage(description) {
        try {
            this.showProgressOverlay();
            const fetchOptions = {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ website_description: description }),
            };

            const response = await fetch('/page_builder', fetchOptions);
            if (!response.ok) {
                const errorData = await response.json();
                showError(errorData.message);
                throw new Error(errorData.message);
            }

            await this.processStream(response.body.getReader());
        } catch (error) {
            console.error('Stream failed:', error);
            showError(
                error.message || 'An error occurred while building the page'
            );
            throw error;
        } finally {
            this.hideProgressOverlay();
        }
    }

    async processStream(reader) {
        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const messages = decoder.decode(value).split('\n\n');
            for (const message of messages) {
                if (!message.trim() || !message.startsWith('data: ')) continue;
                await this.handleMessage(message);
            }
        }
    }

    async handleMessage(message) {
        try {
            const jsonData = JSON.parse(message.replace('data: ', ''));
            this.startNewMessageGroup();
            await this.processMessageType(jsonData);
        } catch (error) {
            console.error('Error parsing SSE data:', error);
            throw error;
        }
    }

    async processMessageType(jsonData) {
        switch (jsonData.type) {
            case 'error':
                showError(jsonData.message);
                throw new Error(jsonData.message);

            case 'info':
                await this.addProgressItem(
                    'message',
                    `You have ${jsonData.remaining_requests} requests remaining`
                );
                break;

            case 'progress':
                await this.pendingImageLoads;
                await this.addProgressItem('message', jsonData.message);
                break;

            case 'section_complete':
            case 'component_complete':
                await this.pendingImageLoads;
                this.updatePreviewIframe(jsonData.content);
                if (jsonData.type === 'component_complete') {
                    await this.addProgressItem(
                        'message',
                        'Component build complete!'
                    );
                    return;
                }
                break;

            case 'image':
                await this.addProgressItem(
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

    // UI Methods
    showProgressOverlay() {
        document.getElementById('progress-overlay').classList.remove('d-none');
    }

    hideProgressOverlay() {
        document.getElementById('progress-overlay').classList.add('d-none');
    }

    startNewMessageGroup() {
        this.currentMessageGroup = null;
    }

    async addProgressItem(type, content, imageUrl = null) {
        if (type === 'message') {
            await this.addMessageItem(content);
        } else if (type === 'image') {
            await this.addImageItem(content, imageUrl);
        }
        this.streamContainer.scrollTop = this.streamContainer.scrollHeight;
    }

    async addMessageItem(content) {
        if (!this.currentMessageGroup) {
            this.currentMessageGroup = document.createElement('div');
            this.currentMessageGroup.className = 'message-group mb-3';
            this.streamContainer.appendChild(this.currentMessageGroup);
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = 'message-item';
        messageDiv.textContent = content;
        this.currentMessageGroup.appendChild(messageDiv);
    }

    async addImageItem(description, imageUrl) {
        const imageContainer = document.createElement('div');
        imageContainer.className = 'image-container mb-3';

        const imageElement = document.createElement('img');
        imageElement.className = 'generated-image img-fluid';
        imageElement.alt = description;

        const imageLoadPromise = new Promise((resolve, reject) => {
            imageElement.onload = resolve;
            imageElement.onerror = reject;
            imageElement.src = imageUrl;
        });

        const descriptionDiv = document.createElement('div');
        descriptionDiv.className = 'image-description mt-2';
        descriptionDiv.textContent = description;

        imageContainer.appendChild(imageElement);
        imageContainer.appendChild(descriptionDiv);
        this.streamContainer.appendChild(imageContainer);

        // Update the pending image loads promise
        this.pendingImageLoads = imageLoadPromise;
        await this.pendingImageLoads;
    }
}

// Export a singleton instance
export const pageBuilder = new PageBuilder();
