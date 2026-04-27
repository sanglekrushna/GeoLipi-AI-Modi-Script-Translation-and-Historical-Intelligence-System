let map;
let markers = [];
let magicWand = false;

// Initialize Dashboard
document.addEventListener('DOMContentLoaded', () => {
    initMap();
    loadLocations();
});

function initMap() {
    map = L.map('map', {
        center: [18.5204, 73.8567],
        zoom: 7,
        zoomControl: false,
        preferCanvas: true,
        updateWhenZooming: false,
        updateWhenIdle: true,
        zoomAnimation: true,
        fadeAnimation: true
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
        maxZoom: 18,
        updateWhenIdle: true,
        keepBuffer: 2
    }).addTo(map);

    L.control.zoom({ position: 'bottomright' }).addTo(map);
}

async function loadLocations() {
    try {
        const response = await fetch('/api/sites');
        let locations = await response.json();
        
        if (!locations || locations.length === 0) {
            locations = [
                { name: "Sinhagad Fort", lat: 18.3663, lng: 73.7559, year: 1647, modi_text: "𑘭𑘱𑘽𑘮𑘐𑘞", category: "Fort", description: "Failsafe entry: Strategically important fort.", image: "/static/images/sinhagad_fort.png" }
            ];
        }

        locations.forEach(loc => {
            if (loc.lat && loc.lng) {
                const marker = L.circleMarker([parseFloat(loc.lat), parseFloat(loc.lng)], {
                    radius: 8,
                    fillColor: "#c4a962",
                    color: "#fff",
                    weight: 1,
                    opacity: 1,
                    fillOpacity: 0.8
                }).addTo(map);

                marker.bindPopup(`<b>${loc.name}</b>`);
                marker.on('click', () => {
                    marker.openPopup();
                    onMarkerClick(loc);
                });
                markers.push({ data: loc, marker: marker });
            }
        });
        
        // Initial filter application
        applyFilters();
    } catch (err) {
        console.error("Error loading locations:", err);
    }
}

function applyFilters() {
    const century = document.getElementById('century-filter').value;
    const category = document.getElementById('category-filter').value;
    
    let visibleCount = 0;
    
    markers.forEach(m => {
        const year = m.data.year;
        let cMatch = true;
        
        if (century !== 'all') {
            if (century === 'ancient') {
                cMatch = year < 1200;
            } else {
                const cNum = parseInt(century);
                cMatch = year > (cNum - 1) * 100 && year <= cNum * 100;
            }
        }
        
        let catMatch = true;
        if (category !== 'all') {
            catMatch = (m.data.category === category);
        }
        
        if (cMatch && catMatch) {
            if (!map.hasLayer(m.marker)) {
                m.marker.addTo(map);
            }
            visibleCount++;
        } else {
            if (map.hasLayer(m.marker)) {
                map.removeLayer(m.marker);
            }
        }
    });
    
    document.getElementById('site-count').innerText = visibleCount;
}

async function onMarkerClick(loc) {
    highlightMarker(loc);
    map.setView([parseFloat(loc.lat), parseFloat(loc.lng)], 16, { animate: true });
    updateRightPanel(loc);
}

function updateRightPanel(loc) {

    const panel = document.getElementById('right-panel');
    panel.style.opacity = '0';
    document.getElementById('panel-welcome').style.display = 'none';
    document.getElementById('place-data').style.display = 'block';
    
    setTimeout(() => {
        panel.style.opacity = '1';
        panel.style.transition = 'opacity 0.5s ease-in-out';
    }, 50);

    document.getElementById('place-name').innerText = loc.name;
    document.getElementById('place-year').innerText = loc.year;
    
    const imgEl = document.getElementById('place-image');
    const imageSrc = loc.image || loc.image_url || "https://via.placeholder.com/400x250?text=No+Image";
    
    imgEl.style.opacity = '0';
    imgEl.onload = () => { imgEl.style.opacity = '1'; };
    imgEl.onerror = () => { 
        imgEl.src = 'https://via.placeholder.com/600x300?text=Historical+Site+Image+Unavailable'; 
        imgEl.style.opacity = '1';
    };
    imgEl.src = imageSrc;

    const modiSection = document.getElementById('modi-section');
    if (loc.modi_text && loc.modi_text.trim() !== "") {
        modiSection.style.display = 'block';
        document.getElementById('modi-raw').innerText = loc.modi_text;
    } else {
        modiSection.style.display = 'none';
    }

    document.getElementById('dev-text').innerText = loc.devanagari || "---";
    document.getElementById('eng-text').innerText = loc.english || "---";

    // Magic Wand UI Control
    const aiInsightSection = document.getElementById('ai-insight-container');
    const nearbySection = document.getElementById('nearby-section');

    if (magicWand === true) {
        aiInsightSection.style.display = 'block';
        nearbySection.style.display = 'block';
        renderNearby(loc);
        generateInsight(loc);
    } else {
        aiInsightSection.style.display = 'none';
        nearbySection.style.display = 'none';
        clearInsight();
    }
}

