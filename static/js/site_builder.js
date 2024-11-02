import {
  checkRequestLimit,
  incrementRequestCount,
  saveThumbnail,
} from "./storage.js";

import { createThumbnail, loadSavedThumbnails } from "./thumbnailManager.js";

let currentMessageGroup = null;

// Function to handle submitting the description
function showProgressOverlay() {
  document.getElementById("progress-overlay").classList.remove("d-none");
}

function hideProgressOverlay() {
  document.getElementById("progress-overlay").classList.add("d-none");
}

let pendingImageLoads = Promise.resolve();

async function addProgressItem(type, content, imageUrl = null) {
  const streamContainer = document.getElementById("progress-stream");

  if (type === "message") {
    if (!currentMessageGroup) {
      currentMessageGroup = document.createElement("div");
      currentMessageGroup.className = "progress-item mb-3";
      streamContainer.appendChild(currentMessageGroup);
    }

    const messageDiv = document.createElement("div");
    messageDiv.textContent = content;
    currentMessageGroup.appendChild(messageDiv);
  } else if (type === "image") {
    if (!currentMessageGroup.imageContainer) {
      currentMessageGroup.imageContainer = document.createElement("div");
      currentMessageGroup.imageContainer.className = "image-grid mt-2";
      currentMessageGroup.imageContainer.style.display = "grid";
      currentMessageGroup.imageContainer.style.gridTemplateColumns =
        "repeat(auto-fill, minmax(150px, 1fr))";
      currentMessageGroup.imageContainer.style.gap = "8px";
      currentMessageGroup.appendChild(currentMessageGroup.imageContainer);
    }

    const imageLoadPromise = new Promise((resolve, reject) => {
      const img = document.createElement("img");
      img.src = imageUrl;
      img.alt = content;
      img.style.width = "100%";
      img.style.height = "100px";
      img.style.objectFit = "cover";
      img.style.borderRadius = "4px";

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
  hideError();
  try {
    const description = document.getElementById("website-description").value;

    if (!description) {
      showError("Please enter a description.");
      return;
    }

    if (!checkRequestLimit()) {
      showError(
        "You have reached the maximum number of requests. Thank you for trying it out!"
      );
      return;
    }

    incrementRequestCount();
    // Reset progress containers
    document.getElementById("progress-stream").innerHTML = "";
    startNewMessageGroup();

    const response = await fetch("/page_builder", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
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
      const messages = chunk.split("data: ").filter((msg) => msg.trim());

      for (const msg of messages) {
        try {
          const jsonData = JSON.parse(msg.trim());

          // Handle error messages from server
          if (jsonData.type === "error") {
            showError(jsonData.message);
            return;
          }
          if (jsonData.type === "progress") {
            await pendingImageLoads; // Wait for any pending images
            await addProgressItem("message", jsonData.message);
          } else if (jsonData.type === "image") {
            await addProgressItem("image", jsonData.description, jsonData.url);
          } else if (jsonData.type === "html") {
            await pendingImageLoads;
            console.log("html", jsonData.content);
            updatePreviewIframe(jsonData.content);
          }
        } catch (e) {
          // If parsing fails, check if it's HTML content
          const trimmedMsg = msg.trim();
          if (trimmedMsg.startsWith("<")) {
            await pendingImageLoads;
            console.log("html", trimmedMsg);
            updatePreviewIframe(trimmedMsg);
          } else {
            console.error("Error parsing message:", e);
            showError("Error processing server response");
          }
        }
      }
    }
  } catch (error) {
    console.error("Error submitting description:", error);
    showError(`Failed to generate website: ${error.message}`);
  } finally {
    hideProgressOverlay();
  }
}

function updatePreviewIframe(htmlContent) {
  const iframe = document.getElementById("preview");
  iframe.contentWindow.document.open();
  iframe.contentWindow.document.write(htmlContent);
  iframe.contentWindow.document.close();
}

function download(filename, text) {
  const element = document.createElement("a");
  element.setAttribute(
    "href",
    "data:text/html;charset=utf-8," + encodeURIComponent(text)
  );
  element.setAttribute("download", filename);

  element.style.display = "none";
  document.body.appendChild(element);

  element.click();

  document.body.removeChild(element);
}

function handleSaveHtml() {
  const iframe = document.getElementById("preview");
  const htmlContent = iframe.contentWindow.document.documentElement.outerHTML;
  download("website-description.html", htmlContent);
}

async function handleSavePage() {
  const title = prompt("Enter title for the current page: ");
  if (title === null) {
    return;
  }
  const iframe = document.getElementById("preview");
  const htmlContent = iframe.contentWindow.document.documentElement.outerHTML;
  const thumbnail = await createThumbnail(iframe, htmlContent, title);
  document.getElementById("thumbnails-container").appendChild(thumbnail);

  // Save thumbnail data
  saveThumbnail({
    id: thumbnail.id,
    title: title,
    html: htmlContent,
    timestamp: Date.now(),
  });
}

document
  .getElementById("submit-description")
  .addEventListener("click", handleSubmitDescription);
document.getElementById("save-html").addEventListener("click", handleSaveHtml);
document.getElementById("save-page").addEventListener("click", handleSavePage);
document
  .querySelector(".thumbnails-toggle")
  .addEventListener("click", function () {
    const wrapper = this.closest(".thumbnails-wrapper");
    wrapper.classList.toggle("collapsed");
  });
document
  .querySelector(".error-container .btn-close")
  .addEventListener("click", hideError);
loadSavedThumbnails();
