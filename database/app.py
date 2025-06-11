from flask import Flask, request, jsonify
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
from pymongo import MongoClient

app = Flask(__name__)

# Pobierz connection string z env
MONGODB_ATLAS_URI = os.environ.get('MONGODB_ATLAS_URI')
MONGODB_DBNAME = os.environ.get('MONGODB_DBNAME', 'scraper')
MONGODB_COLLECTION = os.environ.get('MONGODB_COLLECTION', 'results')

if not MONGODB_ATLAS_URI:
    raise RuntimeError("Brak zmiennej środowiskowej MONGODB_ATLAS_URI")

client = MongoClient(MONGODB_ATLAS_URI)
db = client[MONGODB_DBNAME]
collection = db[MONGODB_COLLECTION]

@app.route('/save', methods=['POST'])
def save():
    data = request.get_json()
    results = data.get('results', [])
    if results:
        # Wstaw wiele dokumentów naraz
        collection.insert_many(results)
    return '', 200

@app.route('/results', methods=['GET'])
def results():
    # Pobierz wszystkie dokumenty, usuń _id (nie jest serializowalny do JSON)
    docs = list(collection.find({}, {'_id': 0}).sort('_id', -1))  # sortowanie od najnowszych
    return jsonify(docs)

@app.route('/delete', methods=['POST'])
def delete():
    data = request.get_json()
    url = data.get('url')
    if url:
        collection.delete_one({'url': url})
        return '', 200
    return 'Missing url', 400

@app.route('/clear', methods=['DELETE'])
def clear():
    collection.delete_many({})
    return '', 200

@app.route('/health')
def health():
    try:
        # Prosta operacja sprawdzająca połączenie
        client.admin.command('ping')
        return "OK", 200
    except Exception:
        return "ERROR", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
