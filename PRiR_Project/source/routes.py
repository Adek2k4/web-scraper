from flask import request, jsonify
from bson import ObjectId

def init_routes(app):
    @app.route('/')
    def home():
        return jsonify({"message": "Aplikacja działa!", "status": "OK"})
    
    @app.route('/add_user', methods=['POST'])
    def add_user():
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Brak danych JSON"}), 400
            
            result = app.db["users"].insert_one(data)
            return jsonify({
                "message": "Użytkownik dodany",
                "inserted_id": str(result.inserted_id)
            }), 201
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/get_users', methods=['GET'])
    def get_users():
        try:
            users = list(app.db["users"].find({}, {"_id": 0}))
            return jsonify({
                "users": users,
                "count": len(users)
            })
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/get_users_with_id', methods=['GET'])
    def get_users_with_id():
        try:
            users = []
            for user in app.db["users"].find({}):
                user["_id"] = str(user["_id"])  # Konwertuj ObjectId na string
                users.append(user)
            
            return jsonify({
                "users": users,
                "count": len(users)
            })
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500