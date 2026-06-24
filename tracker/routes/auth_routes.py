from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from ..auth import (
    admin_required,
    create_user,
    get_all_users,
    reset_user_password,
    set_user_active,
    verify_credentials,
)

bp = Blueprint("auth_bp", __name__)

ROLES = ["cotizador", "admin"]


@bp.route("/login", methods=["GET", "POST"], endpoint="login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = verify_credentials(username, password)
        if user:
            login_user(user)
            next_url = request.args.get("next") or url_for("dashboard")
            return redirect(next_url)
        error = "Credenciales incorrectas o cuenta desactivada."
    return render_template("login.html", error=error)


@bp.route("/logout", methods=["POST"], endpoint="logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("auth_bp.login"))


@bp.route("/usuarios", methods=["GET"], endpoint="users")
@admin_required
def users():
    return render_template("users.html", users=get_all_users(), roles=ROLES)


@bp.route("/usuarios/nuevo", methods=["GET", "POST"], endpoint="new_user")
@admin_required
def new_user():
    errors = {}
    form = {"username": "", "role": "cotizador", "password": "", "password2": ""}
    if request.method == "POST":
        form["username"] = request.form.get("username", "").strip()
        form["role"] = request.form.get("role", "cotizador")
        form["password"] = request.form.get("password", "")
        form["password2"] = request.form.get("password2", "")
        if not form["username"]:
            errors["username"] = "El nombre de usuario es obligatorio."
        if not form["password"]:
            errors["password"] = "La contraseña es obligatoria."
        elif form["password"] != form["password2"]:
            errors["password2"] = "Las contraseñas no coinciden."
        elif len(form["password"]) < 6:
            errors["password"] = "Mínimo 6 caracteres."
        if form["role"] not in ROLES:
            errors["role"] = "Rol inválido."
        if not errors:
            try:
                create_user(form["username"], form["password"], form["role"])
                flash(f"Usuario '{form['username']}' creado.", "success")
                return redirect(url_for("auth_bp.users"))
            except Exception:
                errors["username"] = "Ese nombre de usuario ya existe."
    return render_template(
        "user_form.html", form=form, errors=errors, action="new", roles=ROLES
    )


@bp.route("/usuarios/<int:user_id>/toggle", methods=["POST"], endpoint="toggle_user")
@admin_required
def toggle_user(user_id):
    active_str = request.form.get("active", "0")
    set_user_active(user_id, active_str == "1")
    flash("Estado de usuario actualizado.", "success")
    return redirect(url_for("auth_bp.users"))


@bp.route("/mi-cuenta/contrasena", methods=["GET", "POST"], endpoint="change_own_password")
@login_required
def change_own_password():
    errors = {}
    if request.method == "POST":
        current_pw = request.form.get("current_password", "")
        password = request.form.get("password", "")
        password2 = request.form.get("password2", "")
        if not current_pw:
            errors["current_password"] = "Ingresa tu contraseña actual."
        elif not verify_credentials(current_user.username, current_pw):
            errors["current_password"] = "Contraseña actual incorrecta."
        if not errors:
            if not password:
                errors["password"] = "La contraseña nueva es obligatoria."
            elif password != password2:
                errors["password2"] = "Las contraseñas no coinciden."
            elif len(password) < 6:
                errors["password"] = "Mínimo 6 caracteres."
        if not errors:
            reset_user_password(current_user.id, password)
            flash("Contraseña actualizada correctamente.", "success")
            return redirect(url_for("dashboard"))
    return render_template(
        "user_form.html",
        form={"current_password": "", "password": "", "password2": ""},
        errors=errors,
        action="change_own",
    )


@bp.route(
    "/usuarios/<int:user_id>/reset-password",
    methods=["GET", "POST"],
    endpoint="reset_password",
)
@admin_required
def reset_password(user_id):
    errors = {}
    if request.method == "POST":
        password = request.form.get("password", "")
        password2 = request.form.get("password2", "")
        if not password:
            errors["password"] = "La contraseña es obligatoria."
        elif password != password2:
            errors["password2"] = "Las contraseñas no coinciden."
        elif len(password) < 6:
            errors["password"] = "Mínimo 6 caracteres."
        if not errors:
            reset_user_password(user_id, password)
            flash("Contraseña actualizada.", "success")
            return redirect(url_for("auth_bp.users"))
    return render_template(
        "user_form.html",
        form={"password": "", "password2": ""},
        errors=errors,
        action="reset",
        user_id=user_id,
        roles=ROLES,
    )
