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
from generators import brown8
from generators import flash_quines_allonge
from generators import kai
from generators import ohana75_8boules
from generators import ohana75_10boules
from generators import quatre_coin
from generators import pol
from generators import sun
from generators import pow as powgen
from generators import win
from generators import rubis90
from generators import vai
from generators import wow4
from generators import bno
from generators import ngo
from generators import diamant
from generators import rui
from generators import tureia
from generators import champagne
from generators import fan90
from generators import oaoa
from generators import lagoon
from generators import havai
from generators import flash_debout
from generators import dual_dab
from generators import cerf_volant
from generators import ohana75_20boules

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
    "cocotie_mer": {
        "nom": "COCOTIE MER",
        "email": os.environ.get("COCOTIE_MER_EMAIL", "teagai10.fariki08@gmail.com"),
        "zone": "Faaa (Tahiti)",
        "tel": "",
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


def envoyer_email_simple(destinataire, sujet, corps, copie=None):
    """Envoie un email texte simple (SMTP Gmail). Renvoie (ok, message)."""
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

def _variante(fn, couleur_force, style_force="eco"):
    """Crée une version d'un générateur qui force la couleur (True/False) et la gamme."""
    def _w(**kwargs):
        kwargs["couleur"] = couleur_force
        kwargs["style"] = style_force
        return fn(**kwargs)
    return _w

def _enregistrer_paire(base_id, nom, emoji, cpf, fn, kwarg_nb="nb_cartes"):
    """Enregistre les 4 variantes d'un jeu — vision 2 gammes :
    ÉCO (écriture fine, économie de toner)  et  PREMIUM (écriture grasse, style P15).
    Chacune en (Couleur) et (N&B). 1 ligne = 4 entrées au menu.
    Les identifiants historiques (…_couleur / …_nb) restent sur la gamme ÉCO :
    les anciennes commandes se régénèrent à l'identique."""
    _enregistrer_jeu(base_id + "_couleur", nom + " · ÉCO (Couleur)", emoji, cpf,
                     _variante(fn, True, "eco"),  kwarg_nb=kwarg_nb, couleur=True)
    _enregistrer_jeu(base_id + "_nb",      nom + " · ÉCO (N&B)",     emoji, cpf,
                     _variante(fn, False, "eco"), kwarg_nb=kwarg_nb, couleur=False)
    _enregistrer_jeu(base_id + "_p15_couleur", nom + " · PREMIUM (Couleur)", emoji, cpf,
                     _variante(fn, True, "p15"),  kwarg_nb=kwarg_nb, couleur=True)
    _enregistrer_jeu(base_id + "_p15_nb",      nom + " · PREMIUM (N&B)",     emoji, cpf,
                     _variante(fn, False, "p15"), kwarg_nb=kwarg_nb, couleur=False)

#                  id base          nom                 emoji  cartes/feuille  fonction
_enregistrer_paire("triple_action", "Triple Action 75",  "🎯", 10, triple_action.generer_pdf, kwarg_nb="nb_tickets")
_enregistrer_paire("aloha75",       "Aloha 75",          "🌺", 12, aloha75.generer_pdf)
_enregistrer_paire("p6_marathon",   "P6 Marathon",       "6️⃣", 6,  p6_marathon.generer_pdf)
_enregistrer_paire("bingo_ball",    "Bingo Ball",        "🎱", 10, bingo_ball.generer_pdf)
_enregistrer_paire("ohana75_2s",    "OHANA 75 · 2 séries","🌺", 2,  ohana75_2series.generer_pdf)
_enregistrer_paire("brown8",        "BROWN 8 boules",     "🟤", 8,  brown8.generer_pdf)
_enregistrer_paire("flash_quines",  "FLASH QUINES allongé","⚡", 9,  flash_quines_allonge.generer_pdf)
_enregistrer_paire("kai",           "KAI 7 boules",       "🍽️", 12, kai.generer_pdf)
_enregistrer_paire("ohana75_8b",    "OHANA 75 · 8 boules","🌺", 9,  ohana75_8boules.generer_pdf)
_enregistrer_paire("ohana75_10b",   "OHANA 75 · 10 boules","🌺", 9,  ohana75_10boules.generer_pdf)
_enregistrer_paire("quatre_coin",   "4 COIN","🎯", 6,  quatre_coin.generer_pdf)
_enregistrer_paire("pol",           "POL 6 boules","🎲", 12, pol.generer_pdf)
_enregistrer_paire("sun",           "SUN 8 boules","☀️", 12, sun.generer_pdf)
_enregistrer_paire("pow",           "POW 8 boules","💥", 12, powgen.generer_pdf)
_enregistrer_paire("win",           "WIN 9 boules","🏆", 12, win.generer_pdf)
_enregistrer_paire("rubis90",       "RUBIS 90","💎", 12, rubis90.generer_pdf)
_enregistrer_paire("vai",           "VAI 9 boules","🌊", 12, vai.generer_pdf)
_enregistrer_paire("wow4",          "WOW 4","🎆", 12, wow4.generer_pdf)
_enregistrer_paire("bno",           "BNO 8 boules","🎯", 12, bno.generer_pdf)
_enregistrer_paire("ngo",           "NGO 8 boules","🎳", 12, ngo.generer_pdf)
_enregistrer_paire("diamant",       "DIAMANT","💎", 6,  diamant.generer_pdf)
_enregistrer_paire("rui",           "RUI","🎴", 12, rui.generer_pdf)
_enregistrer_paire("tureia",        "TUREIA","🔶", 6,  tureia.generer_pdf)
_enregistrer_paire("champagne",     "CHAMPAGNE","🥂", 6,  champagne.generer_pdf)
_enregistrer_paire("fan90",         "FAN 90","☀️", 8,  fan90.generer_pdf)
_enregistrer_paire("oaoa",          "OAOA","⭕", 12, oaoa.generer_pdf)
_enregistrer_paire("lagoon",        "LAGOON 5 boules","🏝️", 12, lagoon.generer_pdf)
_enregistrer_paire("havai",         "HAVAI","🌋", 6,  havai.generer_pdf)
_enregistrer_paire("flash_debout",  "FLASH QUINES DEBOUT","⚡", 8,  flash_debout.generer_pdf)
_enregistrer_paire("dual_dab",      "DUAL DAB 75","🤜", 6,  dual_dab.generer_pdf)
_enregistrer_paire("cerf_volant",   "CERF VOLANT","🪁", 6,  cerf_volant.generer_pdf)
_enregistrer_paire("ohana20b",      "OHANA 75 · 20 boules","🌺", 5,  ohana75_20boules.generer_pdf)
# --- Ajouter un futur jeu A4 = UNE ligne _enregistrer_paire(...) (crée Couleur + N&B) ---
# _enregistrer_paire("ohana90", "OHANA 90", "🌺", 8, ohana90.generer_pdf)

# Table cartes/feuille dérivée automatiquement du registre
CARTES_PAR_FEUILLE = {jid: j["cartes_par_feuille"] for jid, j in REGISTRE_JEUX.items()}


def generer_jeu(programme, nb_cartes, couleur, perso, evenement_id=""):
    """Génère le PDF A4 de N'IMPORTE QUEL jeu du registre. perso = champs de personnalisation.
    evenement_id (optionnel) : active le QR de vérification par carton."""
    jeu = REGISTRE_JEUX.get(programme) or REGISTRE_JEUX.get("triple_action")
    kwargs = {
        jeu["kwarg_nb"]: nb_cartes, "serie_start": 1, "theme": "", "couleur": couleur,
        "nom_evenement": perso.get("nom_evenement", ""), "titre_jeu": perso.get("titre_jeu", ""),
        "couleur_perso": perso.get("couleur_perso", ""), "date_lieu": perso.get("date_lieu", ""),
        "telephone": perso.get("telephone", ""),
    }
    if evenement_id:
        kwargs["evenement_id"] = evenement_id
    return jeu["generer"](**kwargs)


def _nouvel_evenement_id(programme):
    """Génère un identifiant d'événement court, lisible et unique (ex. TK7QK2)."""
    import secrets
    table = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "TK" + "".join(secrets.choice(table) for _ in range(6))


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


# ══ VÉRIFICATION DES CARTONS (scan du QR par l'organisateur) ══════════════════

def _aujourdhui_tahiti():
    """La date du jour en Polynésie (UTC-10)."""
    from datetime import datetime, timedelta
    return (datetime.utcnow() - timedelta(hours=10)).date()


def _appliquer_date_tournoi(res, evenement_id):
    """🔐 QR À DATE : si l'événement porte une date de tournoi, le carton n'est
    ACTIF que ce jour-là (+ le lendemain, pour les tournois qui finissent tard).
    Avant -> PAS_ACTIF · Après -> TERMINE (carton expiré, gain non réclamable)."""
    try:
        if res.get("statut") != "VALIDE":
            return res
        ev = db.get_evenement(evenement_id) or {}
        dt = (ev.get("date_tournoi") or "").strip()
        if not dt:
            return res
        from datetime import datetime, timedelta
        jour = datetime.strptime(dt, "%Y-%m-%d").date()
        auj = _aujourdhui_tahiti()
        if auj < jour:
            res["statut"] = "PAS_ACTIF"
            res["message"] = ("Carton du tournoi du %s — le QR ne sera actif que ce jour-l\u00e0."
                              % jour.strftime("%d/%m/%Y"))
        elif auj > jour + timedelta(days=1):
            res["statut"] = "TERMINE"
            res["message"] = ("Le tournoi du %s est termin\u00e9 — carton expir\u00e9."
                              % jour.strftime("%d/%m/%Y"))
    except Exception:
        pass
    return res


def _page_verif(statut, message, evenement_id, serie, code, ev=None, extra=""):
    """Page mobile simple et lisible : gros bandeau coloré VALIDE / COPIE / etc."""
    couleurs = {
        "VALIDE": ("#16a34a", "✅", "CARTON VALIDE"),
        "DEJA_RECLAME": ("#dc2626", "🚫", "DÉJÀ RÉCLAMÉ"),
        "INCONNU": ("#dc2626", "❌", "CARTON NON RECONNU"),
        "HORS_LOT": ("#d97706", "⚠️", "HORS DE CE LOT"),
        "PAS_ACTIF": ("#d97706", "🕒", "PAS ENCORE ACTIF"),
        "TERMINE": ("#dc2626", "⛔", "TOURNOI TERMINÉ"),
    }
    coul, emoji, titre = couleurs.get(statut, ("#334155", "❔", statut))
    nom_ev = (ev or {}).get("nom") or evenement_id or "—"
    bouton = ""
    if statut == "VALIDE":
        bouton = (
            '<form method="POST" action="/v/%s/%06d/%s/reclamer" style="margin-top:22px">'
            '<button style="width:100%%;padding:16px;font-size:1.1rem;font-weight:700;'
            'background:#16a34a;color:#fff;border:none;border-radius:12px">'
            'VALIDER LE GAIN (marquer réclamé)</button></form>'
            % (evenement_id, int(serie), code)
        )
    return Response("""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Vérification MANAPRINT</title></head>
<body style="margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:#0f172a;color:#f1f5f9;padding:0">
<div style="max-width:460px;margin:0 auto;padding:20px">
  <p style="text-align:center;letter-spacing:.2em;font-size:.7rem;color:#94a3b8;text-transform:uppercase">MANAPRINT · Vérification</p>
  <div style="background:%s;border-radius:18px;padding:28px 20px;text-align:center;margin-top:10px">
    <div style="font-size:3rem;line-height:1">%s</div>
    <div style="font-size:1.5rem;font-weight:800;margin-top:8px">%s</div>
  </div>
  <div style="background:#1e293b;border-radius:14px;padding:18px;margin-top:16px;line-height:1.7">
    <div style="font-size:.95rem;color:#cbd5e1">%s</div>
    <hr style="border:none;border-top:1px solid #334155;margin:14px 0">
    <div style="font-size:.85rem;color:#94a3b8">Événement</div>
    <div style="font-weight:700">%s</div>
    <div style="font-size:.85rem;color:#94a3b8;margin-top:8px">Carton N°</div>
    <div style="font-weight:700">%06d · code %s</div>
    %s
  </div>
  %s
  <p style="text-align:center;font-size:.72rem;color:#64748b;margin-top:22px">
    Sécurité 2KEA & Associé — un carton ne peut être validé qu'une seule fois.</p>
</div></body></html>""" % (
        coul, emoji, titre, message, nom_ev, int(serie), code, extra, bouton
    ), mimetype="text/html")


@app.route("/api/verifier-carton-code", methods=["POST"])
def api_verifier_carton_code():
    """Vérification MANUELLE (plan B des tournois) : N° de carton + code 6
    lettres, SANS scanner. L'événement est retrouvé automatiquement."""
    d = request.get_json(force=True, silent=True) or {}
    try:
        serie = int(d.get("serie", 0) or 0)
    except Exception:
        serie = 0
    code = (d.get("code", "") or "").strip().upper()
    if serie <= 0 or len(code) != 6:
        return jsonify({"statut": "INCONNU",
                        "message": "Entre le N\u00b0 du carton et son code \u00e0 6 lettres."})
    try:
        from generators import qr_verif as _qrv
        with db.get_db() as conn:
            evs = [r[0] for r in conn.execute(
                "SELECT id FROM evenements ORDER BY rowid DESC LIMIT 300")]
        for ev in evs:
            if _qrv.code_verif(ev, serie) == code:
                res = db.verifier_carton(ev, serie, code)
                res["evenement_id"] = ev
                res = _appliquer_date_tournoi(res, ev)
                try:
                    if res.get("statut") in ("VALIDE", "DEJA_RECLAME"):
                        res["couleur_nom"], res["couleur_hex"] = _qrv.couleur_carton(ev, serie)
                except Exception:
                    pass
                return jsonify(res)
    except Exception as e:
        return jsonify({"statut": "INCONNU", "message": "Erreur de v\u00e9rification : %s" % e})
    return jsonify({"statut": "INCONNU",
                    "message": "Aucun carton ne correspond \u00e0 ce N\u00b0 + code."})


@app.route("/v/<evenement_id>/<int:serie>/<code>")
def verifier_carton_page(evenement_id, serie, code):
    """Page ouverte quand l'organisateur scanne le QR d'un carton."""
    res = db.verifier_carton(evenement_id, serie, code)
    res = _appliquer_date_tournoi(res, evenement_id)
    # 🎨 Couleur officielle du carton (imprimée en N&B, prouvée ici en couleur)
    extra = ""
    if res["statut"] in ("VALIDE", "DEJA_RECLAME"):
        try:
            from generators import qr_verif as _qrv
            nom_c, hex_c = _qrv.couleur_carton(evenement_id, serie)
            extra = (
                '<div style="font-size:.85rem;color:#94a3b8;margin-top:8px">Couleur du carton</div>'
                '<div style="display:inline-block;margin-top:4px;padding:8px 22px;border-radius:10px;'
                'font-weight:800;font-size:1.05rem;background:%s;color:#fff">%s</div>' % (hex_c, nom_c)
            )
        except Exception:
            extra = ""
    return _page_verif(res["statut"], res["message"], evenement_id, serie, code,
                       ev=res.get("evenement"), extra=extra)


@app.route("/v/<evenement_id>/<int:serie>/<code>/reclamer", methods=["POST"])
def reclamer_carton_page(evenement_id, serie, code):
    """Valide le gain : marque le carton réclamé (après vérif du code)."""
    # revérifier le code avant d'agir (empêche une réclamation forgée)
    res = db.verifier_carton(evenement_id, serie, code)
    res = _appliquer_date_tournoi(res, evenement_id)
    if res["statut"] == "DEJA_RECLAME":
        return _page_verif("DEJA_RECLAME", res["message"], evenement_id, serie, code,
                           ev=res.get("evenement"))
    if res["statut"] != "VALIDE":
        return _page_verif(res["statut"], res["message"], evenement_id, serie, code,
                           ev=res.get("evenement"))
    rec = db.reclamer_carton(evenement_id, serie)
    if rec.get("deja"):
        return _page_verif("DEJA_RECLAME", "Carton déjà réclamé entre-temps.",
                           evenement_id, serie, code, ev=res.get("evenement"))
    return _page_verif("VALIDE", "✔ Gain validé. Ce carton est maintenant marqué comme réclamé "
                       "et ne pourra plus être validé une seconde fois.",
                       evenement_id, serie, code, ev=res.get("evenement"),
                       extra='<div style="margin-top:10px;color:#16a34a;font-weight:700">RÉCLAMÉ ✓</div>')


@app.route("/api/verifier-carton", methods=["POST"])
def api_verifier_carton():
    """Version API (pour une future app de scan)."""
    d = request.get_json(force=True, silent=True) or {}
    res = db.verifier_carton(d.get("evenement_id", ""), d.get("serie", 0), d.get("code", ""))
    res = _appliquer_date_tournoi(res, evenement_id)
    # 🎨 la couleur officielle accompagne le verdict (pastille au caller)
    try:
        from generators import qr_verif as _qrv
        if res.get("statut") in ("VALIDE", "DEJA_RECLAME"):
            res["couleur_nom"], res["couleur_hex"] = _qrv.couleur_carton(evenement_id, serie)
    except Exception:
        pass
    return jsonify(res)


@app.route("/caller")
@app.route("/caller/<evenement_id>")
def caller(evenement_id=None):
    """MANAPRINT CALLER : tirage des boules + vérification QR intégrée."""
    return render_template("caller.html")


@app.route("/caller-qr")
def caller_qr():
    """Page imprimable : un QR code qui ouvre le CALLER. À coller sur la table de l'organisateur."""
    base = os.environ.get("MANAPRINT_BASE_URL", request.host_url.rstrip("/"))
    url_caller = base + "/caller"
    # QR en SVG (aucune dépendance externe : marche partout, imprimable net à toute taille)
    qr_svg = ""
    try:
        from reportlab.graphics.barcode import qr as _qr
        w = _qr.QrCodeWidget(url_caller); w.barLevel = "M"
        code = w.qr
        code.make()
        n = code.getModuleCount()
        cell = 280.0 / n
        rects = []
        for r in range(n):
            for cidx in range(n):
                if code.isDark(r, cidx):
                    x = cidx * cell
                    y = r * cell
                    rects.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f"/>' % (x, y, cell + 0.4, cell + 0.4))
        qr_svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="280" height="280" '
                  'viewBox="0 0 280 280" fill="#000"><rect width="280" height="280" fill="#fff"/>'
                  + "".join(rects) + "</svg>")
    except Exception:
        qr_svg = ""

    return Response("""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>QR CALLER — MANAPRINT</title>
<style>@media print{.noprint{display:none}}</style></head>
<body style="margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:#fff;color:#0f172a;text-align:center;padding:30px">
  <div style="max-width:420px;margin:0 auto;border:2px solid #0f172a;border-radius:18px;padding:28px">
    <div style="font-size:1.5rem;font-weight:800">&#127921; MANAPRINT CALLER</div>
    <div style="color:#475569;font-size:.85rem;margin-top:4px">Scannez pour ouvrir le tirage &amp; la v&eacute;rification</div>
    <div style="width:280px;height:280px;margin:20px auto">%s</div>
    <div style="font-size:.8rem;color:#475569;word-break:break-all">%s</div>
    <div style="margin-top:16px;font-size:.75rem;color:#94a3b8">2KEA &amp; Associ&eacute; &mdash; Tirage s&eacute;curis&eacute;</div>
  </div>
  <button class="noprint" onclick="window.print()" style="margin-top:22px;padding:14px 26px;font-size:1rem;font-weight:700;background:#0f172a;color:#fff;border:none;border-radius:12px;cursor:pointer">&#128424; Imprimer cette affichette</button>
</body></html>""" % (qr_svg or "QR indisponible", url_caller), mimetype="text/html")


