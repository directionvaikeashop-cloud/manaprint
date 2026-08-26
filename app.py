"""
MANAPRINT — Application Flask
Relie : contrôle d'accès (Pacific Ink / international), génération PDF, espace gestion.
Déployable sur Railway (même stack que Ticket Bingo).
"""
import os
import hashlib
import secrets
from flask import Flask, request, jsonify, send_file, render_template, session, Response, make_response, redirect
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
from generators import quines90
from generators import kai
from generators import ohana75_8boules
from generators import ohana75_10boules
from generators import quatre_coin
from generators import pol
from generators import sun
from generators import pow as powgen
from generators import pow9 as pow9gen
from generators import poe_parau as poeparaugen
from generators import poe as poegen
from generators import bng as bnggen
from generators import hakari as hakarigen
from generators import henua_enana as henuaenanagen
from generators import tiare as tiaregen
from generators import tuamotu as tuamotugen
from generators import societe as societegen
from generators import australes as australesgen
from generators import gambier as gambiergen
from generators import parata as paratagen
from generators import katiu as katiugen
from generators import ok as okgen
from generators import feu as feugen
from generators import vision as visiongen
from generators import taptap as taptapgen
from generators import joie as joiegen
from generators import caller as callergen
from generators import valider as validergen
from generators import chance as chancegen
from generators import opoa as opoagen
from generators import francs as francsgen
from generators import francs500
from generators import dollar1
from generators import francs1000
from generators import francs5000
from generators import tesla as teslagen
from generators import salute as salutegen
from generators import pietra as pietragen
from generators import triple as triplegen
from generators import triple_bg90 as tbg90gen
from generators import triple_bn90 as tbn90gen
from generators import triple_bi90 as tbi90gen
from generators import triple_bg75 as tbg75gen
from generators import triple_bn75 as tbn75gen
from generators import triple_bi75 as tbi75gen
from generators import win
from generators import rubis90
from generators import rubis75
from generators import sicilio
from generators import avinda
from generators import losange
from generators import italia
from generators import italia_villes
from generators import italia_escalier
from generators import vai
from generators import wow4
from generators import maia as maiagen
from generators import corsica as corsicagen
from generators import bno
from generators import ngo
from generators import diamant
from generators import rui
from generators import tureia
from generators import tureia_atoll
from generators import vanille
from generators import spacex
from generators import champagne
from generators import fan90
from generators import oaoa
from generators import lagoon
from generators import havai
from generators import flash_debout
from generators import dual_dab
from generators import cerf_volant
from generators import bubulle
from generators import moorea
from generators import triple_action_90
from generators import trio75
from generators import trio90
from generators import funday
from generators import huahine
from generators import boules40
from generators import tea
from generators import ohana75_4series
from generators import ohana90_4series
from generators import ohana90_2series
from generators import ohana90_3series
from generators import bgo
from generators import igo
from generators import kea
from generators import moon
from generators import ani
from generators import brown14
from generators import ino8
from generators import ino
from generators import tahaa
from generators import tahaa90
from generators import baam
from generators import papeari
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
from generators import bin6
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
# \U0001f511 06/08 : une connexion partenaire tient 30 JOURS. Avant, le cookie
# mourait a la fermeture du navigateur — sur un telephone, cela arrive
# sans arret, et l ecran affichait alors « Serveur occupe » (message
# trompeur) au lieu de proposer de se reconnecter.
from datetime import timedelta as _timedelta
app.permanent_session_lifetime = _timedelta(days=30)

# ── Envoi d'email (impression partenaire FUN AND CO) ──────────────────────────
import smtplib
from email.message import EmailMessage

FUN_AND_CO_EMAIL = os.environ.get("FUN_AND_CO_EMAIL", "funandco24@gmail.com")
SMTP_USER = os.environ.get("SMTP_USER", "")   # ex: ton.compte@gmail.com
SMTP_PASS = os.environ.get("SMTP_PASS", "")   # mot de passe d'application Gmail

# ── Partenaires d'impression (le client polynésien peut faire imprimer chez eux) ──
# Pour en ajouter un : ajoute une ligne ici (id, nom, email, zone, tel). C'est tout.
# ═══ 🔒 LES JEUX RÉSERVÉS (sceau Maeva 13/08) ═══
# Certains partenaires n'ont pas accès à tous les jeux dans « Ma fabrique ».
# ⚠️ Ce sont les SEPT JEUX HABILLÉS — ceux au puzzle, au soleil, aux
# glaçons, aux nuages, à la chenille. Maeva les réserve.
# Pour en réserver d'autres un jour : ajouter le slug du partenaire ici,
# avec la liste des jeux qu'il ne doit pas voir.
JEUX_HABILLES = {
    "win", "kai", "sun", "wiz", "rai", "tahaa", "tahaa90", "baam", "papeari",
    "fan90", "lagoon", "boules60", "fleche", "brown8", "diamant",
    "cerf_volant", "boules40", "bubulle", "dual_dab",
    "aloha75", "pol", "bingo_ball", "rubis75", "losange",
    "ani",
}
JEUX_INTERDITS = {
    "ranihei": JEUX_HABILLES,
}


def _jeu_interdit(slug, programme):
    """🔒 Ce partenaire a-t-il le droit de fabriquer ce jeu ?"""
    if not slug:
        return False
    return _base_jeu(programme) in JEUX_INTERDITS.get(slug, ())


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
        # 🖨️ L'enseigne imprimée sur les cartons de SA fabrique (demande Maeva 01/08 :
        # « FUN&CO veut le même outil que RANIHEI, à son nom »).
        "enseigne_pdf": "FUN&CO",
        "tel_pdf": "87 26 73 24",
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
        # 🖨️ L'enseigne imprimée sur les cartons de SA fabrique (demande Maeva 29/07)
        "enseigne_pdf": "RANIHEI AND SISTER RAROMATAI",
        "tel_pdf": "87 77 39 19",
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
# ── 🖨️ LA TEINTE DES CHIFFRES EN NOIR & BLANC (sceau Maeva, 05/08) ─────────
# « pour la teneur du noir et blanc de nos PDF, utilise le gris 30 % ».
# Chacun des 125 générateurs porte son propre _GRIS_ECO (0,50 d'origine).
# Plutôt que de retoucher 125 fichiers, la maison impose ici SA teinte à
# tous : un seul réglage, un seul déploiement.
# Maeva veut 30 % D'ENCRE : « le noir en impression est très fort ».
# En clarté, 30 % d'encre = 0,70 (plus PÂLE que l'ancien 0,50).
#   0,70 = le réglage retenu — un tiers de toner en moins sur les gros jeux
#   0,50 = l'ancien (trop chargé)   ·   0,30 = très foncé
# Le microtexte intérieur suit automatiquement (il vaut la teinte × 0,45).
# La gamme PREMIUM (_GRIS_P15) n'est pas touchée.
GRIS_CHIFFRES_ECO = 0.50   # 🎨 50 % D'ENCRE POUR TOUS LES JEUX (sceau Maeva 07/08).
                           # ⚠️ LANGAGE IMPRIMEUR : le chiffre que Maeva donne est
                           # la TENEUR EN ENCRE ; la valeur du code est son
                           # complement — 50 % d'encre = Color(0,50).
                           # Historique : 50 % au depart, 30 % le 05/08 (trop pale),
                           # 67 % puis 60 % puis 50 % pour tous le 07/08.


# 🎨 LES TEINTES PARTICULIÈRES — un jeu peut avoir la sienne.
# (vide aujourd'hui : toute la maison est a 50 % d'encre. Le mecanisme
#  reste pret si un jeu se revele trop gourmand — une ligne suffit,
#  par exemple "p6_marathon": 0.60)
GRIS_PARTICULIERS = {
}


def _imposer_gris_maison():
    """Applique GRIS_CHIFFRES_ECO à tous les générateurs déjà chargés,
    sauf à ceux qui ont leur teinte à eux (GRIS_PARTICULIERS)."""
    try:
        from reportlab.lib import colors as _col
        teinte = _col.Color(GRIS_CHIFFRES_ECO, GRIS_CHIFFRES_ECO, GRIS_CHIFFRES_ECO)
    except Exception:
        return 0
    import sys as _sys
    poses = 0
    for _nom, _mod in list(_sys.modules.items()):
        if not _nom.startswith("generators.") or _mod is None:
            continue
        if hasattr(_mod, "_GRIS_ECO"):
            try:
                _court = _nom.split(".")[-1]
                _v = GRIS_PARTICULIERS.get(_court)
                _mod._GRIS_ECO = _col.Color(_v, _v, _v) if _v is not None else teinte
                poses += 1
            except Exception:
                pass
    return poses


_GRIS_POSES = _imposer_gris_maison()
print(f"[TEINTE] gris des chiffres {GRIS_CHIFFRES_ECO} appliqué à {_GRIS_POSES} jeux")

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
_enregistrer_paire("aloha75",       "Aloha 75",          "🌺", 8, aloha75.generer_pdf)
_enregistrer_paire("p6_marathon",   "P6 Marathon",       "6️⃣", 6,  p6_marathon.generer_pdf)
_enregistrer_paire("p6_casino",     "PJOKER",            "🃏", 6,  p6_marathon.generer_pdf_casino)
_enregistrer_paire("bingo_ball",    "Bingo Ball",        "🎱", 8, bingo_ball.generer_pdf)
_enregistrer_paire("ohana75_2s",    "OHANA 75 · 2 séries","🌺", 2,  ohana75_2series.generer_pdf)
_enregistrer_paire("brown8",        "BROWN 8 boules",     "🟤", 8,  brown8.generer_pdf)
_enregistrer_paire("flash_quines",  "FLASH QUINES allongé","⚡", 9,  flash_quines_allonge.generer_pdf)
_enregistrer_paire("quines90",      "QUINES 90","🎟️", 18, quines90.generer_pdf)
_enregistrer_paire("kai",           "KAI 7 boules",       "🍽️", 12, kai.generer_pdf)
_enregistrer_paire("ohana75_8b",    "OHANA 75 · 8 boules","🌺", 9,  ohana75_8boules.generer_pdf)
_enregistrer_paire("ohana75_8b_smo","OHANA 75 · 8 boules SMORFIA","🎴", 9,  ohana75_8boules.generer_pdf_smorfia)
_enregistrer_paire("ohana75_8b_myst","OHANA 75 · 8 boules MYSTÈRE","💰", 9,  ohana75_8boules.generer_pdf_mystere)
_enregistrer_paire("ohana75_10b",   "OHANA 75 · 10 boules","🌺", 9,  ohana75_10boules.generer_pdf)
_enregistrer_paire("ohana75_10b_myst","OHANA 75 · 10 boules MYSTÈRE","💰", 9,  ohana75_10boules.generer_pdf_mystere)
_enregistrer_paire("quatre_coin",   "4 COIN","🎯", 6,  quatre_coin.generer_pdf)
_enregistrer_paire("pol",           "POL 6 boules","🎲", 8, pol.generer_pdf)
_enregistrer_paire("sun",           "SUN 8 boules","☀️", 12, sun.generer_pdf)
_enregistrer_paire("sun_casino",    "SUN CASINO","🎲", 12, sun.generer_pdf_casino)
_enregistrer_paire("pow",           "POW 8 boules","💥", 12, powgen.generer_pdf)
_enregistrer_paire("pow9",          "POW 9 boules", "\U0001f9fa", 12, pow9gen.generer_pdf)
_enregistrer_paire("pow_casino",    "POW CASINO","🎲", 12, powgen.generer_pdf_casino)
_enregistrer_paire("poe_parau",     "POE PARAU 6 boules", "🦪", 12, poeparaugen.generer_pdf)
_enregistrer_paire("poe",           "POE 6 boules", "⚪", 12, poegen.generer_pdf)
_enregistrer_paire("bng",           "BNG 5 boules", "🟢", 12, bnggen.generer_pdf)
_enregistrer_paire("hakari",        "HAKARI 6 boules", "🥥", 12, hakarigen.generer_pdf)
_enregistrer_paire("henua_enana",   "HENUA ENANA 7 boules", "🗺️", 12, henuaenanagen.generer_pdf)
_enregistrer_paire("tiare",         "TIARE 50-90", "🌼", 12, tiaregen.generer_pdf)
_enregistrer_paire("tuamotu",       "TUAMOTU 8 boules", "🏝️", 8, tuamotugen.generer_pdf)
_enregistrer_paire("societe",       "SOCIÉTÉ 7 boules", "⛰️", 8, societegen.generer_pdf)
_enregistrer_paire("australes",     "AUSTRALES 7 boules", "🐋", 8, australesgen.generer_pdf)
_enregistrer_paire("gambier",       "GAMBIER 7 boules", "🐚", 8, gambiergen.generer_pdf)
_enregistrer_paire("parata",        "PARATA 6 plages", "🦈", 6, paratagen.generer_pdf)
_enregistrer_paire("katiu",         "KATIU 7 boules", "🐠", 8, katiugen.generer_pdf)
_enregistrer_paire("ok",            "OK 7 boules", "👌", 12, okgen.generer_pdf)
_enregistrer_paire("feu",           "FEU 5 boules", "🔥", 12, feugen.generer_pdf)
_enregistrer_paire("vision",        "VISION 6 boules", "👁️", 8, visiongen.generer_pdf)
_enregistrer_paire("taptap",        "TAP TAP 5 boules", "👏", 8, taptapgen.generer_pdf)
_enregistrer_paire("joie",          "JOIE 5 boules", "😄", 12, joiegen.generer_pdf)
_enregistrer_paire("caller",        "CALLER 6 boules", "👍", 12, callergen.generer_pdf)
_enregistrer_paire("valider",       "VALIDER 6 boules", "✅", 12, validergen.generer_pdf)
_enregistrer_paire("chance",        "CHANCE 6 boules", "🍀", 8, chancegen.generer_pdf)
_enregistrer_paire("opoa",          "OPOA 7 boules", "🏔️", 8, opoagen.generer_pdf)
_enregistrer_paire("francs",        "100 FRANCS 7 boules", "🪙", 12, francsgen.generer_pdf)
_enregistrer_paire("francs500",     "500 FRANCS", "\U0001f4b5", 8,  francs500.generer_pdf)
_enregistrer_paire("dollar1",       "1 DOLLAR",   "\U0001f4b5", 10, dollar1.generer_pdf)
_enregistrer_paire("francs1000",    "1000 FRANCS","\U0001f4b4", 8,  francs1000.generer_pdf)
_enregistrer_paire("francs5000",    "5000 FRANCS","\U0001f48e", 8,  francs5000.generer_pdf)
_enregistrer_paire("tesla",         "TESLA 5 boules", "🚗", 8, teslagen.generer_pdf)
_enregistrer_paire("salute",        "SALUTE 6 boules", "🗺️", 8, salutegen.generer_pdf)
_enregistrer_paire("salute_smo",    "SALUTE SMORFIA", "🎴", 8, salutegen.generer_pdf_smorfia)
_enregistrer_paire("pietra",        "PIETRA 8 boules", "🌰", 8, pietragen.generer_pdf)
_enregistrer_paire("pietra_smo",    "PIETRA SMORFIA", "🎴", 8, pietragen.generer_pdf_smorfia)
_enregistrer_paire("triple_bo90",   "TRIPLE BO90 9 boules", "3️⃣", 7, triplegen.generer_pdf)
_enregistrer_paire("triple_bg90",   "TRIPLE BG90 9 boules", "🅱️", 7, tbg90gen.generer_pdf)
_enregistrer_paire("triple_bn90",   "TRIPLE BN90 9 boules", "🟤", 7, tbn90gen.generer_pdf)
_enregistrer_paire("triple_bi90",   "TRIPLE BI90 9 boules", "🔵", 7, tbi90gen.generer_pdf)
_enregistrer_paire("triple_bg75",   "TRIPLE BG75 9 boules", "💠", 7, tbg75gen.generer_pdf)
_enregistrer_paire("triple_bn75",   "TRIPLE BN75 9 boules", "🔶", 7, tbn75gen.generer_pdf)
_enregistrer_paire("triple_bi75",   "TRIPLE BI75 9 boules", "💙", 7, tbi75gen.generer_pdf)

