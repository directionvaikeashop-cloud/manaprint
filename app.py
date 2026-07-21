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
from generators import moorea
from generators import triple_action_90
from generators import funday
from generators import huahine
from generators import boules40
from generators import tea
from generators import ohana75_4series
from generators import ohana90_4series
from generators import bgo
from generators import igo
from generators import kea
from generators import moon
from generators import ani
from generators import brown14
from generators import ino8
from generators import tahaa
from generators import boules60
from generators import ahuru
from generators import tchin
from generators import ing
from generators import lunes75
from generators import miss75
from generators import bien_sur
from generators import ohana90_12boules
from generators import ohana90_24boules
from generators import lettre_u
from generators import lettre_l
from generators import topday
from generators import fleche
from generators import yes
from generators import bio
from generators import bio5
from generators import zin
from generators import rai
from generators import bin8
from generators import pow6
from generators import bg90
from generators import bo90
from generators import bn90
from generators import bi90
from generators import bgo5
from generators import bo75
from generators import bg75
from generators import bn75
from generators import wiz
from generators import p15_marathon
from generators import p12_marathon
from generators import ohana75_20boules

app = Flask(__name__)
app.secret_key = os.environ.get("MANAPRINT_SECRET", "dev-secret-a-changer-en-prod")

# ── Envoi d'email (impression partenaire FUN AND CO) ──────────────────────────
import smtplib
from email.message import EmailMessage

FUN_AND_CO_EMAIL = os.environ.get("FUN_AND_CO_EMAIL", "funandco24@gmail.com")
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
        # 💡 Mêmes conditions que RANIHEI : PDF 1,5 F (2KEA & Associé) —
        # tarif d'impression à demander directement au partenaire.
        "prix_pdf_seul": 1.5,
    },
    "cocotie_mer": {
        "nom": "COCOTIE MER",
        "email": os.environ.get("COCOTIE_MER_EMAIL", "teagai10.fariki08@gmail.com"),
        "zone": "Faaa (Tahiti)",
        "tel": "",
        # 💡 Mêmes conditions que RANIHEI : PDF 1,5 F (2KEA & Associé) —
        # tarif d'impression à demander directement au partenaire.
        "prix_pdf_seul": 1.5,
    },
    "ranihei": {
        "nom": "RANIHEI",
        "email": os.environ.get("RANIHEI_EMAIL", "tetuanuiheini@gmail.com"),
        "zone": "Raiatea",
        "tel": "87 77 39 19 · 87 27 62 26",
        # 💡 Modèle spécial : la plateforme ne facture que le PDF (1,5 F la feuille) —
        # l'impression se règle DIRECTEMENT avec RANIHEI.
        "prix_pdf_seul": 1.5,
    },
}

def envoyer_email_pdf(destinataire, sujet, corps, pdf_io, nom_fichier, copie=None,
                      pdf2_io=None, nom2_fichier=None):
    """Envoie un email avec un PDF en pièce jointe (SMTP Gmail). Renvoie (ok, message).
    copie : adresse mise en copie (CC), ex. la plateforme pour garder une trace.
    pdf2_io/nom2_fichier : 2e pièce jointe optionnelle (rapport confidentiel)."""
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
        if pdf_io is not None:   # None = trop lourd pour Gmail -> le lien du coffre-fort suffit
            pdf_io.seek(0)
            msg.add_attachment(pdf_io.read(), maintype="application", subtype="pdf", filename=nom_fichier)
        if pdf2_io is not None and nom2_fichier:
            pdf2_io.seek(0)
            msg.add_attachment(pdf2_io.read(), maintype="application", subtype="pdf",
                               filename=nom2_fichier)
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
_enregistrer_paire("moorea",        "MOOREA",     "🌴", 8,  moorea.generer_pdf)
_enregistrer_paire("triple_action_90", "TRIPLE ACTION 90", "🎪", 10, triple_action_90.generer_pdf)
_enregistrer_paire("funday",        "FUNDAY",     "🎈", 20, funday.generer_pdf)
_enregistrer_paire("huahine",       "HUAHINE",    "⛵", 8,  huahine.generer_pdf)
_enregistrer_paire("boules40",      "40 BOULES",  "🎳", 12, boules40.generer_pdf)
_enregistrer_paire("tea",           "TEA",        "🍵", 12, tea.generer_pdf)
_enregistrer_paire("ohana75_4series", "OHANA 75 · 4 séries", "🌺", 4, ohana75_4series.generer_pdf)
_enregistrer_paire("ohana90_4series", "OHANA 90 · 4 séries", "🌸", 4, ohana90_4series.generer_pdf)
_enregistrer_paire("bgo",           "BGO",        "🔠", 12, bgo.generer_pdf)
_enregistrer_paire("igo",           "IGO",        "🎱", 12, igo.generer_pdf)
_enregistrer_paire("kea",           "KEA",        "🌿", 12, kea.generer_pdf)
_enregistrer_paire("moon",          "MOON",       "🌙", 6,  moon.generer_pdf)
_enregistrer_paire("ani",           "ANI",        "🌠", 12, ani.generer_pdf)
_enregistrer_paire("brown14",       "BROWN 14 boules", "🟤", 8, brown14.generer_pdf)
_enregistrer_paire("ino8",          "INO 8 boules", "🎐", 12, ino8.generer_pdf)
_enregistrer_paire("tahaa",         "TAHAA",      "🥥", 18, tahaa.generer_pdf)
_enregistrer_paire("boules60",      "60 BOULES",  "🔵", 12, boules60.generer_pdf)
_enregistrer_paire("ahuru",         "AHURU",      "🔟", 10, ahuru.generer_pdf)
_enregistrer_paire("tchin",         "TCHIN",      "🍻", 12, tchin.generer_pdf)
_enregistrer_paire("ing",           "ING",        "🧭", 12, ing.generer_pdf)
_enregistrer_paire("lunes75",       "LUNES 75",   "🌜", 12, lunes75.generer_pdf)
_enregistrer_paire("miss75",        "MISS 75",    "👑", 4,  miss75.generer_pdf)
_enregistrer_paire("bien_sur",      "BIEN SÛR",   "✅", 8,  bien_sur.generer_pdf)
_enregistrer_paire("ohana90_12b",   "OHANA 90 · 12 boules", "🌼", 9, ohana90_12boules.generer_pdf)
_enregistrer_paire("ohana90_24b",   "OHANA 90 · 24 boules", "💮", 6, ohana90_24boules.generer_pdf)
_enregistrer_paire("lettre_u",      "LETTRE U",   "😃", 6,  lettre_u.generer_pdf)
_enregistrer_paire("lettre_l",      "LETTRE L",   "😄", 6,  lettre_l.generer_pdf)
_enregistrer_paire("topday",        "TOPDAY",     "🔝", 12, topday.generer_pdf)
_enregistrer_paire("fleche",        "FLÈCHE",     "🏹", 6,  fleche.generer_pdf)
_enregistrer_paire("yes",           "YES",        "👍", 15, yes.generer_pdf)
_enregistrer_paire("bio",           "BIO 8 boules", "🌱", 12, bio.generer_pdf)
_enregistrer_paire("bio5",          "BIO 5 boules", "🌿", 12, bio5.generer_pdf)
_enregistrer_paire("zin",           "ZIN",        "⚡", 12, zin.generer_pdf)
_enregistrer_paire("rai",           "RAI",        "🌈", 12, rai.generer_pdf)
_enregistrer_paire("bin8",          "BIN 8 boules", "🎯", 12, bin8.generer_pdf)
_enregistrer_paire("pow6",          "POW 5 boules", "💫", 12, pow6.generer_pdf)
_enregistrer_paire("bg90",          "BG 90",      "🎱", 12, bg90.generer_pdf)
_enregistrer_paire("bo90",          "BO 90",      "🟠", 12, bo90.generer_pdf)
_enregistrer_paire("bn90",          "BN 90",      "🟤", 12, bn90.generer_pdf)
_enregistrer_paire("bi90",          "BI 90",      "🔵", 12, bi90.generer_pdf)
_enregistrer_paire("bgo5",          "BGO 5 boules", "🅾️", 12, bgo5.generer_pdf)
_enregistrer_paire("bo75",          "BO 75",      "🔷", 12, bo75.generer_pdf)
_enregistrer_paire("bg75",          "BG 75",      "💠", 12, bg75.generer_pdf)
_enregistrer_paire("bn75",          "BN 75",      "🔶", 12, bn75.generer_pdf)
_enregistrer_paire("wiz",           "WIZ 4 boules", "🧙", 12, wiz.generer_pdf)
_enregistrer_paire("p15_marathon",  "P15 Marathon", "🥥", 15, p15_marathon.generer_pdf)
_enregistrer_paire("p12_marathon",  "P12 Marathon", "🌴", 12, p12_marathon.generer_pdf)
_enregistrer_paire("ohana20b",      "OHANA 75 · 20 boules","🌺", 5,  ohana75_20boules.generer_pdf)
# --- Ajouter un futur jeu A4 = UNE ligne _enregistrer_paire(...) (crée Couleur + N&B) ---
# _enregistrer_paire("ohana90", "OHANA 90", "🌺", 8, ohana90.generer_pdf)

# Table cartes/feuille dérivée automatiquement du registre
CARTES_PAR_FEUILLE = {jid: j["cartes_par_feuille"] for jid, j in REGISTRE_JEUX.items()}


def generer_jeu(programme, nb_cartes, couleur, perso, evenement_id="", serie_start=1):
    """Génère le PDF A4 de N'IMPORTE QUEL jeu du registre. perso = champs de personnalisation.
    evenement_id (optionnel) : active le QR de vérification par carton.
    ⚠️ serie_start pilote AUSSI le tirage des numéros : deux commandes doivent
    recevoir des serie_start DIFFÉRENTS, sinon leurs cartons sont identiques !
    (bug des 6 PDF jumeaux détecté par Maeva le 18/07/2026 — corrigé ici)"""
    jeu = REGISTRE_JEUX.get(programme) or REGISTRE_JEUX.get("triple_action")
    kwargs = {
        jeu["kwarg_nb"]: nb_cartes, "serie_start": max(1, int(serie_start)), "theme": "", "couleur": couleur,
        "nom_evenement": perso.get("nom_evenement", ""), "titre_jeu": perso.get("titre_jeu", ""),
        "couleur_perso": perso.get("couleur_perso", ""), "date_lieu": perso.get("date_lieu", ""),
        "telephone": perso.get("telephone", ""),
    }
    if evenement_id:
        kwargs["evenement_id"] = evenement_id
    return jeu["generer"](**kwargs)


