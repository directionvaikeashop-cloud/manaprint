"""
MANAPRINT — Application Flask
Relie : contrôle d'accès (Pacific Ink / international), génération PDF, espace gestion.
Déployable sur Railway (même stack que Ticket Bingo).
"""
import os
import hashlib
from flask import Flask, request, jsonify, send_file, render_template, session, Response
from functools import wraps

import database as db
from generators import bingo
from generators import triple_action
from generators import aloha75
from generators import p6_marathon
from generators import bingo_ball
from generators import ohana75_2series

app = Flask(__name__)
app.secret_key = os.environ.get("MANAPRINT_SECRET", "dev-secret-a-changer-en-prod")

# ── Envoi d'email (impression partenaire FUN AND CO) ──────────────────────────
import smtplib
from email.message import EmailMessage

FUN_AND_CO_EMAIL = os.environ.get("FUN_AND_CO_EMAIL", "funandco.24@gmail.com")
SMTP_USER = os.environ.get("SMTP_USER", "")   # ex: ton.compte@gmail.com
SMTP_PASS = os.environ.get("SMTP_PASS", "")   # mot de passe d'application Gmail

# ── Partenaires d'impression (le client polynésien peut faire imprimer chez eux) ──
# Pour en ajouter un : ajoute une ligne ici (id, nom, email, zone, tel). C'est tout.
PARTENAIRES = {
    "2kea_papeete": {
        "nom": "2KEA & Associé — Papeete",
        "email": os.environ.get("PAPEETE_EMAIL", "directionvaikeashop@gmail.com"),
        "zone": "Papeete (Tahiti)",
        "tel": "89 52 98 83",
    },
    "fun_and_co": {
        "nom": "FUN AND CO",
        "email": FUN_AND_CO_EMAIL,
        "zone": "Presqu'île (Tahiti Iti)",
        "tel": "87 26 73 24",
    },
    "2kea_raiatea": {
        "nom": "2KEA & Associé — Raiatea",
        "email": os.environ.get("RAIATEA_EMAIL", "vaikeashop04@gmail.com"),
        "zone": "Raiatea (Îles Sous-le-Vent)",
        "tel": "87 77 34 26",
    },
}

def envoyer_email_pdf(destinataire, sujet, corps, pdf_io, nom_fichier, copie=None):
    """Envoie un email avec un PDF en pièce jointe (SMTP Gmail). Renvoie (ok, message).
    copie : adresse mise en copie (CC), ex. la plateforme pour garder une trace."""
    if not SMTP_USER or not SMTP_PASS:
        return False, "Email non configuré (SMTP_USER / SMTP_PASS manquants sur Railway)"
    try:
        msg = EmailMessage()
        msg["Subject"] = sujet
        msg["From"] = SMTP_USER
        msg["To"] = destinataire
        if copie:
            msg["Cc"] = copie
        msg.set_content(corps)
        pdf_io.seek(0)
        msg.add_attachment(pdf_io.read(), maintype="application", subtype="pdf", filename=nom_fichier)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)
        return True, "Email envoyé"
    except Exception as e:
        return False, "Echec email : " + str(e)

# Code de gestion — À DÉFINIR via variable d'environnement en production
CODE_ADMIN = os.environ.get("MANAPRINT_ADMIN_CODE", "2KEA-MOOREA")

# Noms réservés : un client ne peut pas les utiliser dans sa personnalisation
NOMS_RESERVES = ["tukea", "2kea", "maeva", "2kea&associe", "2kea & associe", "2kea associe"]

# ============================================================
# REGISTRE UNIVERSEL DES JEUX (format A4)
# Pour AJOUTER un jeu : 1) place le module dans generators/ (fonction generer_pdf)
#                       2) ajoute UNE seule ligne _enregistrer_jeu(...) ci-dessous.
# Le jeu apparaît AUTOMATIQUEMENT dans le menu du générateur. C'est tout.
# ============================================================
REGISTRE_JEUX = {}