# ── 💰 GRILLE 2KEA « PAQUETS DE 25 » (décision Maeva 23/07) ──────────────────
# PREMIUM en veilleuse (le code reste, réactivable). ÉCO seulement :
# anciens jeux 150 F (N&B) / 250 F (Couleur) les 25 feuilles ;
# les 23 nouveaux jeux nés les 22-23/07 : 250 F / 300 F les 25 feuilles
# (soit 10 / 12 F la feuille). Quantités par paquets de 25 (25 → 250).
NOUVEAUX_JEUX = {
    "gambier", "parata", "katiu", "ok", "feu", "vision", "taptap", "joie",
    "caller", "valider", "chance", "opoa", "francs", "tesla", "salute", "pietra",
    "triple_bo90", "triple_bg90", "triple_bn90", "triple_bi90",
    "triple_bg75", "triple_bn75", "triple_bi75", "rubis75", "sicilio", "sicilio_smo", "avinda", "avinda_myst", "losange", "italia",
}

# 💰 GRILLE DU 05/08 (décision Maeva) — les 25 feuilles :
#     • COULEUR : 250 F pour TOUS les jeux (10 F la feuille)
#     • NOIR & BLANC : 150 F pour les jeux ci-dessous (6 F la feuille)
#                      185 F pour tous les autres (7,4 F la feuille)
# Les prix fixés par un partenaire et le tarif international restent souverains.
TARIF_NB_150 = {
    "igo",            # IGO 5 boules
    "boules40",       # 40 BOULES
    "fan90",          # FAN 90
    "lunes75",        # LUNES 75
    "rubis75",        # RUBIS 75
    "lettre_u",       # LETTRE U
    "boules60",       # 60 BOULES
    "lettre_l",       # LETTRE L
    "champagne",      # CHAMPAGNE
    "topday",         # TOP DAY
    "bo75",           # BO 75
    "diamant",        # DIAMANT
    "yes",            # YES
    "fleche",         # FLÈCHE
    "p6_marathon",    # P6 MARATHON
    "quatre_coin",    # 4 COIN
    "bg75",           # BG 75
    "funday",         # FUNDAY
    "bn75",           # BN 75
    "ohana90_24b",    # OHANA 90 · 24 boules
    "huahine",        # HUAHINE
    "ohana90_12b",    # OHANA 90 · 12 boules
    "bi90",           # BI 90
    "bn90",           # BN 90
    "bgo5",           # BGO 5 boules
    "bno",            # BNO 8 boules (la normale)
    "moorea",         # MOOREA
    "ino",            # INO 5 boules (la normale)
    "rubis90",        # RUBIS 90
}
PRIX_NB_AUTRES = 7.4   # 185 F les 25 feuilles

# 💵 LES JEUX À BILLETS (décision Maeva 13/08) : 250 F les 25 feuilles,
# en noir & blanc comme en couleur. Ce sont les plus travaillés du
# catalogue — le dessin du billet, la rosace, les chiffres étirés.
TARIF_BILLETS_250 = {
    "dollar1",      # 1 DOLLAR
    "francs500",    # 500 FRANCS
    "francs1000",   # 1000 FRANCS
    "francs5000",   # 5000 FRANCS
}
PRIX_BILLETS = 10.0            # 250 F les 25 feuilles, en noir & blanc
# 🎨 EN COULEUR, LES BILLETS SONT À PART (décision Maeva 13/08) : 375 F les
# 25 feuilles, au lieu des 250 F de tous les autres jeux. ⚠️ POURQUOI CE
# SUPPLÉMENT : sur les autres jeux, la couleur ne teinte que les chiffres ;
# ici, c'est LE BILLET LUI-MÊME qui sera imprimé dans les couleurs de
# l'original — bien plus d'encre, et un rendu de vraie monnaie.
PRIX_BILLETS_COULEUR = 15.0    # 375 F les 25 feuilles

# 🎨 LES DEUX OFFRES EN COULEUR (décision Maeva, 05/08 — nouvelles machines
# attendues en novembre) :
#   ① « PDF seul »   : 3,5 F la feuille (87 F les 25) — le client reçoit son
#                      fichier tout de suite, il l'imprime où il veut ;
#   ② « Impression » : 250 F les 25 (le tarif de base), mais la commande part
#                      d'abord en DEMANDE : Maeva répond depuis son espace de
#                      gestion « oui on peut imprimer » ou « non ». Le client
#                      ne paie qu'APRÈS un oui.
# Le noir & blanc ne change pas : impression directe, 150 ou 185 F les 25.
PRIX_PDF_SEUL_COULEUR = 3.5
STATUT_DEMANDE = "attente_reponse"   # la commande attend la réponse de 2KEA

def _base_jeu(programme):
    """Identifiant du jeu sans son suffixe de variante (_p15_couleur, _nb…)."""
    p = str(programme or "")
    for suf in ("_p15_couleur", "_p15_nb", "_couleur", "_nb"):
        if p.endswith(suf):
            return p[:-len(suf)]
    return p
_enregistrer_paire("win",           "WIN 9 boules","🏆", 12, win.generer_pdf)
_enregistrer_paire("win_casino",    "WIN CASINO","🎲", 12, win.generer_pdf_casino)
_enregistrer_paire("rubis90",       "RUBIS 90","💎", 12, rubis90.generer_pdf)
_enregistrer_paire("rubis75",       "RUBIS 75 · 32 pts","💎", 8, rubis75.generer_pdf)
_enregistrer_paire("sicilio",       "SICILIO",          "🔷", 6,  sicilio.generer_pdf)
_enregistrer_paire("sicilio_smo",   "SICILIO SMORFIA",  "🎴", 6,  sicilio.generer_pdf_smorfia)
_enregistrer_paire("avinda",        "A VINDA · 2 séries","🍷", 2,  avinda.generer_pdf)
_enregistrer_paire("avinda_myst",   "A VINDA MYSTÈRE LETTRE","🔮", 2,  avinda.generer_pdf_mystere)
_enregistrer_paire("avinda_fort",   "A VINDA FORTUNO","💰", 2,  avinda.generer_pdf_fortune)
_enregistrer_paire("losange",       "LOSANGE · 8 boules","🪁", 8,  losange.generer_pdf)
_enregistrer_paire("italia",        "ITALIA",     "🇮🇹", 10, italia.generer_pdf)
_enregistrer_paire("italia_villes", "ITALIA VILLES","🗺️", 6,  italia_villes.generer_pdf)
_enregistrer_paire("italia_esc",    "ITALIA ESCALIER","\U0001fa9c", 10, italia_escalier.generer_pdf)
_enregistrer_paire("vai",           "VAI 9 boules","🌊", 8, vai.generer_pdf)
_enregistrer_paire("wow4",          "WOW 4","🎆", 12, wow4.generer_pdf)
_enregistrer_paire("maia",          "MAIA \u00b7 Ma\u00efa", "🍌", 12, maiagen.generer_pdf)
_enregistrer_paire("corsica",       "CORSICA \u00b7 l'\u00eele de la beaut\u00e9", "\u2b50", 8, corsicagen.generer_pdf)
_enregistrer_paire("bno",           "BNO 8 boules","🎯", 12, bno.generer_pdf)
_enregistrer_paire("bno_casino",    "BNO CASINO","🎰", 12, bno.generer_pdf_casino)
_enregistrer_paire("ngo",           "NGO 8 boules","🎳", 12, ngo.generer_pdf)
_enregistrer_paire("ngo_casino",    "NGO CASINO","🎰", 12, ngo.generer_pdf_casino)
_enregistrer_paire("diamant",       "DIAMANT","💎", 8,  diamant.generer_pdf)
_enregistrer_paire("rui",           "RUI","🎴", 12, rui.generer_pdf)
_enregistrer_paire("tureia",        "TUREIA","🔶", 6,  tureia.generer_pdf)
_enregistrer_paire("tureia_atoll", "ATOLL DE TUREIA","🏝️", 8,  tureia_atoll.generer_pdf)
_enregistrer_paire("vanille",      "VANILLE DE DONA","🌼", 6,  vanille.generer_pdf)
_enregistrer_paire("spacex",       "SPACE X",   "🚀", 1,  spacex.generer_pdf)
_enregistrer_paire("champagne",     "CHAMPAGNE","🥂", 6,  champagne.generer_pdf)
_enregistrer_paire("fan90",         "FAN 90","☀️", 8,  fan90.generer_pdf)
_enregistrer_paire("oaoa",          "OAOA","⭕", 12, oaoa.generer_pdf)
_enregistrer_paire("lagoon",        "LAGOON 5 boules","🏝️", 8, lagoon.generer_pdf)
_enregistrer_paire("havai",         "HAVAI","🌋", 8,  havai.generer_pdf)  # 2×4 = 8 cartons/feuille (corrigé 04/08 : 6 déclarés → 188 pages au lieu de 250)
_enregistrer_paire("flash_debout",  "FLASH QUINES DEBOUT","⚡", 8,  flash_debout.generer_pdf)
_enregistrer_paire("dual_dab",      "DUAL DAB 75","🤜", 8,  dual_dab.generer_pdf)
_enregistrer_paire("cerf_volant",   "CERF VOLANT","🪁", 8,  cerf_volant.generer_pdf)
_enregistrer_paire("bubulle",       "BUBULLE",    "\U0001fae7", 8,  bubulle.generer_pdf)
_enregistrer_paire("moorea",        "MOOREA",     "🌴", 6,  moorea.generer_pdf)
_enregistrer_paire("triple_action_90", "TRIPLE ACTION 90", "🎪", 8, triple_action_90.generer_pdf)
_enregistrer_paire("trio75",        "TRIO 75",     "\U0001f3ab", 2,  trio75.generer_pdf)
_enregistrer_paire("trio90",        "TRIO 90",     "\U0001f4cf", 2,  trio90.generer_pdf)
_enregistrer_paire("funday",        "FUNDAY",     "🎈", 10, funday.generer_pdf)
_enregistrer_paire("huahine",       "HUAHINE",    "⛵", 8,  huahine.generer_pdf)
_enregistrer_paire("boules40",      "40 BOULES",  "🎳", 8, boules40.generer_pdf)
_enregistrer_paire("tea",           "TEA",        "🍵", 12, tea.generer_pdf)
_enregistrer_paire("ohana75_4series", "OHANA 75 · 4 séries", "🌺", 4, ohana75_4series.generer_pdf)
_enregistrer_paire("ohana90_4series", "OHANA 90 · 4 séries", "🌸", 4, ohana90_4series.generer_pdf)
_enregistrer_paire("ohana90_2series", "OHANA 90 · 2 séries", "🌸", 2, ohana90_2series.generer_pdf)
_enregistrer_paire("ohana90_3series", "OHANA 90 · 3 séries", "🌸", 3, ohana90_3series.generer_pdf)
_enregistrer_paire("bgo",           "BGO",        "🔠", 12, bgo.generer_pdf)
_enregistrer_paire("igo",           "IGO",        "🎱", 12, igo.generer_pdf)
_enregistrer_paire("kea",           "KEA",        "🌿", 12, kea.generer_pdf)
_enregistrer_paire("moon",          "MOON",       "🌙", 8,  moon.generer_pdf)
_enregistrer_paire("ani",           "TEAHUPOO",        "🌊", 8, ani.generer_pdf)
_enregistrer_paire("brown14",       "BROWN 14 boules", "🟤", 8, brown14.generer_pdf)
_enregistrer_paire("ino8",          "INO 8 boules", "🎐", 12, ino8.generer_pdf)
_enregistrer_paire("ino",           "INO 5 boules", "🎏", 12, ino.generer_pdf)
_enregistrer_paire("tahaa",         "TAHAA",      "🥥", 8, tahaa.generer_pdf)
_enregistrer_paire("tahaa90",       "TAHAA 90",   "\U0001f41b", 8,  tahaa90.generer_pdf)
_enregistrer_paire("baam",          "BAAM",       "\U0001f388", 8,  baam.generer_pdf)
_enregistrer_paire("papeari",       "PAPEARI",    "\U0001f38a", 8,  papeari.generer_pdf)
_enregistrer_paire("boules60",      "60 BOULES",  "🔵", 8, boules60.generer_pdf)
_enregistrer_paire("ahuru",         "AHURU",      "🔟", 10, ahuru.generer_pdf)
_enregistrer_paire("tchin",         "TCHIN",      "🍻", 12, tchin.generer_pdf)
_enregistrer_paire("ing",           "ING",        "🧭", 12, ing.generer_pdf)
_enregistrer_paire("ing_casino",    "ING CASINO","🎰", 12, ing.generer_pdf_casino)
_enregistrer_paire("lunes75",       "LUNES 75",   "🌜", 12, lunes75.generer_pdf)
_enregistrer_paire("miss75",        "MISS 75",    "👑", 4,  miss75.generer_pdf)
_enregistrer_paire("bien_sur",      "BIEN SÛR",   "✅", 8,  bien_sur.generer_pdf)
_enregistrer_paire("ohana90_12b",   "OHANA 90 · 12 boules", "🌼", 9, ohana90_12boules.generer_pdf)
_enregistrer_paire("ohana90_24b",   "OHANA 90 · 24 boules", "💮", 6, ohana90_24boules.generer_pdf)
_enregistrer_paire("lettre_u",      "LETTRE U",   "😃", 6,  lettre_u.generer_pdf)
_enregistrer_paire("lettre_l",      "LETTRE L",   "😄", 6,  lettre_l.generer_pdf)
_enregistrer_paire("topday",        "TOPDAY",     "🔝", 12, topday.generer_pdf)
_enregistrer_paire("fleche",        "TAHITI",     "🌺", 8,  fleche.generer_pdf)
_enregistrer_paire("yes",           "YES",        "👍", 15, yes.generer_pdf)
_enregistrer_paire("bio",           "BIO 8 boules", "🌱", 12, bio.generer_pdf)
_enregistrer_paire("bio5",          "BIO 5 boules", "🌿", 12, bio5.generer_pdf)
_enregistrer_paire("zin",           "ZIN",        "⚡", 12, zin.generer_pdf)
_enregistrer_paire("rai",           "RAI",        "🌈", 12, rai.generer_pdf)
_enregistrer_paire("bin6",          "BIN 6 boules", "\U0001f3af", 12, bin6.generer_pdf)
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
_enregistrer_paire("ohana20b_smo",  "OHANA 75 · 20 boules SMORFIA","🎴", 5,  ohana75_20boules.generer_pdf_smorfia)
_enregistrer_paire("ohana20b_myst", "OHANA 75 · 20 boules MYSTÈRE","💰", 5,  ohana75_20boules.generer_pdf_mystere)
# --- Ajouter un futur jeu A4 = UNE ligne _enregistrer_paire(...) (crée Couleur + N&B) ---
# _enregistrer_paire("ohana90", "OHANA 90", "🌺", 8, ohana90.generer_pdf)