def _nom_evenement_complet(perso):
    """🏷️ Le nom qui vivra dans le QR : « CLIENT/ASSOCIATION — TITRE DU JEU ».
    Au scan d'un carton, l'organisateur voit À QUI appartient le lot (vision Maeva)."""
    assoc = (perso.get("nom_evenement") or "").strip()
    titre = (perso.get("titre_jeu") or "").strip()
    if assoc and titre and assoc.upper() != titre.upper():
        return f"{assoc} \u2014 {titre}"
    return assoc or titre or "Événement"


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

def _rapport_confidentiel(commande_id, cmd, perso, evenement_id, nb_cartes):
    """📋🤫 COMPTE-RENDU CONFIDENTIEL de l'organisatrice : la carte secrète
    série -> couleur de tout le lot (+ date, événement). À NE PAS montrer
    aux joueurs — c'est la grille de contrôle des couleurs fantômes."""
    import io as _io
    from reportlab.pdfgen import canvas as _cv
    from reportlab.lib.pagesizes import A4 as _A4
    from reportlab.lib import colors as _co
    from reportlab.lib.units import mm as _mm
    from generators import qr_verif as _qrv

    buf = _io.BytesIO()
    c = _cv.Canvas(buf, pagesize=_A4, pageCompression=1)
    W, H = _A4
    HEXA = dict(_qrv._PALETTE)

    def entete(page):
        c.setFillColor(_co.HexColor("#dc2626"))
        c.rect(0, H - 16 * _mm, W, 16 * _mm, stroke=0, fill=1)
        c.setFillColor(_co.white)
        c.setFont("Helvetica-Bold", 13)
        c.drawCentredString(W / 2, H - 7 * _mm,
                            "CONFIDENTIEL — R\u00c9SERV\u00c9 \u00c0 L'ORGANISATRICE")
        c.setFont("Helvetica", 8)
        c.drawCentredString(W / 2, H - 12.5 * _mm,
                            "Grille de contr\u00f4le des couleurs — ne pas montrer aux joueurs")
        c.setFillColor(_co.HexColor("#1F2937"))
        c.setFont("Helvetica-Bold", 10)
        c.drawString(15 * _mm, H - 23 * _mm,
                     "Commande #%s  \u00b7  %s  \u00b7  \u00c9v\u00e9nement %s" % (
                         commande_id, cmd.get("programme", ""), evenement_id))
        c.setFont("Helvetica", 8.5)
        infos = "%s  \u00b7  %s carton(s), s\u00e9ries %06d \u00e0 %06d" % (
            perso.get("nom_evenement", ""), nb_cartes, 1, nb_cartes)
        if perso.get("date_tournoi"):
            infos += "  \u00b7  \ud83d\udd10 actif le %s" % perso["date_tournoi"]
        c.drawString(15 * _mm, H - 28 * _mm, infos)
        c.setFillColor(_co.HexColor("#6b7280")); c.setFont("Helvetica", 7)
        c.drawRightString(W - 12 * _mm, H - 23 * _mm, "page %d" % page)

    choix = (perso.get("couleur_qr") or "").strip().upper()
    if choix and choix in HEXA:
        entete(1)
        c.setFillColor(_co.HexColor("#1F2937")); c.setFont("Helvetica-Bold", 14)
        c.drawString(15 * _mm, H - 45 * _mm, "Couleur choisie pour TOUT le lot :")
        c.setFillColor(_co.HexColor(HEXA[choix]))
        c.roundRect(15 * _mm, H - 62 * _mm, 60 * _mm, 12 * _mm, 3 * _mm, stroke=0, fill=1)
        c.setFillColor(_co.white); c.setFont("Helvetica-Bold", 13)
        c.drawCentredString(45 * _mm, H - 58 * _mm, choix)
        c.setFillColor(_co.HexColor("#6b7280")); c.setFont("Helvetica", 9)
        c.drawString(15 * _mm, H - 70 * _mm,
                     "Chaque scan de carton de ce lot doit afficher cette pastille.")
    else:
        # Loterie : la table s\u00e9rie -> couleur, en colonnes compactes
        COLS, LIGNES = 6, 44
        par_page = COLS * LIGNES
        page = 1
        entete(page)
        y_top = H - 38 * _mm
        col_w = (W - 24 * _mm) / COLS
        i = 0
        for serie in range(1, nb_cartes + 1):
            if i == par_page:
                c.showPage(); page += 1; entete(page); i = 0
            colu = i // LIGNES
            lig = i % LIGNES
            x = 12 * _mm + colu * col_w
            y = y_top - lig * 5.2 * _mm
            nom, hx = _qrv.couleur_carton(evenement_id, serie)
            c.setFillColor(_co.HexColor(hx))
            c.rect(x, y - 0.6 * _mm, 3.2 * _mm, 3.2 * _mm, stroke=0, fill=1)
            c.setFillColor(_co.HexColor("#1F2937")); c.setFont("Helvetica", 7.5)
            c.drawString(x + 4.4 * _mm, y, "%06d" % serie)
            c.setFont("Helvetica-Bold", 7.5)
            c.drawString(x + 15.5 * _mm, y, nom)
            i += 1
    c.save()
    buf.seek(0)
    return buf


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
    <div style="font-size:.85rem;color:#94a3b8">Client / Association \u00b7 \u00c9v\u00e9nement</div>
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
    # 🐛 RÉPARATION (juil. 2026) : les variables restaient dans le JSON ->
    # NameError -> erreur 500 -> « impossible de vérifier » au scan du caller.
    evenement_id = d.get("evenement_id", "")
    serie = d.get("serie", 0)
    code = d.get("code", "")
    res = db.verifier_carton(evenement_id, serie, code)
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
    "moorea": (1, 75),
    "triple90": (1, 90),
    "funday": (1, 90),
    "huahine": (1, 90),
    "boules40": (1, 40),
    "tea": (35, 67),
    "ohana90": (1, 90),
    "bgo": (1, 75),
    "igo": (16, 75),
    "kea": (35, 67),
    "moon": (1, 75),
    "ani": (61, 90),
    "brown14": (1, 75),
    "ino8": (16, 75),
    "tahaa": (1, 75),
    "boules60": (1, 60),
    "ahuru": (1, 75),
    "tchin": (1, 30),
    "ing": (16, 60),
    "lunes75": (1, 75),
    "miss75": (1, 75),
    "bien_sur": (1, 75),
    "ohana90_12b": (1, 90),
    "ohana90_24b": (1, 90),
    "lettre_u": (1, 75),
    "lettre_l": (1, 75),
    "topday": (1, 75),
    "fleche": (1, 75),
    "yes": (1, 90),
    "bio": (1, 75),
    "bio5": (1, 75),
    "zin": (1, 36),
    "rai": (30, 59),
    "bin8": (1, 36),
    "pow6": (1, 27),
    "bg90": (1, 90),
    "bo90": (1, 90),
    "bn90": (1, 90),
    "bi90": (1, 90),
    "bgo5": (1, 75),
    "bo75": (1, 75),
    "bg75": (1, 75),
    "bn75": (1, 75),
    "wiz": (1, 45),
    "p15_marathon": (1, 75),
    "ohana20b": (1, 75),
}