def _enregistrer_jeu(jeu_id, nom, emoji, cartes_par_feuille, generer, kwarg_nb="nb_cartes", couleur=True):
    """Enregistre un jeu A4 (tolérant). couleur=True (arc-en-ciel) ou False (N&B)."""
    try:
        REGISTRE_JEUX[jeu_id] = {
            "nom": nom, "emoji": emoji,
            "cartes_par_feuille": cartes_par_feuille,
            "generer": generer, "kwarg_nb": kwarg_nb, "couleur": couleur,
        }
        print(f"[JEU A4 INSTALLE] {emoji} {nom}")
    except Exception as e:
        print(f"[JEU A4 ABSENT] {nom} : {e}")

def _variante(fn, couleur_force):
    """Crée une version d'un générateur qui force la couleur (True/False)."""
    def _w(**kwargs):
        kwargs["couleur"] = couleur_force
        return fn(**kwargs)
    return _w

def _enregistrer_paire(base_id, nom, emoji, cpf, fn, kwarg_nb="nb_cartes"):
    """Enregistre les 2 variantes d'un jeu : (Couleur) et (N&B). 1 ligne = 2 entrées."""
    _enregistrer_jeu(base_id + "_couleur", nom + " (Couleur)", emoji, cpf,
                     _variante(fn, True),  kwarg_nb=kwarg_nb, couleur=True)
    _enregistrer_jeu(base_id + "_nb",      nom + " (N&B)",     emoji, cpf,
                     _variante(fn, False), kwarg_nb=kwarg_nb, couleur=False)

#                  id base          nom                 emoji  cartes/feuille  fonction
_enregistrer_paire("triple_action", "Triple Action 75",  "🎯", 10, triple_action.generer_pdf, kwarg_nb="nb_tickets")
_enregistrer_paire("aloha75",       "Aloha 75",          "🌺", 12, aloha75.generer_pdf)
_enregistrer_paire("p6_marathon",   "P6 Marathon",       "6️⃣", 6,  p6_marathon.generer_pdf)
_enregistrer_paire("bingo_ball",    "Bingo Ball",        "🎱", 10, bingo_ball.generer_pdf)
_enregistrer_paire("ohana75_2s",    "OHANA 75 · 2 séries","🌺", 2,  ohana75_2series.generer_pdf)
# --- Ajouter un futur jeu A4 = UNE ligne _enregistrer_paire(...) (crée Couleur + N&B) ---
# _enregistrer_paire("ohana90", "OHANA 90", "🌺", 8, ohana90.generer_pdf)

# Table cartes/feuille dérivée automatiquement du registre
CARTES_PAR_FEUILLE = {jid: j["cartes_par_feuille"] for jid, j in REGISTRE_JEUX.items()}


def generer_jeu(programme, nb_cartes, couleur, perso):
    """Génère le PDF A4 de N'IMPORTE QUEL jeu du registre. perso = champs de personnalisation."""
    jeu = REGISTRE_JEUX.get(programme) or REGISTRE_JEUX.get("triple_action")
    kwargs = {
        jeu["kwarg_nb"]: nb_cartes, "serie_start": 1, "theme": "", "couleur": couleur,
        "nom_evenement": perso.get("nom_evenement", ""), "titre_jeu": perso.get("titre_jeu", ""),
        "couleur_perso": perso.get("couleur_perso", ""), "date_lieu": perso.get("date_lieu", ""),
        "telephone": perso.get("telephone", ""),
    }
    return jeu["generer"](**kwargs)


def contient_nom_reserve(*champs):
    """Retourne le mot réservé détecté (ou None) dans n'importe quel champ."""
    for champ in champs:
        if not champ:
            continue
        texte = champ.lower()
        # enlever espaces/ponctuation pour attraper les variantes (2 kea, tu-kea…)
        compact = "".join(ch for ch in texte if ch.isalnum())
        for reserve in NOMS_RESERVES:
            r_compact = "".join(ch for ch in reserve if ch.isalnum())
            if reserve in texte or r_compact in compact:
                return reserve
    return None