# Plages de boules par jeu (le serveur est la seule autorité — l'organisateur ne choisit rien)
_PLAGES_CALLER = {
    "aloha75": (1, 75), "ohana75": (1, 75), "brown8": (1, 75), "p6_marathon": (1, 75),
    "triple": (1, 75), "bingo_ball": (1, 75), "quatre_coin": (1, 75),
    "kai": (1, 29), "flash90": (1, 90), "quines90": (1, 90),
    "pol": (30, 60),
    "sun": (1, 24),
    "pow": (1, 27),
    "win": (1, 45),
    "rubis90": (1, 90),
    "vai": (61, 90),
    "wow4": (30, 60),
    "bno": (1, 75),
    "ngo": (31, 75),
    "diamant": (1, 75),
    "rui": (30, 59),
    "tureia": (1, 75),
    "champagne": (1, 75),
    "fan90": (1, 90),
    "oaoa": (16, 75),
    "lagoon": (1, 50),
    "havai": (1, 75),
    "flash_debout": (1, 90),
    "dual_dab": (1, 75),
    "cerf_volant": (1, 75),
    "ohana20b": (1, 75),
}


# Jeux à colonnes NON contiguës : liste explicite des boules valides
_BOULES_CALLER = {
    "bno": [n for n in range(1, 16)] + [n for n in range(31, 46)] + [n for n in range(61, 76)],
    "tureia": [n for n in range(1, 31)] + [n for n in range(46, 76)],  # colonne 31-45 morte
    "fan90": [n for n in range(1, 11)] + [n for n in range(20, 91)],   # sans le 11 à 19
    "oaoa": [n for n in range(16, 31)] + [n for n in range(61, 76)],   # O 16-30 et A 61-75
    "cerf_volant": [n for n in range(1, 31)] + [n for n in range(46, 76)],  # sans le 31-45
}