# Jeux à colonnes NON contiguës : liste explicite des boules valides
_BOULES_CALLER = {
    "bno": [n for n in range(1, 16)] + [n for n in range(31, 46)] + [n for n in range(61, 76)],
    "tureia": [n for n in range(1, 31)] + [n for n in range(46, 76)],  # colonne 31-45 morte
    "fan90": [n for n in range(1, 11)] + [n for n in range(20, 91)],   # sans le 11 à 19
    "oaoa": [n for n in range(16, 31)] + [n for n in range(61, 76)],   # O 16-30 et A 61-75
    "cerf_volant": [n for n in range(1, 31)] + [n for n in range(46, 76)],  # sans le 31-45
    "huahine": [n for n in range(1, 16)] + [n for n in range(46, 61)] + [n for n in range(76, 91)],  # 3 familles : 1-15, 46-60, 76-90
    "bgo": [n for n in range(1, 16)] + [n for n in range(46, 76)],  # B 1-15 · G 46-60 · O 61-75
    "igo": [n for n in range(16, 31)] + [n for n in range(46, 76)],  # I 16-30 · G 46-60 · O 61-75
    "moon": [n for n in range(1, 31)] + [n for n in range(46, 76)],  # M·O·O·N — le 31-45 n'existe pas
    "ino8": [n for n in range(16, 46)] + [n for n in range(61, 76)],  # I 16-30 · N 31-45 · O 61-75
    "ahuru": [n for n in range(1, 16)] + [n for n in range(31, 76)],  # AHURU — le 16-30 n'existe pas
    "lunes75": [n for n in range(1, 31)] + [n for n in range(46, 76)],  # LUNES 75 — le 31-45 n'existe pas
    "bio": [n for n in range(1, 31)] + [n for n in range(61, 76)],  # BIO — B 1-15 · I 16-30 · O 61-75
    "bio5": [n for n in range(1, 31)] + [n for n in range(61, 76)],  # BIO 5 — mêmes boules que BIO
    "bg90": [n for n in range(1, 16)] + [n for n in range(46, 61)] + [n for n in range(76, 91)],  # BG 90 — B 1-15 · G 46-60 · 90 76-90
    "bo90": [n for n in range(1, 16)] + [n for n in range(61, 91)],  # BO 90 — B 1-15 · O 61-75 · 90 76-90
    "bn90": [n for n in range(1, 16)] + [n for n in range(31, 46)] + [n for n in range(76, 91)],  # BN 90 — B 1-15 · N 31-45 · 90 76-90
    "bi90": [n for n in range(1, 31)] + [n for n in range(76, 91)],  # BI 90 — B 1-15 · I 16-30 · 90 76-90
    "bgo5": [n for n in range(1, 16)] + [n for n in range(46, 76)],  # BGO 5 — B 1-15 · G 46-60 · O 61-75
    "bo75": [n for n in range(1, 16)] + [n for n in range(46, 76)],  # BO 75 — B 1-15 · O 46-60 · 75 61-75
    "bg75": [n for n in range(1, 16)] + [n for n in range(46, 76)],  # BG 75 — B 1-15 · G 46-60 · 75 61-75
    "bn75": [n for n in range(1, 16)] + [n for n in range(31, 46)] + [n for n in range(61, 76)],  # BN 75 — B 1-15 · N 31-45 · 75 61-75
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

    # ⚖ COCHÉS D'OFFICE : PAIR/IMPAIR + FINALITÉS (règle des tournois) :
    # « PAIRS +5 » = toutes les paires ET tous les numéros finissant par 5
    # sont COCHÉS D'OFFICE sur les cartons — le caller ne tire que dans
    # les boules RESTANTES, jusqu'au cri BINGO. Filtré CÔTÉ SERVEUR,
    # donc toujours imprévisible et journalisé.
    mode = (d.get("mode") or "tous").strip().lower()
    if mode in ("pair", "impair"):
        base = boules_valides if boules_valides else list(range(bmin, bmax + 1))
        reste = 0 if mode == "pair" else 1
        finalites = set()
        for f in (d.get("finalites") or []):
            try:
                f = int(f)
                if 0 <= f <= 9:
                    finalites.add(f)
            except Exception:
                continue   # une valeur farfelue n'annule pas les autres
        # le sac = tout SAUF les cochés d'office
        boules_valides = [n for n in base
                          if not (n % 2 == reste or (n % 10) in finalites)]

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
    import random as _rnd
    pdf = generer_jeu(programme, nb_essai, couleur, perso,
                      serie_start=_rnd.randint(1, 900000))   # chaque essai = des cartes neuves

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


# ══ APERÇUS VISUELS DES JEUX (vision Maeva) ═══════════════════════════
# Chaque jeu du menu montre sa vignette : la 1re feuille, générée UNE fois
# puis gardée sur le Volume (/data/apercus). Les futurs jeux ont leur
# visuel automatiquement, sans aucun travail manuel.
import threading as _threading
_APERCU_LOCK = _threading.Lock()

def _dossier_apercus():
    base = os.path.dirname(os.environ.get("MANAPRINT_DB", "") or "") or "/tmp"
    d = os.path.join(base, "apercus")
    try:
        os.makedirs(d, exist_ok=True)
    except Exception:
        d = "/tmp"
    return d

def _fabriquer_apercu(jeu_id):
    """Fabrique (si absente) la vignette PNG d'une variante. Renvoie le chemin ou None."""
    chemin = os.path.join(_dossier_apercus(), jeu_id + ".png")
    if os.path.exists(chemin):
        return chemin
    with _APERCU_LOCK:
        if os.path.exists(chemin):
            return chemin
        try:
            import pypdfium2 as _pdfium
            jeu = REGISTRE_JEUX[jeu_id]
            pdf_buf = generer_jeu(jeu_id, jeu["cartes_par_feuille"], jeu["couleur"],
                                  {"telephone": "89 22 23 05"})
            doc = _pdfium.PdfDocument(pdf_buf.read())
            image = doc[0].render(scale=420 / 595.0).to_pil()
            image.save(chemin + ".tmp", "PNG", optimize=True)
            os.replace(chemin + ".tmp", chemin)   # écriture atomique (réflexe TUKEA)
            doc.close()
            return chemin
        except Exception as e:
            print(f"[APERCU] échec {jeu_id} : {e}")
            return None


def _prechauffer_apercus():
    """🔥 PRÉCHAUFFAGE : fabrique toutes les vignettes en coulisses au démarrage —
    quand un client ouvre le menu, tout est déjà prêt et instantané."""
    import time as _time
    import random as _rand
    _time.sleep(6 + _rand.uniform(0, 20))   # démarrage décalé (chaque ouvrier son tour)
    faites = 0
    for jid in list(REGISTRE_JEUX.keys()):
        if not os.path.exists(os.path.join(_dossier_apercus(), jid + ".png")):
            if _fabriquer_apercu(jid):
                faites += 1
            _time.sleep(0.8)   # pas de course : la priorité reste aux clients
    print(f"[APERCU] préchauffage terminé — {faites} vignettes fabriquées")


def _lancer_prechauffage():
    _threading.Thread(target=_prechauffer_apercus, daemon=True).start()


_lancer_prechauffage()


@app.route("/apercu/<jeu_id>.png", methods=["GET"])
def apercu_jeu(jeu_id):
    """Vignette PNG d'un jeu du registre — servie du cache (préchauffé au démarrage)."""
    if jeu_id not in REGISTRE_JEUX:
        jeu_id = jeu_id + "_couleur"          # tolérance : id de base -> ÉCO Couleur
        if jeu_id not in REGISTRE_JEUX:
            return "jeu inconnu", 404
    chemin = _fabriquer_apercu(jeu_id)
    if not chemin:
        return "aperçu indisponible", 503
    reponse = send_file(chemin, mimetype="image/png")
    reponse.headers["Cache-Control"] = "public, max-age=86400"
    return reponse


@app.route("/api/partenaires", methods=["GET"])
def api_partenaires():
    """Liste des points d'impression partenaires (pour le menu déroulant)."""
    _prix = _lire_prix_partenaires()
    return jsonify({"ok": True, "partenaires": [
        {"id": k, "nom": v["nom"], "zone": v["zone"], "tel": v["tel"],
         "prix_pdf_seul": v.get("prix_pdf_seul"),
         "prix_client": _prix.get(k) or None,
         "public": bool(v.get("public"))}
        for k, v in PARTENAIRES.items()
    ]})


# ── COMMANDE — calcul du prix + création ──────────────────────────────────────
def _valider_creer_commande(data, mode_paiement="manuel", panier_id=None):
    """Valide UNE commande (personnalisation, téléphone, noms réservés, partenaire)
    et la crée en base. Utilisée par /api/commander (commande seule) ET par le
    panier d'achat (chaque article du panier passe par les MÊMES contrôles).
    Retourne (None, resultat) si ok, ou (reponse_json, code_http) si refus."""
    programme = data.get("programme", "triple_action")
    couleur = REGISTRE_JEUX.get(programme, {}).get("couleur", True)
    nb_feuilles = max(1, min(int(data.get("nb_feuilles", 10)), 250))  # plafond : 250 feuilles par commande

    # Personnalisation OBLIGATOIRE (sécurité)
    nom_evenement = data.get("nom_evenement", "").strip()
    titre_jeu = data.get("titre_jeu", "").strip()
    date_lieu = data.get("date_lieu", "").strip()
    telephone = data.get("telephone", "").strip()
    if not nom_evenement or not titre_jeu or not date_lieu or not telephone:
        return (jsonify({"ok": False, "message": "Personnalisation obligatoire : nom du client/association, nom du tournoi, date et numéro de téléphone du responsable."}), 400), None

    # Profil polynésien : le téléphone doit être un numéro polynésien (87/88/89/40)
    if session.get("acces") == "polynesien" and not est_numero_polynesien(telephone):
        return (jsonify({"ok": False, "message": "Pour le tarif Polynésien, le téléphone du responsable doit être un numéro polynésien (87, 88, 89 ou 40). Si vous êtes hors Polynésie, utilisez l'accès Client International."}), 400), None

    # Noms réservés interdits dans la personnalisation
    reserve = contient_nom_reserve(nom_evenement, titre_jeu, date_lieu)
    if reserve:
        return (jsonify({"ok": False, "message": "Ce nom est réservé et ne peut pas être utilisé dans la personnalisation. Merci d'indiquer le nom de votre propre événement."}), 400), None

    import json as _json
    # 🖨️ Partenaire d'impression OBLIGATOIRE : plus d'auto-impression.
    # Toutes les commandes passent par le réseau d'imprimeurs partenaires.
    partenaire = (data.get("partenaire", "") or "").strip()
    if not partenaire and data.get("fun_and_co"):
        partenaire = "fun_and_co"  # compatibilité ancienne case
    if partenaire not in PARTENAIRES:
        return (jsonify({"ok": False,
                         "message": "Choisis un imprimeur partenaire dans la liste."}), 400), None
    params_perso = _json.dumps({
        "theme": data.get("theme", ""),
        "nom_evenement": nom_evenement,
        "titre_jeu": titre_jeu,
        "couleur_perso": data.get("couleur_perso", ""),
        "date_lieu": date_lieu,
        "telephone": telephone,
        "partenaire": partenaire,
        "fun_and_co": (partenaire == "fun_and_co"),
        # 🐛 RÉPARATION (juil. 2026) : ces 3 champs étaient envoyés par le
        # formulaire mais jamais sauvegardés -> date-serrure, couleur choisie
        # et rapport confidentiel par email ne fonctionnaient pas en commande.
        "date_tournoi": (data.get("date_tournoi", "") or "").strip(),
        "couleur_qr": (data.get("couleur_qr", "") or "").strip(),
        "email_organisateur": (data.get("email_organisateur", "") or "").strip(),
        # 🖨️ MODE BOUTIQUE RAPIDE : cartons sans microtexte (QR conservé),
        # pour l'impression directe par clé USB sans pause.
        "impression_rapide": bool(data.get("impression_rapide")),
    })

    # 💡 Tarif spécial partenaire (ex. RANIHEI : PDF seul à 1,5 F —
    # l'impression se règle directement avec le partenaire)
    prix_special = PARTENAIRES[partenaire].get("prix_pdf_seul")
    # 💰 ...sauf si le partenaire a fixé SES prix clients dans son espace :
    # le client paie CE prix (tout compris) — la redevance 1,5 F reste
    # l'affaire privée entre le partenaire et 2KEA (facture automatique).
    _pp = _lire_prix_partenaires().get(partenaire) or {}
    _cle_prix = db._gamme_du_programme(programme) + ("_couleur" if couleur else "_nb")
    if _pp.get(_cle_prix):
        prix_special = float(_pp[_cle_prix])
    commande_id, montant = db.creer_commande(
        identifiant=session.get("identifiant"),
        origine=session["acces"],
        programme=programme,
        couleur=couleur,
        nb_feuilles=nb_feuilles,
        mode_paiement=mode_paiement,
        params_perso=params_perso,
        panier_id=panier_id,
        prix_feuille=prix_special,
    )
    jeu = REGISTRE_JEUX.get(programme, {})
    libelle = f"{jeu.get('emoji','')} {jeu.get('nom', programme)} — {nb_feuilles} feuille(s)".strip()
    return None, {"commande_id": commande_id, "montant": int(montant), "libelle": libelle}


# ── 💳 STRIPE (paiement par carte, comme sur Ticket Bingo) ────────────────────
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "").strip()
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "").strip()
if not STRIPE_SECRET_KEY:
    # 🩹 auto-guérison : un nom de variable avec un espace invisible (copier-coller)
    for _k, _v in os.environ.items():
        if _k.strip() == "STRIPE_SECRET_KEY" and _v.strip():
            STRIPE_SECRET_KEY = _v.strip()
            print(f"[STRIPE] clé retrouvée sous le nom {_k!r} (espace parasite corrigé)")
            break