def est_numero_polynesien(tel):
    """Vrai si le numéro est polynésien : 8 chiffres commençant par 87, 88, 89 (mobiles) ou 40 (fixe).
    Tolère +689, espaces, points, tirets."""
    if not tel:
        return False
    chiffres = "".join(ch for ch in tel if ch.isdigit())
    if chiffres.startswith("689"):
        chiffres = chiffres[3:]
    # un numéro polynésien a 8 chiffres et commence par 87, 88, 89 ou 40
    if len(chiffres) == 8 and chiffres[:2] in ("87", "88", "89", "40"):
        return True
    return False


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
    # Compteur de visiteurs (IP anonymisée par hachage, jamais stockée en clair)
    try:
        ip = (request.headers.get("X-Forwarded-For", request.remote_addr or "") or "").split(",")[0].strip()
        ip_hash = hashlib.sha256(("manaprint:" + ip).encode("utf-8")).hexdigest()[:16]
        db.enregistrer_visite(ip_hash, "/", request.headers.get("User-Agent", ""), _detecter_source())
    except Exception:
        pass
    return render_template("index.html")


def _detecter_source():
    """Source de la visite : ?source= explicite, sinon déduite du référent."""
    src = (request.args.get("source", "") or request.args.get("utm_source", "") or "").strip().lower()[:40]
    if src:
        return src
    ref = (request.headers.get("Referer", "") or "").lower()
    if not ref:
        return "direct"
    for cle, nom in [("facebook", "facebook"), ("fb.", "facebook"), ("messenger", "facebook"),
                     ("instagram", "instagram"), ("tiktok", "tiktok"), ("whatsapp", "whatsapp"),
                     ("wa.me", "whatsapp"), ("youtube", "youtube"), ("google", "google"),
                     ("bing", "bing"), ("ticket-bingo", "ticketbingo")]:
        if cle in ref:
            return nom
    return "autre-site"