@app.route("/api/caller/tirer", methods=["POST"])
def api_caller_tirer():
    """Tire UNE boule côté serveur (imprévisible, horodatée, journalisée).
    L'organisateur ne peut ni choisir ni deviner la boule suivante."""
    import secrets
    d = request.get_json(force=True, silent=True) or {}
    jeu = d.get("jeu", "aloha75")
    if jeu not in _PLAGES_CALLER:
        return jsonify({"ok": False, "message": "Jeu inconnu."}), 400
    bmin, bmax = _PLAGES_CALLER[jeu]
    boules_valides = _BOULES_CALLER.get(jeu)

    partie_id = (d.get("partie_id") or "").strip()
    if not partie_id:
        # nouvelle partie : identifiant aléatoire non devinable
        partie_id = "P" + secrets.token_hex(6).upper()
        db.creer_partie(partie_id, jeu, bmin, bmax)

    boule = db.tirer_boule(partie_id, bmin, bmax, boules_valides)
    if boule is None:
        return jsonify({"ok": False, "message": "Toutes les boules sont sorties.",
                        "partie_id": partie_id, "tirees": db.boules_tirees(partie_id)}), 409
    return jsonify({"ok": True, "partie_id": partie_id, "boule": boule,
                    "tirees": db.boules_tirees(partie_id)})