# Table cartes/feuille dérivée automatiquement du registre
CARTES_PAR_FEUILLE = {jid: j["cartes_par_feuille"] for jid, j in REGISTRE_JEUX.items()}


# 🖼️ LA LISTE OFFICIELLE DES JEUX DÉCORABLES (filigranes) — première vague
JEUX_MOTIF = {"pow", "pow6", "ino", "ino8", "bgo5", "bio5", "boules40", "boules60"}


def _jeu_decorable(programme):
    base = str(programme or "")
    for suffixe in ("_couleur", "_nb"):
        if base.endswith(suffixe):
            base = base[: -len(suffixe)]
    return base in JEUX_MOTIF


def serie_depart(commande_id, programme=None):
    """🔢 LE PREMIER NUMÉRO DE SÉRIE d'une commande.

    ⚠️⚠️ CORRIGÉ LE 12/08 : la formule d'avant était `commande_id * 100 + 1`,
    ce qui ne laissait que CENT numéros par commande. Or 500 feuilles font
    3 000 à 6 000 cartons : la commande n°37 (séries 3701 → 6700) écrasait
    la n°38 (à partir de 3801) sur près de 2 900 numéros. Deux clientes
    pouvaient recevoir un carton portant le MÊME numéro de série — de quoi
    fausser une vérification par QR le jour du loto.

    Chaque commande reçoit désormais une TRANCHE de 10 000, largement de
    quoi loger la plus grosse commande courante (500 feuilles × 12 = 6 000).
    Les numéros SE SUIVENT donc d'une rame à l'autre à l'intérieur d'une
    même commande — ce que demandent les clientes qui achètent trois rames
    de 500 feuilles : leurs cartons se suivent sans trou ni doublon.

    ⚠️ POURQUOI 20 000 SUR 50 TRANCHES : les cartons affichent la série sur
    SIX chiffres (« N° %06d »). Au-delà d'un million le numéro serait
    tronqué à l'impression, et deux cartons pourraient sembler identiques.
    La tranche de 20 000 loge la plus grosse commande vue (1 500 feuilles
    × 12 = 18 000 cartons) ; 50 tranches × 20 000 = 1 000 000, soit
    exactement six chiffres. Deux commandes ne peuvent porter le même
    numéro que si elles sont séparées de cinquante — des semaines d'écart.
    """
    return (max(1, int(commande_id)) % 50) * 20000 + 1


def page_depart(commande_id):
    """📄 LE PREMIER NUMÉRO DE PAGE d'une commande.

    Quand une cliente achète plusieurs rames en une fois, elles voyagent
    dans le même panier. Chaque rame repartait de « page 001 » : trois
    rames de 250 feuilles portaient TROIS FOIS les pages 001 à 250,
    impossibles à ranger dans l'ordre (signalé par Maeva le 12/08).
    On additionne donc les feuilles des commandes précédentes du panier.

    ⚠️ Une commande seule, hors panier, démarre à 1 comme avant.
    """
    try:
        cmd = db.get_commande(commande_id)
        pan = (cmd or {}).get("panier_id")
        if not pan:
            return 1
        avant = 0
        for c in db.commandes_du_panier(pan):
            if int(c.get("id") or 0) >= int(commande_id):
                break
            avant += int(c.get("nb_feuilles") or 0)
        return avant + 1
    except Exception:
        return 1


def renumeroter_pages(pdf_buf, depart):
    """📄 Réécrit le numéro de page en haut de chaque feuille.

    ⚠️⚠️ POURQUOI ICI ET PAS DANS LES GÉNÉRATEURS : ils sont 121 à écrire
    « no_page = 1 ». Les modifier tous demanderait 121 déploiements à la
    main — intenable. On repasse donc SUR le PDF fini : un carré blanc
    couvre l'ancien numéro, le nouveau se pose par-dessus. Un seul
    fichier à déployer, et les 144 jeux en profitent d'un coup.
    """
    depart = max(1, int(depart))
    if depart <= 1:
        pdf_buf.seek(0)
        return pdf_buf
    import io as _io3
    try:
        from pypdf import PdfWriter as _W, PdfReader as _R
    except ImportError:
        from PyPDF2 import PdfWriter as _W, PdfReader as _R
    from reportlab.pdfgen import canvas as _cv
    from reportlab.lib.pagesizes import A4 as _A4
    from reportlab.lib import colors as _co
    from reportlab.lib.units import mm as _mm
    pdf_buf.seek(0)
    lu = _R(pdf_buf)
    W, H = _A4
    tampon = _io3.BytesIO()
    c = _cv.Canvas(tampon, pagesize=_A4)
    for i in range(len(lu.pages)):
        # on efface l'ancien numéro, puis on écrit le nouveau
        c.setFillColor(_co.white)
        c.rect(W / 2 - 12 * _mm, H - 9.5 * _mm, 24 * _mm, 5.0 * _mm, stroke=0, fill=1)
        c.setFillColor(_co.Color(0.72, 0.72, 0.72))
        c.setFont("Helvetica", 5.4)
        c.drawCentredString(W / 2, H - 7.2 * _mm, "%03d" % (depart + i))
        c.showPage()
    c.save()
    tampon.seek(0)
    couche = _R(tampon)
    sortie = _W()
    for i, page in enumerate(lu.pages):
        try:
            page.merge_page(couche.pages[i])
        except Exception:
            pass
        sortie.add_page(page)
    buf = _io3.BytesIO()
    sortie.write(buf)
    buf.seek(0)
    return buf


def page_depart(commande_id):
    """📄 LE PREMIER NUMÉRO DE PAGE d'une commande.

    Quand une cliente achète plusieurs rames en une fois, elles voyagent
    dans le même panier. Chaque rame repartait de « page 001 » : trois
    rames de 250 feuilles portaient TROIS FOIS les pages 001 à 250,
    impossibles à ranger dans l'ordre (signalé par Maeva le 12/08).
    On additionne donc les feuilles des commandes précédentes du panier.

    ⚠️ Une commande seule, hors panier, démarre à 1 comme avant.
    """
    try:
        cmd = db.get_commande(commande_id)
        pan = (cmd or {}).get("panier_id")
        if not pan:
            return 1
        avant = 0
        for c in db.commandes_du_panier(pan):
            if int(c.get("id") or 0) >= int(commande_id):
                break
            avant += int(c.get("nb_feuilles") or 0)
        return avant + 1
    except Exception:
        return 1


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
    # 📄 LE NUMÉRO DE PAGE DE DÉPART. Les générateurs qui ne connaissent
    # pas encore « page_start » l'ignorent sans broncher (voir _fabriquer).
    _pdep = 1
    try:
        _pdep = max(1, int((perso or {}).get("page_start") or 1))
    except Exception:
        _pdep = 1
    if _pdep > 1:
        kwargs["page_start"] = _pdep
    # 🖼️ motif en filigrane : seuls les jeux de la liste officielle décorent
    _motif_choisi = str((perso or {}).get("motif") or "").strip().lower()
    if _motif_choisi and _jeu_decorable(programme):
        kwargs["motif"] = _motif_choisi

    # ⚠️⚠️ LES GROSSES COMMANDES SE FABRIQUENT EN PLUSIEURS FOURNÉES.
    # Chaque générateur plafonne à 10 000 cartons. À 12 cartons la feuille
    # cela ne fait que 833 feuilles — or des clientes commandent 3 rames de
    # 500, soit 1 500 feuilles. Elles auraient reçu un paquet incomplet
    # SANS LE SAVOIR (découvert le 12/08).
    # On découpe donc en fournées de 9 000 cartons, et on recolle les PDF.
    # Les séries continuent d'une fournée à l'autre : les numéros SE
    # SUIVENT, comme les clientes le demandent.
    # 🛟 tous les générateurs ne connaissent pas encore « page_start » :
    # on retente sans, plutôt que de laisser tomber la commande.
    def _fabriquer(k):
        try:
            return jeu["generer"](**k)
        except TypeError:
            return jeu["generer"](**{x: y for x, y in k.items() if x != "page_start"})

    PLAFOND = 9000
    demande = max(1, int(nb_cartes))
    if demande <= PLAFOND:
        return _fabriquer(kwargs)

    morceaux = []
    debut = max(1, int(serie_start))
    reste = demande
    while reste > 0:
        lot = min(PLAFOND, reste)
        k = dict(kwargs)
        k[jeu["kwarg_nb"]] = lot
        k["serie_start"] = debut
        # les pages continuent aussi d'une fournée à l'autre
        _par_f = max(1, int(CARTES_PAR_FEUILLE.get(programme, 1)))
        k["page_start"] = _pdep + (demande - reste) // _par_f
        morceaux.append(_fabriquer(k).read())
        debut += lot
        reste -= lot
    import io as _io2
    try:
        from pypdf import PdfWriter as _W, PdfReader as _R
    except ImportError:
        from PyPDF2 import PdfWriter as _W, PdfReader as _R
    sortie = _W()
    for m in morceaux:
        for page in _R(_io2.BytesIO(m)).pages:
            sortie.add_page(page)
    buf = _io2.BytesIO()
    sortie.write(buf)
    buf.seek(0)
    return buf


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
        try:
            db._index_commandes()   # ⚡ la base retrouve vite les dernieres commandes
        except Exception:
            pass
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
            infos += "  \u00b7  🔐 actif le %s" % perso["date_tournoi"]
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
    # 🛟 l'événement arrive parfois en TEXTE (carton générique, événement
    # inconnu) : on ne plante plus, on affiche simplement ce qu'on a.
    if isinstance(ev, dict):
        nom_ev = ev.get("nom") or evenement_id or "—"
    else:
        nom_ev = (ev if isinstance(ev, str) and ev.strip() else None) or evenement_id or "—"
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
  <!-- 🎱 LA PORTE DU CALLER (sceau Maeva 02/08) : chaque QR de carton devient
       un chemin vers notre application de tirage, en ligne ET hors-ligne. -->
  <div style="background:#1e293b;border-radius:14px;padding:18px;margin-top:16px">
    <div style="font-size:.95rem;font-weight:700;margin-bottom:4px">🎱 Envie d'animer votre propre loto\u00a0?</div>
    <div style="font-size:.85rem;color:#94a3b8;line-height:1.6">Le tirage des boules MANAPRINT, gratuit, dans votre t\u00e9l\u00e9phone.</div>
    <a href="/caller" style="display:block;margin-top:12px;padding:14px;border-radius:10px;background:#38bdf8;color:#0b1120;
       font-weight:800;text-align:center;text-decoration:none">📡 Ouvrir le CALLER (avec internet)</a>
    <a href="/caller-local" style="display:block;margin-top:8px;padding:14px;border-radius:10px;background:#22c55e;color:#0b1120;
       font-weight:800;text-align:center;text-decoration:none">📴 Ouvrir le CALLER HORS-LIGNE (sans r\u00e9seau)</a>
    <a href="/" style="display:block;margin-top:8px;padding:12px;border-radius:10px;border:1px solid #475569;color:#e2e8f0;
       font-weight:700;text-align:center;text-decoration:none;font-size:.9rem">🛒 Commander mes cartons</a>
  </div>
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
    """🔁 PORTE TOURNANTE (sceau Maeva 01/08, « résous-le définitivement ») :
    l'adresse historique renvoie vers l'adresse du jour, qui porte l'empreinte
    de la version. Aucun cache au monde ne peut resservir une vieille copie
    sur une adresse qu'il n'a jamais vue."""
    if request.args.get("v") == _VERSION_EMPREINTE:
        return _rendre_caller(evenement_id)
    rep = redirect(f"{request.path}?v={_VERSION_EMPREINTE}", code=302)
    rep.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return rep


def _rendre_caller(evenement_id=None):
    resp = make_response(render_template("caller.html", tampon=TAMPON_VERSION))
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    return resp


@app.route("/voix-caller.mp3")
def voix_caller_mp3():
    """La bande audio des annonces du CALLER (1 a 90) — un vrai fichier
    audio sort sur les enceintes Bluetooth (JBL...), contrairement a la
    synthese vocale du telephone qui reste parfois muette dessus."""
    chemin = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generators", "voix_caller.mp3")
    return send_file(chemin, mimetype="audio/mpeg", max_age=86400)


