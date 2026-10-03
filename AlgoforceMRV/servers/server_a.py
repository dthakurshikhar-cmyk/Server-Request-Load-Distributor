from flask import Flask, request, jsonify
import time

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    workload = data.get('workload', 10)
    
    # Simulate actual physical processing time based on workload size
    time.sleep(workload * 0.01) 
    
    return jsonify({
        "status": "Processed successfully",
        "processed_by": "Server A (5001)",
        "workload_consumed": workload
    })

if __name__ == '__main__':
    app.run(port=5001)