@app.route("/api/caller/journal/<partie_id>")
def api_caller_journal(partie_id):
    """Journal horodaté d'une partie (preuve infalsifiable de l'ordre des tirages)."""
    return jsonify({"ok": True, "partie_id": partie_id, "journal": db.journal_partie(partie_id)})


@app.route("/evenement/<evenement_id>")
def tableau_evenement(evenement_id):
    """Tableau de bord organisateur : suivi des cartons réclamés pour un événement."""
    st = db.stats_evenement(evenement_id)
    if not st:
        return Response("<p style='font-family:sans-serif;padding:20px'>Événement inconnu.</p>",
                        mimetype="text/html")
    ev = st["evenement"]
    return Response("""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s — MANAPRINT</title></head>
<body style="margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:#0f172a;color:#f1f5f9">
<div style="max-width:460px;margin:0 auto;padding:22px">
  <p style="text-align:center;letter-spacing:.2em;font-size:.7rem;color:#94a3b8;text-transform:uppercase">MANAPRINT · Événement</p>
  <h1 style="font-size:1.3rem;text-align:center;margin:4px 0 2px">%s</h1>
  <p style="text-align:center;color:#94a3b8;font-size:.8rem">Code événement : <b style="color:#f1f5f9">%s</b></p>
  <div style="display:flex;gap:12px;margin-top:18px">
    <div style="flex:1;background:#1e293b;border-radius:14px;padding:16px;text-align:center">
      <div style="font-size:2rem;font-weight:800">%d</div>
      <div style="font-size:.78rem;color:#94a3b8">cartons du lot</div>
    </div>
    <div style="flex:1;background:#16a34a22;border:1px solid #16a34a55;border-radius:14px;padding:16px;text-align:center">
      <div style="font-size:2rem;font-weight:800;color:#4ade80">%d</div>
      <div style="font-size:.78rem;color:#94a3b8">gains validés</div>
    </div>
  </div>
  <p style="font-size:.8rem;color:#94a3b8;line-height:1.7;margin-top:20px">
    Pour vérifier un carton gagnant, scannez son QR code avec l'appareil photo de votre téléphone.
    La page affichera <b style="color:#4ade80">VALIDE</b>, <b style="color:#f87171">DÉJÀ RÉCLAMÉ</b> (photocopie)
    ou <b style="color:#f87171">NON RECONNU</b> (faux carton).</p>
  <p style="text-align:center;font-size:.72rem;color:#64748b;margin-top:22px">
    Sécurité 2KEA & Associé</p>
</div></body></html>""" % (
        ev["nom"] or evenement_id, ev["nom"] or evenement_id, evenement_id,
        st["total"], st["reclames"]
    ), mimetype="text/html")


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