@app.route("/diag-visiteurs")
def diag_visiteurs():
    """Statistiques de fréquentation. Accès : ?cle=TON_CODE_ADMIN."""
    if (request.args.get("cle", "") or "").strip() != CODE_ADMIN:
        return Response("Acces reserve. Ajoute ?cle=TON_CODE_ADMIN a l'adresse.",
                        status=403, mimetype="text/plain; charset=utf-8")
    s = db.stats_visites()
    lignes = ""
    for j in s["par_jour"]:
        lignes += (f'<tr style="border-bottom:1px solid rgba(255,255,255,.08)">'
                   f'<td style="padding:8px 10px;color:#e2e8f0">{j["j"]}</td>'
                   f'<td style="padding:8px 10px;color:#34d399;font-weight:600">{j["n"]} visite(s)</td>'
                   f'<td style="padding:8px 10px;color:#a78bfa">{j["u"]} visiteur(s) unique(s)</td></tr>')
    if not lignes:
        lignes = '<tr><td colspan="3" style="padding:14px;color:#94a3b8;text-align:center">Aucune visite enregistrée pour l\'instant.</td></tr>'

    emoji_src = {"facebook":"📘","instagram":"📸","tiktok":"🎵","whatsapp":"💬",
                 "youtube":"▶️","google":"🔎","qr":"🔳","ticketbingo":"🎱",
                 "direct":"🔗","autre-site":"🌐"}
    lignes_src = ""
    for r in s["par_source"]:
        nom = r["s"]; em = emoji_src.get(nom, "•")
        lignes_src += (f'<tr style="border-bottom:1px solid rgba(255,255,255,.08)">'
                       f'<td style="padding:8px 10px;color:#e2e8f0">{em} {nom}</td>'
                       f'<td style="padding:8px 10px;color:#34d399;font-weight:600">{r["n"]} visite(s)</td>'
                       f'<td style="padding:8px 10px;color:#a78bfa">{r["u"]} unique(s)</td></tr>')
    if not lignes_src:
        lignes_src = '<tr><td colspan="3" style="padding:14px;color:#94a3b8;text-align:center">Aucune source pour l\'instant.</td></tr>'

    def carte(emoji, valeur, libelle, couleur):
        return (f'<div style="flex:1;min-width:140px;background:#1e293b;border:1px solid #334155;'
                f'border-radius:12px;padding:16px;text-align:center">'
                f'<div style="font-size:26px">{emoji}</div>'
                f'<div style="font-size:30px;font-weight:800;color:{couleur};line-height:1.2">{valeur}</div>'
                f'<div style="font-size:12px;color:#94a3b8;margin-top:2px">{libelle}</div></div>')

    cartes = (
        carte("👁️", s["visites_auj"], "Visites aujourd'hui", "#34d399")
        + carte("🧍", s["uniques_auj"], "Visiteurs uniques aujourd'hui", "#a78bfa")
        + carte("📈", s["total"], "Visites au total", "#60a5fa")
        + carte("👥", s["uniques"], "Visiteurs uniques (total)", "#f472b6")
        + carte("🎲", s["essais"], "Essais gratuits lancés", "#fbbf24")
        + carte("🖨️", s["impressions"], "Générations de cartes", "#22d3ee")
        + carte("📄", s["feuilles"], "Feuilles générées", "#fb923c")
        + carte("🛒", s["commandes"], "Commandes créées", "#4ade80")
    )

    html = f'''<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>MANAPRINT — Visiteurs</title></head>
<body style="margin:0;background:#0f172a;color:#f1f5f9;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;padding:18px;max-width:760px;margin:0 auto">
<h1 style="font-size:20px;margin:0 0 4px">📊 MANAPRINT — Fréquentation</h1>
<div style="font-size:13px;color:#94a3b8;margin-bottom:18px">Statistiques de la plateforme manaprint.up.railway.app</div>
<div style="display:flex;flex-wrap:wrap;gap:10px;margin-bottom:24px">{cartes}</div>
<h2 style="font-size:15px;margin:0 0 10px;color:#cbd5e1">D'où viennent tes visiteurs ?</h2>
<table style="width:100%;border-collapse:collapse;background:#1e293b;border-radius:12px;overflow:hidden;margin-bottom:24px">
<thead><tr style="background:#334155"><th style="padding:10px;text-align:left;font-size:12px;color:#cbd5e1">Source</th><th style="padding:10px;text-align:left;font-size:12px;color:#cbd5e1">Visites</th><th style="padding:10px;text-align:left;font-size:12px;color:#cbd5e1">Uniques</th></tr></thead>
<tbody>{lignes_src}</tbody></table>
<h2 style="font-size:15px;margin:0 0 10px;color:#cbd5e1">Détail des 14 derniers jours</h2>
<table style="width:100%;border-collapse:collapse;background:#1e293b;border-radius:12px;overflow:hidden">
<thead><tr style="background:#334155"><th style="padding:10px;text-align:left;font-size:12px;color:#cbd5e1">Jour</th><th style="padding:10px;text-align:left;font-size:12px;color:#cbd5e1">Visites</th><th style="padding:10px;text-align:left;font-size:12px;color:#cbd5e1">Visiteurs uniques</th></tr></thead>
<tbody>{lignes}</tbody></table>
<div style="font-size:11px;color:#64748b;margin-top:18px;line-height:1.6">Les visiteurs sont comptés de façon anonyme (adresse IP hachée, jamais stockée en clair).<br>« Visiteur unique » = une même personne ne compte qu'une fois par mesure.</div>
</body></html>'''
    return Response(html, mimetype="text/html; charset=utf-8")


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


# ── ACCÈS CLIENT POLYNÉSIEN (sans machine, télécharge ou vient chez 2KEA) ──────
@app.route("/api/client-polynesien", methods=["POST"])
def client_poly():
    data = request.get_json(force=True)
    nom = data.get("nom", "").strip()
    email = data.get("email", "").strip()
    if not nom or "@" not in email:
        return jsonify({"ok": False, "message": "Nom et email requis"}), 400
    db.enregistrer_client_intl(nom, email, "Polynésie française")
    session["acces"] = "polynesien"
    session["identifiant"] = email
    return jsonify({"ok": True})


