from pymongo import MongoClient

def init_db(app):
    try:
        client = MongoClient("mongodb+srv://admin:admin21226@21226cluster.wobvyfg.mongodb.net/?retryWrites=true&w=majority&appName=21226Cluster")
        db = client["scrapperData"]
        
        app.db = db
        
        client.admin.command('ping')
        print("Połączono z MongoDB!")
        
    except Exception as e:
        print(f"Błąd połączenia z bazą danych: {e}")
        raise