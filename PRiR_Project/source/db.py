from pymongo import MongoClient


def init_db(app):
    client = MongoClient("mongodb+srv://admin:admin21226@21226cluster.wobvyfg.mongodb.net/?retryWrites=true&w=majority&appName=21226Cluster")
    db = client["scrapperData"]
    collection = db["users"]