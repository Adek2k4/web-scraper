from flask import Flask, request, jsonify
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from engine import scrape_multiprocess

app = Flask(__name__)

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    urls = data.get('urls', [])
    results = scrape_multiprocess(urls)
    return jsonify(results)

@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
