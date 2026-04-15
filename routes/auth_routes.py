from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from extensions import db
from models.user import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Missing JSON body"}), 400

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"msg": "username, email and password are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "Username already exists"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Email already exists"}), 400

    hashed = generate_password_hash(password)
    user = User(username=username, email=email, password_hash=hashed)
    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "User created"}), 201


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Missing JSON body"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"msg": "username and password are required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"msg": "Invalid username or password"}), 401
        
    # IMPORTANT: identity as STRING to satisfy JWT subject requirement
    access_token = create_access_token(identity=str(user.id))


    return jsonify({"access_token": access_token}), 200


# (Optional) quick test route for token
@auth_bp.route("/auth/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()   # this will be a string
    return jsonify({"user_id": user_id}), 200
