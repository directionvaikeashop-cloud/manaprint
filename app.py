"""
MANAPRINT — Application Flask
Relie : contrôle d'accès (Pacific Ink / international), génération PDF, espace gestion.
Déployable sur Railway (même stack que Ticket Bingo).
"""
import os
from flask import Flask, request, jsonify, send_file, render_template, session
from functools import wraps

import database as db
from generators import bingo

app = Flask(__name__)
app.secret_key = os.environ.get("MANAPRINT_SECRET", "dev-secret-a-changer-en-prod")

# Code de gestion — À DÉFINIR via variable d'environnement en production
CODE_ADMIN = os.environ.get("MANAPRINT_ADMIN_CODE", "2KEA-MOOREA")


@app.before_request
def _setup():
    # Initialise la base au premier appel
    if not getattr(app, "_db_ready", False):
        db.init_db()
        db.init_machines(4)
        app._db_ready = True


# ── PAGES ─────────────────────────────────────────────────────────────────────
@app.route("/")
def accueil():
    return render_template("index.html")


# ── ACCÈS CLIENT PACIFIC INK ──────────────────────────────────────────────────
@app.route("/api/verifier-pacific-ink", methods=["POST"])
def verifier_pi():
    data = request.get_json(force=True)
    numero = data.get("numero", "")
    if db.verifier_client_pi(numero):
        session["acces"] = "pacific_ink"
        session["identifiant"] = db.normalize_num(numero)
        return jsonify({"ok": True})
    return jsonify({"ok": False, "message": "Numéro non confirmé"}), 404


# ── ACCÈS CLIENT INTERNATIONAL ────────────────────────────────────────────────
@app.route("/api/client-international", methods=["POST"])
def client_intl():
    data = request.get_json(force=True)
    nom = data.get("nom", "").strip()
    email = data.get("email", "").strip()
    pays = data.get("pays", "").strip()
    if not nom or "@" not in email:
        return jsonify({"ok": False, "message": "Nom et email requis"}), 400
    db.enregistrer_client_intl(nom, email, pays)
    session["acces"] = "international"
    session["identifiant"] = email
    return jsonify({"ok": True})


# ── GÉNÉRATION PDF ────────────────────────────────────────────────────────────
@app.route("/api/generer", methods=["POST"])
def generer():
    if "acces" not in session:
        return jsonify({"ok": False, "message": "Accès non autorisé"}), 403

    data = request.get_json(force=True)
    programme = data.get("programme", "ohana75")
    theme = data.get("theme", "")
    nb_cartes = max(1, min(int(data.get("nb_cartes", 1)), 50))

    # Génère le PDF
    pdf = bingo.generer_pdf(programme=programme, theme=theme, nb_cartes=nb_cartes)

    # Enregistre l'impression (facturation 1,5% à la feuille)
    db.enregistrer_impression(
        origine=session["acces"],
        identifiant=session.get("identifiant"),
        programme=programme,
        theme=theme,
        nb_feuilles=nb_cartes,
    )

    return send_file(
        pdf,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"manaprint_{programme}.pdf",
    )


# ── ESPACE GESTION (2KEA & Associé) ───────────────────────────────────────────
def admin_requis(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if not session.get("admin"):
            return jsonify({"ok": False, "message": "Non autorisé"}), 403
        return f(*args, **kwargs)
    return wrap


@app.route("/api/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json(force=True)
    if data.get("code") == CODE_ADMIN:
        session["admin"] = True
        return jsonify({"ok": True})
    return jsonify({"ok": False, "message": "Code incorrect"}), 401


@app.route("/api/admin/clients-pi", methods=["GET"])
@admin_requis
def admin_lister_pi():
    return jsonify({"ok": True, "clients": db.lister_clients_pi()})


@app.route("/api/admin/clients-pi", methods=["POST"])
@admin_requis
def admin_ajouter_pi():
    data = request.get_json(force=True)
    ok, msg = db.ajouter_client_pi(
        data.get("numero", ""), data.get("nom"), data.get("ile"), data.get("machine_id")
    )
    return jsonify({"ok": ok, "message": msg})


@app.route("/api/admin/clients-pi/<numero>", methods=["DELETE"])
@admin_requis
def admin_retirer_pi(numero):
    db.retirer_client_pi(numero)
    return jsonify({"ok": True})


@app.route("/api/admin/machines", methods=["GET"])
@admin_requis
def admin_machines():
    return jsonify({"ok": True, "machines": db.lister_machines()})


@app.route("/api/admin/machines/installer", methods=["POST"])
@admin_requis
def admin_installer_machine():
    data = request.get_json(force=True)
    db.installer_machine(
        data.get("machine_id"), data.get("client_nom"),
        data.get("client_num"), data.get("ile")
    )
    # Ajoute automatiquement le numéro à la liste des clients confirmés
    db.ajouter_client_pi(
        data.get("client_num"), data.get("client_nom"),
        data.get("ile"), data.get("machine_id")
    )
    return jsonify({"ok": True})


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "service": "manaprint"})


if __name__ == "__main__":
    db.init_db()
    db.init_machines(4)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
