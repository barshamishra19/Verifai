// File Upload Logic
document.getElementById('video-input').addEventListener('change', () => {
    document.getElementById('analyze-btn').classList.remove('hidden');
    document.querySelector('.drop-zone p').innerText = "File Selected";
});

document.getElementById('analyze-btn').addEventListener('click', async () => {
    // ... (Existing Upload Logic)
    const videoInput = document.getElementById('video-input');
    if (videoInput.files.length === 0) return;

    startLoading();

    const formData = new FormData();
    formData.append('file', videoInput.files[0]);

    try {
        const response = await fetch('http://localhost:8000/api/analyze', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        showResults(result);
    } catch (error) {
        handleError(error);
    }
});

// Scan Page Logic
document.getElementById('scan-btn').addEventListener('click', async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    if (!tab) {
        alert("No active tab found.");
        return;
    }

    startLoading();

    try {
        const url = tab.url.toLowerCase();
        const isSocialMedia = ['youtube.com', 'youtu.be', 'tiktok.com', 'instagram.com', 'twitter.com', 'x.com'].some(s => url.includes(s));

        let videoUrl = null;

        if (isSocialMedia) {
            // For social media, the page URL IS the video URL for yt-dlp
            videoUrl = tab.url;
            console.log("Social media detected, using Page URL:", videoUrl);
        } else {
            // Execute script to find video for static sites
            const injectionResults = await chrome.scripting.executeScript({
                target: { tabId: tab.id },
                func: () => {
                    const v = document.querySelector('video');
                    if (v) return v.src || (v.querySelector('source') ? v.querySelector('source').src : null);

                    // Fallback for sites that might hide video tags
                    const iframe = document.querySelector('iframe[src*="video"], iframe[src*="embed"]');
                    if (iframe) return iframe.src;

                    return null;
                }
            });
            videoUrl = injectionResults[0].result;
        }

        if (!videoUrl || videoUrl.startsWith('blob:')) {
            const msg = videoUrl?.startsWith('blob:')
                ? "This video format (blob) is protected and cannot be scanned directly. Try scanning the main page URL instead."
                : "No scanable video found on this page.";
            alert(msg);
            resetUI();
            return;
        }

        // Send URL to Backend
        const response = await fetch('http://localhost:8000/api/analyze_url', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: videoUrl })
        });

        if (!response.ok) throw new Error("Backend failed to download/analyze");

        const result = await response.json();
        showResults(result);

    } catch (error) {
        handleError(error);
    }
});

function startLoading() {
    document.getElementById('upload-view').classList.add('hidden');
    document.getElementById('loading-view').classList.remove('hidden');
}

function handleError(error) {
    alert("Error: " + error.message);
    console.error(error);
    resetUI();
}

// ... (Rest of existing code)

function showResults(data) {
    document.getElementById('loading-view').classList.add('hidden');
    document.getElementById('result-view').classList.remove('hidden');

    const badge = document.getElementById('verdict-badge');
    badge.innerText = data.classification;
    badge.className = data.classification === "AI-Generated" ? "ai-bad" : "real-good";

    document.getElementById('score-pct').innerText = (data.final_confidence * 100).toFixed(1) + "%";

    const evidenceList = document.getElementById('evidence-container');
    evidenceList.innerHTML = "<strong>Evidence Found:</strong><br>";
    data.evidence.forEach(ev => {
        const div = document.createElement('div');
        div.style.marginBottom = "8px";
        div.innerHTML = `• <b>${ev.type}:</b> ${ev.explanation}`;
        evidenceList.appendChild(div);
    });
}

function resetUI() {
    document.getElementById('upload-view').classList.remove('hidden');
    document.getElementById('loading-view').classList.add('hidden');
    document.getElementById('result-view').classList.add('hidden');
}

document.getElementById('reset-btn').addEventListener('click', resetUI);