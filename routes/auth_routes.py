from flask import Blueprint, request, jsonify, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity


from extensions import db
from models.user import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/auth/register", methods=["POST"])
def register():

    if request.is_json:
        data = request.get_json()
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
    else:
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

    if not username or not email or not password:
        return "All fields required", 400

    if User.query.filter_by(username=username).first():
        return "Username exists", 400

    if User.query.filter_by(email=email).first():
        return "Email exists", 400

    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        role="user"
    )

    db.session.add(user)
    db.session.commit()

    return redirect(url_for("login"))


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