function generateInsight(loc) {
    const insightText = document.getElementById('insight-text');
    insightText.innerHTML = `
        <div class="ai-loading">
            <span></span><span></span><span></span>
            Generating historical analysis...
        </div>
    `;
    
    fetch('/api/insight', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            name: loc.name,
            year: loc.year,
            description: loc.description
        })
    }).then(res => res.json()).then(data => {
        insightText.innerHTML = `<div class="ai-result">${data.insight}</div>`;
    }).catch(err => {
        // ACTUALLY show the local records if the AI fails
        const fallbackText = `🏛️ <strong>${loc.name}</strong> (${loc.year})<br><br>${loc.description}<br><br><small style='color:#7a8fa6;'>[Note: Displaying local records as AI is currently unavailable]</small>`;
        insightText.innerHTML = `<div class="ai-result">${fallbackText}</div>`;
    });
}

function clearInsight() {
    document.getElementById('insight-text').innerHTML = "";
}

function renderNearby(currentLoc) {
    const nearbyList = document.getElementById('nearby-list');
    nearbyList.innerHTML = '';
    
    const nearby = markers
        .map(m => {
            const dist = getDistance(
                currentLoc.lat, currentLoc.lng, 
                m.data.lat, m.data.lng
            );
            return { ...m.data, distance: dist };
        })
        .filter(site => site.name !== currentLoc.name && site.distance <= 5)
        .sort((a, b) => a.distance - b.distance);

    if (nearby.length === 0) {
        nearbyList.innerHTML = `
            <div class="no-sites">
                No nearby historical sites within 5 km
            </div>
        `;
        return;
    }

    nearby.forEach(site => {
        const item = document.createElement('div');
        item.className = 'nearby-card';
        item.onclick = () => focusSite(site.name);
        
        const metaStr = `${site.year || 'Unknown'} • ${site.category || 'Historical Site'}`;
        
        item.innerHTML = `
            <div class="left">
                <div class="title">${site.name}</div>
                <div class="meta">${metaStr}</div>
            </div>
            <div class="distance-badge">${site.distance.toFixed(2)} km</div>
        `;
        nearbyList.appendChild(item);
    });
}

function getDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; 
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
}

async function toggleWand() {
    const activeMarker = markers.find(m => m.marker.options.fillColor === "#ff0000");
    if (!activeMarker) {
        alert("Please select a location on the map first!");
        return;
    }

    magicWand = !magicWand;
    
    const btn = document.getElementById('wand-toggle');
    const aiInsightSection = document.getElementById('ai-insight-container');
    const nearbySection = document.getElementById('nearby-section');

    if (magicWand) {
        btn.innerText = "✨ Magic Wand: ON";
        btn.classList.add('active-wand');
        aiInsightSection.style.display = 'block';
        nearbySection.style.display = 'block';
        
        const selectedSite = activeMarker.data;
        renderNearby(selectedSite);
        generateInsight(selectedSite);
    } else {
        btn.innerText = "✨ Magic Wand: OFF";
        btn.classList.remove('active-wand');
        aiInsightSection.style.display = 'none';
        nearbySection.style.display = 'none';
        clearInsight();
    }
}

function highlightMarker(loc) {
    markers.forEach(m => {
        m.marker.setStyle({
            fillColor: "#c4a962",
            radius: 8,
            weight: 1
        });
    });

    const active = markers.find(m => m.data.name === loc.name);
    if (active) {
        active.marker.setStyle({
            fillColor: "#ff0000",
            radius: 12,
            weight: 3
        });
        active.marker.bringToFront();
    }
}

function focusSite(siteName) {
    const siteObj = markers.find(m => m.data.name === siteName);
    if (!siteObj) return;

    const site = siteObj.data;

    // move map
    map.flyTo([parseFloat(site.lat), parseFloat(site.lng)], 16, {
        animate: true,
        duration: 1.2
    });

    // open marker popup
    siteObj.marker.openPopup();

    // highlight marker
    highlightMarker(site);

    // update right panel
    updateRightPanel(site);
}

