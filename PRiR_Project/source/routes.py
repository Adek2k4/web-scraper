from flask import request, jsonify

def init_routes(app):
    @app.route('/add_user', methods=['POST'])
    def add_user():
        result = app.db["users"].insert_one(request.json)
        return jsonify({"inserted_id": str(result.inserted_id)})

    @app.route('/get_users', methods=['GET'])
    def get_users():
        users = list(app.db["users"].find({}, {"_id": 0}))
        return jsonify(users)