# ── GÉNÉRATION — MODE ESSAI (gratuit, 1 feuille, 3 max) ───────────────────────
@app.route("/api/essai", methods=["POST"])
def essai():
    if "acces" not in session:
        return jsonify({"ok": False, "message": "Accès non autorisé"}), 403

    identifiant = session.get("identifiant", "anon")

    data = request.get_json(force=True)
    programme = data.get("programme", "triple_action")
    theme = data.get("theme", "")
    couleur = REGISTRE_JEUX.get(programme, {}).get("couleur", True)

    # Personnalisation OBLIGATOIRE (sécurité : chaque ticket est identifié)
    # Vérifiée AVANT de décompter l'essai, pour ne pas pénaliser le client.
    nom_evenement = data.get("nom_evenement", "").strip()
    titre_jeu = data.get("titre_jeu", "").strip()
    date_lieu = data.get("date_lieu", "").strip()
    telephone = data.get("telephone", "").strip()
    if not nom_evenement or not titre_jeu or not date_lieu or not telephone:
        return jsonify({"ok": False, "message": "Personnalisation obligatoire : nom du client/association, nom du tournoi, date et numéro de téléphone du responsable."}), 400

    # Profil polynésien : le téléphone doit être un numéro polynésien (87/88/89/40)
    if session.get("acces") == "polynesien" and not est_numero_polynesien(telephone):
        return jsonify({"ok": False, "message": "Pour le tarif Polynésien, le téléphone du responsable doit être un numéro polynésien (87, 88, 89 ou 40). Si vous êtes hors Polynésie, utilisez l'accès Client International."}), 400

    # Noms réservés interdits dans la personnalisation
    reserve = contient_nom_reserve(nom_evenement, titre_jeu, date_lieu)
    if reserve:
        return jsonify({"ok": False, "message": "Ce nom est réservé et ne peut pas être utilisé dans la personnalisation. Merci d'indiquer le nom de votre propre événement."}), 400

    ok, restants = db.incrementer_essai(identifiant)
    if not ok:
        return jsonify({"ok": False, "message": "Vous avez utilisé vos 3 essais. De nouveaux essais seront disponibles dans 5 minutes. Vous pouvez aussi passer commande dès maintenant.", "essais_restants": 0}), 402

    # Essai = 1 seule feuille (selon le jeu)
    perso = {
        "nom_evenement": nom_evenement, "titre_jeu": titre_jeu,
        "couleur_perso": data.get("couleur_perso", ""), "date_lieu": date_lieu,
        "telephone": telephone,
    }
    nb_essai = CARTES_PAR_FEUILLE.get(programme, 10)  # 1 feuille
    pdf = generer_jeu(programme, nb_essai, couleur, perso)

    resp = send_file(pdf, mimetype="application/pdf", as_attachment=True,
                     download_name=f"ESSAI_manaprint_{programme}.pdf")
    resp.headers["X-Essais-Restants"] = str(restants)
    return resp


@app.route("/api/essais-restants", methods=["GET"])
def essais_restants():
    if "acces" not in session:
        return jsonify({"ok": False}), 403
    identifiant = session.get("identifiant", "anon")
    utilises = db.get_essais(identifiant)
    return jsonify({"ok": True, "restants": max(0, db.NB_ESSAIS_MAX - utilises)})


@app.route("/api/jeux", methods=["GET"])
def api_jeux():
    """Liste des jeux du registre universel (pour construire le menu côté page)."""
    return jsonify({"ok": True, "jeux": [
        {"id": jid, "nom": j["nom"], "emoji": j["emoji"],
         "cartes_par_feuille": j["cartes_par_feuille"], "couleur": j["couleur"]}
        for jid, j in REGISTRE_JEUX.items()
    ]})


@app.route("/api/partenaires", methods=["GET"])
def api_partenaires():
    """Liste des points d'impression partenaires (pour le menu déroulant)."""
    return jsonify({"ok": True, "partenaires": [
        {"id": k, "nom": v["nom"], "zone": v["zone"], "tel": v["tel"]}
        for k, v in PARTENAIRES.items()
    ]})