// Tab Switching Logic
function switchTab(tabName) {
    const container = document.querySelector('.dashboard-container');
    const tabs = document.querySelectorAll('.nav-item');
    const views = document.querySelectorAll('.content-view');
    
    // Update Nav
    tabs.forEach(tab => tab.classList.remove('active'));
    const activeTab = document.getElementById(`tab-${tabName}`);
    if (activeTab) activeTab.classList.add('active');

    // Update Views
    views.forEach(view => view.classList.remove('active'));
    const activeView = document.getElementById(`${tabName}-view`);
    if (activeView) activeView.classList.add('active');

    // Toggle Sidebar/Right Panel Layout
    const translatorSidebar = document.getElementById('translator-sidebar');
    const rightPanel = document.getElementById('right-panel');
    const placeData = document.getElementById('place-data');
    const panelWelcome = document.getElementById('panel-welcome');

    if (tabName === 'translator') {
        if (container) container.classList.add('translator-active');
        if (translatorSidebar) translatorSidebar.style.display = 'block';
        if (rightPanel) rightPanel.style.display = 'none';
        if (placeData) placeData.style.display = 'none';
        if (panelWelcome) panelWelcome.style.display = 'none';
        
        const placeName = document.getElementById('place-name');
        if (placeName) placeName.innerText = 'Modi Lipi Script Translator';
        
        const placeYear = document.getElementById('place-year');
        if (placeYear) placeYear.style.display = 'none';
    } else {
        if (container) container.classList.remove('translator-active');
        if (translatorSidebar) translatorSidebar.style.display = 'none';
        if (rightPanel) rightPanel.style.display = 'block';
        
        const placeYear = document.getElementById('place-year');
        if (placeYear) placeYear.style.display = 'inline-block';
        
        const activeMarker = markers.find(m => m.marker.options.fillColor === "#ff0000");
        if (activeMarker) {
            if (placeData) placeData.style.display = 'block';
            if (panelWelcome) panelWelcome.style.display = 'none';
            const placeName = document.getElementById('place-name');
            if (placeName) placeName.innerText = activeMarker.data.name;
        } else {
            if (panelWelcome) panelWelcome.style.display = 'block';
            if (placeData) placeData.style.display = 'none';
            const placeName = document.getElementById('place-name');
            if (placeName) placeName.innerText = 'Select a Location';
        }

        // Refresh map layout
        if (map) {
            setTimeout(() => { map.invalidateSize(); }, 500);
        }
    }
}
// Native Translator Functionality
async function generateInterpretation() {
    const input = document.getElementById("sourceInput").value.trim();
    const outputField = document.getElementById("englishOutput");

    if (!input) {
        alert("Please enter Modi script first.");
        return;
    }

    outputField.value = "Generating interpretation...";
    outputField.style.opacity = "0.6";

    fetch("/translate", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ text: input })
    })
    .then(res => res.json())
    .then(data => {
        console.log("TRANSLATION RESPONSE:", data);
        
        // SAFE FIX: assign output properly
        document.getElementById("englishOutput").value = data.english || "No output generated";
        outputField.style.opacity = "1";
    })
    .catch(err => {
        console.error("Translation Error:", err);
        document.getElementById("englishOutput").value = "Translation failed (check console)";
        outputField.style.opacity = "1";
    });
}



// Native OCR Functionality
let selectedOCRFile = null;

function clearOCRImage() {
    selectedOCRFile = null;
    document.getElementById('ocr-file-input').value = "";
    document.getElementById('file-preview').style.display = 'none';
    document.getElementById('drop-zone').style.display = 'block';
    document.getElementById('ocr-dev-output').value = "";
    document.getElementById('ocr-eng-output').value = "";
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        selectedOCRFile = file;
        const reader = new FileReader();
        reader.onload = (e) => {
            const preview = document.getElementById('preview-img');
            preview.src = e.target.result;
            document.getElementById('file-preview').style.display = 'block';
            document.getElementById('drop-zone').style.display = 'none';
        };
        reader.readAsDataURL(file);
    }
}


async function runNativeOCR() {
    if (!selectedOCRFile) {
        alert("Please select or drop an image first.");
        return;
    }

    const devOutput = document.getElementById('ocr-dev-output');
    const engOutput = document.getElementById('ocr-eng-output');

    devOutput.value = "Processing image...";
    engOutput.value = "Translating results...";

    const formData = new FormData();
    formData.append("image", selectedOCRFile);

    try {
        const response = await fetch("/api/ocr", {
            method: "POST",
            body: formData
        });
        
        const data = await response.json();
        console.log("OCR Response:", data);

        if (data.error) {
            devOutput.value = "Error: " + data.error;
            engOutput.value = "---";
        } else {
            devOutput.value = data.devanagari || "No text detected";
            engOutput.value = data.english || "No translation generated";
        }
    } catch (err) {
        console.error("OCR Error:", err);
        devOutput.value = "Connection Error.";
        engOutput.value = "Unable to reach server.";
    }
}

