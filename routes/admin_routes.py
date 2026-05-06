from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
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

@admin_bp.route("/delete-user/<int:user_id>")
def delete_user(user_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    current_user = User.query.get(session["user_id"])

    if not current_user or current_user.role != "admin":
        return abort(403)

    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash("You cannot delete your own admin account.", "danger")
        return redirect(url_for("admin_dashboard"))

    db.session.delete(user)
    db.session.commit()

    flash("User deleted successfully.", "success")
    return redirect(url_for("admin_dashboard"))

@admin_bp.route("/edit-user/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    current_user = User.query.get(session["user_id"])

    if not current_user or current_user.role != "admin":
        return abort(403)

    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        role = request.form.get("role")

        # validation
        existing = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing and existing.id != user.id:
            flash("Username or Email already exists", "danger")
            return redirect(url_for("admin.edit_user", user_id=user.id))

        user.username = username
        user.email = email
        user.role = role

        db.session.commit()

        flash("User updated successfully", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("edit_user.html", user=user)

@admin_bp.route("/update-role/<int:user_id>", methods=["POST"])
def update_role(user_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    current_user = User.query.get(session["user_id"])

    if not current_user or current_user.role != "admin":
        return abort(403)

    user = User.query.get_or_404(user_id)
    new_role = request.form.get("role")

    allowed_roles = ["admin", "recruiter", "user"]

    if new_role not in allowed_roles:
        flash("Invalid role selected.", "danger")
        return redirect(url_for("admin_dashboard"))

    user.role = new_role
    db.session.commit()

    flash("User role updated successfully.", "success")
    return redirect(url_for("admin_dashboard"))