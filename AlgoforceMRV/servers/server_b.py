from flask import Flask, request, jsonify
import time

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    workload = data.get('workload', 10)
    time.sleep(workload * 0.002)
    
    return jsonify({
        "status": "Processed successfully",
        "processed_by": "Server B (5002)",
        "workload_consumed": workload
    })

if __name__ == '__main__':
    app.run(port=5002)