@app.route("/kikiri/<int:n>.mp3")
def kikiri_mp3(n):
    """🎲🎙️ LA VOIX DE TATIE MAEVA pour les dés (kikiri), enregistrée le 05/08.
    Un vrai fichier audio sort sur les enceintes Bluetooth (JBL), là où la
    synthèse du téléphone reste parfois muette."""
    if n < 1 or n > 9:
        return ("", 404)
    dossier = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "generators", "kikiri")
    chemin = os.path.join(dossier, "kikiri-%d.mp3" % n)
    if not os.path.exists(chemin):
        # 🛟 ANTI-PANNE : le navigateur ajoute parfois « (1) » au nom d'un
        # fichier téléchargé deux fois (vécu le 05/08 avec kikiri-3).
        # On accepte donc « kikiri-3 (1).mp3 » et compagnie.
        try:
            import glob as _glob
            trouves = sorted(_glob.glob(os.path.join(dossier, "kikiri-%d*.mp3" % n)))
            chemin = trouves[0] if trouves else chemin
        except Exception:
            pass
    if not os.path.exists(chemin):
        return ("", 404)
    return send_file(chemin, mimetype="audio/mpeg", max_age=86400)


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
    "sun_casino": (1, 24),
    "p6_casino": (1, 75),
    "pow": (1, 27),
    "pow9": (1, 27),
    "pow_casino": (1, 27),
    "poe_parau": (1, 75),
    "poe": (45, 90),
    "bng": (1, 60),
    "hakari": (1, 75),
    "henua_enana": (1, 75),
    "tiare": (50, 90),
    "tuamotu": (1, 75),
    "societe": (1, 75),
    "australes": (1, 75),
    "gambier": (1, 75),
    "parata": (1, 90),
    "katiu": (1, 75),
    "ok": (1, 75),
    "feu": (1, 75),
    "vision": (1, 75),
    "taptap": (1, 90),
    "joie": (1, 75),
    "caller": (1, 75),
    "valider": (31, 75),
    "chance": (1, 90),
    "opoa": (1, 75),
    "francs": (46, 90),
    "francs500": (1, 75),
    "dollar1": (1, 75),
    "francs1000": (1, 90),
    "francs5000": (1, 65),
    "tesla": (1, 60),
    "salute": (1, 75),
    "salute_smo": (1, 75),
    "pietra": (1, 75),
    "pietra_smo": (1, 75),
    "triple_bo90": (1, 90),
    "triple_bg90": (1, 90),
    "triple_bn90": (1, 90),
    "triple_bi90": (1, 90),
    "triple_bg75": (1, 75),
    "triple_bn75": (1, 75),
    "triple_bi75": (1, 75),
    "win": (1, 45),
    "win_casino": (1, 45),
    "rubis90": (1, 90),
    "rubis75": (1, 75),
    "sicilio": (1, 90),
    "sicilio_smo": (1, 90),
    "avinda": (1, 75),
    "avinda_myst": (1, 75),
    "avinda_fort": (1, 75),
    "ohana75_8b_myst": (1, 75),
    "ohana75_10b_myst": (1, 75),
    "losange": (1, 75),
    "italia": (1, 75),
    "trio75": (1, 75),
    "trio90": (1, 90),
    "italia_esc": (1, 75),
    "italia_villes": (1, 75),
    "vai": (61, 90),
    "wow4": (30, 60),
    "maia": (30, 59),
    "corsica": (1, 80),
    "bno": (1, 75),
    "bno_casino": (1, 75),
    "ngo": (31, 75),
    "ngo_casino": (31, 75),
    "diamant": (1, 75),
    "rui": (30, 59),
    "tureia": (1, 75),
    "tureia_atoll": (1, 75),
    "vanille": (30, 75),
    "spacex": (1, 90),
    "champagne": (1, 75),
    "fan90": (1, 90),
    "oaoa": (16, 75),
    "lagoon": (1, 50),
    "bubulle": (1, 75),
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
    "ino": (16, 75),
    "tahaa": (1, 75),
    "tahaa90": (1, 90),
    "baam": (31, 75),
    "papeari": (1, 75),
    "boules60": (1, 60),
    "ahuru": (1, 75),
    "tchin": (1, 30),
    "ing": (16, 60),
    "ing_casino": (16, 60),
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
    "bin6": (1, 36),
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
    "ohana20b_smo": (1, 75),
    "ohana20b_myst": (1, 75),
    "ohana75_8b": (1, 75),
    "ohana75_8b_smo": (1, 75),
}


# Jeux à colonnes NON contiguës : liste explicite des boules valides
# 🅰️ LES LETTRES SONT DES BOULES (décision Maeva 30/07 : « les boules de
# lettre seront tirées comme les boules de chiffres normales — on tire le A,
# on tire le 1 ») : codes 101=A … 112=L, mêlés au sac, tirés par le même
# moteur, journalisés pareil. Le caller affiche/chante la lettre.
_LETTRE_CODES = {100 + i + 1: l for i, l in enumerate("ABCDEFGHIJKL")}
# 💰 LES MONTANTS SONT DES BOULES (sceau Maeva 30/07, 19 montants — imprimés aux
# coupes ils ne promettent rien, seul le tirage public journalisé attribue) :
_MONTANT_CODES = {200 + i + 1: mv for i, mv in enumerate(avinda.MONTANTS)}
# 💰 LES PIONS DE VALEUR AU TIRAGE (sceau Maeva 01/08) : 6 boules de plus dans
# les 3 sacs CASINO — elles ne cochent aucun numéro, elles se gagnent.
_PIONS_CALLER = [201, 202, 203, 204, 205, 206]   # 5 · 10 · 15 · 20 · 50 · 100 F

_JOKER_CODE = 300   # 🃏 LA BOULE JOKER — EN RÉSERVE (décision Maeva 30/07 :
#     « pour le lancement pas le joker, après les résultats du marché ») ;
#     pour la réveiller : remettre "p6_casino" au sac ci-dessous avec [_JOKER_CODE],
#     et rallumer _JOKER_ACTIF dans p6_marathon.py + les entrées des 2 callers.

_BOULES_CALLER = {
    # \u2b50 CORSICA : ses numeros vont de 1 a 80
    "corsica": [n for n in range(1, 81)],
    # 🍌 MAIA : ses numeros vont de 30 a 59 seulement
    "maia": [n for n in range(30, 60)],
    # 🟢 BNG : ses lettres sautent des quinzaines entieres
    #   B 1-15  ·  N 31-45  ·  G 46-60  = 45 boules, pas 60
    "bng": [n for n in range(1, 16)] + [n for n in range(31, 46)] + [n for n in range(46, 61)],
    "avinda_fort": list(range(1, 76)) + sorted(_MONTANT_CODES),          # 94 boules 🍷💰
    "ohana75_8b_myst": [n for n in range(1, 31)] + [n for n in range(46, 76)] + sorted(_MONTANT_CODES),  # 79 💰
    "ohana75_10b_myst": list(range(1, 76)) + sorted(_MONTANT_CODES),     # 94 💰
    "ohana20b_myst": list(range(1, 76)) + sorted(_MONTANT_CODES),        # 94 💰
    "avinda_myst": list(range(1, 76)) + sorted(_LETTRE_CODES),   # 87 boules 🍷🅰️
    "bno": [n for n in range(1, 16)] + [n for n in range(31, 46)] + [n for n in range(61, 76)],
    "bno_casino": [n for n in range(1, 16)] + [n for n in range(31, 46)] + [n for n in range(61, 76)] + _PIONS_CALLER,
    "ing_casino": [n for n in range(16, 61)] + _PIONS_CALLER,
    "ngo_casino": [n for n in range(31, 76)] + _PIONS_CALLER,
    "tureia": [n for n in range(1, 31)] + [n for n in range(46, 76)],
    "tureia_atoll": [n for n in range(1, 31)] + [n for n in range(46, 76)],  # colonne 31-45 morte
    "fan90": [n for n in range(1, 11)] + [n for n in range(20, 91)],   # sans le 11 à 19
    "oaoa": [n for n in range(16, 31)] + [n for n in range(61, 76)],   # O 16-30 et A 61-75
    "cerf_volant": [n for n in range(1, 31)] + [n for n in range(46, 76)],  # sans le 31-45
    "huahine": [n for n in range(1, 16)] + [n for n in range(46, 61)] + [n for n in range(76, 91)],  # 3 familles : 1-15, 46-60, 76-90
    "bgo": [n for n in range(1, 16)] + [n for n in range(46, 76)],  # B 1-15 · G 46-60 · O 61-75
    "igo": [n for n in range(16, 31)] + [n for n in range(46, 76)],  # I 16-30 · G 46-60 · O 61-75
    "moon": [n for n in range(1, 31)] + [n for n in range(46, 76)],  # M·O·O·N — le 31-45 n'existe pas
    "ino8": [n for n in range(16, 46)] + [n for n in range(61, 76)],  # I 16-30 · N 31-45 · O 61-75
    "ino": [n for n in range(16, 46)] + [n for n in range(61, 76)],   # INO 5 boules — mêmes zones
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
    "ok": [n for n in range(1, 16)] + [n for n in range(31, 76)],       # OK — le 16-30 n'existe pas sur les billets
    "vision": [n for n in range(1, 31)] + [n for n in range(46, 76)],   # VISION — le 31-45 n'existe pas
    "taptap": [n for n in range(1, 16)] + [n for n in range(46, 91)],   # TAP TAP — le 16-45 n'existe pas
    "joie": [n for n in range(16, 31)] + [n for n in range(46, 76)],    # JOIE — le 1-15 et le 31-45 n'existent pas
    "caller": [n for n in range(1, 16)] + [n for n in range(46, 76)],   # CALLER — le 16-45 n'existe pas
    "chance": [n for n in range(1, 16)] + [n for n in range(31, 46)] + [n for n in range(76, 91)],  # CHANCE — trèfles 1-15 · 31-45 · 76-90
    "opoa": [n for n in range(1, 16)] + [n for n in range(31, 76)],  # OPOA — le 16-30 et le 76-90 n'existent pas
    "tesla": [n for n in range(1, 31)] + [n for n in range(46, 61)],  # TESLA — la voiture roule sur 1-30 et 46-60
    "salute": [n for n in range(1, 31)] + [n for n in range(46, 76)],  # SALUTE — le X couvre 1-30 et 46-75
    "pietra": [n for n in range(1, 31)] + [n for n in range(46, 76)],  # PIETRA — la couronne couvre 1-30 et 46-75
    "ohana75_8b": [n for n in range(1, 31)] + [n for n in range(46, 76)],  # OHANA 75 · 8 boules — le 31-45 n'existe pas
    "ohana75_8b_smo": [n for n in range(1, 31)] + [n for n in range(46, 76)],  # son jumeau SMORFIA — mêmes boules
    "triple_bo90": [n for n in range(1, 16)] + [n for n in range(61, 91)],  # TRIPLE BO90 — les 3 cases couvrent 1-15 et 61-90
    "triple_bg90": [n for n in range(1, 16)] + [n for n in range(46, 61)] + [n for n in range(76, 91)],  # TRIPLE BG90 — B, G et 90
    "triple_bn90": [n for n in range(1, 16)] + [n for n in range(31, 46)] + [n for n in range(76, 91)],  # TRIPLE BN90 — B, N et 90
    "triple_bi90": [n for n in range(1, 31)] + [n for n in range(76, 91)],  # TRIPLE BI90 — B, I et 90
    "triple_bg75": [n for n in range(1, 16)] + [n for n in range(46, 76)],  # TRIPLE BG75 — B, G et 75
    "triple_bn75": [n for n in range(1, 16)] + [n for n in range(31, 46)] + [n for n in range(61, 76)],  # TRIPLE BN75 — B, N et 75
    "triple_bi75": [n for n in range(1, 16)] + [n for n in range(16, 31)] + [n for n in range(61, 76)],  # TRIPLE BI75 — B, I et 75
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
                          if n > 100   # les lettres ne sont jamais cochées d'office
                          or not (n % 2 == reste or (n % 10) in finalites)]

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


_MYSTERE_JEUX = set()   # 🔮 éteint (Maeva 30/07 : les lettres-boules remplacent la révélation)   # 🔮 les jeux au verre mystère (vision Maeva 29/07)
# 🔮 Les colonnes du mystère et leurs plages (sceau Maeva 29/07 : « BIO ») —
# règle de colonne : un mystère dans le I ne peut valoir qu'un numéro du I.
_MYSTERE_COLONNES = {"avinda_myst": (("B", 1, 15), ("I", 16, 30), ("O", 61, 75))}


# ══ 📴 FORMULE HORS-LIGNE (demande clients, 30/07) ═══════════════════
# Deux formules du CALLER : ① /caller — tirage au SERVEUR, journal de preuve
# horodaté chez MANAPRINT (recommandée pour les tournois à cagnotte) ;
# ② /caller-local — la page s'installe dans l'appareil (service worker) et
# fonctionne SANS INTERNET : sac, tirage (hasard crypto du navigateur), voix
# et journal vivent localement, journal exportable en CSV en fin de partie.

_SW_CALLER_LOCAL = """
// 📴→🔄 v2 (sceau Maeva 30/07) : RÉSEAU D'ABORD quand il y a internet (les
// mises à jour arrivent toutes seules), CACHE EN SECOURS quand il n'y en a
// pas (la promesse hors-ligne tient) ; les vieux caches sont balayés.
const CACHE = 'mpcl-v4';   // ⚡ v4 : balaye le gardien cassé de la v3
// ⚠️⚠️ 13/08 : « /caller-local » A ÉTÉ RETIRÉ DE CETTE LISTE. Cette adresse
// répond par une REDIRECTION (302) vers /crieur-local, or `addAll` refuse
// les redirections — et comme il met tout en réserve d'un seul coup, UNE
// SEULE page fautive faisait échouer TOUTE l'installation. C'était la cause
// du « mode hors-ligne non installé » que Maeva voyait sur sa vraie
// plateforme. On ne garde que les adresses qui répondent vraiment 200.
const PAGES = ['/crieur-local', '/caller-local/manifest.json', '/caller-local/icone.svg'];
const BANDE = '/voix-caller.mp3';   // 🎙️ la voix enregistrée, gardée pour les salles sans réseau
// 🎲🎙️ les 9 mots du kikiri dits par Tatie Maeva : mis en réserve eux aussi,
// pour que les dés parlent dans les vallées sans réseau.
const KIKIRI = [1,2,3,4,5,6,7,8,9].map(n => '/kikiri/' + n + '.mp3');
self.addEventListener('install', e => {
  // ⚡ 13/08 : CHAQUE page est mise en réserve SÉPARÉMENT. Avec `addAll`,
  // une seule adresse en échec faisait tout tomber ; ici, si l'une manque,
  // les autres passent quand même et le hors-ligne s'installe.
  e.waitUntil(
    caches.open(CACHE)
      .then(c => Promise.all(PAGES.map(u => c.add(u).catch(() => null)))
        .then(() => c.add(BANDE).catch(() => null))
        .then(() => Promise.all(KIKIRI.map(u => c.add(u).catch(() => null)))))
      .then(() => self.skipWaiting())
  );
});
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(noms => Promise.all(noms.filter(n => n !== CACHE).map(n => caches.delete(n))))
      .then(() => self.clients.claim())
  );
});
self.addEventListener('fetch', e => {
  const u = new URL(e.request.url);
  // 🎙️ la bande ne change jamais : cache d'abord, et on la garde au passage
  if (u.pathname === BANDE) {
    e.respondWith(
      caches.match(e.request, { ignoreSearch: true }).then(r => r || fetch(e.request).then(rep => {
        const copie = rep.clone();
        caches.open(CACHE).then(c => c.put(e.request, copie));
        return rep;
      }))
    );
    return;
  }
  // /caller-local redirige vers /crieur-local : on le laisse passer au
  // réseau, mais on répond depuis la réserve s'il n'y a plus d'internet.
  if (!PAGES.includes(u.pathname) && u.pathname !== '/caller-local') return;
  e.respondWith(
    fetch(e.request).then(rep => {
      const copie = rep.clone();
      caches.open(CACHE).then(c => c.put(e.request, copie));
      return rep;
    }).catch(() => caches.match(e.request) || caches.match('/crieur-local'))
  );
});
"""

_ICONE_CALLER_LOCAL = """<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'>
<rect width='100' height='100' rx='22' fill='#0b1120'/>
<circle cx='50' cy='50' r='30' fill='#38bdf8'/>
<text x='50' y='62' font-size='34' text-anchor='middle' font-family='sans-serif'
      font-weight='bold' fill='#06263a'>90</text></svg>"""


# ══ 🏷️ TAMPON DE VERSION AUTOMATIQUE (sceau Maeva 31/07) ═══════════════
# Calculé au démarrage à partir des fichiers EUX-MÊMES : plus jamais besoin
# d'écrire une date à la main, et on sait toujours quelle version tourne.
def _empreinte_version():
    import hashlib
    h = hashlib.md5()
    for nom in ("app.py", "templates/caller.html", "templates/caller_local.html"):
        try:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), nom), "rb") as f:
                h.update(f.read())
        except Exception:
            pass
    return h.hexdigest()[:6]


