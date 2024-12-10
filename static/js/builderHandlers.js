import { pageBuilder } from "./components/PageBuilder.js";
import {
  createThumbnail,
  loadSavedThumbnails,
  saveThumbnail,
} from "./thumbnailManager.js";
import { showError, hideError } from "./utils/utils.js";

async function handleSubmitDescription() {
  const submitButton = document.getElementById("submit-description");
  submitButton.disabled = true;
  try {
    const description = document.getElementById("website-description").value;

    if (!description) {
      showError("Please enter a description.");
      return;
    }

    // Reset progress containers
    document.getElementById("progress-stream").innerHTML = "";
    await pageBuilder.buildPage(description);
  } catch (error) {
    console.error("Error submitting description:", error);
    showError(`Failed to generate website: ${error.message}`);
  } finally {
    submitButton.disabled = false;
    document.getElementById("website-description").value = "";
  }
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

  const saveOverlay = document.getElementById("save-overlay");
  saveOverlay.classList.remove("d-none");

  try {
    const iframe = document.getElementById("preview");
    const htmlContent = iframe.contentWindow.document.documentElement.outerHTML;
    const thumbnail = await createThumbnail(iframe, htmlContent, title);
    document.getElementById("thumbnails-container").appendChild(thumbnail);

    saveThumbnail({
      id: thumbnail.id,
      title: title,
      html: htmlContent,
      timestamp: Date.now(),
    });

    pageBuilder.updatePreviewIframe("");
  } finally {
    saveOverlay.classList.add("d-none");
  }
}

function handleDescriptionInput() {
  const description = document.getElementById("website-description").value;
  const submitButton = document.getElementById("submit-description");
  const shouldBeDisabled = !description.trim();
  submitButton.disabled = shouldBeDisabled;
}

function initializeEventListeners() {
  const textarea = document.getElementById("website-description");
  if (textarea) {
    textarea.addEventListener("input", handleDescriptionInput);
    handleDescriptionInput();
  } else {
    console.error("Textarea not found!");
  }

  document
    .getElementById("submit-description")
    .addEventListener("click", handleSubmitDescription);
  document
    .getElementById("save-html")
    .addEventListener("click", handleSaveHtml);
  document
    .getElementById("save-page")
    .addEventListener("click", handleSavePage);
  document
    .querySelector(".thumbnails-toggle")
    .addEventListener("click", function () {
      const wrapper = this.closest(".thumbnails-wrapper");
      wrapper.classList.toggle("collapsed");
    });
  document
    .querySelector(".error-container .btn-close")
    .addEventListener("click", hideError);
}

document.addEventListener("DOMContentLoaded", () => {
  initializeEventListeners();
  loadSavedThumbnails();
});
