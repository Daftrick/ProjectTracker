import json

from flask import Blueprint, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required, login_user, logout_user

from ..auth import (
    AUTH_DB,
    KNOWN_PERMISSIONS,
    admin_required,
    create_user,
    delete_user,
    get_all_users,
    get_user_by_username,
    record_login,
    reset_user_password,
    set_user_active,
    set_user_permissions,
    update_user_role,
    update_username,
    verify_credentials,
)
from ..extensions import csrf
from ..storage import today

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
            record_login(user.id)
            next_url = request.args.get("next") or url_for("dashboard")
            return redirect(next_url)
        error = "Credenciales incorrectas o cuenta desactivada."
    return render_template("login.html", error=error)


@bp.route("/logout", methods=["POST"], endpoint="logout")
@csrf.exempt
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("auth_bp.login"))


@bp.route("/usuarios", methods=["GET"], endpoint="users")
@admin_required
def users():
    raw = get_all_users()
    for u in raw:
        try:
            u["permissions"] = json.loads(u.get("permissions") or "{}")
        except (ValueError, TypeError):
            u["permissions"] = {}
    return render_template(
        "users.html",
        users=raw,
        roles=ROLES,
        known_permissions=KNOWN_PERMISSIONS,
    )


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


@bp.route("/usuarios/<int:user_id>/edit-role", methods=["POST"], endpoint="edit_user_role")
@admin_required
def edit_user_role(user_id):
    role = request.form.get("role", "cotizador")
    if role not in ROLES:
        flash("Rol inválido.", "warning")
        return redirect(url_for("auth_bp.users"))
    update_user_role(user_id, role)
    flash("Rol actualizado.", "success")
    return redirect(url_for("auth_bp.users"))


@bp.route("/usuarios/<int:user_id>/edit-permissions", methods=["POST"], endpoint="edit_user_permissions")
@admin_required
def edit_user_permissions(user_id):
    perms = {p: (request.form.get(p) == "1") for p in KNOWN_PERMISSIONS}
    set_user_permissions(user_id, perms)
    flash("Permisos actualizados.", "success")
    return redirect(url_for("auth_bp.users"))


@bp.route("/usuarios/<int:user_id>/edit-username", methods=["POST"], endpoint="edit_username")
@admin_required
def edit_username_view(user_id):
    new_username = request.form.get("username", "").strip()
    if not new_username:
        flash("El nombre de usuario no puede estar vacío.", "warning")
        return redirect(url_for("auth_bp.users"))
    if get_user_by_username(new_username):
        flash(f"El nombre de usuario '{new_username}' ya está en uso.", "warning")
        return redirect(url_for("auth_bp.users"))
    update_username(user_id, new_username)
    flash(f"Nombre de usuario actualizado a '{new_username}'.", "success")
    return redirect(url_for("auth_bp.users"))


@bp.route("/usuarios/<int:user_id>/delete", methods=["POST"], endpoint="delete_user")
@admin_required
def delete_user_view(user_id):
    if user_id == current_user.id:
        flash("No puedes eliminar tu propia cuenta.", "warning")
        return redirect(url_for("auth_bp.users"))
    delete_user(user_id)
    flash("Usuario eliminado.", "success")
    return redirect(url_for("auth_bp.users"))


@bp.route("/admin/backup/auth-db", methods=["GET"], endpoint="backup_auth_db")
@admin_required
def backup_auth_db():
    return send_file(
        AUTH_DB,
        as_attachment=True,
        download_name=f"auth-backup-{today()}.db",
        mimetype="application/octet-stream",
    )


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