def _base_url():
    return os.environ.get("MANAPRINT_BASE_URL", request.host_url.rstrip("/"))


def _session_stripe_panier(panier_id):
    """Crée la session de paiement Stripe pour un panier (XPF = devise sans
    décimales : les montants s'envoient tels quels). Retourne l'URL de paiement."""
    import stripe
    stripe.api_key = STRIPE_SECRET_KEY
    cmds = db.commandes_du_panier(panier_id)
    line_items, total = [], 0
    for cmd in cmds:
        jeu = REGISTRE_JEUX.get(cmd["programme"], {})
        nom = f"{jeu.get('emoji','')} {jeu.get('nom', cmd['programme'])} — {cmd['nb_feuilles']} feuille(s)".strip()
        montant = int(cmd["montant"])
        total += montant
        line_items.append({
            "price_data": {"currency": "xpf", "unit_amount": montant,
                           "product_data": {"name": nom}},
            "quantity": 1,
        })
    s = stripe.checkout.Session.create(
        mode="payment",
        line_items=line_items,
        success_url=_base_url() + "/?paiement=succes",
        cancel_url=_base_url() + "/?paiement=annule",
        metadata={"panier_id": str(panier_id)},
    )
    db.maj_panier(panier_id, total=total, stripe_session=s.id)
    return s.url, total


@app.route("/api/commander", methods=["POST"])
def commander():
    if "acces" not in session:
        return jsonify({"ok": False, "message": "Accès non autorisé"}), 403
    data = request.get_json(force=True)
    mode_paiement = data.get("mode_paiement", "manuel")  # 'stripe' | 'manuel'
    err, res = _valider_creer_commande(data, mode_paiement=mode_paiement)
    if err:
        return err
    commande_id, montant = res["commande_id"], res["montant"]

    # Mode manuel : la commande est en attente de validation par 2KEA
    if mode_paiement == "manuel":
        return jsonify({
            "ok": True, "commande_id": commande_id, "montant": montant,
            "mode": "manuel",
            "message": f"Commande enregistrée ({montant} XPF). Elle sera générée après validation du paiement par 2KEA & Associé.",
        })

    # 💳 Mode stripe : mini-panier d'une seule commande -> paiement carte
    if not STRIPE_SECRET_KEY:
        return jsonify({"ok": False,
                        "message": "Le paiement par carte n'est pas encore activé. Choisis le paiement en boutique."}), 400
    try:
        panier_id = db.creer_panier(session.get("identifiant"))
        with db.get_db() as conn:
            conn.execute("UPDATE commandes SET panier_id = ? WHERE id = ?", (panier_id, commande_id))
        url, total = _session_stripe_panier(panier_id)
        return jsonify({"ok": True, "mode": "stripe", "url": url, "montant": total})
    except Exception as e:
        print(f"[STRIPE ERREUR] commander : {e}")
        return jsonify({"ok": False, "message": "Paiement carte momentanément indisponible. Choisis le paiement en boutique."}), 502


@app.route("/api/panier/checkout", methods=["POST"])
def panier_checkout():
    """🛒 Le panier d'achat : plusieurs jeux, un seul paiement.
    items = liste de commandes (mêmes champs que /api/commander).
    mode_paiement = 'stripe' (carte) ou 'manuel' (boutique/virement)."""
    if "acces" not in session:
        return jsonify({"ok": False, "message": "Accès non autorisé"}), 403
    data = request.get_json(force=True, silent=True) or {}
    items = data.get("items") or []
    mode_paiement = data.get("mode_paiement", "stripe")
    if not isinstance(items, list) or not (1 <= len(items) <= 10):
        return jsonify({"ok": False, "message": "Le panier doit contenir entre 1 et 10 articles."}), 400

    panier_id = db.creer_panier(session.get("identifiant"))
    resume, total = [], 0
    for pos, item in enumerate(items, 1):
        err, res = _valider_creer_commande(item, mode_paiement=mode_paiement, panier_id=panier_id)
        if err:
            corps, code = err
            d = corps.get_json()
            d["message"] = f"Article {pos} : " + (d.get("message") or "refusé")
            d["article"] = pos
            return jsonify(d), code
        resume.append(res)
        total += res["montant"]

    if mode_paiement == "manuel":
        return jsonify({
            "ok": True, "mode": "manuel", "panier_id": panier_id, "montant": total,
            "articles": resume,
            "message": f"Panier enregistré ({len(resume)} article(s), {total} XPF). Il sera généré après validation du paiement par 2KEA & Associé.",
        })

    if not STRIPE_SECRET_KEY:
        return jsonify({"ok": False,
                        "message": "Le paiement par carte n'est pas encore activé. Choisis le paiement en boutique."}), 400
    try:
        url, total = _session_stripe_panier(panier_id)
        return jsonify({"ok": True, "mode": "stripe", "url": url, "montant": total, "panier_id": panier_id})
    except Exception as e:
        print(f"[STRIPE ERREUR] checkout : {e}")
        return jsonify({"ok": False, "message": "Paiement carte momentanément indisponible. Choisis le paiement en boutique."}), 502


@app.route("/webhook/stripe", methods=["GET"])
def webhook_stripe_visite():
    """Visite au navigateur : on rassure au lieu du 405 « Method Not Allowed »."""
    return ("\u2705 La porte Stripe de MANAPRINT est VIVANTE. "
            "Elle n'accepte que les livraisons de Stripe (POST) \u2014 "
            "pour v\u00e9rifier les paiements, utilisez le Dashboard Stripe "
            "(D\u00e9veloppeurs \u2192 Webhooks \u2192 tentatives r\u00e9centes).", 200)