_VERSION_EMPREINTE = _empreinte_version()
import datetime as _dt
_VERSION_DEPART = _dt.datetime.now().strftime("%d/%m %H:%M")
TAMPON_VERSION = f"{_VERSION_EMPREINTE} \u00b7 {_VERSION_DEPART}"


@app.route("/version")
def page_version():
    """🏷️ Carte d'identité de la version EN LIGNE (lisible par tous)."""
    rep = make_response(
        "MANAPRINT — version en ligne\n"
        f"empreinte : {_VERSION_EMPREINTE}\n"
        f"serveur démarré : {_VERSION_DEPART}\n"
        f"jeux au registre : {len(REGISTRE_JEUX) // 4}\n",
        200,
    )
    rep.headers["Content-Type"] = "text/plain; charset=utf-8"
    rep.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return rep


@app.route("/sw-manaprint.js")
def sw_racine():
    """🛡️ Le gardien hors-ligne SERVI À LA RACINE (sceau Maeva 31/07) : depuis
    un sous-dossier il n'avait pas le droit de veiller sur la page elle-même
    — c'était la cause du « mode hors-ligne non installé »."""
    rep = Response(_SW_CALLER_LOCAL, mimetype="application/javascript")
    rep.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    rep.headers["Service-Worker-Allowed"] = "/"
    return rep


@app.route("/crieur")
def crieur_neuf():
    """🆕 PORTE NEUVE (sceau Maeva 31/07) : même page que /caller, mais à une
    adresse SANS PASSÉ — aucun cache, aucun gardien ne peut servir du vieux."""
    rep = make_response(render_template("caller.html", tampon=TAMPON_VERSION))
    rep.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    rep.headers["Pragma"] = "no-cache"
    return rep


@app.route("/crieur-local")
def crieur_local_neuf():
    """🆕 PORTE NEUVE de la formule hors-ligne."""
    rep = make_response(render_template("caller_local.html", tampon=TAMPON_VERSION))
    rep.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    rep.headers["Pragma"] = "no-cache"
    return rep


@app.route("/caller-local")
def caller_local():
    """🔁 PORTE TOURNANTE de la formule hors-ligne (même principe)."""
    if request.args.get("v") == _VERSION_EMPREINTE:
        return _rendre_caller_local()
    rep = redirect(f"{request.path}?v={_VERSION_EMPREINTE}", code=302)
    rep.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return rep


def _rendre_caller_local():
    rep = make_response(render_template("caller_local.html", tampon=TAMPON_VERSION))
    rep.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    rep.headers["Pragma"] = "no-cache"
    return rep


@app.route("/caller-local/sw.js")
def caller_local_sw():
    rep = Response(_SW_CALLER_LOCAL, mimetype="application/javascript")
    rep.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return rep


@app.route("/caller-local/manifest.json")
def caller_local_manifest():
    return jsonify({
        "name": "MANAPRINT CALLER hors-ligne",
        "short_name": "CALLER 📴",
        "start_url": "/caller-local",
        "display": "standalone",
        "background_color": "#0b1120",
        "theme_color": "#0b1120",
        "icons": [{"src": "/caller-local/icone.svg", "sizes": "any", "type": "image/svg+xml"}],
    })


@app.route("/caller-local/icone.svg")
def caller_local_icone():
    return Response(_ICONE_CALLER_LOCAL, mimetype="image/svg+xml")


