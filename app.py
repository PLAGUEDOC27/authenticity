from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///auth_validator.db"
    app.config["SECRET_KEY"] = "change_this_secret"
    app.config["JWT_SECRET_KEY"] = "change_this_jwt_secret"

    db.init_app(app)
    jwt.init_app(app)

    from routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp)

    @app.route("/")
    def home():
        return "Authenticity Validator is running with DB and auth"

    with app.app_context():
        db.create_all()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
