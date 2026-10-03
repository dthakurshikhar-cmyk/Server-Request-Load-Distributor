import heapq
import requests
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- Server Capacity Limits ---
# Each server can only process exactly 3 requests simultaneously.
MAX_CONCURRENT_REQUESTS = 3

capacity_locks = {
    5001: threading.Semaphore(MAX_CONCURRENT_REQUESTS),
    5002: threading.Semaphore(MAX_CONCURRENT_REQUESTS),
    5003: threading.Semaphore(MAX_CONCURRENT_REQUESTS)
}

# Structure: [current_backlog_load, port_number, server_name, setup_time, processing_speed]
# Added limitations (setup time & speed) directly to your structure.
server_pool = [
    [0, 5001, "Server A (Heavy)", 15.0, 10.0],
    [0, 5002, "Server B (General)", 5.0, 3.0],
    [0, 5003, "Server C (Fast)", 0.0, 1.0]
]

heap_lock = threading.Lock()

@app.route('/route', methods=['POST'])
def distribute_request():
    data = request.json
    req_id = data.get('id')
    workload = data.get('workload', 10)

    with heap_lock:
        # 1. EVALUATE LIMITATIONS & BUILD PRIORITY QUEUE
        request_pq = []
        
        for s in server_pool:
            current_backlog = s[0]
            port = s[1]
            name = s[2]
            setup_time = s[3]
            speed = s[4]
            
            # The Math calculation for this specific server
            est_time = setup_time + ((current_backlog + workload) / speed)
            
            # Push to Priority Queue (Min-Heap). Formatted as: (priority_score, port, server_reference)
            heapq.heappush(request_pq, (est_time, port, s))

        # 2. PRIORITY QUEUE / GREEDY CHOICE
        # Extract the server with the absolute minimum calculated time
        best_tuple = heapq.heappop(request_pq)
        
        min_time = best_tuple[0]
        best_server = best_tuple[2] # Reference to the winning server's list

        current_load = best_server[0]
        port = best_server[1]
        name = best_server[2]
        setup_time = best_server[3]
        speed = best_server[4]
        
        # Add this request's workload to the winning server's tracking state
        best_server[0] += workload
        
        # 3. DISPLAY THE CALCULATION
        decision_log = (
            f"Priority Queue Greedy Choice: Selected {name}. "
            f"Calculation: {setup_time}ms setup + ({current_load}u pending + {workload}u incoming) / {speed} speed = {min_time:.1f}ms estimated time."
        )

    # 4. CAPACITY CHECK & STALLING
    capacity_locks[port].acquire()

    # 5. PROXY TO ACTUAL SERVER
    target_url = f"http://127.0.0.1:{port}/process"
    try:
        resp = requests.post(target_url, json=data, timeout=20)
        server_response = resp.json()
    except Exception as e:
        server_response = {"status": "Error", "message": str(e)}
    finally:
        # FREE THE SLOT
        capacity_locks[port].release()

    # 6. DRAIN QUEUE POST-EXECUTION
    with heap_lock:
        for s in server_pool:
            if s[1] == port:
                s[0] -= workload
                break

    return jsonify({
        "req_id": req_id,
        "assigned_server": name,
        "port": port,
        "decision_reason": decision_log,
        "server_response": server_response
    })

if __name__ == '__main__':
    app.run(port=8080, threaded=True)