@app.route("/webhook/stripe", methods=["POST"])
def webhook_stripe():
    """💳 Stripe confirme le paiement -> le panier passe payé et la fabrication
    démarre toute seule pour chaque article (PDF -> partenaire, rapport -> client).
    Signature vérifiée : personne ne peut simuler un paiement. Idempotent."""
    import stripe
    if not STRIPE_WEBHOOK_SECRET:
        return jsonify({"ok": False, "message": "webhook non configuré"}), 400
    payload = request.get_data()
    signature = request.headers.get("Stripe-Signature", "")
    try:
        event = stripe.Webhook.construct_event(payload, signature, STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        print(f"[STRIPE WEBHOOK] signature refusée : {e}")
        return jsonify({"ok": False}), 400

    if event["type"] == "checkout.session.completed":
        sess = event["data"]["object"]
        # ⚠️ SDK Stripe v15 : StripeObject n'est plus un dict (.get = piège !) ->
        # accès par CROCHETS uniquement (leçon apprise sur Ticket Bingo).
        try:
            panier_id = int(sess["metadata"]["panier_id"])
        except Exception:
            panier_id = 0
        if panier_id:
            cmds = db.marquer_panier_payee(panier_id)
            if cmds is None:
                print(f"[STRIPE WEBHOOK] panier {panier_id} introuvable")
            elif not cmds:
                print(f"[STRIPE WEBHOOK] panier {panier_id} déjà traité (webhook doublon)")
            else:
                for cmd in cmds:
                    nom_part = lancer_fabrication(cmd["id"])
                    print(f"[STRIPE PAYE] commande {cmd['id']} du panier {panier_id} -> fabrication ({nom_part or 'sans partenaire ?'})")
    return jsonify({"ok": True})


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
            nom=_nom_evenement_complet(perso),
            identifiant=cmd["identifiant"],
            programme=programme,
            serie_min=1,
            serie_max=nb_cartes,
            date_tournoi=perso.get("date_tournoi", ""),
            couleur_qr=perso.get("couleur_qr", ""),
        )
    except Exception:
        evenement_id = ""  # anti-panne : en cas d'échec, on génère sans QR

    # 🖨️ MODE BOUTIQUE RAPIDE : sans microtexte (QR conservé) si demandé.
    try:
        from generators import securite as _secs
        _secs.activer_mode_rapide(bool(perso.get("impression_rapide")))
    except Exception:
        pass
    try:
        pdf = generer_jeu(programme, nb_cartes, couleur, perso, evenement_id=evenement_id,
                          serie_start=commande_id * 100 + 1)
    finally:
        try:
            _secs.activer_mode_rapide(False)
        except Exception:
            pass

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
def lancer_fabrication(commande_id, seulement_rapport=False):
    """🏭 FABRICATION EN ARRIÈRE-PLAN — partagée entre la validation manuelle (2KEA)
    et le paiement par carte (webhook Stripe). Les grosses commandes (des centaines
    de feuilles + sécurité) prennent plusieurs minutes : on fabrique dans un thread,
    le PDF part chez le partenaire, le rapport confidentiel chez l'organisateur.
    Retourne le nom du partenaire (ou '' si aucun partenaire valide)."""
    import json as _json
    cmd = db.get_commande(commande_id)
    if not cmd:
        return ""
    perso = _json.loads(cmd["params_perso"] or "{}")
    pid = perso.get("partenaire") or ("fun_and_co" if perso.get("fun_and_co") else "")
    if not pid or pid not in PARTENAIRES:
        return ""
    part = PARTENAIRES[pid]

    def _fabriquer_et_envoyer():
        try:
            cpf = CARTES_PAR_FEUILLE.get(cmd["programme"], 10)
            nb_cartes = cmd["nb_feuilles"] * cpf
            evenement_id = ""
            try:
                evenement_id = _nouvel_evenement_id(cmd["programme"])
                db.creer_evenement(
                    evenement_id=evenement_id,
                    nom=_nom_evenement_complet(perso),
                    identifiant=cmd["identifiant"], programme=cmd["programme"],
                    serie_min=1, serie_max=nb_cartes,
                    date_tournoi=perso.get("date_tournoi", ""),
                    couleur_qr=perso.get("couleur_qr", ""),
                )
            except Exception:
                evenement_id = ""
            # 🖨️ MODE BOUTIQUE RAPIDE : sans microtexte (QR conservé) si demandé.
            # Le drapeau est isolé au thread de fabrication -> aucune fuite ailleurs.
            try:
                from generators import securite as _secm
                _secm.activer_mode_rapide(bool(perso.get("impression_rapide")))
            except Exception:
                pass
            try:
                # 🎲 chaque commande = son propre point de départ (cartes UNIQUES,
                # mais refabrication à l'identique pour le 📬 Renvoyer)
                pdf = generer_jeu(cmd["programme"], nb_cartes, bool(cmd["couleur"]), perso,
                                  evenement_id=evenement_id,
                                  serie_start=commande_id * 100 + 1)
            finally:
                try:
                    _secm.activer_mode_rapide(False)
                except Exception:
                    pass
            # 🗄️ AU COFFRE-FORT d'abord : le PDF est sauvé sur le disque —
            # même si l'email échoue, il reste téléchargeable pour toujours.
            lien_cartons = _ranger_au_coffre(commande_id, "cartons", pdf)
            pdf.seek(0, 2); taille_pdf = pdf.tell(); pdf.seek(0)
            piece_cartons = pdf if taille_pdf <= LIMITE_PIECE_JOINTE else None
            note_taille = ("" if piece_cartons is not None else
                           "\n\u26a0\ufe0f PDF trop volumineux pour l'email : "
                           "utilisez le lien de téléchargement ci-dessous.\n")
            sujet = f"MANAPRINT — Commande #{commande_id} à imprimer"
            corps = (
                f"Bonjour {part['nom']},\n\n"
                f"Une nouvelle commande validée est à imprimer ({part['zone']}) :\n\n"
                f"  • Client : {cmd['identifiant']}\n"
                f"  • Événement : {perso.get('nom_evenement','')}\n"
                f"  • Jeu : {cmd['programme']} — {cmd['nb_feuilles']} feuille(s)\n"
                f"  • Téléphone du responsable : {perso.get('telephone','')}\n\n"
                "Le PDF prêt à imprimer est en pièce jointe."
                + note_taille +
                (f"\n\U0001f517 Lien de secours (téléchargement direct) :\n{lien_cartons}\n" if lien_cartons else "") +
                "\n— MANAPRINT / 2KEA & Associé"
            )
            # 📋🤫 le compte-rendu confidentiel série -> couleur
            try:
                rapport = _rapport_confidentiel(commande_id, cmd, perso,
                                                evenement_id, nb_cartes)
            except Exception:
                rapport = None
            lien_rapport = _ranger_au_coffre(commande_id, "rapport", rapport) if rapport is not None else ""
            email_cli = (perso.get("email_organisateur") or "").strip()
            if seulement_rapport:
                # 🤫 MODE RAPPORT SEUL (rattrapage discret) : l'imprimeur ne reçoit RIEN
                if not (email_cli and rapport is not None):
                    print(f"[RAPPORT SEUL] cmd {commande_id} : pas d'email client ou pas de rapport")
                    return
                corps_cli = (
                    f"Bonjour,\n\n"
                    f"Voici (à nouveau) votre RAPPORT CONFIDENTIEL — commande MANAPRINT #{commande_id} "
                    f"({cmd['programme']} — {cmd['nb_feuilles']} feuille(s)).\n\n"
                    "\u26a0\ufe0f À garder pour vous : ne le montrez JAMAIS aux joueurs.\n"
                    "Au scan de chaque carton gagnant, la pastille de couleur affichée\n"
                    "doit correspondre à cette grille.\n"
                    + (f"\n\U0001f517 Lien de secours du rapport :\n{lien_rapport}\n" if lien_rapport else "") +
                    "\n— MANAPRINT / 2KEA & Associé — manaprint.app"
                )
                ok2, m2 = envoyer_email_pdf(
                    email_cli,
                    f"MANAPRINT — Rapport CONFIDENTIEL — commande #{commande_id}",
                    corps_cli, rapport,
                    f"CONFIDENTIEL_couleurs_cmd{commande_id}.pdf",
                    copie=SMTP_USER or None)
                print(f"[RAPPORT SEUL] cmd {commande_id} -> {email_cli} : {ok2} ({m2})")
                return
            if email_cli and rapport is not None:
                # 🖨️ l'imprimeur ne reçoit QUE les cartons...
                ok, m = envoyer_email_pdf(part["email"], sujet, corps, piece_cartons,
                                          f"manaprint_cmd{commande_id}.pdf",
                                          copie=SMTP_USER or None)
                # 📧 ...et l'ORGANISATEUR reçoit son rapport confidentiel
                corps_cli = (
                    f"Bonjour,\n\n"
                    f"Votre commande MANAPRINT #{commande_id} est validée "
                    f"({cmd['programme']} — {cmd['nb_feuilles']} feuille(s)).\n\n"
                    "\u26a0\ufe0f En pièce jointe : votre RAPPORT CONFIDENTIEL — la grille\n"
                    "de contrôle des couleurs de vos cartons.\n"
                    "\u00c0 garder pour vous : ne le montrez JAMAIS aux joueurs.\n"
                    "Au scan de chaque carton gagnant, la pastille de couleur affichée\n"
                    "doit correspondre à cette grille.\n"
                    + (f"\n\U0001f517 Lien de secours du rapport :\n{lien_rapport}\n" if lien_rapport else "") +
                    "\n— MANAPRINT / 2KEA & Associé — manaprint.app"
                )
                ok2, m2 = envoyer_email_pdf(
                    email_cli,
                    f"MANAPRINT — Rapport CONFIDENTIEL — commande #{commande_id}",
                    corps_cli, rapport,
                    f"CONFIDENTIEL_couleurs_cmd{commande_id}.pdf",
                    copie=SMTP_USER or None)
                print(f"[RAPPORT CONFIDENTIEL] cmd {commande_id} -> {email_cli} : {ok2} ({m2})")
            else:
                # repli (pas d'email client) : le rapport voyage avec les cartons
                ok, m = envoyer_email_pdf(part["email"], sujet, corps, piece_cartons,
                                          f"manaprint_cmd{commande_id}.pdf",
                                          copie=SMTP_USER or None,
                                          pdf2_io=rapport,
                                          nom2_fichier=f"CONFIDENTIEL_couleurs_cmd{commande_id}.pdf")
            # 🗄️ MODE SANS FACTEUR : les PDF sont DÉJÀ au coffre-fort — la
            # commande est donc RÉUSSIE même si Gmail dort (boîte bloquée...).
            # Les emails sont un bonus, jamais une condition.
            db.marquer_commande_generee(commande_id)
            # 🧾 LA FACTURE DU DÛ 2KEA (1,5 F/feuille) : TOUJOURS fabriquée et
            # rangée au coffre ; l'email part si le facteur veut bien.
            try:
                fact_pdf, fact_part, fact_montant = _facture_commande_pdf(cmd)
                lien_fact = _ranger_au_coffre(commande_id, "facture", fact_pdf)
                corps_fact = (
                    f"Bonjour {fact_part.get('nom', '')},\n\n"
                    f"Veuillez trouver la facture des redevances PDF MANAPRINT "
                    f"pour la commande #{commande_id} :\n\n"
                    f"  \u2022 Jeu : {cmd['programme']} \u2014 {cmd['nb_feuilles']} feuille(s)\n"
                    f"  \u2022 Redevance : 1,5 F / feuille \u2192 TOTAL : {fact_montant} XPF\n"
                    + (f"\n\U0001f517 Lien de secours :\n{lien_fact}\n" if lien_fact else "") +
                    "\n\u00c0 r\u00e9gler \u00e0 2KEA & Associ\u00e9 selon vos modalit\u00e9s habituelles.\n\n"
                    "\u2014 MANAPRINT / 2KEA & Associ\u00e9 \u2014 manaprint.app"
                )
                okf, mf = envoyer_email_pdf(
                    part["email"],
                    f"MANAPRINT \u2014 Facture du d\u00fb 2KEA \u2014 commande #{commande_id} ({fact_montant} XPF)",
                    corps_fact, fact_pdf,
                    f"facture_2kea_cmd{commande_id}.pdf",
                    copie=SMTP_USER or None)
                print(f"[FACTURE 2KEA] cmd {commande_id} -> {part['email']} (+copie plateforme) : {okf} ({mf})")
            except Exception as e:
                print(f"[FACTURE 2KEA] cmd {commande_id} : {e}")
            if ok:
                print(f"[FABRICATION OK] commande {commande_id} envoyée à {part['nom']}")
            else:
                print(f"[FABRICATION SANS FACTEUR] commande {commande_id} FABRIQUÉE et au "
                      f"coffre-fort (⬇️/🗂️/🧾 dans la gestion) — email non parti : {m}")
        except Exception as e:
            print(f"[FABRICATION ERREUR] commande {commande_id} : {e}")

    import threading as _th
    _th.Thread(target=_fabriquer_et_envoyer, daemon=True).start()
    return part["nom"]


URL_BASE = os.environ.get("URL_BASE", "https://manaprint.app")
LIMITE_PIECE_JOINTE = 22 * 1024 * 1024   # au-delà, Gmail refuse : on envoie le LIEN


def _dossier_lots():
    """🗄️ Le coffre-fort des PDF fabriqués (Volume Railway) — plus jamais un lot perdu."""
    base = os.path.dirname(os.environ.get("MANAPRINT_DB", "/tmp/manaprint.db")) or "/tmp"
    d = os.path.join(base, "lots")
    os.makedirs(d, exist_ok=True)
    return d


def _jeton_lot(commande_id):
    import hashlib
    return hashlib.sha256(f"{commande_id}:{CODE_ADMIN}:lot".encode()).hexdigest()[:12]


def _ranger_au_coffre(commande_id, quoi, pdf_io):
    """Écrit le PDF au coffre (écriture atomique) et retourne son lien de téléchargement."""
    try:
        chemin = os.path.join(_dossier_lots(), f"cmd{commande_id}_{quoi}.pdf")
        pdf_io.seek(0)
        with open(chemin + ".tmp", "wb") as f:
            f.write(pdf_io.read())
        os.replace(chemin + ".tmp", chemin)
        pdf_io.seek(0)
        return f"{URL_BASE}/lot/{commande_id}/{_jeton_lot(commande_id)}/{quoi}.pdf"
    except Exception as e:
        print(f"[COFFRE] cmd {commande_id} {quoi} : {e}")
        return ""


@app.route("/lot/<int:commande_id>/<jeton>/<quoi>.pdf", methods=["GET"])
def telecharger_lot(commande_id, jeton, quoi):
    """Lien de secours des emails : téléchargement direct du PDF fabriqué."""
    if quoi not in ("cartons", "rapport", "facture") or jeton != _jeton_lot(commande_id):
        return "lien invalide", 403
    chemin = os.path.join(_dossier_lots(), f"cmd{commande_id}_{quoi}.pdf")
    if not os.path.exists(chemin):
        return ("PDF pas encore au coffre — dans l'espace gestion, utilisez "
                "📬 Renvoyer les emails pour relancer la fabrication."), 404
    return send_file(chemin, mimetype="application/pdf",
                     download_name=f"manaprint_cmd{commande_id}_{quoi}.pdf")