# ── COMMANDE — calcul du prix + création ──────────────────────────────────────
@app.route("/api/commander", methods=["POST"])
def commander():
    if "acces" not in session:
        return jsonify({"ok": False, "message": "Accès non autorisé"}), 403

    data = request.get_json(force=True)
    programme = data.get("programme", "triple_action")
    couleur = REGISTRE_JEUX.get(programme, {}).get("couleur", True)
    nb_feuilles = max(1, min(int(data.get("nb_feuilles", 500)), 5000))
    mode_paiement = data.get("mode_paiement", "manuel")  # 'stripe' | 'manuel'

    # Personnalisation OBLIGATOIRE (sécurité)
    nom_evenement = data.get("nom_evenement", "").strip()
    titre_jeu = data.get("titre_jeu", "").strip()
    date_lieu = data.get("date_lieu", "").strip()
    telephone = data.get("telephone", "").strip()
    if not nom_evenement or not titre_jeu or not date_lieu or not telephone:
        return jsonify({"ok": False, "message": "Personnalisation obligatoire : nom du client/association, nom du tournoi, date et numéro de téléphone du responsable."}), 400

    # Profil polynésien : le téléphone doit être un numéro polynésien (87/88/89/40)
    if session.get("acces") == "polynesien" and not est_numero_polynesien(telephone):
        return jsonify({"ok": False, "message": "Pour le tarif Polynésien, le téléphone du responsable doit être un numéro polynésien (87, 88, 89 ou 40). Si vous êtes hors Polynésie, utilisez l'accès Client International."}), 400

    # Noms réservés interdits dans la personnalisation
    reserve = contient_nom_reserve(nom_evenement, titre_jeu, date_lieu)
    if reserve:
        return jsonify({"ok": False, "message": "Ce nom est réservé et ne peut pas être utilisé dans la personnalisation. Merci d'indiquer le nom de votre propre événement."}), 400

    import json as _json
    # Partenaire d'impression choisi (ex. "fun_and_co", "vaikea_raiatea"). Vide = le client télécharge lui-même.
    partenaire = (data.get("partenaire", "") or "").strip()
    if partenaire and partenaire not in PARTENAIRES:
        partenaire = ""
    # Compatibilité ancienne case "fun_and_co"
    if not partenaire and data.get("fun_and_co"):
        partenaire = "fun_and_co"
    params_perso = _json.dumps({
        "theme": data.get("theme", ""),
        "nom_evenement": nom_evenement,
        "titre_jeu": titre_jeu,
        "couleur_perso": data.get("couleur_perso", ""),
        "date_lieu": date_lieu,
        "telephone": telephone,
        "partenaire": partenaire,
        "fun_and_co": (partenaire == "fun_and_co"),
    })

    commande_id, montant = db.creer_commande(
        identifiant=session.get("identifiant"),
        origine=session["acces"],
        programme=programme,
        couleur=couleur,
        nb_feuilles=nb_feuilles,
        mode_paiement=mode_paiement,
        params_perso=params_perso,
    )

    # Mode manuel : la commande est en attente de validation par 2KEA
    montant_aff = int(montant) if float(montant).is_integer() else montant
    if mode_paiement == "manuel":
        return jsonify({
            "ok": True, "commande_id": commande_id, "montant": montant_aff,
            "mode": "manuel",
            "message": f"Commande enregistrée ({montant_aff} XPF). Elle sera générée après validation du paiement par 2KEA & Associé.",
        })

    # Mode stripe : à brancher (emplacement prêt)
    # TODO Stripe : créer une session de paiement et renvoyer l'URL de checkout
    return jsonify({
        "ok": True, "commande_id": commande_id, "montant": montant,
        "mode": "stripe",
        "message": "Paiement en ligne bientôt disponible. Pour l'instant, choisissez le paiement sur place.",
        "stripe_pret": False,
    })