@app.route("/api/caller/mystere", methods=["POST"])
def api_caller_mystere():
    """🔮 LA RÉVÉLATION DU MYSTÈRE (vision Maeva) : l'hôte choisit le MOMENT,
    le hasard choisit le NUMÉRO. La boule-mystère est une boule NORMALE tirée
    du sac restant par le même moteur — journalisée, horodatée — et elle
    remplit TOUS les verres « ? » de la salle au même instant.
    Garde-fou : déverrouillée seulement après le premier quart du sac."""
    d = request.get_json(force=True, silent=True) or {}
    jeu = str(d.get("jeu") or "")
    partie_id = (d.get("partie_id") or "").strip()
    if jeu not in _MYSTERE_JEUX:
        return jsonify({"ok": False, "message": "Ce jeu n'a pas de verre myst\u00e8re."}), 400
    if not partie_id:
        return jsonify({"ok": False, "message": "Tirez d'abord quelques boules \u2014 le myst\u00e8re doit m\u00fbrir."}), 400
    bmin, bmax = _PLAGES_CALLER[jeu]
    univers = _BOULES_CALLER.get(jeu) or list(range(bmin, bmax + 1))
    tirees = db.boules_tirees(partie_id)
    seuil = max(1, len(univers) // 4)
    if len(tirees) < seuil:
        return jsonify({"ok": False, "message": f"Le myst\u00e8re m\u00fbrit encore \u2014 "
                        f"d\u00e9verrouillage \u00e0 la {seuil}e boule ({len(tirees)}/{seuil})."}), 403
    # 🔮 TRIPLE RÉVÉLATION : une boule-mystère PAR COLONNE, chacune dans sa plage
    mysteres = {}
    for lettre, a, b in _MYSTERE_COLONNES[jeu]:
        boule = db.tirer_boule(partie_id, bmin, bmax, list(range(a, b + 1)))
        if boule is None:   # colonne épuisée (rarissime) : on le dit honnêtement
            mysteres[lettre] = None
            continue
        mysteres[lettre] = boule
        print(f"[MYSTERE] partie {partie_id} \u00b7 jeu {jeu} \u00b7 colonne {lettre} "
              f"\u2192 boule-myst\u00e8re {boule}")
    if not any(v for v in mysteres.values()):
        return jsonify({"ok": False, "message": "Toutes les boules sont sorties."}), 409
    return jsonify({"ok": True, "partie_id": partie_id, "mysteres": mysteres,
                    "tirees": db.boules_tirees(partie_id)})


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
    # 🔒 un partenaire connecté ne voit pas les jeux qui lui sont réservés
    _slug = session.get("partenaire_slug") or ""
    _interdits = JEUX_INTERDITS.get(_slug, ())
    return jsonify({"ok": True, "jeux": [
        {"id": jid, "nom": j["nom"], "emoji": j["emoji"],
         "cartes_par_feuille": j["cartes_par_feuille"], "couleur": j["couleur"]}
        for jid, j in REGISTRE_JEUX.items()
        if "_p15" not in jid                      # 🌙 PREMIUM en veilleuse
        and _base_jeu(jid) not in _interdits      # 🔒 réservés à leur enseigne
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
    try:
        os.nice(10)      # le prechauffage passe apres les visiteurs
    except Exception:
        pass
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
    # 🌙 PREMIUM en veilleuse : seule la gamme ÉCO est en vente pour l'instant
    if "_p15" in str(programme):
        return (jsonify({"ok": False, "message": "La gamme PREMIUM est momentanément en pause — choisis la version ÉCO du jeu."}), 400), None
    couleur = REGISTRE_JEUX.get(programme, {}).get("couleur", True)
    nb_feuilles = int(data.get("nb_feuilles", 25))
    # 📦 Vente par PAQUETS DE 25 feuilles (25, 50, 75… jusqu'à 250)
    if nb_feuilles < 25 or nb_feuilles > 500 or nb_feuilles % 25 != 0:  # 1 à 20 paquets de 25 (27/07)
        return (jsonify({"ok": False, "message": "Les feuilles se commandent par paquets de 25 (25, 50, 75… jusqu'à 250)."}), 400), None

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
        "motif": (data.get("motif", "") or "").strip().lower(),
        # 🖨️ MODE BOUTIQUE RAPIDE : cartons sans microtexte (QR conservé),
        # pour l'impression directe par clé USB sans pause.
        "impression_rapide": bool(data.get("impression_rapide")),
        # 🎨 l'offre choisie en couleur : "pdf" (fichier seul) ou "impression"
        "offre": ("pdf" if (couleur and (data.get("offre") or "").strip().lower() == "pdf")
                  else ("impression" if couleur else "")),
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
    # 🖼️💰 SUPPLÉMENT MOTIF (décision Maeva) : chez 2KEA & Associé, un PDF
    # généré avec motif passe à ÉCO 8/12 F · PREMIUM 12/16 F (= tarif + 2 F).
    # Facturé UNIQUEMENT si le jeu sait décorer (inspection de signature) et
    # seulement sur le tarif standard — les prix fixés par un partenaire ou
    # le tarif PDF seul (1,5 F) restent souverains et inchangés.
    _motif_cmd = str(data.get("motif") or "").strip().lower()
    if _motif_cmd and _jeu_decorable(programme):
        if prix_special is None:
            # 🖼️💰 chez 2KEA & Associé : +2 F (ÉCO 8/12 · PREMIUM 12/16)
            _gamme_m = db._gamme_du_programme(programme)
            prix_special = db.prix_feuille_profil(session["acces"], couleur, _gamme_m) + 2
        else:
            # 🖼️💰 chez les partenaires : l'option motif vaut +0,5 F/feuille
            # (sur le PDF seul 1,5 F -> 2 F, ou sur leurs prix libres)
            prix_special = float(prix_special) + 0.5
    # 💰 NOUVEAUX JEUX (22-23/07) : 250 F N&B / 300 F Couleur les 25 feuilles.
    # Tarif standard 2KEA seulement — prix partenaires et PDF seul
    # international restent souverains.
    # 💰 GRILLE DU 05/08 : la couleur reste au tarif de base (250 F les 25) ;
    # en noir & blanc, seuls les jeux de TARIF_NB_150 gardent 150 F —
    # tous les autres passent à 185 F les 25 feuilles.
    # 💵 LES JEUX À BILLETS : 250 F les 25, en N&B comme en couleur.
    # ⚠️ Ce test vient AVANT celui du noir & blanc, sinon ils retomberaient
    # à 185 F. Les prix partenaires et l'international restent souverains.
    if (prix_special is None
            and session.get("acces") != "international"
            and db._gamme_du_programme(programme) == "eco"
            and _base_jeu(programme) in TARIF_BILLETS_250):
        prix_special = PRIX_BILLETS_COULEUR if couleur else PRIX_BILLETS
    if (prix_special is None and not couleur
            and session.get("acces") != "international"
            and db._gamme_du_programme(programme) == "eco"
            and _base_jeu(programme) not in TARIF_NB_150):
        prix_special = PRIX_NB_AUTRES
    # 🎨 OFFRE « PDF SEUL » EN COULEUR : 3,5 F la feuille. Le tarif partenaire,
    # le PDF seul international et le supplément motif restent souverains.
    offre = (data.get("offre") or "").strip().lower()
    if (couleur and offre == "pdf" and prix_special is None
            and session.get("acces") != "international"):
        prix_special = PRIX_PDF_SEUL_COULEUR
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


# ── 🏦 VIREMENT — coordonnées bancaires affichées au client ──────────────────
# Le RIB vit dans la variable Railway MANAPRINT_RIB (modifiable sans toucher au
# code) : texte libre, ex. « Banque XXX — 2KEA & Associé — n° 12345 67890 … ».
RIB_VIREMENT = os.environ.get("MANAPRINT_RIB", "").strip()

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


def _mana_demandes():
    """🌺 Combien de CRÉDITS MANA le client veut-il dépenser ?"""
    try:
        d = request.get_json(silent=True) or {}
        return max(0, int(d.get("mana") or 0))
    except Exception:
        return 0


def _session_stripe_panier(panier_id, mana_utilises=0):
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
    # ═══ 🌺 LA RÉDUCTION CRÉDIT MANA ═══
    # 1 CRÉDIT MANA = 50 F de réduction (sceau Maeva 13/08).
    # ⚠️ On passe par un COUPON Stripe plutôt que de rogner les montants
    # des lignes : la facture montre alors clairement la remise, et le
    # client voit ce que sa fidélité lui a fait gagner.
    # ⚠️⚠️ Les crédits ne sont RETIRÉS DU COMPTE qu'ici, à la création de
    # la session — et le nombre est plafonné par ce qu'il possède ET par
    # le total du panier : on ne descend jamais en dessous de zéro franc.
    remise = 0
    ident_mana = ""
    for cmd in cmds:
        if "@" in (cmd.get("identifiant") or ""):
            ident_mana = cmd["identifiant"].strip()
            break
    n_mana = 0
    if mana_utilises and ident_mana:
        compte = db.mana_du_client(ident_mana)
        n_mana = min(int(mana_utilises), int(compte.get("credits") or 0))
        # on ne peut pas rendre le panier gratuit : on garde 1 F minimum
        n_mana = min(n_mana, max(0, (total - 1)) // db.VALEUR_CREDIT_XPF)
        if n_mana > 0:
            remise = n_mana * db.VALEUR_CREDIT_XPF

    kwargs = dict(
        mode="payment",
        line_items=line_items,
        success_url=_base_url() + "/?paiement=succes",
        cancel_url=_base_url() + "/?paiement=annule",
        metadata={"panier_id": str(panier_id)},
    )
    if remise:
        try:
            coupon = stripe.Coupon.create(
                amount_off=remise, currency="xpf", duration="once",
                name=f"{n_mana} CR\u00c9DIT MANA")
            kwargs["discounts"] = [{"coupon": coupon.id}]
            kwargs["metadata"]["mana_utilises"] = str(n_mana)
            kwargs["metadata"]["mana_client"] = ident_mana
        except Exception as e:
            print(f"[MANA] la remise n'a pas pu \u00eatre pos\u00e9e : {e}")
            remise = 0
            n_mana = 0

    s = stripe.checkout.Session.create(**kwargs)
    if n_mana:
        # ⚠️ on retire les crédits MAINTENANT : le client les a engagés.
        # S'il abandonne le paiement, ils sont perdus pour cette session —
        # c'est le prix de la simplicité, et cela évite qu'il dépense deux
        # fois les mêmes crédits en ouvrant deux paiements.
        db.mana_utiliser(ident_mana, n_mana)
        print(f"[MANA] {ident_mana} utilise {n_mana} cr\u00e9dit(s) \u2192 {remise} F de remise")
    db.maj_panier(panier_id, total=max(0, total - remise), stripe_session=s.id)
    return s.url, max(0, total - remise)


@app.route("/api/demande-impression", methods=["POST"])
def demande_impression():
    """🎨🖨️ LA DEMANDE D'IMPRESSION EN COULEUR (décision Maeva du 05/08).
    Le client ne paie RIEN ici : sa commande part en attente et 2KEA répond
    « oui on peut imprimer » ou « non » depuis l'espace de gestion."""
    if "acces" not in session:
        return jsonify({"ok": False, "message": "Accès non autorisé"}), 403
    data = request.get_json(force=True, silent=True) or {}
    data["offre"] = "impression"
    err, res = _valider_creer_commande(data, mode_paiement="demande")
    if err:
        return err
    commande_id, montant = res["commande_id"], res["montant"]
    with db.get_db() as conn:
        conn.execute("UPDATE commandes SET statut = ? WHERE id = ?",
                     (STATUT_DEMANDE, commande_id))
    return jsonify({
        "ok": True, "commande_id": commande_id, "montant": int(montant),
        "mode": "demande",
        "message": ("Demande enregistrée. Nous vérifions si nos machines peuvent "
                    "imprimer en couleur et nous te répondons rapidement. "
                    "Tu ne paieras qu'après notre accord."),
    })


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
        url, total = _session_stripe_panier(panier_id, mana_utilises=_mana_demandes())
        return jsonify({"ok": True, "mode": "stripe", "url": url, "montant": total})
    except Exception as e:
        print(f"[STRIPE ERREUR] commander : {e}")
        return jsonify({"ok": False, "message": "Paiement carte momentanément indisponible. Choisis le paiement en boutique."}), 502


@app.route("/api/panier/checkout", methods=["POST"])
def panier_checkout():
    """🛒 Le panier d'achat : plusieurs jeux, un seul paiement.
    items = liste de commandes (mêmes champs que /api/commander).
    mode_paiement = 'stripe' (carte), 'boutique' (comptoir 2KEA) ou 'virement'."""
    if "acces" not in session:
        return jsonify({"ok": False, "message": "Accès non autorisé"}), 403
    data = request.get_json(force=True, silent=True) or {}
    items = data.get("items") or []
    mode_paiement = data.get("mode_paiement", "stripe")
    if mode_paiement == "manuel":  # compat ancien front : manuel = boutique
        mode_paiement = "boutique"
    if mode_paiement not in ("stripe", "boutique", "virement"):
        return jsonify({"ok": False, "message": "Mode de paiement inconnu."}), 400
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

    if mode_paiement in ("boutique", "virement"):
        rep = {"ok": True, "mode": mode_paiement, "panier_id": panier_id,
               "montant": total, "articles": resume}
        if mode_paiement == "virement":
            rep["rib"] = RIB_VIREMENT
            rep["reference"] = f"MANAPRINT-{panier_id}"
            rep["message"] = (f"Panier enregistré ({len(resume)} article(s), {total} XPF). "
                              f"Fais ton virement avec la référence MANAPRINT-{panier_id} : "
                              "tes PDF seront générés dès réception du virement par 2KEA & Associé.")
        else:
            rep["message"] = (f"Panier enregistré ({len(resume)} article(s), {total} XPF). "
                              "Passe régler en boutique 2KEA & Associé : tes PDF seront générés dès le paiement encaissé.")
        return jsonify(rep)

    if not STRIPE_SECRET_KEY:
        return jsonify({"ok": False,
                        "message": "Le paiement par carte n'est pas encore activé. Choisis le paiement en boutique."}), 400
    try:
        url, total = _session_stripe_panier(panier_id, mana_utilises=_mana_demandes())
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
                    # ═══ 🌺 CRÉDIT MANA ═══
                    # ⚠️⚠️ C'EST LE SEUL ENDROIT OÙ LE COMPTEUR MONTE.
                    # Maeva l'a écrit noir sur blanc : « le compteur ne doit
                    # JAMAIS augmenter au moment où le client clique sur
                    # Commander — il doit augmenter uniquement après
                    # confirmation définitive du paiement par carte ».
                    # Nous sommes ici dans le webhook `checkout.session.completed`
                    # de Stripe : le paiement est confirmé PAYÉ/SUCCEEDED.
                    try:
                        _crediter_mana(cmd)
                    except Exception as e:
                        print(f"[MANA] commande {cmd['id']} : {e}")

    # 💸 REMBOURSEMENT : on annule la progression qu'il avait donnée.
    # « En cas de remboursement ultérieur, le système doit pouvoir annuler
    # la progression ou les crédits générés par cette commande afin
    # d'éviter les abus » (sceau Maeva 13/08).
    if event["type"] in ("charge.refunded", "charge.dispute.created"):
        try:
            obj = event["data"]["object"]
            pan = 0
            try:
                pan = int(obj["metadata"]["panier_id"])
            except Exception:
                pan = 0
            if pan:
                for c in db.commandes_du_panier(pan):
                    if db.mana_annuler(c["id"]):
                        print(f"[MANA] commande {c['id']} rembours\u00e9e \u2014 progression annul\u00e9e")
        except Exception as e:
            print(f"[MANA REMBOURSEMENT] {e}")
    return jsonify({"ok": True})


# ═══ 🌺 CRÉDIT MANA — qui a droit à la progression ? ═══
# 5 JEUX achetés ET PAYÉS EN LIGNE PAR CARTE = 1 CRÉDIT MANA offert.
#
# ⚠️⚠️ NE COMPTENT PAS (liste écrite par Maeva le 13/08) :
#   espèces · virement bancaire · paiement en boutique · commande SMS ·
#   paiement manuel · crédit ou geste commercial · toute autre méthode
#   hors carte bancaire en ligne.
# Ces commandes peuvent être enregistrées dans MANAPRINT, mais elles
# apportent ZÉRO progression MANA.
MANA_MODES_ELIGIBLES = ("stripe",)


def _mana_eligible(cmd):
    """🌺 Cette commande fait-elle progresser le compteur ?"""
    if not cmd:
        return False
    # ① réglée EN LIGNE PAR CARTE — et rien d'autre
    if (cmd.get("mode_paiement") or "") not in MANA_MODES_ELIGIBLES:
        return False
    # ② le paiement est bien confirmé
    if (cmd.get("statut") or "") not in ("payee", "generee", "fabriquee", "envoyee"):
        return False
    # ③ commandée directement sur MANAPRINT — pas une fabrique partenaire
    #    ni un ravitaillement interne
    if (cmd.get("mode_paiement") or "") in ("fabrique_partenaire", "ravitaillement"):
        return False
    # ④ un client identifiable, sinon on ne saurait à qui créditer
    if "@" not in (cmd.get("identifiant") or ""):
        return False
    return True


def _crediter_mana(cmd):
    """🌺 Compte UN JEU au client, et annonce le crédit s'il tombe."""
    if not _mana_eligible(cmd):
        return
    ident = (cmd.get("identifiant") or "").strip()
    prog, gagnes = db.mana_compter(cmd["id"], ident)
    print(f"[MANA] {ident} \u2014 commande {cmd['id']} \u2192 {prog}/{db.PDF_PAR_CREDIT}"
          + (f" \U0001f381 +{gagnes} CR\u00c9DIT MANA" if gagnes else ""))
    if gagnes:
        try:
            envoyer_email_simple(
                ident, "\U0001f338 Vous avez gagn\u00e9 un CR\u00c9DIT MANA !",
                "Ia ora na,\n\n"
                f"F\u00e9licitations ! Vos {db.PDF_PAR_CREDIT} jeux achet\u00e9s vous offrent "
                f"{gagnes} CR\u00c9DIT MANA \U0001f381\n\n"
                "Il vous attend sur votre compte MANAPRINT \u2014 \u00e0 utiliser quand vous voudrez.\n\n"
                "Plus vous utilisez MANAPRINT, plus vos CR\u00c9DITS MANA se cumulent !\n\n"
                "M\u0101uruuru,\nMANAPRINT")
        except Exception as e:
            print(f"[MANA] l'annonce du cr\u00e9dit n'est pas partie : {e}")


@app.route("/api/mana/mon-compte", methods=["GET"])
def api_mana_mon_compte():
    """🌺 Le client consulte sa progression et ses crédits."""
    ident = (session.get("identifiant") or "").strip()
    if not ident:
        return jsonify({"ok": False, "message": "Connectez-vous pour voir vos CR\u00c9DITS MANA."}), 403
    return jsonify({"ok": True, "mana": db.mana_du_client(ident)})


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
        # VENTE DE PDF SEUL, EN COULEUR UNIQUEMENT (sceau Maeva 05/08) :
        # le client emporte le fichier et l'imprime lui-meme, donc le QR de
        # verification n'a plus de sens -> la signature TUKEA prend sa place,
        # et chaque photocopie devient une petite publicite.
        _secs.activer_signature(bool(couleur) and perso.get("offre") == "pdf")
        # 🏠 TIRAGE DE LA MAISON (ravitaillement, fabrique a l'enseigne) :
        # pas de QR — il ne sert qu'aux commandes des clients.
        _secs.activer_sans_qr(cmd.get("mode_paiement") in
                              ("ravitaillement", "fabrique_partenaire"))
    except Exception:
        pass
    try:
        # 📄 les pages continuent d'une rame à l'autre dans le même panier.
        # ⚠️ On écrit dans un NOUVEAU nom, jamais dans `perso` — voir la note
        # du 12/08 plus bas : réaffecter un nom déjà utilisé plus haut dans la
        # même fonction le rend « local » aux yeux de Python et fait échouer
        # tout ce qui le lisait AVANT.
        perso_pages = perso
        try:
            perso_pages = dict(perso or {})
            perso_pages["page_start"] = page_depart(commande_id)
        except Exception:
            perso_pages = perso
        pdf = generer_jeu(programme, nb_cartes, couleur, perso_pages, evenement_id=evenement_id,
                          serie_start=serie_depart(commande_id, programme))
        # ⚠️ 12/08 : PLUS DE RETOUCHE DU PDF ICI. Le numéro de page est
        # désormais passé au générateur (page_start) : le relire pour le
        # réécrire doublait la mémoire et le temps, et tuait les grosses
        # commandes sur Railway.
    finally:
        try:
            _secs.activer_mode_rapide(False)
            _secs.activer_signature(False)
            _secs.activer_sans_qr(False)
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
        # 🐢 06/08 — LA FABRICATION CÈDE LE PAS AU SITE.
        # Fabriquer 250 feuilles occupe le processeur une a deux minutes.
        # Sur un petit serveur, cela etouffait tout : la passerelle de
        # Railway ne recevait plus de reponse et renvoyait « upstream
        # error » a Maeva. On abaisse donc la priorite de CE thread :
        # les visiteurs et l'espace de gestion passent devant, la
        # fabrication prend ce qui reste. Elle dure un peu plus
        # longtemps, mais le site ne s'arrete plus jamais.
        try:
            os.nice(10)
        except Exception:
            pass
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
                # ⚠️ 07/08 : ici la couleur se lit dans la COMMANDE (cmd), pas
                # dans une variable `couleur` — celle-ci n'existe pas dans ce
                # thread. L'erreur etait avalee par le except, et TOUS les
                # reglages tombaient avec elle (la signature ne s'appliquait
                # donc jamais sur ce chemin).
                _secm.activer_signature(bool(cmd["couleur"]) and perso.get("offre") == "pdf")
                # 🏠 TIRAGE DE LA MAISON : pas de QR (il ne sert qu'aux clients)
                _secm.activer_sans_qr(cmd.get("mode_paiement") in
                                      ("ravitaillement", "fabrique_partenaire"))
            except Exception as _e:
                print(f"[DRAPEAUX] non poses : {_e}")
            try:
                # 🎲 chaque commande = son propre point de départ (cartes UNIQUES,
                # mais refabrication à l'identique pour le 📬 Renvoyer)
                # 📄 les pages continuent d'une rame à l'autre dans le même panier.
                # ⚠️⚠️ 12/08 : on écrit dans un NOUVEAU nom (`perso_pages`) et
                # jamais dans `perso`. Réaffecter `perso` ici en faisait une
                # variable LOCALE au thread : Python la déclarait alors
                # inexistante PARTOUT AVANT cette ligne — y compris dans le
                # bloc des drapeaux plus haut — et la fabrication mourait sur
                # « cannot access local variable 'perso' ». Plus aucun PDF ne
                # sortait de l'espace partenaire.
                perso_pages = perso
                try:
                    perso_pages = dict(perso or {})
                    perso_pages["page_start"] = page_depart(commande_id)
                except Exception:
                    perso_pages = perso
                # ⚠️⚠️ 12/08 : ici c'est `cmd["programme"]`, PAS `programme` —
                # cette variable n'existe pas dans ce thread. Le NameError
                # était avalé par le `except` juste en dessous : plus AUCUN
                # PDF ne sortait de l'espace partenaire, en silence.
                # (Même piège qu'en juillet avec `couleur`. Toujours vérifier
                #  qu'une variable existe VRAIMENT dans le thread.)
                pdf = generer_jeu(cmd["programme"], nb_cartes, bool(cmd["couleur"]), perso_pages,
                                  evenement_id=evenement_id,
                                  serie_start=serie_depart(commande_id, cmd["programme"]))
                # ⚠️ 12/08 : plus de retouche du PDF ici non plus — le
                # numéro de page vient du générateur (page_start).
            finally:
                try:
                    _secm.activer_mode_rapide(False)
                    _secm.activer_signature(False)
                    _secm.activer_sans_qr(False)
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
            # 📦 ...sauf le ravitaillement boutique : commande interne 2KEA, pas de facture.
            try:
                if cmd["mode_paiement"] in ("ravitaillement", "fabrique_partenaire"):
                    raise StopIteration("commande interne — pas de facture du dû")
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


# ── 🏭 LE VEILLEUR DES FABRICATIONS (sceau Maeva, 06/08) ──────────────────
# Une fabrication tourne dans un thread. Si le serveur redemarre pendant
# ce temps — un deploiement, une mise en veille de Railway — le thread
# meurt et la commande reste bloquee sur « ⏳ fabrication… » pour toujours.
# Vecu le 06/08 avec deux ravitaillements du jeu 100 FRANCS.
# Ce veilleur repere ces commandes oubliees et relance leur fabrication,
# sans aucun geste de l'administratrice.
_FABRIC_RELANCES = {}          # commande_id -> nombre de relances tentees
DELAI_FABRICATION_FIGEE = 1500  # 25 minutes : au-dela, la fabrication est perdue
MAX_RELANCES = 3


# 🚑 06/08 — GARDE-FOUS D'URGENCE.
# Le veilleur relancait TOUTES les commandes « payee » restees en rade,
# meme vieilles de plusieurs semaines : sur la vraie base cela faisait
# 180 fabrications lancees ENSEMBLE, toutes les 10 minutes. Le serveur
# ne repondait plus a personne et plus aucun PDF ne sortait.
# Desormais : UNE SEULE a la fois, et seulement les commandes RECENTES.
AGE_MAX_RELANCE = 6 * 3600      # au-dela de 6 heures, on ne relance plus
RELANCES_PAR_TOUR = 1           # une seule fabrication relancee par tour


def _fabrications_figees():
    """La (ou les) commande(s) recente(s) dont la fabrication n'a pas abouti.

    On ne remonte pas plus loin que 6 heures : au-dela, la commande est
    trop vieille pour etre relancee toute seule — Tatie la refabriquera
    au 📬 si elle en a besoin. Et on n'en rend qu'UNE a la fois, pour ne
    jamais etouffer le serveur.
    """
    from datetime import datetime as _dtt, timedelta as _td
    maintenant = _dtt.now()
    trop_recent = maintenant - _td(seconds=DELAI_FABRICATION_FIGEE)
    trop_vieux = maintenant - _td(seconds=AGE_MAX_RELANCE)
    figees = []
    for c in db.lister_commandes("payee"):
        try:
            quand = _dtt.fromisoformat(str(c.get("cree_le") or ""))
        except Exception:
            continue
        if not (trop_vieux < quand < trop_recent):
            continue
        if _FABRIC_RELANCES.get(c["id"], 0) >= MAX_RELANCES:
            continue
        figees.append((quand, c))
    figees.sort(key=lambda x: x[0], reverse=True)      # la plus recente d'abord
    return [c for _q, c in figees[:RELANCES_PAR_TOUR]]


# ═══ 📧 LA RELANCE AUTOMATIQUE DES CLIENTS (sceau Maeva 13/08) ═══
# Une commande attend son règlement depuis plusieurs jours ? La plateforme
# écrit au client toute seule pour savoir s'il la maintient.
DELAI_RELANCE = 3 * 24 * 3600     # on attend TROIS JOURS avant d'écrire
DELAI_2E_RELANCE = 7 * 24 * 3600  # une seconde relance au bout d'une semaine
MAX_RELANCES_CLIENT = 2           # ⚠️ jamais plus de DEUX : au-delà on harcèle
_RELANCES_CLIENT = {}             # commande -> nombre de relances envoyées


def _commandes_a_relancer():
    """📧 Les commandes qui attendent leur règlement depuis assez longtemps.

    ⚠️ On ne relance QUE les commandes non payées et pas encore fabriquées.
    Une commande déjà réglée ou déjà partie ne doit jamais recevoir ce
    message — le client s'inquiéterait pour rien.
    """
    from datetime import datetime as _dt, timezone as _tz
    maintenant = _dt.now(_tz.utc)
    sortie = []
    try:
        with db.get_db() as conn:
            lignes = conn.execute(
                "SELECT * FROM commandes WHERE statut IN ('en_attente','nouvelle') "
                "ORDER BY id DESC LIMIT 200").fetchall()
    except Exception:
        return sortie
    for r in lignes:
        c = dict(r)
        cid = int(c.get("id") or 0)
        deja = _RELANCES_CLIENT.get(cid, 0)
        if deja >= MAX_RELANCES_CLIENT:
            continue
        # pas d'email, pas de relance : Tatie appellera au téléphone
        if "@" not in (c.get("identifiant") or ""):
            continue
        try:
            nee = _dt.fromisoformat(str(c.get("cree_le")).replace("Z", "+00:00"))
            if nee.tzinfo is None:
                nee = nee.replace(tzinfo=_tz.utc)
        except Exception:
            continue
        age = (maintenant - nee).total_seconds()
        seuil = DELAI_RELANCE if deja == 0 else DELAI_2E_RELANCE
        if age >= seuil:
            sortie.append(c)
    return sortie


def _relancer_client(cid):
    """📧 Écrit au client : veut-il toujours sa commande ? Renvoie True si parti."""
    cmd = db.get_commande(cid)
    if not cmd:
        return False
    dest = (cmd.get("identifiant") or "").strip()
    if "@" not in dest:
        return False
    jeu = REGISTRE_JEUX.get(cmd.get("programme"), {}).get("nom") or cmd.get("programme") or "votre jeu"
    corps = (
        "Ia ora na,\n\n"
        f"Votre commande n\u00b0{cid} ({jeu} \u00b7 {cmd.get('nb_feuilles')} feuilles \u00b7 "
        f"{cmd.get('montant')} XPF) est toujours en attente de r\u00e8glement chez nous.\n\n"
        "Souhaitez-vous toujours la recevoir ?\n\n"
        "\u2022 Si OUI : r\u00e9pondez simplement \u00e0 ce message, nous la pr\u00e9parons aussit\u00f4t.\n"
        "\u2022 Si NON : dites-le-nous d'un mot, nous l'annulerons sans frais.\n\n"
        "Sans nouvelles de votre part, nous la garderons en attente encore quelques jours.\n\n"
        "M\u0101uruuru,\nMANAPRINT")
    envoyer_email_simple(dest, f"Votre commande n\u00b0{cid} \u2014 la souhaitez-vous toujours ?", corps)
    return True


def _veilleur_relances():
    """👁️📧 Deux fois par jour : relance les clients qui n'ont pas réglé.

    ⚠️ POURQUOI SI ESPACÉ : une relance est un message COMMERCIAL, pas une
    réparation. Écrire deux fois par jour au même client le ferait fuir.
    On attend TROIS JOURS avant la première, UNE SEMAINE avant la seconde,
    et on s'arrête là.
    """
    import time as _t
    _t.sleep(300)     # on laisse le serveur démarrer tranquillement
    while True:
        try:
            for c in _commandes_a_relancer():
                cid = int(c["id"])
                try:
                    if _relancer_client(cid):
                        _RELANCES_CLIENT[cid] = _RELANCES_CLIENT.get(cid, 0) + 1
                        print(f"[VEILLEUR RELANCE] commande {cid} \u2014 relance "
                              f"{_RELANCES_CLIENT[cid]}/{MAX_RELANCES_CLIENT} "
                              f"envoy\u00e9e \u00e0 {c.get('identifiant')}")
                except Exception as e:
                    print(f"[VEILLEUR RELANCE] commande {cid} : {e}")
                _t.sleep(20)      # on espace les envois, le serveur respire
        except Exception as e:
            print(f"[VEILLEUR RELANCE] {e}")
        _t.sleep(12 * 3600)       # deux fois par jour, pas plus


def _veilleur_fabrications():
    """👁️🏭 Toutes les 10 minutes : relance les fabrications restees en rade."""
    import time as _t
    _t.sleep(120)
    while True:
        try:
            for c in _fabrications_figees():
                cid = c["id"]
                _FABRIC_RELANCES[cid] = _FABRIC_RELANCES.get(cid, 0) + 1
                print(f"[VEILLEUR FABRICATION] commande {cid} figee depuis "
                      f"{c.get('cree_le')} — relance "
                      f"{_FABRIC_RELANCES[cid]}/{MAX_RELANCES}")
                lancer_fabrication(cid)
        except Exception as e:
            print(f"[VEILLEUR FABRICATION] {e}")
        _t.sleep(600)


_threading.Thread(target=_veilleur_fabrications, daemon=True).start()
_threading.Thread(target=_veilleur_relances, daemon=True).start()


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
            session.permanent = True          # la connexion tient 30 jours
            session["partenaire_slug"] = slug
            return jsonify({"ok": True, "nom": part["nom"], "zone": part.get("zone", "")})
    return jsonify({"ok": False, "message":
                    "Code partenaire inconnu \u2014 v\u00e9rifiez lettres et chiffres "
                    "(les tirets et espaces n'ont pas d'importance)."})


@app.route("/api/partenaire/logout", methods=["POST"])
def api_partenaire_logout():
    session.pop("partenaire_slug", None)
    return jsonify({"ok": True})


# 🏠 LA MAISON-MÈRE : 2KEA & Associé, c'est Maeva elle-même. Le « dû 2KEA »
# est ce que les AUTRES partenaires lui doivent — sur son propre espace,
# retirer une commande n'efface donc aucune dette.
MAISON_MERE = "2kea_papeete"


@app.route("/api/partenaire/supprimer-commande", methods=["POST"])
def api_partenaire_supprimer():
    """🗑️ Le partenaire retire UNE DE SES FABRIQUES GRATUITES.

    ⚠️⚠️ TROIS VERROUS, et ils comptent (sceau Maeva 13/08) :
      1. la commande doit appartenir À CE partenaire — pas à un autre ;
      2. elle doit être une FABRIQUE (`fabrique_partenaire`) — jamais la
         commande d'un client ;
      3. son DÛ doit être NUL. Les fabriques sont offertes, donc à 0 F ;
         une commande cliente porte le dû 2KEA (1,5 F la feuille), et
         l'effacer effacerait la dette de Maeva. Le partenaire ne doit
         JAMAIS pouvoir supprimer ce qu'il doit.
    Une commande cliente se supprime depuis l'espace de gestion de Tatie.
    """
    # ⚠️⚠️ 13/08 : CE FUT MON ERREUR. Je lisais `session["partenaire"]`,
    # or la session de la plateforme s'appelle `partenaire_slug`. La route
    # ne trouvait donc JAMAIS le partenaire et refusait TOUT en silence —
    # Maeva cliquait sur 🗑️ et rien ne se passait.
    # On passe désormais par `_partenaire_session()`, la même porte que
    # toutes les autres routes du partenaire : un seul endroit à tenir.
    slug, _part = _partenaire_session()
    if not slug:
        return jsonify({"ok": False, "message": "Session expirée — reconnectez-vous."}), 403
    d = request.get_json(silent=True) or {}
    try:
        cid = int(d.get("id") or 0)
    except Exception:
        cid = 0
    if not cid:
        return jsonify({"ok": False, "message": "Commande introuvable."})
    cmd = db.get_commande(cid)
    if not cmd:
        return jsonify({"ok": False, "message": f"La commande {cid} n'existe pas."})
    import json as _json
    try:
        perso = _json.loads(cmd.get("params_perso") or "{}")
    except Exception:
        perso = {}
    # verrou 1 : c'est bien SA commande
    if (perso.get("partenaire") or "") != slug:
        return jsonify({"ok": False, "message": "Cette commande n'est pas la vôtre."}), 403
    # ⚠️⚠️ 13/08 (sceau Maeva) : LA MAISON-MÈRE PEUT TOUT RETIRER.
    # Le « dû 2KEA » est ce que les partenaires doivent à 2KEA — or 2KEA,
    # c'est Maeva : sur SON espace, retirer une commande n'efface aucune
    # dette. Les AUTRES partenaires (FUN&CO, COCOTIE MER, RANIHEI) gardent
    # le garde-fou : ils ne peuvent retirer que leurs fabriques offertes,
    # sinon ils pourraient effacer ce qu'ils doivent sans que Maeva le voie.
    if slug != MAISON_MERE:
        # verrou 2 : c'est bien une fabrique, pas une commande cliente
        if cmd.get("mode_paiement") != "fabrique_partenaire":
            return jsonify({"ok": False,
                            "message": "Seules vos fabriques offertes peuvent être retirées ici. "
                                       "Pour une commande cliente, contactez 2KEA."})
        # verrou 3 : rien à devoir
        # ⚠️ une FABRIQUE est offerte : son dû est nul par définition —
        # c'est le même calcul que la liste (`du = 0 if fabrique_partenaire`).
        du = 0 if cmd.get("mode_paiement") == "fabrique_partenaire" else round(
            int(cmd.get("nb_feuilles") or 0) * 1.5)
        if du:
            return jsonify({"ok": False,
                            "message": "Cette commande porte un dû — elle ne peut pas être retirée ici."})
    try:
        # la même façon de faire que l'espace de gestion
        with db.get_db() as conn:
            conn.execute("DELETE FROM commandes WHERE id = ?", (cid,))
    except Exception as e:
        return jsonify({"ok": False, "message": f"Le retrait a échoué ({type(e).__name__}). Réessayez."})
    print(f"[PARTENAIRE] {slug} a retiré sa fabrique {cid}")
    return jsonify({"ok": True, "message": f"🗑️ Fabrique n°{cid} retirée."})


@app.route("/api/partenaire/mes-commandes", methods=["GET"])
def api_partenaire_mes_commandes():
    """Le tableau de bord du partenaire.

    ⚡ 06/08 — REFAIT A LA RACINE. Avant, cette route chargeait TOUTES
    les commandes de la boutique (plus de 1600) et lisait le detail de
    chacune en Python pour ne garder que celles du partenaire : beaucoup
    de travail a chaque ouverture, et quand le serveur fabriquait, la
    passerelle abandonnait (« upstream error »). Desormais la BASE fait
    le tri elle-meme et ne renvoie que le necessaire.
    """
    import json as _json
    slug, part = _partenaire_session()
    if not slug:
        return jsonify({"ok": False, "message": "connexion requise"}), 403
    try:
        commandes, totaux = db.commandes_du_partenaire(slug, limite=150)
    except Exception as e:
        print(f"[PARTENAIRE] lecture impossible : {e}")
        return jsonify({"ok": False,
                        "message": "Le serveur est occupé — réessayez dans un instant"}), 200
    # le coffre est lu UNE seule fois (le disque de Railway est en reseau)
    try:
        au_coffre_tous = set(os.listdir(_dossier_lots()))
    except Exception:
        au_coffre_tous = set()
    lignes = []
    for cmd in commandes:
        try:
            perso = _json.loads(cmd.get("params_perso") or "{}")
        except Exception:
            perso = {}
        du = 0 if cmd.get("mode_paiement") == "fabrique_partenaire" else round(
            int(cmd.get("nb_feuilles") or 0) * 1.5)
        lignes.append({
            "id": cmd["id"], "date": (cmd.get("cree_le") or "")[:16].replace("T", " "),
            "identifiant": cmd.get("identifiant", ""), "programme": cmd.get("programme", ""),
            "nb_feuilles": cmd.get("nb_feuilles", 0), "statut": cmd.get("statut", ""),
            "du": du,
            "cartons": f"cmd{cmd['id']}_cartons.pdf" in au_coffre_tous,
            "facture": f"cmd{cmd['id']}_facture.pdf" in au_coffre_tous,
            "evenement": perso.get("nom_evenement", "") or perso.get("titre_jeu", ""),
        })
    # 🏠 le slug part au navigateur : la maison-mère voit le 🗑️ partout
    return jsonify({"ok": True, "slug": slug, "nom": part["nom"], "zone": part.get("zone", ""),
                    "commandes": lignes, "stats": totaux,
                    "detail_limite": totaux.get("nb", 0) > len(lignes)})


@app.route("/api/partenaire/generer", methods=["POST"])
def api_partenaire_generer():
    """🖨️ MA FABRIQUE (vision Maeva, née pour RANIHEI de Raiatea) : le partenaire
    génère lui-même ses PDF, à SON enseigne — OFFERT (décision Maeva 29/07 :
    le dû 1,5 F ne s'applique qu'aux commandes de SES clients qui personnalisent
    pour leurs tournois). Les cartons arrivent dans SA liste (bouton ⬇️)."""
    import json as _json
    slug, part = _partenaire_session()
    if not slug:
        return jsonify({"ok": False, "message": "connexion requise"}), 403
    data = request.get_json(force=True, silent=True) or {}
    programme = str(data.get("programme") or "")
    if programme not in REGISTRE_JEUX or "_p15" in programme:
        return jsonify({"ok": False, "message": "Choisissez un jeu (gamme \u00c9CO) dans la liste."}), 400
    # 🔒 LE VERROU : certains jeux sont réservés (sceau Maeva 13/08).
    # ⚠️ Il est ICI, côté serveur : même si le jeu apparaissait dans la
    # liste par erreur, la fabrication serait refusée.
    if _jeu_interdit(slug, programme):
        return jsonify({"ok": False,
                        "message": "Ce jeu n'est pas disponible pour votre enseigne. "
                                   "Contactez 2KEA."}), 403
    try:
        nb_feuilles = int(data.get("nb_feuilles") or 0)
    except Exception:
        nb_feuilles = 0
    if nb_feuilles < 25 or nb_feuilles > 250 or nb_feuilles % 25:
        return jsonify({"ok": False, "message": "Choisissez de 25 \u00e0 250 feuilles, par paquets de 25."}), 400
    enseigne = (str(data.get("titre") or "").strip() or part.get("enseigne_pdf") or part["nom"])[:40]
    telephone = (str(data.get("telephone") or "").strip() or part.get("tel_pdf") or part.get("tel", ""))[:24]
    perso = _json.dumps({
        "theme": "", "nom_evenement": enseigne, "titre_jeu": enseigne,
        "couleur_perso": "", "date_lieu": part.get("zone", ""), "telephone": telephone,
        "partenaire": slug,
        # 🖨️ la case « Impression rapide » de l'espace partenaire
        "impression_rapide": bool(data.get("impression_rapide", True)),
    })
    commande_id, _ = db.creer_commande(
        identifiant=enseigne, origine="polynesien",
        programme=programme, couleur=REGISTRE_JEUX[programme].get("couleur", True),
        nb_feuilles=nb_feuilles, mode_paiement="fabrique_partenaire",
        params_perso=perso, prix_feuille=0,
    )
    db.marquer_commande_payee(commande_id)
    lancer_fabrication(commande_id)
    jeu = REGISTRE_JEUX.get(programme, {})
    return jsonify({"ok": True, "commande_id": commande_id,
                    "message": (f"\U0001f5a8\ufe0f Fabrique #{commande_id} lanc\u00e9e : {nb_feuilles} feuilles de "
                                f"{jeu.get('emoji','')} {jeu.get('nom', programme)} \u00e0 l'enseigne \u00ab {enseigne} \u00bb \u2014 "
                                "appuyez sur \u21bb dans 1-2 minutes, le bouton \u2b07\ufe0f Cartons appara\u00eetra.")})


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


@app.route("/api/admin/forcer-fabrication", methods=["POST"])
@admin_requis
def admin_forcer_fabrication():
    """🔧 RELANCE FORCÉE d'une ou plusieurs commandes bloquées.

    ⚠️ POURQUOI CE BOUTON (12/08) : quatre commandes de 500 feuilles sont
    restées « en fabrication » toute la nuit — le serveur avait tué leurs
    threads faute de mémoire. Or le veilleur automatique ne relance que
    les commandes de MOINS DE SIX HEURES (AGE_MAX_RELANCE, posé le 07/08
    pour éviter les boucles), et le rattrapage Stripe ne cherche que les
    paiements oubliés, pas les fabrications. Ces quatre-là étaient donc
    invisibles pour les deux veilleurs : bloquées pour toujours.

    Ce bouton ignore l'âge et relance ce qu'on lui donne — UNE À LA FOIS,
    car c'est justement quatre fabrications simultanées qui ont étouffé
    le serveur.
    """
    d = request.get_json(silent=True) or {}
    brut = str(d.get("ids") or "").replace(";", ",").replace(" ", ",")
    ids = []
    for x in brut.split(","):
        x = x.strip()
        if x.isdigit():
            ids.append(int(x))
    if not ids:
        return jsonify({"ok": False, "message": "Donne au moins un numéro de commande."})
    faits, absents = [], []
    for cid in ids[:10]:
        cmd = db.get_commande(cid)
        if not cmd:
            absents.append(cid)
            continue
        # on efface le compteur de relances : cette commande a droit à sa chance
        try:
            _FABRIC_RELANCES.pop(cid, None)
        except Exception:
            pass
        try:
            lancer_fabrication(cid)
            faits.append(cid)
        except Exception as e:
            absents.append(f"{cid} ({type(e).__name__})")
    msg = ""
    if faits:
        msg += ("\U0001f527 Relance lancée pour la commande "
                if len(faits) == 1 else "\U0001f527 Relance lancée pour les commandes ")
        msg += ", ".join(str(x) for x in faits)
        msg += ". Compte 2 à 4 minutes par commande, puis rafraîchis la liste."
    if absents:
        msg += "  \u26a0\ufe0f Introuvable(s) : " + ", ".join(str(x) for x in absents)
    return jsonify({"ok": bool(faits), "message": msg, "relancees": faits})


@app.route("/api/admin/relancer-client", methods=["POST"])
@admin_requis
def admin_relancer_client():
    """📧 RELANCE COMMERCIALE : le client veut-il toujours sa commande ?

    ⚠️ À ne pas confondre avec « Débloquer une fabrication » (🔧), qui
    relance la MACHINE. Ici on écrit AU CLIENT : sa commande attend d'être
    payée depuis un moment, et Tatie veut savoir s'il la maintient avant
    de la garder en attente ou de la supprimer (sceau Maeva 13/08).
    """
    d = request.get_json(silent=True) or {}
    try:
        cid = int(d.get("id") or 0)
    except Exception:
        cid = 0
    if not cid:
        return jsonify({"ok": False, "message": "Commande introuvable."})
    cmd = db.get_commande(cid)
    if not cmd:
        return jsonify({"ok": False, "message": f"La commande {cid} n'existe pas."})
    dest = (cmd.get("identifiant") or "").strip()
    if "@" not in dest:
        return jsonify({"ok": False,
                        "message": f"La commande {cid} n'a pas d'adresse email \u2014 "
                                   "appelle le client au t\u00e9l\u00e9phone affich\u00e9 sur la ligne."})
    # ⚠️ la MÊME plume que le veilleur automatique — un seul texte à tenir
    try:
        _relancer_client(cid)
        _RELANCES_CLIENT[cid] = _RELANCES_CLIENT.get(cid, 0) + 1
    except Exception as e:
        return jsonify({"ok": False, "message": f"L'email n'est pas parti ({type(e).__name__}). R\u00e9essaie dans un instant."})
    return jsonify({"ok": True,
                    "message": f"\U0001f4e7 Relance envoy\u00e9e \u00e0 {dest} pour la commande {cid}."})


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


@app.route("/api/admin/demandes-impression", methods=["GET"])
@admin_requis
def admin_demandes_impression():
    """La liste des demandes d'impression couleur qui attendent une réponse."""
    with db.get_db() as conn:
        lignes = conn.execute(
            "SELECT id, identifiant, programme, couleur, nb_feuilles, montant,"
            "       params_perso, cree_le, statut "
            "FROM commandes WHERE statut = ? ORDER BY id DESC",
            (STATUT_DEMANDE,)).fetchall()
    out = []
    for r in lignes:
        try:
            import json as _json
            perso = _json.loads(r["params_perso"] or "{}")
        except Exception:
            perso = {}
        jeu = REGISTRE_JEUX.get(r["programme"], {})
        out.append({
            "id": r["id"],
            "identifiant": r["identifiant"],
            "jeu": f"{jeu.get('emoji','')} {jeu.get('nom', r['programme'])}".strip(),
            "nb_feuilles": r["nb_feuilles"],
            "montant": r["montant"],
            "telephone": perso.get("telephone", ""),
            "nom_evenement": perso.get("nom_evenement", ""),
            "partenaire": perso.get("partenaire", ""),
            "cree_le": r["cree_le"],
        })
    return jsonify({"ok": True, "demandes": out})


@app.route("/api/admin/repondre-impression", methods=["POST"])
@admin_requis
def admin_repondre_impression():
    """✅ / ❌ La réponse de 2KEA à une demande d'impression couleur.
    « oui »  -> la commande rejoint les commandes à valider (le client paie) ;
    « non »  -> la demande est refusée (le client peut reprendre en PDF seul)."""
    data = request.get_json(force=True, silent=True) or {}
    try:
        cid = int(data.get("commande_id") or 0)
    except Exception:
        cid = 0
    reponse = (data.get("reponse") or "").strip().lower()
    if not cid or reponse not in ("oui", "non"):
        return jsonify({"ok": False, "message": "Demande ou réponse manquante."}), 400
    with db.get_db() as conn:
        row = conn.execute("SELECT statut FROM commandes WHERE id = ?", (cid,)).fetchone()
        if not row:
            return jsonify({"ok": False, "message": "Commande introuvable."}), 404
        if row["statut"] != STATUT_DEMANDE:
            return jsonify({"ok": False,
                            "message": "Cette demande a déjà reçu une réponse."}), 409
        if reponse == "oui":
            conn.execute("UPDATE commandes SET statut = 'en_attente', mode_paiement = 'virement' "
                         "WHERE id = ?", (cid,))
        else:
            conn.execute("UPDATE commandes SET statut = 'refusee' WHERE id = ?", (cid,))
    return jsonify({"ok": True, "reponse": reponse,
                    "message": ("Oui envoyé : la commande passe en attente de paiement."
                                if reponse == "oui"
                                else "Non enregistré : la demande est refusée.")})


@app.route("/api/admin/commandes", methods=["GET"])
@admin_requis
def admin_commandes():
    """L'ecran de gestion n'affiche que les commandes EN ATTENTE.
    Avant le 06/08 cette route renvoyait TOUTE l'histoire de la boutique
    (645 Ko et plus de 1600 lignes) : l'onglet mettait un temps fou a
    s'ouvrir sur un telephone. Elle repond desormais au filtre demande,
    et sans filtre elle garde son ancien comportement (compatibilite)."""
    statut = (request.args.get("statut") or "").strip()
    try:
        lignes = db.lister_commandes(statut) if statut else db.lister_commandes()
    except Exception as e:
        print(f"[COMMANDES] lecture impossible : {e}")
        return jsonify({"ok": False, "message": f"Base illisible : {e}"}), 500
    # 🛟 BLINDAGE (06/08) : une SEULE commande abimee (octets illisibles
    # venus d'un vieil enregistrement) faisait tomber TOUTE la liste, et
    # l'ecran affichait « Erreur de chargement ». Chaque valeur est
    # desormais rendue lisible, et une ligne impossible est ecartee
    # plutot que de tout emporter.
    propres, ecartees = [], 0
    for c in lignes:
        try:
            ligne = {}
            for cle, val in dict(c).items():
                if isinstance(val, (bytes, bytearray)):
                    val = val.decode("utf-8", "replace")
                elif val is not None and not isinstance(val, (str, int, float, bool)):
                    val = str(val)
                ligne[str(cle)] = val
            propres.append(ligne)
        except Exception:
            ecartees += 1
    if ecartees:
        print(f"[COMMANDES] {ecartees} ligne(s) illisible(s) ecartee(s)")
    return jsonify({"ok": True, "commandes": propres, "ecartees": ecartees})


@app.route("/api/admin/paiements-stripe", methods=["GET"])
@admin_requis
def admin_paiements_stripe():
    """💳 L'encadré de caisse (sceau Maeva 30/07, affiné le même jour) : la
    vitrine demande LA VÉRITÉ À STRIPE (paniers réellement payés sur 90 jours,
    recette du Rattrapage) et sépare les vrais encaissements des essais
    validés à la main — lecture seule, rien n'est modifié."""
    lignes = [c for c in db.lister_commandes()
              if c.get("mode_paiement") == "stripe" and c.get("statut") in ("payee", "generee")]
    paniers_payes = None
    if STRIPE_SECRET_KEY:
        try:
            import stripe
            import time as _t
            stripe.api_key = STRIPE_SECRET_KEY
            paniers_payes = set()
            sessions = stripe.checkout.Session.list(
                limit=100, created={"gte": int(_t.time()) - 90 * 86400})
            for sess in sessions.auto_paging_iter():
                if sess["payment_status"] != "paid":
                    continue
                try:
                    paniers_payes.add(int(sess["metadata"]["panier_id"]))
                except Exception:
                    pass
        except Exception:
            paniers_payes = None   # Stripe injoignable : repli sans la vérité
    if paniers_payes is not None:
        reels = [c for c in lignes if c.get("panier_id") in paniers_payes]
        essais = [c for c in lignes if c.get("panier_id") not in paniers_payes]
        # ⚠️ 11/08 : les commandes NON recoupées sont renvoyées elles aussi.
        # Depuis la bascule de caisse, Stripe ne voit plus les paiements
        # encaissés sur l'ancien compte : ils sont bien réels, mais
        # invisibles ici. Tatie doit pouvoir les retrouver quand même.
        return jsonify({"ok": True, "verite_stripe": True,
                        "nombre": len(reels),
                        "total": sum(int(c.get("montant") or 0) for c in reels),
                        "dernieres": reels[:15],
                        "nombre_essais": len(essais),
                        "total_essais": sum(int(c.get("montant") or 0) for c in essais),
                        "essais": essais[:30]})
    total = sum(int(c.get("montant") or 0) for c in lignes)
    return jsonify({"ok": True, "verite_stripe": False, "nombre": len(lignes),
                    "total": total, "dernieres": lignes[:15]})


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


@app.route("/api/admin/ravitaillement", methods=["POST"])
@admin_requis
def admin_ravitaillement():
    """📦 RAVITAILLEMENT BOUTIQUE (vision Maeva) : 250 feuilles GRATUITES pour
    le stock 2KEA & Associé. Commande interne auto-validée — la fabrication
    part aussitôt, les PDF filent au coffre-fort (email en bonus)."""
    import json as _json
    data = request.get_json(force=True, silent=True) or {}
    programme = str(data.get("programme") or "")
    if programme not in REGISTRE_JEUX or "_p15" in programme:
        return jsonify({"ok": False, "message": "Choisis un jeu (gamme ÉCO) dans la liste."}), 400
    # 🚦 UN SEUL RAVITAILLEMENT À LA FOIS (06/08) : fabriquer 250 feuilles
    # occupe la machine une a deux minutes. Deux fabrications lancees
    # ensemble se genent, et tout le site ralentit. On refuse donc
    # poliment tant que la precedente n'est pas sortie.
    try:
        from datetime import datetime as _dt2, timedelta as _td2
        recent = _dt2.now() - _td2(minutes=6)
        for _c in db.lister_commandes("payee"):
            if _c.get("mode_paiement") != "ravitaillement":
                continue
            try:
                _quand = _dt2.fromisoformat(str(_c.get("cree_le") or ""))
            except Exception:
                continue
            if _quand > recent:
                return jsonify({"ok": False, "message":
                                "\u23f3 Un ravitaillement est déjà en fabrication "
                                f"(commande n\u00b0{_c['id']}). Laisse-lui une a deux "
                                "minutes : son PDF ira au coffre, puis relance."}), 409
    except Exception:
        pass
    perso = _json.dumps({
        "theme": "", "nom_evenement": "2KEA & Associé",
        "titre_jeu": "Ravitaillement boutique", "couleur_perso": "",
        "date_lieu": "Papeete", "telephone": "89 52 98 83",
        "partenaire": "2kea_papeete",
        # 🖨️ la case « Impression rapide » de l'espace de gestion — cochée par
        # défaut : c'est le réglage qui sort le plus vite à l'imprimante.
        "impression_rapide": bool(data.get("impression_rapide", True)),
    })
    commande_id, _ = db.creer_commande(
        identifiant="2KEA_BOUTIQUE", origine="polynesien",
        programme=programme, couleur=REGISTRE_JEUX[programme].get("couleur", True),
        nb_feuilles=250, mode_paiement="ravitaillement",
        params_perso=perso, prix_feuille=0,
    )
    db.marquer_commande_payee(commande_id)
    lancer_fabrication(commande_id)
    jeu = REGISTRE_JEUX.get(programme, {})
    return jsonify({"ok": True, "commande_id": commande_id,
                    "message": (f"📦 Ravitaillement #{commande_id} lancé : 250 feuilles de "
                                f"{jeu.get('emoji','')} {jeu.get('nom', programme)} en fabrication — "
                                "les PDF arrivent au coffre 🔍 (plusieurs minutes).")})


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
