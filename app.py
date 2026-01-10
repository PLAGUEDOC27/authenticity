from flask import Flask
from extensions import db, jwt

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///auth_validator.db"
    app.config["SECRET_KEY"] = "change_this_secret"
    app.config["JWT_SECRET_KEY"] = "change_this_jwt_secret"

    db.init_app(app)
    jwt.init_app(app)

    # JWT error diagnostics
    from flask_jwt_extended import JWTManager

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        return {"msg": f"Invalid token: {reason}"}, 422

    @jwt.unauthorized_loader
    def missing_token_callback(reason):
        return {"msg": f"Missing token: {reason}"}, 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {"msg": "Token has expired"}, 401

    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.document_routes import document_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(document_bp)

    @app.route("/")
    def home():
        return "Authenticity Validator is running with DB and auth"

    with app.app_context():
        db.create_all()

    return app   # VERY IMPORTANT — must return the app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