# ── GÉNÉRATION PAYÉE — réservée aux commandes validées ────────────────────────
@app.route("/api/generer-commande/<int:commande_id>", methods=["POST"])
def generer_commande(commande_id):
    if "acces" not in session:
        return jsonify({"ok": False, "message": "Accès non autorisé"}), 403

    cmd = db.get_commande(commande_id)
    if not cmd:
        return jsonify({"ok": False, "message": "Commande introuvable"}), 404
    if cmd["statut"] not in ("payee",):
        return jsonify({"ok": False, "message": "Cette commande n'est pas encore validée"}), 402

    import json as _json
    perso = _json.loads(cmd["params_perso"] or "{}")
    couleur = bool(cmd["couleur"])
    nb_feuilles = cmd["nb_feuilles"]
    programme = cmd["programme"]

    cartes_par_feuille = CARTES_PAR_FEUILLE.get(programme, 10)
    nb_cartes = nb_feuilles * cartes_par_feuille
    pdf = generer_jeu(programme, nb_cartes, couleur, perso)

    db.enregistrer_impression(
        origine=cmd["origine"], identifiant=cmd["identifiant"],
        programme=programme, theme=perso.get("theme", ""),
        nb_feuilles=nb_feuilles, couleur=couleur,
    )
    db.marquer_commande_generee(commande_id)

    return send_file(pdf, mimetype="application/pdf", as_attachment=True,
                     download_name=f"manaprint_{programme}.pdf")


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


# ── COMMANDES À VALIDER (paiement manuel) ─────────────────────────────────────
@app.route("/api/admin/commandes", methods=["GET"])
@admin_requis
def admin_commandes():
    return jsonify({"ok": True, "commandes": db.lister_commandes()})


@app.route("/api/admin/commandes/<int:commande_id>/valider", methods=["POST"])
@admin_requis
def admin_valider_commande(commande_id):
    cmd = db.get_commande(commande_id)
    if not cmd:
        return jsonify({"ok": False, "message": "Commande introuvable"}), 404
    db.marquer_commande_payee(commande_id)
    # Impression chez un partenaire : générer le PDF et l'envoyer par email au partenaire choisi
    import json as _json
    perso = _json.loads(cmd["params_perso"] or "{}")
    pid = perso.get("partenaire") or ("fun_and_co" if perso.get("fun_and_co") else "")
    info = ""
    if pid and pid in PARTENAIRES:
        part = PARTENAIRES[pid]
        try:
            cpf = CARTES_PAR_FEUILLE.get(cmd["programme"], 10)
            nb_cartes = cmd["nb_feuilles"] * cpf
            pdf = generer_jeu(cmd["programme"], nb_cartes, bool(cmd["couleur"]), perso)
            sujet = f"MANAPRINT — Commande #{commande_id} à imprimer"
            corps = (
                f"Bonjour {part['nom']},\n\n"
                f"Une nouvelle commande validée est à imprimer ({part['zone']}) :\n\n"
                f"  • Client : {cmd['identifiant']}\n"
                f"  • Événement : {perso.get('nom_evenement','')}\n"
                f"  • Jeu : {cmd['programme']} — {cmd['nb_feuilles']} feuille(s)\n"
                f"  • Téléphone du responsable : {perso.get('telephone','')}\n\n"
                "Le PDF prêt à imprimer est en pièce jointe.\n\n"
                "— MANAPRINT / 2KEA & Associé"
            )
            ok, m = envoyer_email_pdf(part["email"], sujet, corps, pdf,
                                      f"manaprint_cmd{commande_id}.pdf",
                                      copie=SMTP_USER or None)
            if ok:
                db.marquer_commande_generee(commande_id)
                info = f" Le PDF a été envoyé à {part['nom']} pour impression."
            else:
                info = f" ATTENTION : envoi à {part['nom']} échoué — " + m
        except Exception as e:
            info = f" ATTENTION : erreur génération/envoi {part['nom']} — " + str(e)
    return jsonify({"ok": True, "message": "Commande validée." + info})


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