@app.route("/api/demande-machine", methods=["POST"])
def demande_machine():
    """Reçoit une demande de machine (téléphone + email) et l'envoie par email à la plateforme."""
    data = request.get_json(force=True)
    tel = (data.get("telephone") or "").strip()
    email = (data.get("email") or "").strip()
    if not tel and not email:
        return jsonify({"ok": False, "message": "Téléphone ou email requis"}), 400
    corps = (
        "Nouvelle demande de machine — MANAPRINT\n\n"
        "Téléphone : " + (tel or "—") + "\n"
        "Email : " + (email or "—") + "\n"
    )
    dest = SMTP_USER or "directionvaikeashop@gmail.com"
    ok, m = envoyer_email_simple(dest, "MANAPRINT — Demande de machine", corps)
    if ok:
        return jsonify({"ok": True})
    return jsonify({"ok": False, "message": m}), 500


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
    nb_feuilles = max(1, min(int(data.get("nb_feuilles", 10)), 250))  # plafond : 250 feuilles par commande
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

    # ── Mode événement : on crée un événement + QR de vérification pour ce lot ──
    evenement_id = ""
    try:
        evenement_id = _nouvel_evenement_id(programme)
        db.creer_evenement(
            evenement_id=evenement_id,
            nom=perso.get("titre_jeu", "") or perso.get("nom_evenement", "") or "Événement",
            identifiant=cmd["identifiant"],
            programme=programme,
            serie_min=1,
            serie_max=nb_cartes,
        )
    except Exception:
        evenement_id = ""  # anti-panne : en cas d'échec, on génère sans QR

    pdf = generer_jeu(programme, nb_cartes, couleur, perso, evenement_id=evenement_id)

    db.enregistrer_impression(
        origine=cmd["origine"], identifiant=cmd["identifiant"],
        programme=programme, theme=perso.get("theme", ""),
        nb_feuilles=nb_feuilles, couleur=couleur,
    )
    db.marquer_commande_generee(commande_id)

    nom_fichier = "manaprint_%s%s.pdf" % (programme, ("_" + evenement_id) if evenement_id else "")
    return send_file(pdf, mimetype="application/pdf", as_attachment=True,
                     download_name=nom_fichier)


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

        # 🏭 FABRICATION EN ARRIÈRE-PLAN : les grosses commandes (des centaines de
        # feuilles + microtexte de sécurité) prennent plusieurs minutes. On répond
        # IMMÉDIATEMENT au navigateur (fini « Erreur réseau ») et la fabrication +
        # l'envoi au partenaire continuent tranquillement côté serveur.
        def _fabriquer_et_envoyer():
            try:
                cpf = CARTES_PAR_FEUILLE.get(cmd["programme"], 10)
                nb_cartes = cmd["nb_feuilles"] * cpf
                evenement_id = ""
                try:
                    evenement_id = _nouvel_evenement_id(cmd["programme"])
                    db.creer_evenement(
                        evenement_id=evenement_id,
                        nom=perso.get("titre_jeu", "") or perso.get("nom_evenement", "") or "Événement",
                        identifiant=cmd["identifiant"], programme=cmd["programme"],
                        serie_min=1, serie_max=nb_cartes,
                        date_tournoi=perso.get("date_tournoi", ""),
                    )
                except Exception:
                    evenement_id = ""
                pdf = generer_jeu(cmd["programme"], nb_cartes, bool(cmd["couleur"]), perso,
                                  evenement_id=evenement_id)
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
                    print(f"[FABRICATION OK] commande {commande_id} envoyée à {part['nom']}")
                else:
                    print(f"[FABRICATION ECHEC ENVOI] commande {commande_id} : {m}")
            except Exception as e:
                print(f"[FABRICATION ERREUR] commande {commande_id} : {e}")

        import threading as _th
        _th.Thread(target=_fabriquer_et_envoyer, daemon=True).start()
        info = (f" Le PDF est en fabrication et sera envoyé automatiquement à {part['nom']}"
                " (plusieurs minutes pour les grosses commandes).")
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
