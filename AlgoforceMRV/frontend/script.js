const TOTAL_REQUESTS = 100;
const DISTRIBUTOR_URL = "http://127.0.0.1:8080/route";

const delay = ms => new Promise(resolve => setTimeout(resolve, ms));


function generateRandomRequest(id) {
    const types = ["DATA_FETCH", "IMAGE_PROCESS", "ML_INFERENCE", "DB_WRITE"];
    return {
        id: `REQ-${String(id).padStart(3, '0')}`,
        type: types[Math.floor(Math.random() * types.length)],
        workload: Math.floor(Math.random() * 50) + 10 // Random workload size 10-60
    };
}
async function fireRequests() {
    const grid = document.getElementById("request-grid");
    const tableBody = document.getElementById("table-body");
    grid.innerHTML = "";
    tableBody.innerHTML = "";
    document.getElementById("start-btn").disabled = true;

    const requests = [];
    
    // 1. Setup the UI Grid
    for (let i = 1; i <= TOTAL_REQUESTS; i++) {
        const reqData = generateRandomRequest(i);
        requests.push(reqData);
        
        const box = document.createElement("div");
        box.className = "req-box";
        box.id = reqData.id;
        
        box.innerHTML = `
            <div class="id">${reqData.id}</div>
            <div class="data-section">
                <div class="data-row">
                    <span class="data-label">Task Type:</span>
                    <span class="data-value">${reqData.type}</span>
                </div>
                <div class="data-row">
                    <span class="data-label">Workload:</span>
                    <span class="data-value">${reqData.workload} units</span>
                </div>
            </div>
            <div class="status-title">Server Response:</div>
            <div class="status" id="status-${reqData.id}">
                <span style="font-size: 11px; color: #94a3b8; font-style: italic;">Queued in browser...</span>
            </div>
        `;
        grid.appendChild(box);
    }

    // 2. RATE LIMITER: Fire requests with a 50ms gap between each
    for (let reqData of requests) {
        // Update status to show it left the browser
        document.getElementById(`status-${reqData.id}`).innerHTML = 
            `<span style="font-size: 11px; color: #f59e0b; font-style: italic;">Routing request...</span>`;
        
        // Send the request but don't wait for the RESPONSE to fire the next one
        sendRequest(reqData);
        
        // Wait 50 milliseconds before SENDING the next request
        await delay(50); 
    }
    
    document.getElementById("start-btn").disabled = false;
}

function updateUI(result, reqData) {
    const box = document.getElementById(result.req_id);
    const statusDiv = document.getElementById(`status-${result.req_id}`);
    box.classList.add("success");
    
    // Render Response body cleanly
    statusDiv.innerHTML = `
        <div class="data-section" style="background: #ecfdf5; border-color: #a7f3d0;">
            <div class="data-row">
                <span class="data-label">Status:</span>
                <span class="data-value" style="color: #059669; font-weight: bold;">${result.server_response.status}</span>
            </div>
            <div class="data-row">
                <span class="data-label">Node:</span>
                <span class="data-value">${result.server_response.processed_by}</span>
            </div>
            <div class="data-row">
                <span class="data-label">Processed:</span>
                <span class="data-value">${result.server_response.workload_consumed} units</span>
            </div>
        </div>
    `;

    // Append to Dump Table
    const tableBody = document.getElementById("table-body");
    const row = document.createElement("tr");
    row.innerHTML = `
        <td><strong>${result.req_id}</strong></td>
        <td>${reqData.workload} units</td>
        <td>${result.assigned_server}</td>
        <td class="log-reason">${result.decision_reason}</td>
        <td><span style="color:#10b981; font-weight:bold;">200 OK</span></td>
    `;
    tableBody.appendChild(row);
}

async function sendRequest(reqData) {
    try {
        const response = await fetch(DISTRIBUTOR_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(reqData)
        });
        
        const result = await response.json();
        updateUI(result, reqData);
    } catch (error) {
        console.error("Request failed:", error);
        document.getElementById(`status-${reqData.id}`).innerText = "Failed: Connection Error";
    }
}

