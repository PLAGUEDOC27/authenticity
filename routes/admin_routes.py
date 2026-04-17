from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from models.user import User
from extensions import db

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin/create-user", methods=["GET", "POST"])
def create_user():

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")

        # VALIDATION
        if User.query.filter_by(username=username).first():
            flash("Username already exists", "danger")
            return redirect(url_for("admin.create_user"))

        if User.query.filter_by(email=email).first():
            flash("Email already exists", "danger")
            return redirect(url_for("admin.create_user"))

        hashed = generate_password_hash(password)

        user = User(
            username=username,
            email=email,
            password_hash=hashed,
            role=role
        )

        db.session.add(user)
        db.session.commit()

        flash("User created successfully", "success")
        return redirect(url_for("admin.create_user"))

    return render_template("create_user.html")

@admin_bp.route("/set-role/<int:user_id>/<role>")
def set_role(user_id, role):

    user = User.query.get_or_404(user_id)

    if role not in ["admin", "recruiter", "user"]:
        flash("Invalid role", "danger")
        return redirect(url_for("admin_dashboard"))

    user.role = role
    db.session.commit()

    flash(f"{user.username} is now {role}", "success")

    return redirect(url_for("admin_dashboard"))