def _facture_commande_pdf(cmd):
    """🧾 Construit la facture du dû 2KEA & Associé (1,5 F/feuille) pour UNE commande."""
    import json as _json
    from datetime import date as _date
    from generators import facture as _fact
    try:
        perso = _json.loads(cmd.get("params_perso") or "{}")
    except Exception:
        perso = {}
    part = PARTENAIRES.get(perso.get("partenaire") or "", {"nom": "Partenaire", "zone": "", "email": ""})
    feuilles = int(cmd.get("nb_feuilles") or 0)
    montant = round(feuilles * 1.5)
    ligne = {
        "date": (cmd.get("cree_le") or "")[:10] or _date.today().isoformat(),
        "commande": cmd["id"],
        "jeu": cmd.get("programme", ""),
        "feuilles": feuilles,
        "pu": 1.5,
        "montant": montant,
    }
    numero = "C%05d" % cmd["id"]
    libelle = "Commande #%d \u2014 %s" % (cmd["id"], _date.today().strftime("%d/%m/%Y"))
    return _fact.generer_facture(numero, libelle, part, [ligne], montant), part, montant


@app.route("/api/admin/facture-commande/<int:commande_id>", methods=["GET"])
@admin_requis
def admin_facture_commande(commande_id):
    """Le bouton 🧾 : la facture du dû 2KEA de cette commande, à l'écran."""
    cmd = db.get_commande(commande_id)
    if not cmd:
        return "Commande introuvable", 404
    pdf, part, montant = _facture_commande_pdf(cmd)
    return send_file(pdf, mimetype="application/pdf",
                     download_name=f"facture_2kea_cmd{commande_id}.pdf")


@app.route("/api/admin/commandes/<int:commande_id>/supprimer", methods=["POST"])
@admin_requis
def admin_supprimer_commande(commande_id):
    """🗑️ Supprime DÉFINITIVEMENT une commande refusée (erreur, doublon...) —
    et ses PDF du coffre-fort avec. Réservé à l'administratrice, confirmé côté écran."""
    cmd = db.get_commande(commande_id)
    if not cmd:
        return jsonify({"ok": False, "message": f"Commande #{commande_id} introuvable."})
    try:
        with db.get_db() as conn:
            conn.execute("DELETE FROM commandes WHERE id = ?", (commande_id,))
    except Exception as e:
        return jsonify({"ok": False, "message": f"Suppression impossible : {e}"})
    for quoi in ("cartons", "rapport", "facture"):
        try:
            os.remove(os.path.join(_dossier_lots(), f"cmd{commande_id}_{quoi}.pdf"))
        except Exception:
            pass
    return jsonify({"ok": True, "message":
                    f"Commande #{commande_id} supprimée \U0001f5d1\ufe0f "
                    f"({cmd.get('identifiant', '')} \u00b7 {cmd.get('programme', '')} \u00b7 "
                    f"{cmd.get('nb_feuilles', 0)} feuille(s)) — coffre-fort nettoyé."})


@app.route("/api/admin/commandes/<int:commande_id>/pdf/<quoi>", methods=["GET"])
@admin_requis
def admin_pdf_commande(commande_id, quoi):
    """⬇️ Téléchargement direct depuis l'espace gestion (session admin)."""
    if quoi not in ("cartons", "rapport", "facture"):
        return "type inconnu", 400
    chemin = os.path.join(_dossier_lots(), f"cmd{commande_id}_{quoi}.pdf")
    if not os.path.exists(chemin):
        return ("Ce PDF n'est pas encore au coffre-fort (commande fabriquée avant "
                "cette nouveauté, ou fabrication en cours) — utilisez 📬 "
                "Renvoyer les emails pour le refabriquer."), 404
    return send_file(chemin, mimetype="application/pdf",
                     download_name=f"manaprint_cmd{commande_id}_{quoi}.pdf")


def _rattrapage_stripe(jours=10):
    """💳 LE RATTRAPAGE : demande DIRECTEMENT à Stripe les paiements réussis
    des derniers jours et fabrique toute commande passée entre les mailles
    (webhook raté, panne, redéploiement...). Idempotent : sans danger."""
    import time as _t
    if not STRIPE_SECRET_KEY:
        vues = [f"{k!r} ({len((v or '').strip())} caractères utiles)"
                for k, v in os.environ.items() if "STRIPE" in k.upper()]
        detail = " \u00b7 ".join(sorted(vues)) if vues else "AUCUNE variable STRIPE visible"
        return {"ok": False, "message":
                "Stripe non configuré \u2014 \U0001f52c variables STRIPE que la plateforme "
                f"voit dans son environnement : {detail}. "
                "Si la liste est vide ou le nom entre guillemets contient un espace, "
                "le souci est c\u00f4t\u00e9 Railway (service/environnement/nom)."}
    try:
        import stripe
        stripe.api_key = STRIPE_SECRET_KEY
        verifies = 0
        rattrapees = []
        sessions = stripe.checkout.Session.list(
            limit=100, created={"gte": int(_t.time()) - jours * 86400})
        for sess in sessions.auto_paging_iter():
            if sess["payment_status"] != "paid":
                continue
            verifies += 1
            try:
                panier_id = int(sess["metadata"]["panier_id"])
            except Exception:
                continue
            cmds = db.marquer_panier_payee(panier_id)
            if cmds:   # jamais traité jusqu'ici : la fabrication part ENFIN
                for cmd in cmds:
                    lancer_fabrication(cmd["id"])
                    rattrapees.append(cmd["id"])
                print(f"[RATTRAPAGE STRIPE] panier {panier_id} -> commandes {[c['id'] for c in cmds]}")
        if rattrapees:
            msg = (f"{verifies} paiement(s) vérifié(s) sur {jours} jours \u00b7 "
                   f"\U0001f3c6 {len(rattrapees)} commande(s) RATTRAPÉE(S) et partie(s) en "
                   f"fabrication : {', '.join('#' + str(i) for i in rattrapees)}")
        else:
            msg = (f"{verifies} paiement(s) vérifié(s) sur {jours} jours \u2014 "
                   "tout était déjà en règle, aucun client oublié \u2705")
        return {"ok": True, "message": msg, "rattrapees": rattrapees}
    except Exception as e:
        return {"ok": False, "message": f"Erreur Stripe : {e}"}


@app.route("/api/admin/rattrapage-stripe", methods=["POST"])
@admin_requis
def admin_rattrapage_stripe():
    return jsonify(_rattrapage_stripe(jours=10))


def _veilleur_stripe():
    """👁️ LE VEILLEUR : toutes les 30 minutes, vérifie les paiements Stripe
    des 2 derniers jours tout seul — les webhooks ratés ne perdent plus
    JAMAIS un client, sans aucun geste de l'administratrice."""
    import time as _t
    import random as _r
    _t.sleep(90 + _r.uniform(0, 60))
    while True:
        try:
            if STRIPE_SECRET_KEY:
                res = _rattrapage_stripe(jours=2)
                if res.get("rattrapees"):
                    print(f"[VEILLEUR STRIPE] {res['message']}")
        except Exception as e:
            print(f"[VEILLEUR STRIPE] {e}")
        _t.sleep(1800)


_threading.Thread(target=_veilleur_stripe, daemon=True).start()


@app.route("/api/admin/historique-client", methods=["POST"])
@admin_requis
def admin_historique_client():
    """🔍 L'HISTORIQUE COMPLET d'un client : toutes ses commandes (le nom
    est cherché dans l'identifiant ET dans la personnalisation — association,
    événement, titre), avec l'état du coffre-fort pour chaque PDF."""
    import json as _json
    d = request.get_json(silent=True) or {}
    q = (d.get("q") or "").strip().lower()
    if len(q) < 2:
        return jsonify({"ok": False, "message": "Tapez au moins 2 caractères"})
    resultats = []
    for cmd in db.lister_commandes():
        perso = {}
        try:
            perso = _json.loads(cmd.get("params_perso") or "{}")
        except Exception:
            pass
        meule = " ".join(str(x) for x in [
            cmd.get("identifiant", ""), perso.get("nom_evenement", ""),
            perso.get("titre_jeu", ""), perso.get("email_organisateur", ""),
        ]).lower()
        if q in meule:
            au_coffre = os.path.exists(os.path.join(_dossier_lots(), f"cmd{cmd['id']}_cartons.pdf"))
            resultats.append({
                "id": cmd["id"], "date": (cmd.get("cree_le") or "")[:16].replace("T", " "),
                "identifiant": cmd.get("identifiant", ""),
                "programme": cmd.get("programme", ""),
                "nb_feuilles": cmd.get("nb_feuilles", 0),
                "couleur": bool(cmd.get("couleur")),
                "statut": cmd.get("statut", ""),
                "montant": cmd.get("montant", 0),
                "evenement": perso.get("nom_evenement", "") or perso.get("titre_jeu", ""),
                "au_coffre": au_coffre,
            })
    return jsonify({"ok": True, "resultats": resultats,
                    "message": f"{len(resultats)} commande(s) trouvée(s)"})


@app.route("/api/admin/test-email", methods=["POST"])
@admin_requis
def admin_test_email():
    """📮 Envoie un email d'essai et RETOURNE le verdict exact du serveur Gmail —
    le diagnostic en un clic, sans fouiller les journaux Railway."""
    d = request.get_json(silent=True) or {}
    dest = (d.get("dest") or SMTP_USER or "").strip()
    if not dest:
        return jsonify({"ok": False, "message": "Aucun destinataire (et SMTP_USER est vide)"})
    ok, m = envoyer_email_pdf(
        dest,
        "MANAPRINT — Email de test \u2705",
        "Bonjour !\n\nSi vous lisez ceci, la poste MANAPRINT fonctionne parfaitement.\n\n"
        "— Le facteur de manaprint.app",
        None, "")
    etat = f"SMTP_USER = {SMTP_USER or '(vide !)'} \u00b7 SMTP_PASS = {'défini (' + str(len(SMTP_PASS)) + ' caractères)' if SMTP_PASS else '(VIDE !)'}"
    return jsonify({"ok": ok, "message": f"{m} \u2014 {etat}"})


# ══ 🏪 BOUTIQUES PARTENAIRES (vitrine publique + espace privé) ══════════════
# Chaque partenaire a : sa VITRINE (/boutique/<slug>) où ses clients commandent
# avec l'imprimeur verrouillé sur lui, et son ESPACE PRIVÉ (/espace-partenaire)
# où il suit SES commandes, télécharge les cartons et ses factures 2KEA.
_CODES_PARTENAIRES_DEFAUT = {
    "2kea_papeete": "PAP-2358", "fun_and_co": "FUN-7261",
    "cocotie_mer": "MER-4837", "ranihei": "RAN-9145",
}
for _slug_p, _p in PARTENAIRES.items():
    _p["code"] = os.environ.get("CODE_PART_" + _slug_p.upper(),
                                _CODES_PARTENAIRES_DEFAUT.get(_slug_p, _slug_p.upper() + "-2026"))
    # 🏠 Vision Maeva : 2KEA & Associé est LA maison-mère — seule au menu de
    # manaprint.app ; chaque autre partenaire accueille ses clients sur SA vitrine.
    _p["public"] = (_slug_p == "2kea_papeete")


@app.route("/boutique/<slug>", methods=["GET"])
def boutique_partenaire(slug):
    """🏪 La VITRINE du partenaire : le site complet, imprimeur verrouillé sur lui."""
    part = PARTENAIRES.get(slug)
    if not part:
        return "Boutique inconnue \u2014 v\u00e9rifiez l'adresse.", 404
    return render_template("index.html", boutique={
        "slug": slug, "nom": part["nom"], "zone": part.get("zone", ""), "tel": part.get("tel", "")})


@app.route("/espace-partenaire", methods=["GET"])
def page_espace_partenaire():
    return render_template("partenaire.html")


def _partenaire_session():
    slug = session.get("partenaire_slug") or ""
    if slug in PARTENAIRES:
        return slug, PARTENAIRES[slug]
    return None, None


def _normaliser_code(c):
    """Le portier tolérant : seules les LETTRES et les CHIFFRES comptent —
    tirets (courts, longs...), espaces, minuscules et caractères invisibles
    des claviers de téléphone sont pardonnés. FUN-7261 = fun 7261 = FUN–7261."""
    import re as _re
    return _re.sub(r"[^A-Z0-9]", "", str(c or "").upper())


@app.route("/api/partenaire/login", methods=["POST"])
def api_partenaire_login():
    d = request.get_json(silent=True) or {}
    code = _normaliser_code(d.get("code"))
    if len(code) < 4:
        return jsonify({"ok": False, "message": "Entrez votre code partenaire."})
    for slug, part in PARTENAIRES.items():
        if code == _normaliser_code(part.get("code", "")):
            session["partenaire_slug"] = slug
            return jsonify({"ok": True, "nom": part["nom"], "zone": part.get("zone", "")})
    return jsonify({"ok": False, "message":
                    "Code partenaire inconnu \u2014 v\u00e9rifiez lettres et chiffres "
                    "(les tirets et espaces n'ont pas d'importance)."})


@app.route("/api/partenaire/logout", methods=["POST"])
def api_partenaire_logout():
    session.pop("partenaire_slug", None)
    return jsonify({"ok": True})


@app.route("/api/partenaire/mes-commandes", methods=["GET"])
def api_partenaire_mes_commandes():
    import json as _json
    from datetime import date as _date
    slug, part = _partenaire_session()
    if not slug:
        return jsonify({"ok": False, "message": "connexion requise"}), 403
    mois = _date.today().isoformat()[:7]
    lignes = []
    nb_f = du_total = du_mois = 0
    for cmd in db.lister_commandes():
        try:
            perso = _json.loads(cmd.get("params_perso") or "{}")
        except Exception:
            perso = {}
        if (perso.get("partenaire") or "") != slug:
            continue
        du = round(int(cmd.get("nb_feuilles") or 0) * 1.5)
        au_coffre = os.path.exists(os.path.join(_dossier_lots(), f"cmd{cmd['id']}_cartons.pdf"))
        fact_ok = os.path.exists(os.path.join(_dossier_lots(), f"cmd{cmd['id']}_facture.pdf"))
        lignes.append({
            "id": cmd["id"], "date": (cmd.get("cree_le") or "")[:16].replace("T", " "),
            "identifiant": cmd.get("identifiant", ""), "programme": cmd.get("programme", ""),
            "nb_feuilles": cmd.get("nb_feuilles", 0), "statut": cmd.get("statut", ""),
            "du": du, "cartons": au_coffre, "facture": fact_ok,
            "evenement": perso.get("nom_evenement", "") or perso.get("titre_jeu", ""),
        })
        nb_f += int(cmd.get("nb_feuilles") or 0)
        du_total += du
        if (cmd.get("cree_le") or "")[:7] == mois:
            du_mois += du
    return jsonify({"ok": True, "nom": part["nom"], "zone": part.get("zone", ""),
                    "commandes": lignes,
                    "stats": {"nb": len(lignes), "feuilles": nb_f,
                              "du_mois": du_mois, "du_total": du_total}})


_PRIX_PART_LOCK = _threading.Lock()


def _prix_partenaires_chemin():
    base = os.path.dirname(os.environ.get("MANAPRINT_DB", "/tmp/manaprint.db")) or "/tmp"
    return os.path.join(base, "prix_partenaires.json")


def _lire_prix_partenaires():
    """💰 Les prix clients fixés par chaque partenaire dans son espace.
    {slug: {eco_nb, eco_couleur, p15_nb, p15_couleur}} — vide = tarif standard."""
    import json as _json
    try:
        with open(_prix_partenaires_chemin(), encoding="utf-8") as f:
            return _json.load(f) or {}
    except Exception:
        return {}


def _sauver_prix_partenaires(tous):
    import json as _json
    chemin = _prix_partenaires_chemin()
    with _PRIX_PART_LOCK:
        with open(chemin + ".tmp", "w", encoding="utf-8") as f:
            _json.dump(tous, f, ensure_ascii=False, indent=1)
        os.replace(chemin + ".tmp", chemin)


@app.route("/api/partenaire/prix", methods=["GET", "POST"])
def api_partenaire_prix():
    """💰 Le partenaire consulte / fixe SES prix clients (la redevance 1,5 F
    reste un accord privé avec 2KEA — jamais montrée aux clients)."""
    slug, part = _partenaire_session()
    if not slug:
        return jsonify({"ok": False, "message": "connexion requise"}), 403
    if request.method == "GET":
        return jsonify({"ok": True, "prix": _lire_prix_partenaires().get(slug) or {}})
    d = request.get_json(silent=True) or {}
    propre = {}
    for cle in ("eco_nb", "eco_couleur", "p15_nb", "p15_couleur"):
        v = str(d.get(cle, "") or "").strip().replace(",", ".")
        if not v:
            continue
        try:
            x = float(v)
        except Exception:
            return jsonify({"ok": False, "message": f"\u00ab {v} \u00bb n'est pas un prix valide."})
        if not (0 < x <= 10000):
            return jsonify({"ok": False, "message": "Chaque prix doit \u00eatre entre 1 et 10 000 F."})
        propre[cle] = round(x, 1)
    tous = _lire_prix_partenaires()
    if propre:
        tous[slug] = propre
    else:
        tous.pop(slug, None)
    _sauver_prix_partenaires(tous)
    return jsonify({"ok": True, "prix": propre, "message":
                    "Prix enregistr\u00e9s \u2705 Ils s'appliquent d\u00e8s maintenant sur votre vitrine."
                    if propre else "Prix retir\u00e9s \u2014 retour au tarif standard de la plateforme."})


# ══ 🛍️ LES ARTICLES DES BOUTIQUES (rayon libre de chaque partenaire) ═════════
_ARTICLES_LOCK = _threading.Lock()
LIMITE_PHOTO_ARTICLE = 3 * 1024 * 1024   # 3 Mo par photo
MAX_ARTICLES_PAR_BOUTIQUE = 30


def _articles_chemin():
    base = os.path.dirname(os.environ.get("MANAPRINT_DB", "/tmp/manaprint.db")) or "/tmp"
    return os.path.join(base, "articles_partenaires.json")


def _dossier_photos_articles():
    base = os.path.dirname(os.environ.get("MANAPRINT_DB", "/tmp/manaprint.db")) or "/tmp"
    d = os.path.join(base, "articles_photos")
    os.makedirs(d, exist_ok=True)
    return d


def _lire_articles():
    import json as _json
    try:
        with open(_articles_chemin(), encoding="utf-8") as f:
            return _json.load(f) or {}
    except Exception:
        return {}


def _sauver_articles(tous):
    import json as _json
    chemin = _articles_chemin()
    with _ARTICLES_LOCK:
        with open(chemin + ".tmp", "w", encoding="utf-8") as f:
            _json.dump(tous, f, ensure_ascii=False, indent=1)
        os.replace(chemin + ".tmp", chemin)


@app.route("/api/boutique/<slug>/articles", methods=["GET"])
def api_articles_boutique(slug):
    """🛍️ L'étalage PUBLIC d'une boutique (lu par sa vitrine)."""
    if slug not in PARTENAIRES:
        return jsonify({"ok": False}), 404
    return jsonify({"ok": True, "articles": _lire_articles().get(slug) or []})


@app.route("/articles-photos/<nom_fichier>", methods=["GET"])
def photo_article(nom_fichier):
    import re as _re
    if not _re.fullmatch(r"[a-z0-9_]+\.(jpg|png)", nom_fichier):
        return "photo inconnue", 404
    chemin = os.path.join(_dossier_photos_articles(), nom_fichier)
    if not os.path.exists(chemin):
        return "photo inconnue", 404
    return send_file(chemin, mimetype="image/jpeg" if nom_fichier.endswith(".jpg") else "image/png")


@app.route("/api/partenaire/articles", methods=["GET", "POST"])
def api_partenaire_articles():
    """🛍️ L'OUTIL SPÉCIAL du partenaire : il gère lui-même son rayon d'articles."""
    import base64 as _b64
    import re as _re
    slug, part = _partenaire_session()
    if not slug:
        return jsonify({"ok": False, "message": "connexion requise"}), 403
    tous = _lire_articles()
    miens = tous.get(slug) or []
    if request.method == "GET":
        return jsonify({"ok": True, "articles": miens})
    d = request.get_json(silent=True) or {}

    # ── suppression ──
    if d.get("supprimer"):
        cible = str(d.get("supprimer"))
        garde = [x for x in miens if str(x["id"]) != cible]
        if len(garde) == len(miens):
            return jsonify({"ok": False, "message": "Article introuvable."})
        for x in miens:
            if str(x["id"]) == cible and x.get("photo"):
                try:
                    os.remove(os.path.join(_dossier_photos_articles(), x["photo"]))
                except Exception:
                    pass
        tous[slug] = garde
        _sauver_articles(tous)
        return jsonify({"ok": True, "message": "Article retiré de la vitrine.", "articles": garde})

    # ── ajout / modification ──
    nom = (d.get("nom") or "").strip()[:80]
    if len(nom) < 2:
        return jsonify({"ok": False, "message": "Donnez un nom à l'article."})
    try:
        prix = round(float(str(d.get("prix", "")).replace(",", ".")), 0)
        assert 0 < prix <= 1000000
    except Exception:
        return jsonify({"ok": False, "message": "Le prix doit être un nombre (en XPF)."})
    desc = (d.get("desc") or "").strip()[:200]
    art_id = str(d.get("id") or "").strip()
    existant = next((x for x in miens if str(x["id"]) == art_id), None) if art_id else None
    if existant is None and len(miens) >= MAX_ARTICLES_PAR_BOUTIQUE:
        return jsonify({"ok": False, "message": f"Maximum {MAX_ARTICLES_PAR_BOUTIQUE} articles par boutique."})

    photo_nom = existant.get("photo") if existant else None
    photo_b64 = d.get("photo_base64") or ""
    if photo_b64:
        try:
            brut = _b64.b64decode(_re.sub(r"^data:image/[a-z]+;base64,", "", photo_b64), validate=False)
        except Exception:
            return jsonify({"ok": False, "message": "Photo illisible — réessayez avec un JPG ou un PNG."})
        if len(brut) > LIMITE_PHOTO_ARTICLE:
            return jsonify({"ok": False, "message": "Photo trop lourde (3 Mo maximum)."})
        if brut[:3] == b"\xff\xd8\xff":
            ext = "jpg"
        elif brut[:8] == b"\x89PNG\r\n\x1a\n":
            ext = "png"
        else:
            return jsonify({"ok": False, "message": "Seuls les JPG et PNG sont acceptés."})
        if existant and existant.get("photo"):
            try:
                os.remove(os.path.join(_dossier_photos_articles(), existant["photo"]))
            except Exception:
                pass
        nouvel_id = art_id or str(int(__import__("time").time() * 1000))
        photo_nom = f"{slug}_{nouvel_id}.{ext}"
        with open(os.path.join(_dossier_photos_articles(), photo_nom), "wb") as f:
            f.write(brut)
        art_id = nouvel_id

    if existant:
        existant.update({"nom": nom, "prix": prix, "desc": desc, "photo": photo_nom})
    else:
        art_id = art_id or str(int(__import__("time").time() * 1000))
        miens.append({"id": art_id, "nom": nom, "prix": prix, "desc": desc, "photo": photo_nom})
    tous[slug] = miens
    _sauver_articles(tous)
    return jsonify({"ok": True, "message": "Article en vitrine \u2705", "articles": miens})


@app.route("/api/partenaire/pdf/<int:commande_id>/<quoi>", methods=["GET"])
def api_partenaire_pdf(commande_id, quoi):
    """⬇️ Le partenaire ne télécharge QUE ses cartons et ses factures —
    jamais le rapport confidentiel (réservé à l'organisateur)."""
    import json as _json
    slug, part = _partenaire_session()
    if not slug:
        return "connexion requise", 403
    if quoi not in ("cartons", "facture"):
        return "type non autoris\u00e9", 403
    cmd = db.get_commande(commande_id)
    if not cmd:
        return "commande introuvable", 404
    try:
        perso = _json.loads(cmd.get("params_perso") or "{}")
    except Exception:
        perso = {}
    if (perso.get("partenaire") or "") != slug:
        return "cette commande n'appartient pas \u00e0 votre boutique", 403
    chemin = os.path.join(_dossier_lots(), f"cmd{commande_id}_{quoi}.pdf")
    if not os.path.exists(chemin):
        return ("PDF pas encore au coffre \u2014 il appara\u00eetra ici apr\u00e8s la "
                "fabrication (ou demandez \u00e0 la plateforme un \U0001f4ec renvoi)."), 404
    return send_file(chemin, mimetype="application/pdf",
                     download_name=f"manaprint_cmd{commande_id}_{quoi}.pdf")


@app.route("/api/admin/rafraichir-vignettes", methods=["POST"])
@admin_requis
def admin_rafraichir_vignettes():
    """🧹 Efface toutes les vignettes (après la modification d'un jeu, par ex.)
    et relance le préchauffage : elles se refabriquent toutes seules, à neuf."""
    d = _dossier_apercus()
    n = 0
    try:
        for f in os.listdir(d):
            if f.endswith(".png") or f.endswith(".tmp"):
                os.remove(os.path.join(d, f))
                n += 1
    except Exception:
        pass
    _lancer_prechauffage()
    return jsonify({"ok": True, "message":
                    f"{n} vignettes effacées ✅ La fabrique les refait toutes en coulisses "
                    "(2 à 3 minutes) — recharge la page du menu ensuite."})
# ══════════════════════════════════════════════════════════════════════


@app.route("/api/admin/renvoyer-emails", methods=["POST"])
@admin_requis
def admin_renvoyer_emails():
    """📬 RATTRAPAGE : refabrique une commande et renvoie ses deux emails
    (PDF -> partenaire, rapport confidentiel -> organisateur). Pour les clients
    qui n'ont rien reçu avant la configuration SMTP. Sans risque : le PDF et le
    rapport repartent ensemble, parfaitement assortis."""
    if not SMTP_USER or not SMTP_PASS:
        return jsonify({"ok": False, "message":
                        "Configure d'abord SMTP_USER et SMTP_PASS sur Railway — "
                        "sans le facteur, rien ne peut partir."})
    import json as _json
    data = request.get_json(force=True)
    try:
        commande_id = int(data.get("commande_id") or 0)
    except Exception:
        commande_id = 0
    if not commande_id:
        return jsonify({"ok": False, "message": "Numéro de commande manquant."})
    cmd = db.get_commande(commande_id)
    if not cmd:
        return jsonify({"ok": False, "message": f"Commande #{commande_id} introuvable."})
    try:
        perso = _json.loads(cmd["params_perso"] or "{}")
    except Exception:
        perso = {}
    # 📧 email du client fourni au renvoi : il CORRIGE la commande (sauvé pour toujours)
    email_saisi = (data.get("email_client") or "").strip()
    if email_saisi:
        if "@" not in email_saisi or "." not in email_saisi.split("@")[-1]:
            return jsonify({"ok": False, "message":
                            f"« {email_saisi} » ne ressemble pas à un email valide."})
        perso["email_organisateur"] = email_saisi
        try:
            with db.get_db() as conn:
                conn.execute("UPDATE commandes SET params_perso = ? WHERE id = ?",
                             (_json.dumps(perso, ensure_ascii=False), commande_id))
        except Exception as e:
            return jsonify({"ok": False, "message": f"Impossible d'enregistrer l'email : {e}"})
    email_cli = (perso.get("email_organisateur") or "").strip()
    seulement_rapport = bool(data.get("seulement_rapport"))
    if seulement_rapport and not email_cli:
        return jsonify({"ok": False, "message":
                        "Mode « seulement le rapport » : il faut un email client — "
                        "renseigne le champ \U0001f4e7."})
    part_nom = lancer_fabrication(commande_id, seulement_rapport=seulement_rapport)
    if not part_nom:
        return jsonify({"ok": False, "message":
                        f"La commande #{commande_id} n'a pas de partenaire d'impression "
                        "enregistré — rien à renvoyer par email."})
    dest_rapport = email_cli if email_cli else "(pas d'email client : le rapport voyage avec le PDF du partenaire)"
    if seulement_rapport:
        return jsonify({"ok": True, "message":
                        f"Commande #{commande_id} \U0001f92b rapport confidentiel SEUL → {email_cli} "
                        "(l'imprimeur ne reçoit rien). Envoi en arrière-plan (1 à 3 min)."})
    return jsonify({"ok": True, "message":
                    f"Commande #{commande_id} refabriquée ✅ PDF → {part_nom} · "
                    f"rapport confidentiel → {dest_rapport}. "
                    "Les envois partent en arrière-plan (1 à 3 min pour les grosses commandes) "
                    "— une copie arrive aussi dans ta boîte SMTP."})


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
    nom_part = lancer_fabrication(commande_id)
    info = (f" Le PDF est en fabrication et sera envoyé automatiquement à {nom_part}"
            " (plusieurs minutes pour les grosses commandes).") if nom_part else ""
    return jsonify({"ok": True, "message": "Commande validée." + info})


@app.route("/api/admin/evenements", methods=["GET"])
@admin_requis
def admin_evenements():
    """📜 Historique des lots QR — le registre de résurrection, tout prêt."""
    return jsonify({"ok": True, "evenements": db.lister_evenements()})


@app.route("/api/admin/evenements/redeclarer", methods=["POST"])
@admin_requis
def admin_redeclarer_evenement():
    """🚑 RÉSURRECTION D'ÉVÉNEMENT : re-déclare un lot de cartons déjà imprimés
    dont la fiche a disparu de la base (ex. base non persistante lors d'un
    redéploiement). L'identifiant est dans le QR du carton (manaprint.app/v/ID/...)
    et les codes 6 lettres se recalculent avec le secret : re-déclarer l'événement
    suffit à faire revivre TOUS les cartons du lot. Idempotent (INSERT OR REPLACE)."""
    d = request.get_json(force=True, silent=True) or {}
    evenement_id = (d.get("evenement_id", "") or "").strip().upper()
    if not evenement_id:
        return jsonify({"ok": False, "message": "Identifiant d'événement manquant (il est dans le QR : manaprint.app/v/IDENTIFIANT/...)."}), 400
    try:
        serie_min = int(d.get("serie_min", 1) or 1)
        serie_max = int(d.get("serie_max", 0) or 0)
    except Exception:
        return jsonify({"ok": False, "message": "Séries min/max invalides."}), 400
    if serie_max < serie_min or serie_min < 1:
        return jsonify({"ok": False, "message": "La série max doit être ≥ à la série min (≥ 1)."}), 400
    db.creer_evenement(
        evenement_id=evenement_id,
        nom=(d.get("nom", "") or "Événement ressuscité").strip(),
        identifiant="gestion",
        programme=(d.get("programme", "") or "").strip(),
        serie_min=serie_min,
        serie_max=serie_max,
        date_tournoi=(d.get("date_tournoi", "") or "").strip(),
        couleur_qr=(d.get("couleur_qr", "") or "").strip(),
    )
    return jsonify({"ok": True,
                    "message": "Événement %s re-déclaré (séries %d à %d) — les cartons de ce lot sont de nouveau vérifiables." % (
                        evenement_id, serie_min, serie_max)})


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
