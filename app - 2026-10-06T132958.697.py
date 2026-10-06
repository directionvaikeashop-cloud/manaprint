# 🩹 CORRECTIF 02/09 (Maeva) : TAHAA CLASSIC était déclaré à 8 cartes/feuille
# alors que son générateur en pose 18 (3 colonnes × 6 rangées). Une commande
# de 250 feuilles ne sortait que 112 pages. Les 187 autres jeux ont été
# éprouvés un par un : leur compte est juste.
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
from generators import lundi_pair74
from generators import mardi_pair90
from generators import roma6
from generators import ahe          # 🦪 AHE — création RANIHEI du 23/09
from generators import blossom_pearl  # 🌸 BLOSSOM PEARL — création RANIHEI du 23/09
from generators import makemo       # 🏝️ MAKEMO — création RANIHEI du 23/09
from generators import tureia_ranihei  # 🐢 TUREIA · RANIHEI — création RANIHEI du 23/09
from generators import kai
from generators import ohana75_8boules
from generators import ohana75_10boules
from generators import quatre_coin
from generators import pol
from generators import sun
from generators import pow as powgen
from generators import pow9 as pow9gen
from generators import pow_halloween as powhwgen
from generators import tiare_halloween as tiarehwgen
from generators import poe_parau as poeparaugen
from generators import poe as poegen
from generators import bng as bnggen
from generators import hakari as hakarigen
from generators import hakari_halloween as hakarihwgen
from generators import valider_halloween as validerhwgen
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
from generators import wow6
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

# ═══ 🌺 LES JUMEAUX « CLASSIC » (sceau Maeva 15/08) ═══
# Chaque jeu décoré garde son carton d'ORIGINE, pour les clientes qui
# le préfèrent sobre. Les deux vivent côte à côte dans la boutique.
from generators import aloha75_classic
from generators import pol_classic
from generators import bingo_ball_classic
from generators import rubis75_classic
from generators import losange_classic
from generators import ani_classic
from generators import wow4_classic
from generators import wow6_classic
from generators import moon_classic
from generators import dual_dab_classic
from generators import boules40_classic
from generators import cerf_volant_classic
from generators import brown8_classic
from generators import boules60_classic
from generators import lagoon_classic
from generators import fan90_classic
from generators import win_classic
from generators import kai_classic
from generators import sun_classic
from generators import wiz_classic
from generators import rai_classic
from generators import tahaa_classic
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
from generators import perle
from generators import hunter
from generators import echec_et_mat
from generators import pomare
from generators import unite
from generators import talon
from generators import hoanui
from generators import cristal
from generators import sicile
from generators import tifai
from generators import ranihei
from generators import mabuhai
from generators import raromatai90
from generators import raromatai75
from generators import alalia
from generators import speed90
from generators import joker
from generators import vanira
from generators import sangogo
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
from generators import tiki
from generators import bo75
from generators import bg75
from generators import bn75
from generators import bi75
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
    "ani", "wow4", "wow6", "moon", "tiki",
}
# ⚠️⚠️ 15/08 (sceau Maeva) : RANIHEI N'EST PLUS BLOQUÉE SUR LES JEUX À
# IMAGE — elle en reçoit **500 FEUILLES OFFERTES**, puis paie **1,5 F la
# feuille**. Le verrou sec (403) devient un compteur.
# Pour interdire vraiment un jeu à quelqu'un un jour : remettre son slug
# dans JEUX_INTERDITS ci-dessous.
JEUX_INTERDITS = {}

# ⭐⭐ LES JEUX EXCLUSIFS — un jeu qui n'appartient qu'à une seule enseigne :
# personne d'autre ne le voit ni ne peut le fabriquer.
#   {slug du jeu: {les slugs autorisés}}
#
# ⚠️⚠️ 29/08 (sceau Maeva) : LES SEPT JEUX DE RANIHEI SONT OUVERTS À TOUS.
# La table est VIDE — les 4 partenaires peuvent fabriquer HUNTER,
# ÉCHEC ET MAT, POMARE, UNITÉ, TALON, HOANUI et LES 7 BOULES DE CRISTAL.
# ⚠️ À SAVOIR : ces sept dessins portent « RANIHEI SISTERS & SHOP » et le
#    87 77 39 19 IMPRIMÉS DANS L'IMAGE. Une autre enseigne qui les commande
#    distribuera donc des cartons au nom et au numéro de RANIHEI.
# ⭐ POUR REVERROUILLER un jeu un jour, il suffit de remettre sa ligne ici,
#    par exemple :   "hunter": {"ranihei"},
JEUX_EXCLUSIFS = {}


# ═══ ©️ À QUI APPARTIENT CHAQUE JEU (sceau Maeva 17/09) ═══════════════
# Certains dessins ont été payés et signés par une enseigne : son nom et
# son téléphone sont IMPRIMÉS DANS L'IMAGE. Une autre enseigne qui les
# fabrique distribue donc des cartons à l'en-tête d'un concurrent — et
# surtout elle exploite un dessin qui n'est pas le sien.
# ⚠️ Le jeu n'est PAS fermé : l'autre enseigne peut le fabriquer, mais
#    les feuilles lui sont DUES, et son PDF attend la validation de 2KEA
#    (qui reverse le droit au propriétaire).
# ⚠️ LE PROPRIÉTAIRE, LUI, FABRIQUE LIBREMENT chez lui : c'est son dessin.
#   {slug du jeu: slug de l'enseigne propriétaire}
JEUX_PROPRIETAIRE = {
    # 🌺 les quatorze dessins de RANIHEI SISTERS & SHOP
    "ranihei": "ranihei", "mabuhai": "ranihei", "joker": "ranihei",
    "vanira": "ranihei", "speed90": "ranihei", "sangogo": "ranihei",
    "raromatai75": "ranihei", "raromatai90": "ranihei",
    "hunter": "ranihei", "echec_et_mat": "ranihei", "pomare": "ranihei",
    "unite": "ranihei", "talon": "ranihei", "hoanui": "ranihei",
    "cristal": "ranihei",
    # 👑 les dessins de 2KEA & Associé
    "tifai": "2kea_papeete", "sicile": "2kea_papeete",
    "alalia": "2kea_papeete",
    # ⚠️⚠️ 17/09 (sceau Maeva) : TOUTE CRÉATION OU MODIFICATION DE 2KEA
    #    SORT DE LA GRATUITÉ. Ces huit jeux ont été retravaillés ce
    #    jour-là — nouvelle écriture, économie de toner, recentrage — et
    #    passent donc en propriété 2KEA : les partenaires les paient dès
    #    la première feuille, sans forfait.
    #    ⚠️ Ce sont les jeux qu'ils fabriquent le plus : la bascule change
    #       leur quotidien. Ils en sont avertis par le bandeau de leur
    #       espace (ANNONCES_PARTENAIRE ci-dessus).
    #    ⭐ RÈGLE POUR LA SUITE : chaque nouveau jeu de 2KEA, et chaque
    #       ancien qu'on retouche, s'ajoute ici le jour même.
    "p6_marathon": "2kea_papeete", "p12_marathon": "2kea_papeete",
    "p15_marathon": "2kea_papeete",
    # ⚠️ ATTENTION AUX NOMS : le registre abrège les « 2 séries » en
    #    « _2s » mais garde « _4series » en entier. On met les DEUX formes,
    #    comme ça un renommage futur ne rouvre pas le jeu par accident.
    "ohana75_2s": "2kea_papeete", "ohana75_2series": "2kea_papeete",
    "ohana75_4s": "2kea_papeete", "ohana75_4series": "2kea_papeete",
    "ohana90_2s": "2kea_papeete", "ohana90_2series": "2kea_papeete",
    "ohana90_4s": "2kea_papeete", "ohana90_4series": "2kea_papeete",
    "quines90": "2kea_papeete",
    "lundi_pair74": "2kea_papeete",   # 🌙 création 2KEA du 18/09
    "mardi_pair90": "2kea_papeete",   # ☀️ création 2KEA du 18/09
    "roma6": "2kea_papeete",          # 🏛️ création 2KEA du 19/09
    # 🦪 AHE appartient à RANIHEI : c'est SA maquette, tracee trait pour
    #    trait. Toute autre enseigne qui le fabrique doit la feuille.
    "ahe": "ranihei",                 # 🦪 création RANIHEI du 23/09
    "blossom_pearl": "ranihei",       # 🌸 création RANIHEI du 23/09
    "makemo": "ranihei",              # 🏝️ création RANIHEI du 23/09
    "tureia_ranihei": "ranihei",      # 🐢 création RANIHEI du 23/09
}
PRIX_FEUILLE_DROIT = 1.5     # ce que doit une enseigne sur le jeu d'une autre


# ═══ 📢 LES ANNONCES DE L'ESPACE PARTENAIRE (sceau Maeva 17/09) ══════
# Un bandeau qui s'affiche à la connexion, dans le tableau de bord de
# l'enseigne. {slug: (titre, texte)} — laisser vide pour ne rien montrer.
# ⚠️ C'est un message de 2KEA à SON partenaire : il se lit tel quel, il
#    n'est pas traduit ni reformulé. Pour le retirer, effacer sa ligne.
# ═══ 📢 L'ANNONCE DU 17/09 — LA MÊME POUR TOUT LE MONDE ══════════════
# ⚠️ Maeva l'a voulue identique pour les quatre enseignes : une seule
#    règle, dite une seule fois, de la même façon à chacune. Personne ne
#    reçoit une version adoucie ou durcie de son côté.
# ⚠️ Elle dit LES DEUX SENS : le crédit offert, et les droits d'auteur —
#    ceux de RANIHEI comme ceux de 2KEA. Ne jamais la scinder par
#    enseigne : c'est ce qui rendrait le message suspect.
_ANNONCE_COMMUNE = (
    "\U0001f381 3 000 feuilles offertes sur chaque jeu",
    "\u00c0 partir d'aujourd'hui, chaque enseigne partenaire re\u00e7oit "
    "3 000 FEUILLES OFFERTES SUR CHAQUE JEU du catalogue \u2014 un cr\u00e9dit "
    "par jeu, pas un total : 3 000 feuilles de P6 MARATHON n'entament pas "
    "votre cr\u00e9dit d'OHANA 75. C'est un geste unique, valable une fois "
    "pour toutes, qui ne se renouvelle pas chaque mois. Vous n'avez rien "
    "\u00e0 faire : votre PDF part comme d'habitude tant que le cr\u00e9dit dure. "
    "Au-del\u00e0, la feuille est \u00e0 1,5 F.\n\n"
    "\u00a9\ufe0f LES DESSINS APPARTIENNENT \u00c0 QUI LES A CR\u00c9\u00c9S. Trente jeux "
    "sont enregistr\u00e9s au nom d'une enseigne : quinze \u00e0 RANIHEI SISTERS "
    "& SHOP (RANIHEI, MABUHA\u00cf, JOKER, VANIRA, SPEED 90, SANGOGO, "
    "RAROMATAI 75 et 90, HUNTER, \u00c9CHEC ET MAT, POMARE, UNIT\u00c9, TALON, "
    "HOANUI, CRISTAL) et quinze \u00e0 2KEA & ASSOCI\u00c9 (P6, P12 et P15 "
    "MARATHON, OHANA 75 et OHANA 90 en 2 et 4 s\u00e9ries, QUINES 90, TIFAI, "
    "SICILE, ALALIA). Chacune fabrique LES SIENS librement. Sur le jeu "
    "d'une autre, la feuille est due \u00e0 1,5 F d\u00e8s la premi\u00e8re, et le PDF "
    "attend que la cr\u00e9atrice ait confirm\u00e9 le r\u00e8glement \u2014 elle le fait "
    "depuis l'encadr\u00e9 \u00ab Mes droits \u00bb de son espace.\n\n"
    "Tous les autres jeux du catalogue gardent leur cr\u00e9dit de 3 000 "
    "feuilles. Renseignements : 2KEA & Associ\u00e9, 89 22 23 05.")

ANNONCES_PARTENAIRE = {
    "ranihei": _ANNONCE_COMMUNE,
    "fun_and_co": _ANNONCE_COMMUNE,
    "cocotie_mer": _ANNONCE_COMMUNE,
    "2kea_papeete": _ANNONCE_COMMUNE,
}


def _jeu_d_une_autre(slug, programme):
    """©️ Ce jeu appartient-il à QUELQU'UN D'AUTRE que cette enseigne ?"""
    proprio = JEUX_PROPRIETAIRE.get(_base_jeu(programme or ""))
    return bool(proprio) and (slug or "") != proprio


def _jeu_exclusif_refuse(slug, programme):
    """⭐ Vrai si ce jeu appartient à quelqu'un d'autre."""
    proprios = JEUX_EXCLUSIFS.get(_base_jeu(programme or ""))
    return bool(proprios) and (slug or "") not in proprios


# 🎁 LE QUOTA DES JEUX À IMAGE, partenaire par partenaire.
#    {slug: nombre de feuilles offertes}
# ⚠️ 17/09 : L'ANCIEN CRÉDIT DE RANIHEI (500 feuilles) A ÉTÉ RETIRÉ — les
#    3 000 feuilles par jeu le remplacent et le dépassent largement.
#    Ce qui reste ici est un PLAFOND PLUS SERRÉ, réservé aux JEUX À IMAGE
#    des enseignes qui en ont un : elles épuisent CE crédit-là d'abord,
#    parce qu'un jeu habillé coûte plus cher à produire.
QUOTA_HABILLES = {
    "2kea_papeete": 1500,
}
PRIX_FEUILLE_HABILLEE = 1.5      # ce que coûte la feuille au-delà du quota


# ═══ 🚦 LE QUOTA PAR JEU (sceau Maeva 17/09) ═══════════════════════════
# Chaque enseigne partenaire fabrique GRATUITEMENT jusqu'à 3 000 feuilles
# SUR CHAQUE JEU. Au-delà, le jeu n'est pas fermé : les feuilles suivantes
# lui sont dues, et la plateforme les lui compte.
# ⚠️ CE QUOTA EST PAR JEU ET PAR ENSEIGNE, pas global : 3 000 feuilles de
#    P6 MARATHON n'entament pas le crédit d'OHANA 75.
# ⚠️ IL COMPTE À PARTIR DU 17/09/2026 SEULEMENT. Tout ce qui a été
#    fabriqué avant ce jour ne pèse pas sur le compteur — Maeva a voulu
#    repartir propre. Ne jamais reculer cette date sans le lui demander :
#    ça rouvrirait d'un coup des milliers de feuilles déjà tirées.
# ⚠️⚠️ LA GRATUITÉ EST DÉFINITIVE, PAS MENSUELLE (sceau Maeva 17/09).
#    Ces 3 000 feuilles sont un crédit UNIQUE, valable une fois pour
#    toutes sur chaque jeu. Elles NE SE RENOUVELLENT PAS au mois, ni au
#    trimestre, ni à l'année, et ce qui n'est pas utilisé ne se reporte
#    nulle part. Une fois épuisé sur un jeu, il l'est pour de bon.
#    ⚠️ NE JAMAIS ajouter de remise à zéro périodique ici : ce serait
#       transformer un crédit de lancement en abonnement gratuit.
# ═══ 🏠 LA MAISON NE SE FACTURE PAS ELLE-MÊME (sceau Maeva 17/09) ════
# 2KEA & Associé — Papeete est l'enseigne qui TIENT la plateforme. Elle
# fabrique ce qu'elle veut pour son propre stock de boutique : ni quota
# de 3 000, ni plafond sur les jeux à image, ni règlement.
# ⚠️ CE QUE CETTE EXONÉRATION NE COUVRE PAS : les droits dus à une AUTRE
#    enseigne sur SES dessins. Quand 2KEA fabrique un jeu de RANIHEI, elle
#    le paie comme tout le monde — sinon elle reprendrait d'une main ce
#    qu'elle vient d'accorder, et la protection des créations ne vaudrait
#    plus rien.
ENSEIGNE_MAISON = "2kea_papeete"


# ═══ 🔗 OÙ ENVOYER LE CLIENT POUR LES JEUX D'UNE AUTRE ENSEIGNE ══════
# (sceau Maeva 17/09) Ces jeux ne se vendent pas ici, mais on ne laisse
# pas la cliente dans le vide : la vitrine les montre quand même, avec un
# bandeau « vendu par… » et le moyen de les joindre.
# ⚠️ POUR AJOUTER LA PAGE FACEBOOK : remplacer la chaîne vide ci-dessous
#    par l'adresse complète (https://www.facebook.com/...). Tant qu'elle
#    est vide, le bouton Facebook ne s'affiche pas — rien ne casse.
VITRINE_AUTRES = {
    "ranihei": {
        "nom": "RANIHEI SISTERS & SHOP",
        "tel": "87 77 39 19",
        # ⚠️ 17/09 : leur page n'est pas indexée publiquement, donc son
        #    adresse directe est inconnue. Plutôt qu'inventer un lien qui
        #    tomberait dans le vide, on ouvre une RECHERCHE Facebook sur
        #    leur nom exact : elle les trouve à tous les coups.
        #    ⭐ Le jour où RANIHEI donne l'adresse de sa page, la remplacer
        #       ici par le lien direct (https://www.facebook.com/...).
        "facebook": "https://www.facebook.com/search/top?q=Ranihei%20Sisters%20%26%20Shop",
        "facebook_libelle": "Ranihei Sisters & Shop",
        "mot": "Ces jeux sont des cr\u00e9ations de RANIHEI SISTERS & SHOP. "
               "Contactez-les directement pour les commander.",
    },
}


def _vitrine_autre(programme):
    """🔗 Si ce jeu appartient à une autre enseigne, où envoyer la cliente."""
    pro = JEUX_PROPRIETAIRE.get(_base_jeu(programme or ""))
    if not pro or pro == ENSEIGNE_MAISON:
        return None
    fiche = VITRINE_AUTRES.get(pro)
    if not fiche:
        return None
    return {"enseigne": fiche.get("nom", pro), "tel": fiche.get("tel", ""),
            "facebook": fiche.get("facebook", ""),
            "facebook_libelle": fiche.get("facebook_libelle", "Leur page Facebook"),
            "mot": fiche.get("mot", "")}

QUOTA_PAR_JEU = 3000
QUOTA_DEPART = "2026-09-17"      # AAAA-MM-JJ — le compteur ignore l'avant
PRIX_FEUILLE_QUOTA = 1.5         # ce que coûte la feuille au-delà des 3 000


def _feuilles_faites_sur_jeu(slug, programme):
    """🚦 Combien de feuilles CE partenaire a-t-il fabriquées SUR CE JEU
    depuis QUOTA_DEPART ? On compte les quatre gammes d'un même jeu
    ensemble (couleur, N&B, premium) : c'est bien le même jeu."""
    if not slug or not programme:
        return 0
    base = _base_jeu(programme)
    motifs = ('%"partenaire": "' + str(slug) + '"%',
              '%"partenaire":"' + str(slug) + '"%')
    total = 0
    try:
        with db.get_db() as conn:
            rows = conn.execute(
                "SELECT programme, nb_feuilles FROM commandes "
                "WHERE (params_perso LIKE ? OR params_perso LIKE ?) "
                "  AND mode_paiement IN ('fabrique_partenaire', 'fabrique_habillee', "
                "                        'fabrique_quota', 'fabrique_droit') "
                "  AND date(cree_le) >= date(?)",
                (motifs[0], motifs[1], QUOTA_DEPART)).fetchall()
        for r in rows:
            if _base_jeu(str(r["programme"] or "")) == base:
                total += int(r["nb_feuilles"] or 0)
    except Exception as e:
        print("[QUOTA-JEU] lecture impossible :", e)
    return total


def _feuilles_habillees_faites(slug):
    """🎁 Combien de feuilles de jeux À IMAGE ce partenaire a-t-il déjà
    fabriquées ? On ne compte QUE sa fabrique à lui, et seulement les jeux
    habillés — ses autres commandes ne touchent pas au quota."""
    if not slug:
        return 0
    motifs = ('%"partenaire": "' + str(slug) + '"%',
              '%"partenaire":"' + str(slug) + '"%')
    total = 0
    try:
        with db.get_db() as conn:
            rows = conn.execute(
                "SELECT programme, nb_feuilles FROM commandes "
                "WHERE (params_perso LIKE ? OR params_perso LIKE ?) "
                "  AND mode_paiement IN ('fabrique_partenaire', 'fabrique_habillee')",
                motifs).fetchall()
        for r in rows:
            # ⚠️ 17/09 : on compte sur JEUX_AVEC_IMAGE, la VRAIE liste des
            #    jeux à image (celle des tarifs, tenue à jour). L'ancienne
            #    JEUX_HABILLES était figée à 29 jeux et ignorait tous les
            #    nouveaux — SICILE, TIFAI, MABUHAÏ, VANIRA… — si bien que
            #    le plafond ne se déclenchait jamais sur eux.
            if _base_jeu(str(r["programme"] or "")) in JEUX_AVEC_IMAGE:
                total += int(r["nb_feuilles"] or 0)
    except Exception as e:
        print("[QUOTA] lecture impossible :", e)
    return total


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

# ══ 🖼️ AVEC IMAGE / SANS IMAGE (sceau Maeva 02/09) ════════════════════
# Les clientes se perdaient entre « CLASSIC », « ÉCO » et les jeux décorés.
# Désormais le menu dit simplement si le carton porte un dessin ou non.
# ⚠️ Cette liste a été établie en FABRIQUANT une carte de chaque jeu et en
#    regardant si le PDF contient vraiment une image — pas à la main.
# ⚠️ Elle ne sert QU'À NOMMER. La facturation des jeux à image reste réglée
#    par JEUX_HABILLES, qui est une autre liste, plus courte, et volontaire.
JEUX_AVEC_IMAGE = {
    "sangogo",
    "vanira",
    "joker",
    "speed90",
    "alalia",
    "raromatai75",
    "raromatai90",
    "mabuhai",
    "ranihei",
    "tifai",
    "sicile",
    "aloha75", "ani", "australes", "baam", "bin6", "bingo_ball",
    "boules40", "boules60", "brown8", "bubulle", "caller", "cerf_volant",
    "champagne", "corsica", "cristal", "diamant", "dollar1", "dual_dab",
    "echec_et_mat", "fan90", "fleche", "francs", "francs1000",
    "francs500", "francs5000", "gambier", "hakari", "havai",
    "henua_enana", "hoanui", "huahine", "hunter", "italia_villes", "kai",
    "lagoon", "losange", "maia", "moon", "moorea", "ok", "opoa",
    "papeari", "perle", "pietra", "pietra_smo", "poe_parau", "pol",
    "pomare", "pow9", "quatre_coin", "rai", "rubis75", "salute",
    "salute_smo", "societe", "sun", "tahaa", "tahaa90", "talon", "tesla",
    "tiare", "tiki", "trio75", "trio90", "tuamotu", "tureia_atoll",
    "unite", "vanille", "win", "wiz", "wow4", "wow6",
}


def _suffixe_image(base_id):
    """🖼️ « AVEC IMAGE » si le carton porte un dessin, « SANS IMAGE » sinon."""
    return "AVEC IMAGE" if base_id in JEUX_AVEC_IMAGE else "SANS IMAGE"


def _enregistrer_paire(base_id, nom, emoji, cpf, fn, kwarg_nb="nb_cartes"):
    """Enregistre les 4 variantes d'un jeu — vision 2 gammes :
    ÉCO (écriture fine, économie de toner)  et  PREMIUM (écriture grasse, style P15).
    Chacune en (Couleur) et (N&B). 1 ligne = 4 entrées au menu.
    Les identifiants historiques (…_couleur / …_nb) restent sur la gamme ÉCO :
    les anciennes commandes se régénèrent à l'identique."""
    _img = _suffixe_image(base_id)
    _enregistrer_jeu(base_id + "_couleur", nom + " · " + _img + " (Couleur)", emoji, cpf,
                     _variante(fn, True, "eco"),  kwarg_nb=kwarg_nb, couleur=True)
    _enregistrer_jeu(base_id + "_nb",      nom + " · " + _img + " (N&B)",     emoji, cpf,
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
_enregistrer_paire("lundi_pair74",  "LUNDI PAIR 74","🌙", 12, lundi_pair74.generer_pdf)
_enregistrer_paire("mardi_pair90",  "MARDI PAIR 90","☀️", 12, mardi_pair90.generer_pdf)
_enregistrer_paire("roma6",         "ROMA · 6 boules","🏛️", 8, roma6.generer_pdf)
# ⚠ 6 cartons par feuille, A4 portrait : c'est la planche que RANIHEI a
#   fournie le 23/09 au soir (carton presque carre, 2 colonnes x 3 rangees).
#   Ce chiffre doit TOUJOURS suivre COLS_PAGE x ROWS_PAGE dans
#   generators/ahe.py, sinon la plateforme se trompe dans ses comptes de
#   feuilles et facture de travers.
_enregistrer_paire("ahe",           "AHE","🦪", 6,  ahe.generer_pdf)
# ⚠ 6 cartons par feuille : la planche de RANIHEI, 2 colonnes x 3 rangees.
#   Doit suivre COLS_PAGE x ROWS_PAGE dans generators/blossom_pearl.py.
_enregistrer_paire("blossom_pearl", "BLOSSOM PEARL","🌸", 6,  blossom_pearl.generer_pdf)
# ⚠ 6 cartons par feuille A4 PAYSAGE : la planche de RANIHEI, 2 colonnes
#   x 3 rangees. Doit suivre COLS_PAGE x ROWS_PAGE dans generators/makemo.py.
_enregistrer_paire("makemo",        "MAKEMO","🏝️", 6,  makemo.generer_pdf)
# ⚠ 6 cartons par feuille A4 PAYSAGE : la planche de RANIHEI, 2 colonnes
#   x 3 rangees. Doit suivre COLS_PAGE x ROWS_PAGE dans tureia_ranihei.py.
# ⚠⚠ NE PAS CONFONDRE avec "tureia" (TUREIA 🔶), un AUTRE jeu du
#    catalogue, inscrit plus haut et qui tourne sur generators/tureia.py.
_enregistrer_paire("tureia_ranihei", "TUREIA \u00b7 RANIHEI","\U0001f422", 6,  tureia_ranihei.generer_pdf)
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
_enregistrer_paire("pow_halloween", "POW HALLOWEEN", "🎃", 16, powhwgen.generer_pdf)
_enregistrer_paire("tiare_halloween", "TIARE HALLOWEEN", "🎃", 16, tiarehwgen.generer_pdf)
_enregistrer_paire("pow_casino",    "POW CASINO","🎲", 12, powgen.generer_pdf_casino)
_enregistrer_paire("poe_parau",     "PERLE 90", "🦪", 16, poeparaugen.generer_pdf)
_enregistrer_paire("poe",           "POE 6 boules", "⚪", 12, poegen.generer_pdf)
_enregistrer_paire("bng",           "BNG 5 boules", "🟢", 12, bnggen.generer_pdf)
_enregistrer_paire("hakari",        "HAKARI 6 boules", "🥥", 20, hakarigen.generer_pdf)
_enregistrer_paire("hakari_halloween", "HAKARI HALLOWEEN", "🎃", 20, hakarihwgen.generer_pdf)
_enregistrer_paire("valider_halloween", "VALIDER HALLOWEEN", "🎃", 16, validerhwgen.generer_pdf)
_enregistrer_paire("henua_enana",   "HENUA ENANA 7 boules", "🗺️", 12, henuaenanagen.generer_pdf)
_enregistrer_paire("tiare",         "TIARE 50-90", "🌼", 12, tiaregen.generer_pdf)
_enregistrer_paire("tuamotu",       "TUAMOTU", "🏝️", 12, tuamotugen.generer_pdf)
_enregistrer_paire("societe",       "SOCIÉTÉ 7 boules", "⛰️", 8, societegen.generer_pdf)
_enregistrer_paire("australes",     "AUSTRALES", "🐋", 15, australesgen.generer_pdf)
_enregistrer_paire("gambier",       "GAMBIER 7 boules", "🐚", 8, gambiergen.generer_pdf)
_enregistrer_paire("parata",        "PARATA 6 plages", "🦈", 6, paratagen.generer_pdf)
_enregistrer_paire("katiu",         "KATIU 7 boules", "🐠", 8, katiugen.generer_pdf)
_enregistrer_paire("ok",            "OK 6 boules", "👌", 16, okgen.generer_pdf)
_enregistrer_paire("feu",           "FEU 5 boules", "🔥", 16, feugen.generer_pdf)
_enregistrer_paire("vision",        "VISION 6 boules", "👁️", 8, visiongen.generer_pdf)
_enregistrer_paire("taptap",        "TAP TAP 5 boules", "👏", 8, taptapgen.generer_pdf)
_enregistrer_paire("joie",          "JOIE 5 boules", "😄", 16, joiegen.generer_pdf)
_enregistrer_paire("caller",        "CALLER 6 boules", "👍", 16, callergen.generer_pdf)
_enregistrer_paire("valider",       "VALIDER 6 boules", "✅", 16, validergen.generer_pdf)
_enregistrer_paire("chance",        "CHANCE 6 boules", "🍀", 8, chancegen.generer_pdf)
_enregistrer_paire("opoa",          "OPOA", "🏔️", 15, opoagen.generer_pdf)
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
    "lunes75",        # LUNES 75
    "lettre_u",       # LETTRE U
    "lettre_l",       # LETTRE L
    "topday",         # TOP DAY
    "bo75",           # BO 75
    "yes",            # YES
    "p6_marathon",    # P6 MARATHON
    "bg75",           # BG 75
    "funday",         # FUNDAY
    "bn75",           # BN 75
    "ohana90_24b",    # OHANA 90 · 24 boules
    "ohana90_12b",    # OHANA 90 · 12 boules
    "bi90",           # BI 90
    "bn90",           # BN 90
    "bgo5",           # BGO 5 boules
    "bno",            # BNO 8 boules (la normale)
    "ino",            # INO 5 boules (la normale)
    "rubis90",        # RUBIS 90
}
PRIX_NB_AUTRES = 7.4   # 185 F les 25 feuilles

# ⚠️⚠️ 02/09 — DIX JEUX ONT QUITTÉ `TARIF_NB_150`. Maeva a regardé les
# cartons un par un et a tranché :
#   • 40 BOULES · 60 BOULES · DIAMANT · FAN 90 · RUBIS 75 · TAHITI(fleche)
#     → vrais cartons illustrés (le dessin couvre 53 à 82 % de la feuille),
#       ils passent au tarif image : 225 F les 25 en N&B.
#   • 4 COIN · CHAMPAGNE · HUAHINE · MOOREA
#     → presque que des chiffres (image de 19 à 55 %, souvent de simples
#       cadres de couleur), ils vont au tarif ordinaire : 185 F les 25.
#       Ils sont listés juste en dessous pour échapper au tarif image.
# ⚠️ 02/09 (complément Maeva) : ces quatre-là échappent au tarif image
#    DANS LES DEUX SENS — 185 F en N&B ET 250 F en couleur, comme un jeu
#    sans dessin. Leur image est trop légère pour justifier le supplément.
IMAGE_TARIF_NB_ORDINAIRE = {
    "quatre_coin",   # 4 COIN — des cadres de couleur autour des chiffres
    "champagne",     # CHAMPAGNE — une flûte au milieu, 35 % de la feuille
    "huahine",       # HUAHINE — un petit cœur en filigrane, 19 %
    "moorea",        # MOOREA — la carte de l'île, 55 %
}

# 💵 LES JEUX À BILLETS (décision Maeva 13/08) : 250 F les 25 feuilles,
# en noir & blanc comme en couleur. Ce sont les plus travaillés du
# catalogue — le dessin du billet, la rosace, les chiffres étirés.
TARIF_BILLETS_250 = {
    "dollar1",      # 1 DOLLAR
    "francs500",    # 500 FRANCS
    "francs1000",   # 1000 FRANCS
    "francs5000",   # 5000 FRANCS
}
PRIX_BILLETS = 8.0             # 200 F les 25 feuilles, en noir & blanc
                               # (baissé de 250 à 200 F — sceau Maeva 02/09)
# 🎨 EN COULEUR, LES BILLETS SONT À PART (décision Maeva 13/08) : 375 F les
# 25 feuilles, au lieu des 250 F de tous les autres jeux. ⚠️ POURQUOI CE
# SUPPLÉMENT : sur les autres jeux, la couleur ne teinte que les chiffres ;
# ici, c'est LE BILLET LUI-MÊME qui sera imprimé dans les couleurs de
# l'original — bien plus d'encre, et un rendu de vraie monnaie.
PRIX_BILLETS_COULEUR = 15.0    # 375 F les 25 feuilles

# ══ 🖼️ LA GRILLE DES JEUX À IMAGE (sceau Maeva 02/09) ══════════════════
# Un carton qui porte un dessin coûte plus cher à imprimer qu'un carton nu.
#     • NOIR & BLANC : 225 F les 25 feuilles (9 F la feuille)
#     • COULEUR      : 375 F les 25 feuilles (15 F la feuille)
# ⚠️ DEUX EXCEPTIONS, dans cet ordre :
#   ① LES BILLETS gardent leur tarif à eux : 200 F en N&B, 375 F en couleur.
#   ② LES JEUX DE `TARIF_NB_150` GARDENT LEURS 150 F EN NOIR & BLANC, même
#      s'ils portent un dessin (40 BOULES, DIAMANT, FAN 90, CHAMPAGNE,
#      TAHITI, HUAHINE, MOOREA, 4 COIN, RUBIS 75, 60 BOULES). Maeva a
#      voulu que ces dix-là ne bougent pas.
# En COULEUR, les jeux SANS image restent au tarif de base : 250 F les 25.
PRIX_IMAGE_NB = 9.0            # 225 F les 25 feuilles
PRIX_IMAGE_COULEUR = 15.0      # 375 F les 25 feuilles

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
_enregistrer_paire("wow4",          "WOW 4","🎆", 8, wow4.generer_pdf)
_enregistrer_paire("wow6",          "WOW 6","\U0001f4a5", 8,  wow6.generer_pdf)
_enregistrer_paire("maia",          "MAIA \u00b7 Ma\u00efa", "🍌", 12, maiagen.generer_pdf)
_enregistrer_paire("corsica",       "CORSICA \u00b7 l'\u00eele de la beaut\u00e9", "\u2b50", 8, corsicagen.generer_pdf)
_enregistrer_paire("bno",           "BNO","🎯", 16, bno.generer_pdf)
_enregistrer_paire("bno_casino",    "BNO CASINO","🎰", 12, bno.generer_pdf_casino)
_enregistrer_paire("ngo",           "NGO","🎳", 16, ngo.generer_pdf)
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
_enregistrer_paire("bgo",           "BGO",        "🔠", 16, bgo.generer_pdf)
_enregistrer_paire("igo",           "IGO",        "🎱", 12, igo.generer_pdf)
_enregistrer_paire("kea",           "KEA",        "🌿", 12, kea.generer_pdf)
_enregistrer_paire("moon",          "MOON",       "🌙", 8,  moon.generer_pdf)

# ═══ 🌺 les jumeaux CLASSIC, juste après leurs frères décorés ═══
_enregistrer_paire("aloha75_classic", "ALOHA 75 CLASSIC", "🌺", 12, aloha75_classic.generer_pdf)
_enregistrer_paire("pol_classic", "POL 6 boules CLASSIC", "🎲", 12, pol_classic.generer_pdf)
_enregistrer_paire("bingo_ball_classic", "Bingo Ball CLASSIC", "🎱", 10, bingo_ball_classic.generer_pdf)
_enregistrer_paire("rubis75_classic", "RUBIS 75 CLASSIC", "💎", 10, rubis75_classic.generer_pdf)
_enregistrer_paire("losange_classic", "LOSANGE CLASSIC", "🪁", 6, losange_classic.generer_pdf)
_enregistrer_paire("ani_classic", "TEAHUPOO CLASSIC", "🌊", 12, ani_classic.generer_pdf)
_enregistrer_paire("wow4_classic", "WOW 4 CLASSIC", "🎆", 12, wow4_classic.generer_pdf)
_enregistrer_paire("wow6_classic", "WOW 6 CLASSIC", "💥", 12, wow6_classic.generer_pdf)
_enregistrer_paire("moon_classic", "MOON CLASSIC", "🌙", 8, moon_classic.generer_pdf)
_enregistrer_paire("dual_dab_classic", "DUAL DAB CLASSIC", "🤜", 8, dual_dab_classic.generer_pdf)
_enregistrer_paire("boules40_classic", "40 BOULES CLASSIC", "🎳", 12, boules40_classic.generer_pdf)
_enregistrer_paire("cerf_volant_classic", "CERF VOLANT CLASSIC", "🪁", 6, cerf_volant_classic.generer_pdf)
_enregistrer_paire("brown8_classic", "BROWN 8 CLASSIC", "🟤", 8, brown8_classic.generer_pdf)
_enregistrer_paire("boules60_classic", "60 BOULES CLASSIC", "🎯", 12, boules60_classic.generer_pdf)
_enregistrer_paire("lagoon_classic", "LAGOON CLASSIC", "🏝️", 12, lagoon_classic.generer_pdf)
_enregistrer_paire("fan90_classic", "FAN 90 CLASSIC", "🗝️", 8, fan90_classic.generer_pdf)
_enregistrer_paire("win_classic", "WIN CLASSIC", "🏆", 12, win_classic.generer_pdf)
_enregistrer_paire("kai_classic", "KAI CLASSIC", "🍽️", 12, kai_classic.generer_pdf)
_enregistrer_paire("sun_classic", "SUN CLASSIC", "☀️", 12, sun_classic.generer_pdf)
_enregistrer_paire("wiz_classic", "WIZ CLASSIC", "🧙", 12, wiz_classic.generer_pdf)
_enregistrer_paire("rai_classic", "RAI CLASSIC", "🌈", 12, rai_classic.generer_pdf)
_enregistrer_paire("tahaa_classic", "TAHAA CLASSIC", "🥥", 18, tahaa_classic.generer_pdf)
_enregistrer_paire("ani",           "TEAHUPOO",        "🌊", 8, ani.generer_pdf)
_enregistrer_paire("brown14",       "BROWN 14 boules", "🟤", 16, brown14.generer_pdf)
_enregistrer_paire("ino8",          "INO 8 boules", "🎐", 12, ino8.generer_pdf)
_enregistrer_paire("ino",           "INO 5 boules", "🎏", 12, ino.generer_pdf)
_enregistrer_paire("tahaa",         "TAHAA",      "🥥", 8, tahaa.generer_pdf)
_enregistrer_paire("tahaa90",       "TAHAA 90",   "\U0001f41b", 8,  tahaa90.generer_pdf)
_enregistrer_paire("baam",          "BAAM",       "\U0001f388", 8,  baam.generer_pdf)
_enregistrer_paire("papeari",       "PAPEARI",    "\U0001f38a", 8,  papeari.generer_pdf)
_enregistrer_paire("boules60",      "60 BOULES",  "🔵", 8, boules60.generer_pdf)
_enregistrer_paire("ahuru",         "AHURU",      "🔟", 10, ahuru.generer_pdf)
_enregistrer_paire("tchin",         "TCHIN",      "🍻", 12, tchin.generer_pdf)
_enregistrer_paire("ing",           "ING CLASSIC",        "🧭", 12, ing.generer_pdf)
_enregistrer_paire("perle",         "PERLE",      "\U0001f9aa", 8,  perle.generer_pdf)
_enregistrer_paire("hunter",        "HUNTER",     "\U0001f3af", 5,  hunter.generer_pdf)
_enregistrer_paire("echec_et_mat",  "\u00c9CHEC ET MAT", "\u265f\ufe0f", 12, echec_et_mat.generer_pdf)
_enregistrer_paire("pomare",        "POMARE",     "\U0001f451", 8,  pomare.generer_pdf)
_enregistrer_paire("unite",         "UNIT\u00c9",     "\U0001f497", 10, unite.generer_pdf)
_enregistrer_paire("talon",         "TALON",      "\u26bd", 12,  talon.generer_pdf)
_enregistrer_paire("hoanui",        "HOANUI",     "\U0001f932", 8,  hoanui.generer_pdf)
_enregistrer_paire("cristal",       "LES 7 BOULES DE CRISTAL", "\U0001f52e", 14, cristal.generer_pdf)
_enregistrer_paire("sicile",        "SICILE",     "\U0001f451", 8,  sicile.generer_pdf)
_enregistrer_paire("tifai",         "TIFAI",      "\U0001f422", 8,  tifai.generer_pdf)
_enregistrer_paire("ranihei",       "RANIHEI",    "\U0001f33a", 6,  ranihei.generer_pdf)
_enregistrer_paire("mabuhai",       "MABUHA\u00cf",   "\U0001f64f", 6,  mabuhai.generer_pdf)
_enregistrer_paire("raromatai90",   "RAROMATAI 90", "\U0001f334", 2,  raromatai90.generer_pdf)
_enregistrer_paire("raromatai75",   "RAROMATAI 75", "\U0001f334", 2,  raromatai75.generer_pdf)
_enregistrer_paire("alalia",        "VIN CORSE ALALIA", "\U0001f347", 12, alalia.generer_pdf)
_enregistrer_paire("speed90",       "SPEED 90",   "\u26a1", 8,  speed90.generer_pdf)
_enregistrer_paire("joker",         "JOKER",      "\U0001f0cf", 6,  joker.generer_pdf)
_enregistrer_paire("vanira",        "VANIRA",     "\U0001f33c", 8,  vanira.generer_pdf)
_enregistrer_paire("sangogo",       "SANGOGO",    "\u2b50", 6,  sangogo.generer_pdf)
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
_enregistrer_paire("zin",           "ZIN",        "⚡", 16, zin.generer_pdf)
_enregistrer_paire("rai",           "RAI",        "🌈", 12, rai.generer_pdf)
_enregistrer_paire("bin6",          "BIN 6 boules", "\U0001f3af", 12, bin6.generer_pdf)
_enregistrer_paire("bin8",          "BIN 8 boules", "🎯", 12, bin8.generer_pdf)
_enregistrer_paire("pow6",          "POW 5 boules", "💫", 12, pow6.generer_pdf)
_enregistrer_paire("bg90",          "BG 90",      "🎱", 12, bg90.generer_pdf)
_enregistrer_paire("bo90",          "BO 90",      "🟠", 16, bo90.generer_pdf)
_enregistrer_paire("bn90",          "BN 90",      "🟤", 12, bn90.generer_pdf)
_enregistrer_paire("bi90",          "BI 90",      "🔵", 16, bi90.generer_pdf)
_enregistrer_paire("bgo5",          "BGO 5 boules", "🅾️", 12, bgo5.generer_pdf)
_enregistrer_paire("tiki",          "BGO TIKI",   "🗿", 8, tiki.generer_pdf)
_enregistrer_paire("bo75",          "BO 75",      "🔷", 16, bo75.generer_pdf)
_enregistrer_paire("bg75",          "BG 75",      "💠", 12, bg75.generer_pdf)
_enregistrer_paire("bn75",          "BN 75",      "🔶", 12, bn75.generer_pdf)
_enregistrer_paire("bi75",          "BI 75",      "💙", 16, bi75.generer_pdf)
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
    "lundi_pair74": (2, 74),      # 🌙 LUNDI PAIR 74 — que des PAIRS (liste exacte plus bas)
    "mardi_pair90": (2, 90),      # ☀️ MARDI PAIR 90 — que des PAIRS (liste exacte plus bas)
    "roma6": (2, 90),             # 🏛️ ROMA · 6 boules — que des PAIRS (liste exacte plus bas)
    # 🦪 AHE : trois perles, trois plages — B (1-15), I (16-30) et 76-90.
    #    Le tireur ne sort donc JAMAIS un numero entre 31 et 75 : la liste
    #    exacte des 45 boules est plus bas, dans _BOULES_CALLER.
    "ahe": (1, 90),
    # 🌸 BLOSSOM PEARL : quatre groupes, quatre plages — B (1-15),
    #    I (16-30), N (31-45) et les perles du tour G (46-60). Le tireur
    #    ne sort donc JAMAIS au-dessus de 60.
    "blossom_pearl": (1, 60),
    # 🏝️ MAKEMO : trois groupes — les 2 boules de gauche sur le I (16-30),
    #    les 2 du milieu sur le N (31-45), celle de droite sur 76-90. Le
    #    tireur ne sort donc JAMAIS un numero entre 1 et 15, ni entre 46
    #    et 75 : la liste exacte des 45 boules est plus bas, dans
    #    _BOULES_CALLER.
    "makemo": (16, 90),
    # 🐢 TUREIA · RANIHEI : cinq colonnes de 2 — B, I, N, G et le O
    #    etendu jusqu a 90. Univers complet, 1 a 90.
    "tureia_ranihei": (1, 90),
    "pol": (30, 60),
    "sun": (1, 24),
    "sun_casino": (1, 24),
    "p6_casino": (1, 75),
    "pow": (1, 27),
    "pow9": (1, 27),
    "pow_halloween": (1, 27),
    "pow_casino": (1, 27),
    "poe_parau": (1, 90),
    "poe": (45, 90),
    "bng": (1, 60),
    "hakari": (1, 75),
    "henua_enana": (1, 75),
    "tiare": (50, 90),
    "tiare_halloween": (50, 90),
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
    "valider_halloween": (31, 75),
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
    "wow6": (30, 59),
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
    # 🌺 les jumeaux CLASSIC tirent dans le même sac que leurs frères
    "win_classic": (1, 45),
    "kai_classic": (1, 29),
    "sun_classic": (1, 24),
    "wiz_classic": (1, 45),
    "rai_classic": (30, 59),
    "tahaa_classic": (1, 75),
    "aloha75_classic": (1, 75),
    "bingo_ball_classic": (1, 75),
    "brown8_classic": (1, 75),
    "pol_classic": (30, 60),
    "rubis75_classic": (1, 75),
    "losange_classic": (1, 75),
    "ani_classic": (61, 90),
    "wow4_classic": (30, 60),
    "wow6_classic": (30, 59),
    "moon_classic": (1, 75),
    "dual_dab_classic": (1, 75),
    "boules40_classic": (1, 40),
    "cerf_volant_classic": (1, 75),
    "boules60_classic": (1, 60),
    "lagoon_classic": (1, 50),
    "fan90_classic": (1, 90),
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
    "perle": (16, 60),
    "hunter": (1, 90),
    "echec_et_mat": (1, 90),
    "pomare": (1, 90),
    "unite": (1, 75),
    "talon": (1, 90),
    "hoanui": (1, 90),
    "cristal": (1, 90),
    "sicile": (1, 75),
    "tifai": (1, 75),
    "ranihei": (1, 90),
    "mabuhai": (1, 75),
    "raromatai90": (1, 90),
    "raromatai75": (1, 75),
    "alalia": (1, 75),
    "speed90": (1, 90),
    "joker": (1, 75),
    "vanira": (1, 90),
    "sangogo": (1, 75),
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
    "tiki": (1, 75),
    "bo75": (1, 75),
    "bg75": (1, 75),
    "bn75": (1, 75),
    "bi75": (1, 75),
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
    "tiki": [n for n in range(1, 16)] + [n for n in range(46, 76)],  # BGO TIKI — B 1-15 · G 46-60 · O 61-75
    "bo75": [n for n in range(1, 16)] + [n for n in range(46, 76)],  # BO 75 — B 1-15 · O 46-60 · 75 61-75
    "bg75": [n for n in range(1, 16)] + [n for n in range(46, 76)],  # BG 75 — B 1-15 · G 46-60 · 75 61-75
    "bn75": [n for n in range(1, 16)] + [n for n in range(31, 46)] + [n for n in range(61, 76)],  # BN 75 — B 1-15 · N 31-45 · 75 61-75
    "bi75": [n for n in range(1, 31)] + [n for n in range(61, 76)],  # BI 75 — B 1-15 · I 16-30 · 75 61-75
    "ok": [n for n in range(1, 31)] + [n for n in range(46, 76)],       # OK — B/I/G/O : 1-30 et 46-75 (le 31-45 n'existe pas)
    "vision": [n for n in range(1, 31)] + [n for n in range(46, 76)],   # VISION — le 31-45 n'existe pas
    "taptap": [n for n in range(1, 16)] + [n for n in range(46, 91)],   # TAP TAP — le 16-45 n'existe pas
    "joie": [n for n in range(16, 31)] + [n for n in range(46, 76)],    # JOIE — le 1-15 et le 31-45 n'existent pas
    "caller": [n for n in range(1, 16)] + [n for n in range(46, 76)],   # CALLER — le 16-45 n'existe pas
    "chance": [n for n in range(1, 16)] + [n for n in range(31, 46)] + [n for n in range(76, 91)],  # CHANCE — trèfles 1-15 · 31-45 · 76-90
    "opoa": [n for n in range(1, 76)],  # OPOA — 6 numeros B 1-15 · I 16-30 · N 31-45 · G 46-60 · O 61-75 (le 76-90 n'existe pas)
    "australes": [n for n in range(1, 16)] + [n for n in range(31, 46)] + [n for n in range(61, 76)],  # AUSTRALES — 5 numeros B 1-15 · N 31-45 · O 61-75 (le 16-30 et 46-60 n'existent pas)
    "hakari": [n for n in range(1, 46)] + [n for n in range(61, 76)],  # HAKARI — B 1-15 · I 16-30 · N 31-45 · O 61-75
    "hakari_halloween": [n for n in range(1, 46)] + [n for n in range(61, 76)],  # HAKARI HALLOWEEN — meme regle
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
    "lundi_pair74": [n for n in range(2, 75, 2)],  # 🌙 LUNDI PAIR 74 — 37 boules, QUE DES PAIRS de 2 à 74
    "mardi_pair90": [n for n in range(2, 91, 2)],  # ☀️ MARDI PAIR 90 — 45 boules, QUE DES PAIRS de 2 à 90
    "roma6": [n for n in range(2, 91, 2)],  # 🏛️ ROMA · 6 boules — 45 boules, QUE DES PAIRS de 2 à 90
    # 🦪 AHE — 45 boules : B 1-15, I 16-30, puis 76-90. Rien entre 31 et 75.
    "ahe": [n for n in range(1, 31)] + [n for n in range(76, 91)],
    # 🌸 BLOSSOM PEARL — 60 boules, de 1 a 60, sans trou.
    "blossom_pearl": [n for n in range(1, 61)],
    # 🏝️ MAKEMO — 45 boules : I 16-30, N 31-45, puis 76-90. Rien en
    #    dessous de 16, rien entre 46 et 75.
    "makemo": [n for n in range(16, 46)] + [n for n in range(76, 91)],
    # 🐢 TUREIA · RANIHEI — 90 boules, de 1 a 90, sans trou.
    "tureia_ranihei": [n for n in range(1, 91)],
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

    # ═══ 🏪 LA VITRINE PUBLIQUE NE MONTRE QUE LES JEUX DE LA MAISON ═══
    # (sceau Maeva 17/09) Un visiteur de manaprint.app est chez 2KEA &
    # Associé : il n'y voit pas les jeux dessinés par une autre enseigne.
    # RANIHEI vend les siens dans SA propre boutique, pas dans celle-ci.
    # ⚠️ CE FILTRE NE VAUT QUE POUR LE PUBLIC. Une enseigne CONNECTÉE voit
    #    tout le catalogue, y compris les jeux des autres : elle peut les
    #    fabriquer en payant les droits, c'est tout l'objet de
    #    JEUX_PROPRIETAIRE. Ne jamais étendre ce filtre aux partenaires.
    # ⭐ 17/09 : les jeux d'une AUTRE enseigne RESTENT VISIBLES au public,
    #    mais porteurs d'un « vendu_par » : la page affiche alors les
    #    coordonn\u00e9es de la cr\u00e9atrice au lieu du bouton d'achat.
    #    C'est mieux que de les cacher : la cliente voit le jeu, apprend
    #    qui l'a dessin\u00e9, et sait o\u00f9 le trouver.
    _public = not _slug
    _jeux = []
    for jid, j in REGISTRE_JEUX.items():
        if "_p15" in jid:                         # 🌙 PREMIUM en veilleuse
            continue
        if _base_jeu(jid) in _interdits:          # 🔒 réservés à leur enseigne
            continue
        fiche = {"id": jid, "nom": j["nom"], "emoji": j["emoji"],
                 "cartes_par_feuille": j["cartes_par_feuille"],
                 "couleur": j["couleur"]}
        if _public:
            ailleurs = _vitrine_autre(jid)
            if ailleurs:
                fiche["vendu_par"] = ailleurs
        _jeux.append(fiche)
    return jsonify({"ok": True, "jeux": _jeux})


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
    # ═══ 🏪 LE VERROU DE LA VITRINE, CÔTÉ SERVEUR (sceau Maeva 17/09) ═══
    # Le filtre de /api/jeux cache les jeux d'une autre enseigne, mais un
    # client pourrait encore forcer l'adresse avec leur identifiant. Ici
    # on refuse pour de bon : la boutique de 2KEA ne vend QUE les jeux de
    # 2KEA et ceux qui n'appartiennent à personne.
    # ⚠️ Cette fonction ne sert QUE la vente publique — les partenaires
    #    passent par /api/partenaire/generer, qui a ses propres règles.
    _pro_jeu = JEUX_PROPRIETAIRE.get(_base_jeu(str(programme)))
    if _pro_jeu not in (None, ENSEIGNE_MAISON):
        _nom_pro = (PARTENAIRES.get(_pro_jeu, {}) or {}).get("nom", _pro_jeu)
        return (jsonify({"ok": False, "message":
                "Ce jeu est vendu par " + _nom_pro + ", dans sa propre boutique."}), 403), None

    couleur = REGISTRE_JEUX.get(programme, {}).get("couleur", True)
    nb_feuilles = int(data.get("nb_feuilles", 25))
    # 📦 Vente par PAQUETS DE 25 feuilles (25, 50, 75… jusqu'à 500)
    # ⚠ 23/09 : le code acceptait DÉJÀ 500 mais le message d'erreur disait
    #   encore 250 — un client à qui on refusait 512 feuilles lisait qu'il ne
    #   pouvait pas dépasser 250. Les deux disent maintenant la même chose.
    if nb_feuilles < 25 or nb_feuilles > 500 or nb_feuilles % 25 != 0:  # 1 à 20 paquets de 25 (27/07)
        return (jsonify({"ok": False, "message": "Les feuilles se commandent par paquets de 25 (25, 50, 75… jusqu'à 500)."}), 400), None

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
    # 💵 ① LES BILLETS d'abord — ils ont leur tarif à eux (200 F N&B / 375 F
    #    couleur). Ce test vient EN PREMIER, sinon ils retomberaient ailleurs.
    if (prix_special is None
            and session.get("acces") != "international"
            and db._gamme_du_programme(programme) == "eco"
            and _base_jeu(programme) in TARIF_BILLETS_250):
        prix_special = PRIX_BILLETS_COULEUR if couleur else PRIX_BILLETS
    # 🖼️ ② LES JEUX À IMAGE : 225 F en N&B, 375 F en couleur.
    #    ⚠️ EN NOIR & BLANC, les dix jeux de TARIF_NB_150 sont épargnés :
    #    ils gardent leurs 150 F, c'est la volonté de Maeva.
    if (prix_special is None
            and session.get("acces") != "international"
            and db._gamme_du_programme(programme) == "eco"
            and _base_jeu(programme) in JEUX_AVEC_IMAGE):
        if _base_jeu(programme) in IMAGE_TARIF_NB_ORDINAIRE:
            # ces quatre-là paient comme un jeu sans dessin, des deux côtés :
            # 185 F en N&B ; en couleur on laisse le tarif de base (250 F).
            if not couleur:
                prix_special = PRIX_NB_AUTRES      # 185 F les 25
        elif couleur:
            prix_special = PRIX_IMAGE_COULEUR      # 375 F les 25
        elif _base_jeu(programme) not in TARIF_NB_150:
            prix_special = PRIX_IMAGE_NB           # 225 F les 25
    # ⚫ ③ LE NOIR & BLANC ORDINAIRE : 185 F, sauf les 150 F historiques.
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

# ══ 💳 LES MODES DE PAIEMENT OUVERTS (sceau Maeva 02/09) ══════════════════
# ⚠️⚠️ LA CARTE EST LE SEUL MOYEN ACCEPTÉ. « boutique » et « virement » ont
# été FERMÉS : trop de commandes enregistrées n'étaient jamais honorées.
# ⭐ POUR EN ROUVRIR UN : ajoute son nom ici, et remets son bouton dans
#    templates/index.html (les deux lignes y sont en commentaire).
#    Exemple :  _MODES_PAIEMENT = {"stripe", "virement"}
_MODES_PAIEMENT = {"stripe"}
_MSG_CARTE_SEULE = ("\U0001f4b3 Le paiement se fait par CARTE uniquement. "
                    "Un souci pour payer ? Appelle le 89 22 23 05.")


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
    # 💳 la carte est le seul mode ouvert : tout le reste est refusé d'entrée
    mode_paiement = data.get("mode_paiement", "stripe")
    if mode_paiement == "manuel":          # compat ancien front
        mode_paiement = "boutique"
    if mode_paiement not in _MODES_PAIEMENT:
        return jsonify({"ok": False, "message": _MSG_CARTE_SEULE}), 400
    err, res = _valider_creer_commande(data, mode_paiement=mode_paiement)
    if err:
        return err
    commande_id, montant = res["commande_id"], res["montant"]

    # 💳 Mode stripe : mini-panier d'une seule commande -> paiement carte
    if not STRIPE_SECRET_KEY:
        return jsonify({"ok": False,
                        "message": "\U0001f4b3 Le paiement par carte est momentanément indisponible. Appelle le 89 22 23 05."}), 400
    try:
        panier_id = db.creer_panier(session.get("identifiant"))
        with db.get_db() as conn:
            conn.execute("UPDATE commandes SET panier_id = ? WHERE id = ?", (panier_id, commande_id))
        url, total = _session_stripe_panier(panier_id, mana_utilises=_mana_demandes())
        return jsonify({"ok": True, "mode": "stripe", "url": url, "montant": total})
    except Exception as e:
        print(f"[STRIPE ERREUR] commander : {e}")
        return jsonify({"ok": False, "message": "\U0001f4b3 Paiement par carte momentanément indisponible. Réessaie dans un instant ou appelle le 89 22 23 05."}), 502


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
    # 💳 la carte est le seul mode ouvert (voir _MODES_PAIEMENT plus haut)
    if mode_paiement not in _MODES_PAIEMENT:
        return jsonify({"ok": False, "message": _MSG_CARTE_SEULE}), 400
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
                        "message": "\U0001f4b3 Le paiement par carte est momentanément indisponible. Appelle le 89 22 23 05."}), 400
    try:
        url, total = _session_stripe_panier(panier_id, mana_utilises=_mana_demandes())
        return jsonify({"ok": True, "mode": "stripe", "url": url, "montant": total, "panier_id": panier_id})
    except Exception as e:
        print(f"[STRIPE ERREUR] checkout : {e}")
        return jsonify({"ok": False, "message": "\U0001f4b3 Paiement par carte momentanément indisponible. Réessaie dans un instant ou appelle le 89 22 23 05."}), 502


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
            # ⚡⚡ 03/09 — LE BOUTON ⬇️ S'ALLUME ICI, PAS APRÈS LES EMAILS.
            # Avant, la commande n'était marquée « générée » qu'une fois les
            # deux emails partis, PIÈCES JOINTES COMPRISES (plusieurs Mo par
            # SMTP). Le partenaire attendait donc Gmail, pas la fabrication —
            # d'où l'impression que le téléchargement traînait. Le PDF est
            # DÉJÀ au coffre à cette ligne : on l'annonce tout de suite, et
            # les emails partent ensuite, tranquillement.
            try:
                db.marquer_commande_generee(commande_id)
                print(f"[COFFRE] commande {commande_id} — cartons rangés, "
                      f"bouton \u2b07\ufe0f disponible immédiatement")
            except Exception as _e:
                print(f"[COFFRE] marquage {commande_id} : {_e}")
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
            # 🗄️ (la commande est DÉJÀ marquée « générée » plus haut, dès le
            # rangement au coffre — on ne le refait pas ici.)
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
            _ann = ANNONCES_PARTENAIRE.get(slug)
            return jsonify({"ok": True, "nom": part["nom"], "zone": part.get("zone", ""),
                            "annonce_titre": (_ann[0] if _ann else ""),
                            "annonce_texte": (_ann[1] if _ann else "")})
    return jsonify({"ok": False, "message":
                    "Code partenaire inconnu \u2014 v\u00e9rifiez lettres et chiffres "
                    "(les tirets et espaces n'ont pas d'importance)."})


@app.route("/api/partenaire/droits", methods=["GET"])
def api_partenaire_droits():
    """©️ LES DROITS QUI M'ATTENDENT : les commandes d'autres enseignes sur
    MES dessins, encore en attente de règlement.
    ⚠️ On ne montre QUE les jeux dont ce partenaire est propriétaire —
       jamais ceux d'une autre enseigne."""
    slug = session.get("partenaire_slug")
    if not slug:
        return jsonify({"ok": False, "message": "Connectez-vous."}), 403
    mes_jeux = {j for j, pro in JEUX_PROPRIETAIRE.items() if pro == slug}
    if not mes_jeux:
        return jsonify({"ok": True, "droits": [], "total": 0})
    import json as _json
    out, total = [], 0
    try:
        with db.get_db() as conn:
            rows = conn.execute(
                "SELECT id, programme, nb_feuilles, montant, cree_le, params_perso, statut "
                "FROM commandes WHERE mode_paiement = 'fabrique_droit' "
                "  AND statut = 'en_attente' ORDER BY id DESC").fetchall()
        for r in rows:
            if _base_jeu(str(r["programme"] or "")) not in mes_jeux:
                continue
            try:
                perso = _json.loads(r["params_perso"] or "{}")
            except Exception:
                perso = {}
            demandeur = perso.get("partenaire", "")
            out.append({
                "id": r["id"],
                "date": (r["cree_le"] or "")[:16].replace("T", " "),
                "jeu": REGISTRE_JEUX.get(r["programme"], {}).get("nom", r["programme"]),
                "enseigne": (PARTENAIRES.get(demandeur, {}) or {}).get("nom", demandeur),
                "nb_feuilles": r["nb_feuilles"], "montant": r["montant"] or 0,
            })
            total += r["montant"] or 0
    except Exception as e:
        print("[DROITS] lecture impossible :", e)
        return jsonify({"ok": False, "message": "Lecture impossible."}), 500
    return jsonify({"ok": True, "droits": out, "total": total})


@app.route("/api/partenaire/droits/<int:commande_id>/valider", methods=["POST"])
def api_partenaire_valider_droit(commande_id):
    """©️ LE PROPRIÉTAIRE ENCAISSE ET DÉBLOQUE. Il confirme avoir été réglé :
    le PDF part alors à l'enseigne qui l'a demandé.
    ⚠️⚠️ TROIS VERROUS, tous côté serveur :
        ① il faut être connecté comme partenaire ;
        ② la commande doit être un DROIT en attente ;
        ③ le jeu doit lui appartenir À LUI — sinon 403.
       Sans ce troisième verrou, une enseigne pourrait débloquer les
       commandes d'une autre et se servir dans ses recettes."""
    slug = session.get("partenaire_slug")
    if not slug:
        return jsonify({"ok": False, "message": "Connectez-vous."}), 403
    cmd = db.get_commande(commande_id)
    if not cmd:
        return jsonify({"ok": False, "message": "Commande introuvable."}), 404
    if cmd.get("mode_paiement") != "fabrique_droit" or cmd.get("statut") != "en_attente":
        return jsonify({"ok": False, "message": "Cette commande n'attend pas de r\u00e8glement."}), 400
    if JEUX_PROPRIETAIRE.get(_base_jeu(str(cmd.get("programme") or ""))) != slug:
        return jsonify({"ok": False, "message": "Ce jeu ne vous appartient pas."}), 403
    db.marquer_commande_payee(commande_id)
    nom_part = lancer_fabrication(commande_id)
    return jsonify({"ok": True, "message":
                    ("\u2705 R\u00e8glement confirm\u00e9 \u2014 le PDF part \u00e0 "
                     + (nom_part or "l'enseigne") + ".")})


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
    if _jeu_exclusif_refuse(slug, programme):
        return jsonify({"ok": False,
                        "message": "Ce jeu appartient \u00e0 une autre enseigne."}), 403
    if _jeu_interdit(slug, programme):
        return jsonify({"ok": False,
                        "message": "Ce jeu n'est pas disponible pour votre enseigne. "
                                   "Contactez 2KEA."}), 403
    try:
        nb_feuilles = int(data.get("nb_feuilles") or 0)
    except Exception:
        nb_feuilles = 0
    # ⭐⭐ 23/09 (sceau Maeva : « dans mon espace partenaire je veux pouvoir
    #    générer 500 feuilles au lieu de 250 ») : LE PLAFOND PASSE À 500.
    #    Soit 20 paquets de 25 au lieu de 10, en une seule fabrication.
    #    ⚠ Les quotas ne bougent PAS : les 3 000 feuilles offertes par jeu et
    #    le cadeau sur les jeux à image s'appliquent exactement pareil, et une
    #    commande à cheval sur l'offert et le payant est toujours refusée.
    #    Le partenaire consomme simplement son crédit deux fois plus vite.
    #    ⚠ La liste déroulante de templates/partenaire.html doit monter
    #    jusqu'à 500 elle aussi, sinon le choix n'apparaît pas à l'écran.
    if nb_feuilles < 25 or nb_feuilles > 500 or nb_feuilles % 25:
        return jsonify({"ok": False, "message": "Choisissez de 25 \u00e0 500 feuilles, par paquets de 25."}), 400

    # ═══ 🎁 LE QUOTA DES JEUX À IMAGE (sceau Maeva 15/08) ═══
    # Le partenaire reçoit un nombre de feuilles OFFERTES sur les jeux
    # habillés. Au-delà, chaque feuille lui est due à 1,5 F.
    # ⚠️ On refuse une commande À CHEVAL sur les deux : le partenaire
    # prend d'abord ce qui lui reste d'offert, puis repasse commande.
    # C'est plus honnête que de lui faire perdre son solde.
    _mode = "fabrique_partenaire"      # gratuit par défaut
    _prix = 0

    # ═══ 🚦 LE QUOTA PAR JEU : 3 000 feuilles offertes sur CHAQUE jeu ═══
    # ⚠️ Comme pour le quota des jeux à image, on REFUSE une commande à
    #    cheval sur les deux côtés : l'enseigne prend d'abord ce qui lui
    #    reste d'offert, puis repasse commande pour le payant. C'est plus
    #    honnête que de lui faire perdre son solde.
    # ═══ ©️ LE JEU D'UNE AUTRE ENSEIGNE : dû dès la première feuille ═══
    # Pas de forfait ici : le dessin n'est pas le sien, chaque feuille est
    # due au propriétaire et le PDF attend la validation de 2KEA.
    _proprio = JEUX_PROPRIETAIRE.get(_base_jeu(programme))
    if _jeu_d_une_autre(slug, programme):
        _mode = "fabrique_droit"
        _prix = PRIX_FEUILLE_DROIT

    # 🏠 la maison n'a ni quota ni plafond sur ses propres fabrications
    _maison = (slug == ENSEIGNE_MAISON)
    _faits_jeu = 0 if _maison else _feuilles_faites_sur_jeu(slug, programme)
    _reste_jeu = 10 ** 9 if _maison else max(0, QUOTA_PAR_JEU - _faits_jeu)
    _nom_jeu = REGISTRE_JEUX.get(programme, {}).get("nom", programme)
    if _mode == "fabrique_droit":
        pass                      # déjà payant : le quota ne s'applique pas
    elif nb_feuilles > _reste_jeu:
        if _reste_jeu == 0:
            _mode = "fabrique_quota"
            _prix = PRIX_FEUILLE_QUOTA
        else:
            return jsonify({"ok": False, "message":
                (f"\U0001f6a6 Il vous reste {_reste_jeu} feuille(s) offerte(s) sur "
                 f"{_nom_jeu} (sur {QUOTA_PAR_JEU}). Prenez {_reste_jeu} feuilles "
                 f"pour finir votre cr\u00e9dit, puis les suivantes vous seront "
                 f"compt\u00e9es \u00e0 {PRIX_FEUILLE_QUOTA} F la feuille.")}), 400

    _quota = None if _maison else QUOTA_HABILLES.get(slug)
    if _quota is not None and _base_jeu(programme) in JEUX_AVEC_IMAGE:
        _faites = _feuilles_habillees_faites(slug)
        _reste = max(0, int(_quota) - _faites)
        if nb_feuilles <= _reste:
            pass                        # tout tient dans l'offert
        elif _reste == 0:
            _mode = "fabrique_habillee"   # tout est dû
            _prix = PRIX_FEUILLE_HABILLEE
        else:
            return jsonify({"ok": False, "message":
                (f"\U0001f381 Il vous reste {_reste} feuille(s) offerte(s) sur les jeux "
                 f"\u00e0 image (sur {int(_quota)}). Prenez {_reste} feuilles pour finir "
                 f"votre cadeau, puis les suivantes vous seront compt\u00e9es "
                 f"\u00e0 {PRIX_FEUILLE_HABILLEE} F la feuille.")}), 400
    enseigne = (str(data.get("titre") or "").strip() or part.get("enseigne_pdf") or part["nom"])[:40]
    telephone = (str(data.get("telephone") or "").strip() or part.get("tel_pdf") or part.get("tel", ""))[:24]
    # 🎨 02/10 (sceau Maeva : « peut-on choisir sa couleur aussi en option »)
    #   Le partenaire peut imposer UNE seule couleur à tout son lot. Vide =
    #   arc-en-ciel (le comportement d'avant). On n'accepte qu'un code
    #   hexadécimal #RRGGBB — tout le reste est ignoré (vide). Sans effet sur
    #   une fabrication en noir & blanc : les générateurs n'y touchent pas.
    import re as _re_cp
    _couleur_perso = str(data.get("couleur_perso") or "").strip()
    if not _re_cp.match(r"^#[0-9a-fA-F]{6}$", _couleur_perso):
        _couleur_perso = ""
    perso = _json.dumps({
        "theme": "", "nom_evenement": enseigne, "titre_jeu": enseigne,
        "couleur_perso": _couleur_perso, "date_lieu": part.get("zone", ""), "telephone": telephone,
        "partenaire": slug,
        # 🖨️ la case « Impression rapide » de l'espace partenaire
        "impression_rapide": bool(data.get("impression_rapide", True)),
    })
    commande_id, _ = db.creer_commande(
        identifiant=enseigne, origine="polynesien",
        programme=programme, couleur=REGISTRE_JEUX[programme].get("couleur", True),
        nb_feuilles=nb_feuilles, mode_paiement=_mode,
        params_perso=perso, prix_feuille=_prix,
    )
    # ═══ 🔐 LE DÉPASSEMENT ATTEND LA VALIDATION DE 2KEA (sceau Maeva 17/09)
    # Dans son forfait, rien ne change : la commande est payée d'office et
    # le PDF part tout de suite.
    # DÈS QU'ELLE DÉPASSE, LE PDF N'EST PAS FABRIQUÉ : la commande reste en
    # attente, et Maeva la valide depuis l'admin (« Valider la commande »),
    # ce qui déclenche alors la fabrication et l'envoi.
    # ⚠️⚠️ NE JAMAIS appeler lancer_fabrication() ici pour un dépassement :
    #    ce serait livrer le PDF avant d'avoir été payée.
    _payant = _mode in ("fabrique_quota", "fabrique_habillee", "fabrique_droit")
    if _payant:
        try:
            with db.get_db() as conn:
                conn.execute("UPDATE commandes SET statut = 'en_attente' WHERE id = ?",
                             (commande_id,))
                conn.commit()
        except Exception as e:
            print("[QUOTA] mise en attente impossible :", e)
    else:
        db.marquer_commande_payee(commande_id)
        lancer_fabrication(commande_id)
    jeu = REGISTRE_JEUX.get(programme, {})
    _sup = ""
    if _quota is not None and _base_jeu(programme) in JEUX_AVEC_IMAGE:
        _apres = _feuilles_habillees_faites(slug)
        if _mode == "fabrique_habillee":
            _sup = (f" \u2014 \U0001f4b0 {nb_feuilles} feuilles \u00e0 "
                    f"{PRIX_FEUILLE_HABILLEE} F = {round(nb_feuilles * PRIX_FEUILLE_HABILLEE)} F "
                    f"(votre cadeau de {int(_quota)} feuilles est \u00e9puis\u00e9).")
        else:
            _sup = (f" \u2014 \U0001f381 offert : il vous reste "
                    f"{max(0, int(_quota) - _apres)} feuille(s) sur {int(_quota)}.")
    if _mode == "fabrique_droit":
        _nom_pro = {"ranihei": "RANIHEI SISTERS & SHOP",
                    "2kea_papeete": "2KEA & Associ\u00e9"}.get(_proprio, _proprio)
        _tel_pro = (PARTENAIRES.get(_proprio, {}) or {}).get("tel", "")
        _sup = (f" \u2014 \u00a9\ufe0f Ce jeu appartient \u00e0 {_nom_pro} : "
                f"{nb_feuilles} feuilles \u00e0 {PRIX_FEUILLE_DROIT} F = "
                f"{round(nb_feuilles * PRIX_FEUILLE_DROIT)} F de droits. "
                f"VOTRE PDF EST EN ATTENTE : r\u00e9glez {_nom_pro}"
                + (f" ({_tel_pro})" if _tel_pro else "")
                + ", c'est cette enseigne qui d\u00e9bloquera votre PDF.")
    elif _payant:
        _sup = (f" \u2014 \U0001f510 {nb_feuilles} feuilles au-del\u00e0 de votre forfait "
                f"= {round(nb_feuilles * _prix)} F. VOTRE PDF EST EN ATTENTE : il vous "
                f"sera envoy\u00e9 d\u00e8s que 2KEA aura valid\u00e9 le r\u00e8glement. "
                f"T\u00e9l. 89 22 23 05.")
    return jsonify({"ok": True, "commande_id": commande_id, "supplement": _sup,
                    "message": (f"\U0001f5a8\ufe0f Fabrique #{commande_id} lanc\u00e9e : {nb_feuilles} feuilles de "
                                f"{jeu.get('emoji','')} {jeu.get('nom', programme)} \u00e0 l'enseigne \u00ab {enseigne} \u00bb \u2014 "
                                "appuyez sur \u21bb dans 1-2 minutes, le bouton \u2b07\ufe0f Cartons appara\u00eetra." + _sup)})


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
# ═════════════════════════════════════════════════════════════════════
# 🐉 DRAGON D'OR  et  🐟 FAFAPITI — inscription du 24/09/2026
# ⚠️ NE RIEN METTRE APRÈS : ce bloc doit rester le dernier du fichier.
# ═════════════════════════════════════════════════════════════════════
from generators import dragon_or      # 🐉 création RANIHEI du 24/09
from generators import fafapiti       # 🐟 création RANIHEI du 24/09

JEUX_PROPRIETAIRE["dragon_or"] = "ranihei"
JEUX_PROPRIETAIRE["fafapiti"] = "ranihei"

# ⚠️ INDISPENSABLE : _imposer_gris_maison() a déjà tourné bien plus haut,
#    AVANT que ces deux jeux ne soient chargés. Sans ce rappel ils
#    sortiraient plus foncés que tout le reste du catalogue.
_GRIS_POSES = _imposer_gris_maison()

# ⚠️ 6 cartons par feuille pour les deux : ce chiffre doit TOUJOURS
#    suivre COLS_PAGE x ROWS_PAGE du générateur.
_enregistrer_paire("dragon_or", "DRAGON D'OR", "\U0001f409", 6, dragon_or.generer_pdf)
_enregistrer_paire("fafapiti",  "FAFAPITI",    "\U0001f41f", 6, fafapiti.generer_pdf)

_PLAGES_CALLER["dragon_or"] = (1, 90)
_PLAGES_CALLER["fafapiti"] = (1, 75)

# 🐉 DRAGON D'OR : 90 boules, de 1 a 90, sans trou.
# 🐟 FAFAPITI    : 60 boules seulement — 1 a 30 PUIS 46 a 75.
#    ⚠️ LE N EST MORT : la plage 31-45 ne sort JAMAIS. Ne pas remplacer
#    par un simple (1, 75).
_BOULES_CALLER["dragon_or"] = [n for n in range(1, 91)]
_BOULES_CALLER["fafapiti"] = [n for n in range(1, 31)] + [n for n in range(46, 76)]
print("[RANIHEI] DRAGON D'OR et FAFAPITI inscrits — %d jeux au catalogue" % len(REGISTRE_JEUX))
# ═════════════════════════════════════════════════════════════════════
# 🎶 AREAREA — inscription du 24/09/2026 (création RANIHEI)
# ═════════════════════════════════════════════════════════════════════
from generators import arearea       # 🎶 création RANIHEI du 24/09

JEUX_PROPRIETAIRE["arearea"] = "ranihei"

# ⚠️ INDISPENSABLE : _imposer_gris_maison() a déjà tourné bien plus haut,
#    AVANT que ce jeu ne soit chargé. Sans ce rappel il sortirait plus
#    foncé que tout le reste du catalogue.
_GRIS_POSES = _imposer_gris_maison()

# ⚠️ 6 cartons par feuille : ce chiffre doit TOUJOURS suivre
#    COLS_PAGE x ROWS_PAGE dans generators/arearea.py.
_enregistrer_paire("arearea", "AREAREA", "\U0001f3b6", 6, arearea.generer_pdf)

# 🎶 AREAREA : cinq bulles, une par lettre du BINGO —
#    B 1-15 · I 16-30 · N 31-45 · G 46-60 · O 61-75.
#    75 boules, de 1 a 75, sans un trou.
_PLAGES_CALLER["arearea"] = (1, 75)
_BOULES_CALLER["arearea"] = [n for n in range(1, 76)]
print("[RANIHEI] AREAREA inscrit — %d jeux au catalogue" % len(REGISTRE_JEUX))
GRIS_PARTICULIERS.update({
    "ohana75_2series":  0.26,
    "ohana75_4series":  0.26,
    "ohana75_8boules":  0.26,
    "ohana75_10boules": 0.26,
    "ohana75_20boules": 0.26,
    "p6_marathon":      0.26,
    "ahe":              0.26,
    "blossom_pearl":    0.26,
    "makemo":           0.26,
    "tureia_ranihei":   0.26,
    "dragon_or":        0.26,
    "fafapiti":         0.26,
    "arearea":          0.26,
})
_GRIS_POSES = _imposer_gris_maison()
print("[TEINTE 25/09] gris maison %.2f sur %d jeux, dont %d jeux gras gardes a 0,26"
      % (GRIS_CHIFFRES_ECO, _GRIS_POSES, len(GRIS_PARTICULIERS)))
# ═══════════════════════════════════════════════════════════════════════
# 🎟️ 28/09 — OHANA 75 · 10 BOULES / 18 GRILLES (maquette Maeva du 28/09)
#   ⚠️ JEU NEUF. Il NE REMPLACE PAS le OHANA 75 · 10 boules : celui-ci
#   garde son identifiant "ohana75_10b", ses 9 cartons par feuille et son
#   dessin. Le nouveau vit sous "ohana75_10b18", 18 cartons par feuille.
#   Mêmes plages, même crieur : 75 boules de 1 à 75.
# ═══════════════════════════════════════════════════════════════════════
from generators import ohana75_10b18
GRIS_PARTICULIERS.update({"ohana75_10b18": 0.26})
_GRIS_POSES = _imposer_gris_maison()
_enregistrer_paire("ohana75_10b18", "OHANA 75 · 10 boules / 18 grilles",
                   "\U0001f3ab", 18, ohana75_10b18.generer_pdf)
_PLAGES_CALLER["ohana75_10b18"] = (1, 75)
_BOULES_CALLER["ohana75_10b18"] = [n for n in range(1, 76)]
print("[10B18] 10 BOULES / 18 GRILLES inscrit — %d jeux au catalogue" % len(REGISTRE_JEUX))
# ═══════════════════════════════════════════════════════════════════════
# 🎟️ 28/09 — OHANA 75 · 8 BOULES / 18 GRILLES (maquette Maeva du 28/09)
#   ⚠️ JEU NEUF. Il NE REMPLACE PAS le OHANA 75 · 8 boules, qui garde son
#   identifiant "ohana75_8b" et ses 9 cartons par feuille.
#   ⚠️⚠️ QUATRE plages seulement : le N (31 à 45) N'EXISTE PAS. L'univers
#   est 1-30 PUIS 46-75, soit 60 boules — comme l'ancien 8 boules.
# ═══════════════════════════════════════════════════════════════════════
from generators import ohana75_8b18
GRIS_PARTICULIERS.update({"ohana75_8b18": 0.26})
_GRIS_POSES = _imposer_gris_maison()
_enregistrer_paire("ohana75_8b18", "OHANA 75 · 8 boules / 18 grilles",
                   "\U0001f3ab", 18, ohana75_8b18.generer_pdf)
_PLAGES_CALLER["ohana75_8b18"] = (1, 75)
_BOULES_CALLER["ohana75_8b18"] = [n for n in range(1, 31)] + [n for n in range(46, 76)]
print("[8B18] 8 BOULES / 18 GRILLES inscrit — %d jeux au catalogue" % len(REGISTRE_JEUX))
# ═══════════════════════════════════════════════════════════════════════
# 🌿 28/09 — KEA sur sa nouvelle planche (sceau Maeva : « retire la croix »)
#   ⚠️ CE N'EST PAS UN JEU NEUF : même identifiant, mêmes plages
#   (K 35-45 · E 46-56 · A 57-67), mêmes 9 numéros par carton.
#   Les anciennes commandes se régénèrent à l'identique.
#   ⚠️⚠️ CE QUI CHANGE : 16 cartons par feuille A4 PAYSAGE au lieu de 12
#   en portrait. Sans cette réinscription la boutique facturerait 12
#   cartons par feuille alors qu'il en sort 16.
# ═══════════════════════════════════════════════════════════════════════
GRIS_PARTICULIERS.update({"kea": 0.26})
_GRIS_POSES = _imposer_gris_maison()
_enregistrer_paire("kea", "KEA", "\U0001f33f", 16, kea.generer_pdf)
print("[KEA] nouvelle planche — 16 cartons par feuille, %d jeux au catalogue" % len(REGISTRE_JEUX))
# ═════════════════════════════════════════════════════════════════════
# 💥 28/09 — POW 9 BOULES sur sa nouvelle planche (sceau Maeva)
#   ⚠️ CE N'EST PAS UN JEU NEUF : meme identifiant, memes plages
#   (colonne 1 : 1-9 · colonne 2 : 10-18 · colonne 3 : 19-27), memes
#   9 numeros par carton, le plus petit en haut. Le crieur ne change pas.
#   ⚠️⚠️ CE QUI CHANGE : 16 cartons par feuille A4 PAYSAGE au lieu de 12
#   en portrait. Sans cette reinscription la boutique facturerait 12
#   cartons par feuille alors qu'il en sort 16.
#   ⚠️⚠️ LE PANIER TRESSE DISPARAIT : sa nouvelle planche est au trait
#   pur, sans aucune image. POW 9 sort donc de JEUX_AVEC_IMAGE, sinon le
#   menu annoncerait « AVEC IMAGE » a des clientes qui recevraient un
#   carton sans dessin. (JEUX_HABILLES ne contient pas pow9 : rien ne
#   change a la facturation.)
# ═════════════════════════════════════════════════════════════════════
GRIS_PARTICULIERS.update({"pow9": 0.26})
_GRIS_POSES = _imposer_gris_maison()
JEUX_AVEC_IMAGE.discard("pow9")
_enregistrer_paire("pow9", "POW 9 boules", "\U0001f9fa", 16, pow9gen.generer_pdf)
print("[POW 9] nouvelle planche — 16 cartons par feuille, %d jeux au catalogue" % len(REGISTRE_JEUX))
# ═════════════════════════════════════════════════════════════════════
# ⚠️⚠️ 28/09 — LE PLAFOND DE 375 FEUILLES (signale par Maeva)
#   Une commande de 500 feuilles de KEA n'en sortait que 375.
#   POURQUOI : app.py tient DEUX comptes du nombre de cartons par feuille.
#     · REGISTRE_JEUX   -> ce que le menu affiche      (mis a jour)
#     · CARTES_PAR_FEUILLE -> ce qui sert a FABRIQUER  (photo prise a la
#       ligne 1094, bien avant les blocs ajoutes en fin de fichier)
#   Les jeux inscrits ou reinscrits APRES la ligne 1094 gardaient donc
#   l'ancien chiffre, ou rien du tout (et le code retombe alors sur 10).
#     KEA et POW 9 ........ table 12 au lieu de 16 -> 375 feuilles sur 500
#     10 b/18 g et 8 b/18 g table absente (=10) au lieu de 18 -> 278 sur 500
#     AREAREA, DRAGON D'OR, FAFAPITI : absente (=10) au lieu de 6
#        -> 834 feuilles sortaient pour 500 commandees (papier et toner
#           donnes, et les numeros de serie depassaient leur tranche)
#   ON REMET LA TABLE DE FABRICATION D'ACCORD AVEC LE MENU, pour tous.
#   ⭐ A GARDER : tout bloc ajoute plus bas qui change le nombre de
#      cartons par feuille doit refaire cette mise a jour APRES lui.
# ═════════════════════════════════════════════════════════════════════
_AVANT_CPF = dict(CARTES_PAR_FEUILLE)
CARTES_PAR_FEUILLE.update({_j: _v["cartes_par_feuille"] for _j, _v in REGISTRE_JEUX.items()})
_CORRIGES = sorted(_j for _j in REGISTRE_JEUX if _AVANT_CPF.get(_j) != CARTES_PAR_FEUILLE[_j])
print("[FEUILLES] table de fabrication reaccordee au menu : %d entrees corrigees" % len(_CORRIGES))
for _j in _CORRIGES:
    print("[FEUILLES]    %-28s %s -> %d cartons/feuille"
          % (_j, _AVANT_CPF.get(_j, "absent"), CARTES_PAR_FEUILLE[_j]))
# ═════════════════════════════════════════════════════════════════════
# ⚠️ 28/09 — ALLEGER LE NOIR (sceau Maeva : « la couleur noir est trop
#   forte sur les chiffres et les grilles, peut-on alleger »)
#   NIVEAU B, choisi par elle sur l'image des quatre niveaux.
#   Les cinq planches neuves : TRIO 75, 10 boules/18 grilles,
#   8 boules/18 grilles, KEA, POW 9 boules.
#   Le trait de la planche et le gras des chiffres sont dans les fichiers
#   des jeux. ICI on remet seulement la teinte des chiffres, sinon
#   _imposer_gris_maison() repose 0,26 au demarrage et tout le travail
#   est annule.
#   ⚠️ TRIO 75 n'est pas dans la liste : ses chiffres sont deja a
#      l'encre legere de la maison (0,50), plus clairs que le niveau B.
# ═════════════════════════════════════════════════════════════════════
GRIS_PARTICULIERS.update({
    "ohana75_10b18": 0.40,
    "ohana75_8b18":  0.40,
    "kea":           0.40,
    "pow9":          0.40,
})
_GRIS_POSES = _imposer_gris_maison()
# ⭐ LA REGLE DU 28/09 : tout bloc qui touche au catalogue rememorise
#    la table de fabrication, sinon une commande de 500 feuilles n'en sort
#    que 375 (le plafond trouve ce soir).
CARTES_PAR_FEUILLE.update({_j: _v["cartes_par_feuille"] for _j, _v in REGISTRE_JEUX.items()})
print("[ALLEGE] niveau B pose sur les 5 planches neuves — chiffres gris 0,40")
for _j in ("trio75", "ohana75_10b18", "ohana75_8b18", "kea", "pow9"):
    _m = __import__("sys").modules.get("generators." + _j)
    if _m is not None:
        print("[ALLEGE]    %-16s gris %.2f  gras %.3f"
              % (_j, _m._GRIS_ECO.red, getattr(_m, "_GRAS_TRAIT", 0.0)))
# -*- coding: utf-8 -*-
"""RAI — la maquette de Maeva du 28/09.

⚠️⚠️ RÈGLE ABSOLUE : le décor plus bas EST sa planche, relevée au trait sur
son fichier et transformée en courbes. Les seize cadres à double filet, leurs
bandeaux « R A I » et les quadrillages 3 x 3 : RIEN n'a été redessiné, rien
ajouté, RIEN EFFACÉ — sa planche est vide.
NE PAS « améliorer » le décor.

LA RÈGLE DU JEU NE CHANGE PAS : HUIT boules, par familles de dix —
     colonne 1 : 30 à 39 (x3)   colonne 2 : 40 à 49 (x2)   colonne 3 : 50 à 59 (x3)
Numéros distincts par colonne, ORDRE LIBRE — fidèle à son modèle.
⚠️ LA CASE DU MILIEU RESTE VIDE : elle porte le NUMÉRO DE SÉRIE, comme
   le nuage central de l'ancienne planche. C'est la 9e case, elle ne reçoit
   jamais de boule. Le crieur garde ses plages (30 à 59).

CE QUI CHANGE : 16 cartons par feuille A4 PAYSAGE au lieu de 12 en portrait,
et LES NUAGES DISPARAISSENT — sa nouvelle planche est au trait pur, sans
aucune image. app.py doit donc réinscrire RAI à 16 cartons et le sortir de
JEUX_AVEC_IMAGE (voir le bloc livré).

⚠️ LE TRAIT EST GRIS, PAS NOIR : sa planche est dessinée en gris 118/255.
   On la repose exactement à sa teinte (#767676) en noir et blanc. En couleur
   elle prend la teinte de l'arc-en-ciel, comme avant.

⭐ 28/09, derniere passe (sceau Maeva : « est-ce que le noir utilise ce n'est
pas fort pour notre economie de toner ») — LE TRAIT EST AFFINE DE 2 CRANS.
Mesure sur sa planche : le trait faisait 0,400 mm (0,78 mm pour les cadres).
On retire 0,133 mm de CHAQUE COTE de chaque trait : 0,400 -> 0,267 mm.
⚠️ LE DESSIN N'EST PAS TOUCHE : memes formes, memes places, memes lettres.
   Seule l'epaisseur change. Un cran de plus et ses lettres se decousaient :
   2 crans est le dernier cran propre, verifie a la loupe.
"""
import io
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

try:
    from generators import securite as _sec
except Exception:
    try:
        import securite as _sec
    except Exception:
        _sec = None

try:
    pdfmetrics.registerFont(TTFont("DJL", "/usr/share/fonts/truetype/dejavu/DejaVuSans-ExtraLight.ttf"))
    POLICE = "DJL"
except Exception:
    POLICE = "Helvetica"

RAINBOW = [
    "#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
    "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41",
]
GRIS = colors.Color(0.42, 0.42, 0.42)
GRIS_CLAIR = colors.Color(0.80, 0.80, 0.80)

from reportlab.pdfbase import pdfmetrics as _pm
from reportlab.pdfbase.ttfonts import TTFont as _TF
import os as _os
try:
    _pm.registerFont(_TF("LMROMAN", _os.path.join(
        _os.path.dirname(_os.path.abspath(__file__)), "LatinModern.ttf")))
    _POLICE_ECO = "LMROMAN"
except Exception:
    try:
        _pm.registerFont(_TF("DJLECO", "/usr/share/fonts/truetype/dejavu/DejaVuSans-ExtraLight.ttf"))
        _POLICE_ECO = "DJLECO"
    except Exception:
        _POLICE_ECO = "Helvetica"
_GRIS_ECO = colors.Color(0.40, 0.40, 0.40)
_GRAS_TRAIT = 0.012
_POLICE_P15 = _POLICE_ECO
_GRIS_P15 = colors.Color(0.14, 0.14, 0.14)

# ⭐ LE TRAIT DE SA PLANCHE EN NOIR ET BLANC — mesuré sur son fichier :
#    gris 118 sur 255. Une seule valeur pour l'éclaircir ou le foncer.
TRAIT_NB = "#767676"


def _style_chiffres(style):
    if str(style).lower() in ("p15", "premium"):
        return _POLICE_P15, _GRIS_P15
    return _POLICE_ECO, _GRIS_ECO


PAGE_W, PAGE_H = landscape(A4)
COLONNES = [(30, 39), (40, 49), (50, 59)]
PAR_COLONNE = (3, 2, 3)

MAQ_W, MAQ_H = 1463.0, 996.0
CARTES_PAGE = 16

MARGE_X = 6 * mm
FEUILLE_W = PAGE_W - 2 * MARGE_X
FEUILLE_H = FEUILLE_W * MAQ_H / MAQ_W
MARGE_Y = (PAGE_H - FEUILLE_H) / 2.0

# LES SEIZE GRILLES, RELEVÉES UNE PAR UNE, en millièmes de la planche.
# (bords gauche/droit du cadre, bandeau R A I, les 4 bornes de colonnes,
#  les 4 bornes de rangées)
GRILLES = [
    ([0.68, 238.89],
     [1.0, 44.18],
     [5.47, 81.34, 156.87, 234.11],
     [44.18, 106.93, 168.17, 231.93]),
    ([255.3, 492.48],
     [1.0, 44.18],
     [260.08, 335.27, 410.8, 488.04],
     [44.18, 106.93, 168.17, 231.93]),
    ([505.81, 744.02],
     [1.0, 44.18],
     [510.59, 587.15, 661.65, 738.89],
     [44.18, 106.93, 168.17, 231.93]),
    ([759.74, 997.95],
     [1.0, 44.18],
     [764.52, 841.08, 916.95, 993.16],
     [44.18, 106.93, 168.17, 231.93]),
    ([0.68, 238.89],
     [255.02, 298.19],
     [5.47, 81.34, 156.87, 234.11],
     [298.19, 359.94, 421.18, 485.44]),
    ([255.3, 492.48],
     [255.02, 298.19],
     [260.08, 335.27, 410.8, 488.04],
     [298.19, 359.94, 421.18, 485.44]),
    ([505.81, 744.02],
     [255.02, 298.19],
     [510.59, 587.15, 661.65, 738.89],
     [298.19, 359.94, 421.18, 485.44]),
    ([759.74, 997.95],
     [255.02, 298.19],
     [764.18, 840.74, 916.61, 993.16],
     [298.19, 359.94, 421.18, 485.44]),
    ([0.68, 238.89],
     [508.03, 551.2],
     [5.47, 81.34, 157.21, 234.11],
     [551.2, 612.95, 675.2, 738.96]),
    ([255.3, 492.48],
     [508.03, 551.2],
     [260.08, 335.61, 410.8, 488.04],
     [551.2, 612.95, 675.2, 738.96]),
    ([505.81, 744.02],
     [508.03, 551.2],
     [510.59, 587.15, 661.65, 738.89],
     [551.2, 612.95, 675.2, 738.96]),
    ([759.74, 997.95],
     [508.03, 551.2],
     [764.18, 841.08, 916.61, 993.16],
     [551.2, 612.95, 675.2, 738.96]),
    ([0.68, 238.89],
     [760.04, 802.71],
     [5.47, 81.34, 157.21, 234.11],
     [802.71, 863.45, 925.2, 988.45]),
    ([255.3, 492.48],
     [760.04, 802.71],
     [260.08, 335.27, 410.8, 487.7],
     [802.71, 863.45, 925.2, 988.45]),
    ([505.81, 744.02],
     [760.04, 802.71],
     [510.59, 587.15, 661.65, 738.89],
     [802.71, 863.45, 925.2, 988.45]),
    ([759.74, 997.95],
     [760.04, 802.71],
     [764.18, 840.74, 916.61, 992.82],
     [802.71, 863.45, 925.2, 988.45]),
]

_T_CASE = 41.0
_T_SERIE_CENTRE = 9.0
_T_TEL = 5.0


def _poser_decor(c, x0, y0):
    """Grave la planche UNE FOIS par document, puis la tamponne.
    ⚠️ La marque est posée SUR LE CANEVAS, jamais dans un dictionnaire
    indexé par id() : Python réutilise les id() libérés."""
    nom = "RAI_DECOR"
    if not getattr(c, "_rai_forme_faite", False):
        c.beginForm(nom, lowerx=0, lowery=0, upperx=FEUILLE_W, uppery=FEUILLE_H)
        p = c.beginPath()
        for contour in _DECOR.split("|"):
            i = 0
            n = len(contour)
            while i < n:
                cmd = contour[i]
                j = i + 1
                while j < n and contour[j] not in "mlc":
                    j += 1
                v = [float(x) for x in contour[i + 1:j].split(",")]
                if cmd == "m":
                    p.moveTo(v[0] / 1000.0 * FEUILLE_W, FEUILLE_H - v[1] / 1000.0 * FEUILLE_H)
                elif cmd == "l":
                    p.lineTo(v[0] / 1000.0 * FEUILLE_W, FEUILLE_H - v[1] / 1000.0 * FEUILLE_H)
                else:
                    p.curveTo(v[0] / 1000.0 * FEUILLE_W, FEUILLE_H - v[1] / 1000.0 * FEUILLE_H,
                              v[2] / 1000.0 * FEUILLE_W, FEUILLE_H - v[3] / 1000.0 * FEUILLE_H,
                              v[4] / 1000.0 * FEUILLE_W, FEUILLE_H - v[5] / 1000.0 * FEUILLE_H)
                i = j
            p.close()
        c.drawPath(p, stroke=0, fill=1)
        c.endForm()
        c._rai_forme_faite = True
    c.saveState()
    c.translate(x0, y0)
    c.doForm(nom)
    c.restoreState()


def _gen_carte(rng):
    """8 boules : 3 + 2 + 3 distincts par famille de dix, ordre LIBRE."""
    return [rng.sample(range(pmin, pmax + 1), n)
            for (pmin, pmax), n in zip(COLONNES, PAR_COLONNE)]


# ⚠️ Deux cartons identiques dans la même rame : ce jeu ne peut fabriquer
#    que 720 x 90 x 720 = 46 656 000 cartons différents (ordre libre).
#    Une rame de 500 feuilles en contient 8 000 : le calcul donne 1 risque
#    sur 1 458. On garde donc en mémoire, pendant tout le document, les
#    cartons déjà sortis.
def _tirer(rng, deja):
    for _ in range(200):
        g = _gen_carte(rng)
        cle = tuple(tuple(col) for col in g)
        if cle not in deja:
            deja.add(cle)
            return g
    return g


def _dessiner_feuille(c, x0, y0, cartes, series, couleur_hex, titre_jeu="",
                      telephone="", style="eco"):
    police_ch, gris_ch = _style_chiffres(style)
    col = colors.HexColor(couleur_hex)
    c.setFillColor(col)
    _poser_decor(c, x0, y0)

    def MX(v):
        return x0 + v / 1000.0 * FEUILLE_W

    def MY(v):
        return y0 + FEUILLE_H - v / 1000.0 * FEUILLE_H

    for gi, (bord, bandeau, cols, rows) in enumerate(GRILLES):
        colonnes = cartes[gi]
        # la grille 3x3, LE CENTRE LAISSÉ LIBRE (il porte la série)
        grille = [
            [colonnes[0][0], colonnes[1][0], colonnes[2][0]],
            [colonnes[0][1], None,           colonnes[2][1]],
            [colonnes[0][2], colonnes[1][1], colonnes[2][2]],
        ]
        for ri in range(3):
            for ci in range(3):
                val = grille[ri][ci]
                cx = MX((cols[ci] + cols[ci + 1]) / 2.0)
                cy = MY((rows[ri] + rows[ri + 1]) / 2.0)
                if val is None:
                    # ⭐ LA CASE DU MILIEU : le numéro de série, comme sur
                    #    le nuage central de l'ancienne planche.
                    c.setFillColor(col)
                    c.setFont(POLICE, _T_SERIE_CENTRE)
                    c.drawCentredString(cx, cy - _T_SERIE_CENTRE * 0.34,
                                        "N\u00b0 %05d" % series[gi])
                    continue
                cy -= _T_CASE * 0.34
                if _sec:
                    _sec.chiffre_micro(c, val, cx, cy, _T_CASE, gris_ch, police_ch,
                                       epaisseur=_GRAS_TRAIT)
                else:
                    c.setFillColor(gris_ch)
                    c.setFont(police_ch, _T_CASE)
                    c.drawCentredString(cx, cy, str(val))
        if telephone:
            c.setFillColor(GRIS)
            c.setFont(POLICE, _T_TEL)
            c.drawRightString(MX(bord[1]) - 1.0 * mm, MY(bandeau[1]) + 1.2 * mm,
                              telephone[:14])
        if _sec:
            try:
                _sec.cadre_micro(c, MX(bord[0]), MY(rows[3]),
                                 MX(bord[1]) - MX(bord[0]),
                                 MY(bandeau[0]) - MY(rows[3]),
                                 series[gi], retrait=0.7 * mm)
            except Exception:
                pass


def generer_pdf(nb_cartes=16, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", style="eco", evenement_id="", motif="",
                page_start=1, **_):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=landscape(A4), pageCompression=1)

    nb_cartes = max(1, min(int(nb_cartes), 10000))
    nb_pages = (nb_cartes + CARTES_PAGE - 1) // CARTES_PAGE

    rng = random.Random(430000 + int(serie_start))
    serie = int(serie_start)
    no_page = max(1, int(page_start))
    _deja = set()

    for _p in range(nb_pages):
        if nom_evenement:
            c.setFillColor(colors.black); c.setFont(POLICE, 8)
            c.drawCentredString(PAGE_W / 2, PAGE_H - 4.6 * mm, nom_evenement)
        c.setFillColor(GRIS_CLAIR); c.setFont(POLICE, 5.5)
        c.drawRightString(PAGE_W - 5 * mm, PAGE_H - 4.6 * mm, "%03d" % no_page)

        cartes = [_tirer(rng, _deja) for _k in range(CARTES_PAGE)]
        series = [serie + k for k in range(CARTES_PAGE)]
        coul = (couleur_perso if (couleur and couleur_perso)
                else RAINBOW[(serie - 1) % len(RAINBOW)] if couleur else TRAIT_NB)
        _dessiner_feuille(c, MARGE_X, MARGE_Y, cartes, series, coul,
                          titre_jeu, telephone, style=style)
        serie += CARTES_PAGE
        c.showPage()
        no_page += 1

    c.save()
    buf.seek(0)
    return buf


# ══ LE DESSIN DE SA PLANCHE, RELEVÉ AU TRAIT ═════════════════════════
_DECOR = "m15.3,998.6c14.7,998.5,13.5,998.2,12.7,998.1c11.3,997.9,10.0,997.2,9.7,996.6c9.6,996.4,9.4,996.2,9.1,996.2c8.9,996.2,8.6,996.0,8.4,995.7c8.3,995.4,8.0,995.2,7.7,995.2c7.2,995.2,3.8,990.0,2.7,987.7c2.2,986.7,1.9,985.4,1.9,984.9c1.9,984.4,1.7,983.7,1.5,983.5c1.3,983.3,1.2,982.7,1.2,982.2c1.2,981.7,1.0,981.1,0.9,980.8c0.6,980.5,0.6,959.7,0.6,879.4c0.6,799.1,0.6,778.4,0.9,778.0c1.0,777.8,1.2,777.1,1.2,776.5c1.2,775.9,1.3,775.2,1.5,775.0c1.7,774.8,1.9,774.2,1.9,773.7c1.9,773.3,2.2,772.3,2.6,771.5c3.0,770.7,3.3,769.9,3.3,769.7c3.3,769.1,7.1,763.7,7.5,763.7c7.7,763.7,8.0,763.4,8.2,763.1c8.3,762.9,8.7,762.6,8.9,762.6c9.1,762.6,9.4,762.4,9.6,762.1c9.8,761.8,10.1,761.6,10.3,761.6c10.5,761.6,10.8,761.4,11.0,761.1c11.2,760.8,11.6,760.6,12.0,760.6c12.4,760.6,12.9,760.4,13.1,760.1c13.5,759.5,227.2,759.5,227.6,760.1c227.8,760.4,228.3,760.6,228.7,760.6c229.1,760.6,229.5,760.8,229.7,761.1c229.9,761.4,230.2,761.6,230.4,761.6c230.6,761.6,231.0,761.8,231.1,762.1c231.3,762.4,231.5,762.6,231.7,762.6c231.8,762.6,232.3,763.1,232.6,763.7c233.0,764.2,233.5,764.7,233.7,764.7c234.2,764.7,236.7,768.5,236.7,769.2c236.7,769.5,237.0,770.1,237.3,770.5c238.0,771.5,238.8,773.7,238.8,774.6c238.8,775.0,239.0,775.7,239.2,776.2c239.4,776.8,239.5,777.5,239.5,777.9c239.5,778.3,239.7,778.8,239.8,779.1c240.1,779.4,240.1,799.9,240.1,879.3c240.1,958.6,240.1,979.1,239.8,979.4c239.7,979.7,239.5,980.4,239.5,981.1c239.5,981.8,239.4,982.8,239.2,983.3c239.0,983.8,238.8,984.5,238.8,984.7c238.8,984.9,238.7,985.3,238.5,985.6c238.3,985.8,238.1,986.3,238.1,986.6c238.1,986.9,237.8,987.6,237.4,988.1c237.0,988.7,236.7,989.4,236.7,989.7c236.7,990.4,234.0,994.2,233.6,994.2c233.4,994.2,233.0,994.6,232.6,995.2c232.3,995.8,231.8,996.2,231.6,996.2c231.4,996.2,231.0,996.5,230.8,996.7c230.5,997.0,230.0,997.3,229.7,997.3c229.3,997.3,229.0,997.4,228.9,997.6c228.8,997.7,228.2,997.9,227.5,998.0c226.9,998.2,225.6,998.4,224.7,998.6c222.7,999.0,17.2,999.0,15.3,998.6|m269.5,998.6c268.9,998.5,267.9,998.2,267.3,998.1c266.7,998.0,266.1,997.7,266.1,997.5c266.0,997.4,265.6,997.3,265.3,997.3c264.4,997.3,263.0,996.2,262.2,995.0c261.9,994.5,261.5,994.2,261.3,994.2c260.6,994.2,257.7,989.3,256.8,986.5c256.3,985.1,255.8,983.8,255.7,983.7c255.5,983.6,255.4,982.7,255.4,981.8c255.4,980.9,255.3,980.0,255.1,979.8c254.9,979.4,254.9,958.8,254.9,878.9c254.9,799.0,254.9,778.4,255.1,778.0c255.3,777.8,255.4,777.1,255.4,776.5c255.4,775.9,255.6,775.2,255.8,775.0c256.0,774.8,256.1,774.3,256.1,774.0c256.1,773.6,256.3,773.2,256.5,772.9c256.7,772.7,256.8,772.2,256.8,771.9c256.8,771.6,257.0,771.1,257.2,770.9c257.4,770.6,257.5,770.2,257.5,769.9c257.5,769.2,260.6,764.7,261.1,764.7c261.3,764.7,261.7,764.2,262.1,763.7c262.5,763.1,263.0,762.6,263.2,762.6c263.4,762.6,263.7,762.4,263.9,762.1c264.0,761.8,264.3,761.6,264.6,761.6c264.8,761.6,265.1,761.4,265.3,761.1c265.4,760.8,265.9,760.6,266.5,760.6c267.1,760.6,267.6,760.4,267.8,760.1c268.0,759.8,289.7,759.7,374.5,759.7c459.3,759.7,481.0,759.8,481.2,760.1c481.4,760.4,481.8,760.6,482.2,760.6c482.6,760.6,483.1,760.8,483.3,761.1c483.4,761.4,483.8,761.6,484.0,761.6c484.2,761.6,484.5,761.8,484.7,762.1c484.8,762.4,485.1,762.6,485.3,762.6c485.4,762.6,485.7,762.9,485.8,763.1c486.0,763.4,486.3,763.7,486.5,763.7c486.9,763.7,490.3,768.4,490.3,768.9c490.3,769.1,490.6,769.8,491.0,770.5c491.4,771.2,491.7,772.1,491.7,772.3c491.7,772.6,491.9,773.0,492.0,773.3c492.2,773.5,492.4,774.0,492.4,774.3c492.4,774.6,492.5,775.1,492.7,775.3c493.3,776.0,493.4,777.8,493.6,789.2c493.8,803.7,493.8,954.4,493.6,968.4c493.4,979.9,493.2,981.9,492.7,982.5c492.5,982.7,492.4,983.4,492.4,984.0c492.4,984.6,492.2,985.3,492.0,985.6c491.9,985.8,491.7,986.3,491.7,986.6c491.7,986.9,491.5,987.4,491.3,987.6c491.2,987.9,491.0,988.3,491.0,988.6c491.0,989.3,487.7,994.2,487.2,994.2c487.0,994.2,486.6,994.6,486.2,995.2c485.8,995.8,485.4,996.2,485.2,996.2c485.0,996.2,484.6,996.5,484.3,996.7c484.1,997.0,483.6,997.3,483.3,997.3c483.0,997.3,482.6,997.4,482.4,997.6c480.7,998.8,482.7,998.8,374.9,998.8c317.5,998.9,270.1,998.8,269.5,998.6|m520.5,998.6c519.9,998.5,518.9,998.2,518.2,998.1c517.5,998.0,516.9,997.7,516.8,997.5c516.8,997.4,516.4,997.3,516.1,997.3c515.7,997.3,515.2,997.0,515.0,996.7c514.7,996.5,514.3,996.2,514.1,996.2c513.9,996.2,513.6,996.0,513.5,995.7c513.3,995.4,513.0,995.2,512.8,995.2c512.3,995.2,507.6,988.3,507.6,987.6c507.6,987.3,507.4,986.8,507.3,986.6c507.1,986.4,506.9,985.9,506.9,985.6c506.9,985.3,506.8,984.8,506.6,984.6c506.1,983.8,505.9,980.2,505.7,965.0c505.5,945.0,505.5,814.1,505.7,793.9c505.9,777.8,506.0,776.0,506.6,775.3c506.8,775.1,506.9,774.4,506.9,773.8c506.9,773.2,507.1,772.5,507.3,772.2c507.4,772.0,507.6,771.6,507.6,771.3c507.6,770.5,512.3,763.7,512.8,763.7c513.0,763.7,513.4,763.2,513.8,762.6c514.2,762.0,514.7,761.6,515.1,761.6c515.4,761.6,515.9,761.4,516.0,761.1c516.2,760.8,516.6,760.6,517.1,760.6c517.5,760.6,517.9,760.4,518.1,760.1c518.3,759.8,540.1,759.7,625.4,759.7c710.7,759.7,732.4,759.8,732.7,760.1c732.8,760.4,733.3,760.6,733.7,760.6c734.1,760.6,734.6,760.8,734.7,761.1c734.9,761.4,735.2,761.6,735.4,761.6c735.7,761.6,736.0,761.8,736.1,762.1c736.3,762.4,736.6,762.6,736.7,762.6c736.8,762.6,737.5,763.3,738.1,764.1c738.8,765.0,739.5,765.7,739.8,765.8c740.0,765.8,740.3,766.2,740.3,766.6c740.3,767.0,740.8,768.0,741.4,768.8c742.0,769.6,742.5,770.6,742.5,770.9c742.5,771.2,742.6,771.7,742.8,771.9c743.0,772.1,743.2,772.6,743.2,772.9c743.2,773.3,743.3,773.7,743.5,774.0c743.7,774.2,743.9,774.7,743.9,775.0c743.9,775.3,744.0,775.8,744.2,776.0c744.4,776.3,744.6,777.0,744.6,778.1c744.6,778.9,744.7,779.9,744.9,780.1c745.1,780.4,745.1,800.8,745.1,879.4c745.1,958.1,745.1,978.4,744.9,978.8c744.7,979.0,744.6,979.9,744.6,980.8c744.6,981.8,744.4,982.6,744.2,982.8c744.0,983.1,743.9,983.6,743.9,984.0c743.9,984.9,743.2,986.9,742.4,988.3c742.0,988.9,741.8,989.6,741.8,989.8c741.8,990.4,739.8,993.1,739.4,993.1c739.2,993.1,738.6,993.8,738.0,994.7c737.2,995.9,736.8,996.2,736.2,996.2c735.8,996.2,735.4,996.5,735.2,996.7c735.0,997.0,734.7,997.3,734.5,997.3c734.3,997.3,734.0,997.4,733.9,997.5c733.9,997.7,733.4,997.9,732.8,998.1c732.3,998.2,731.2,998.4,730.5,998.6c729.0,999.0,522.0,999.0,520.5,998.6|m774.0,998.6c773.5,998.5,772.4,998.2,771.7,998.1c771.1,998.0,770.5,997.7,770.4,997.5c770.3,997.4,770.0,997.3,769.6,997.3c769.3,997.3,768.8,997.0,768.5,996.7c768.3,996.5,767.9,996.2,767.7,996.2c767.5,996.2,767.0,995.8,766.7,995.2c766.3,994.6,765.9,994.2,765.7,994.2c765.2,994.2,761.9,989.3,761.9,988.7c761.9,988.3,761.7,987.9,761.5,987.6c761.3,987.4,761.2,986.9,761.2,986.6c761.2,986.3,761.0,985.8,760.8,985.6c760.6,985.3,760.5,984.9,760.5,984.7c760.5,984.4,760.3,983.8,760.1,983.4c759.2,981.1,759.2,981.9,759.2,879.4c759.2,776.7,759.2,776.5,760.2,775.3c760.3,775.1,760.5,774.6,760.5,774.3c760.5,774.0,760.6,773.5,760.8,773.3c761.0,773.0,761.2,772.6,761.2,772.2c761.2,771.9,761.3,771.4,761.5,771.2c761.7,771.0,761.9,770.5,761.9,770.2c761.9,769.5,765.1,764.7,765.6,764.7c765.8,764.7,766.3,764.2,766.7,763.7c767.0,763.1,767.5,762.6,767.7,762.6c768.0,762.6,768.3,762.4,768.4,762.1c768.6,761.8,769.0,761.6,769.4,761.6c769.7,761.6,770.1,761.4,770.3,761.1c770.5,760.8,770.9,760.6,771.3,760.6c771.7,760.6,772.2,760.4,772.4,760.1c772.8,759.5,985.8,759.5,986.2,760.1c986.4,760.4,986.9,760.6,987.3,760.6c987.7,760.6,988.1,760.8,988.3,761.1c988.5,761.4,988.9,761.6,989.3,761.6c989.9,761.6,990.3,761.9,990.8,762.6c991.1,763.2,991.6,763.7,991.8,763.7c992.5,763.7,995.7,768.8,996.6,771.4c997.1,772.7,997.4,774.0,997.4,774.2c997.4,774.4,997.6,774.8,997.8,775.0c998.0,775.2,998.1,775.9,998.1,776.5c998.1,777.1,998.3,777.8,998.4,778.0c998.7,778.4,998.7,799.2,998.7,879.9c998.7,960.7,998.7,981.5,998.4,981.8c998.3,982.1,998.1,982.7,998.1,983.2c998.1,983.7,998.0,984.3,997.8,984.5c997.6,984.8,997.4,985.2,997.4,985.4c997.4,986.5,996.5,988.5,994.3,991.7c993.0,993.6,991.8,995.2,991.6,995.2c991.3,995.2,991.0,995.4,990.9,995.7c990.7,996.0,990.4,996.2,990.2,996.2c989.9,996.2,989.7,996.4,989.6,996.6c989.3,997.2,988.0,997.9,986.7,998.1c986.0,998.2,984.8,998.4,984.1,998.6c982.5,999.0,775.6,999.0,774.0,998.6|m72.0,997.2c75.3,997.0,79.5,996.8,81.4,996.7c84.1,996.6,84.9,996.6,85.5,997.1c86.5,997.8,89.0,997.8,89.9,997.1c90.5,996.6,90.6,996.6,91.0,997.1c91.4,997.6,91.4,997.6,91.7,997.1c91.9,996.7,92.1,996.6,92.3,997.0c92.9,997.6,129.4,997.6,129.9,997.0c130.3,996.4,132.9,996.5,133.4,997.1c134.0,997.8,135.2,997.7,135.9,997.1c136.3,996.6,136.5,996.6,136.8,997.0c137.3,997.6,142.2,997.6,142.9,997.0c143.6,996.4,168.3,996.6,176.8,997.2c184.1,997.8,217.0,997.5,217.4,997.0c217.7,996.4,219.0,996.5,219.5,997.1c220.1,997.7,220.8,997.7,221.4,997.1c221.9,996.6,222.0,996.6,222.2,997.1c222.4,997.5,222.6,997.5,222.8,997.2c223.1,996.9,223.2,996.9,223.5,997.2c223.7,997.5,223.9,997.5,224.1,997.1c224.3,996.7,224.8,996.6,225.7,996.6c226.5,996.6,227.2,996.4,227.5,996.1c227.7,995.8,228.3,995.6,228.7,995.5c229.1,995.5,229.5,995.3,229.7,995.0c229.9,994.7,230.2,994.5,230.4,994.5c230.6,994.5,231.1,994.0,231.5,993.5c231.8,992.9,232.3,992.4,232.5,992.4c233.0,992.4,235.6,988.6,235.6,987.9c235.6,987.7,235.9,987.0,236.3,986.4c236.6,985.9,237.0,985.2,237.0,984.9c237.0,984.5,237.1,984.1,237.3,983.9c237.5,983.6,237.7,982.9,237.7,982.2c237.7,981.5,237.8,980.7,238.0,980.5c238.4,979.8,238.4,778.7,238.0,778.0c237.8,777.8,237.7,777.3,237.7,776.9c237.7,776.4,237.5,775.9,237.3,775.7c237.1,775.4,237.0,774.9,237.0,774.4c237.0,773.9,236.6,773.0,236.3,772.2c235.9,771.5,235.6,770.8,235.6,770.7c235.6,770.1,232.2,765.4,231.8,765.4c231.6,765.4,231.3,765.1,231.1,764.9c231.0,764.6,230.7,764.3,230.5,764.3c230.4,764.3,230.1,764.1,229.9,763.8c229.8,763.5,229.4,763.3,229.1,763.3c228.8,763.3,228.5,763.1,228.3,762.8c228.0,762.3,227.2,762.1,222.7,761.6c218.0,761.0,15.3,761.3,14.9,761.9c14.8,762.1,14.2,762.3,13.5,762.3c12.9,762.3,12.3,762.5,12.2,762.8c12.0,763.1,11.5,763.3,11.1,763.3c10.7,763.3,10.2,763.5,10.1,763.8c9.9,764.1,9.6,764.3,9.4,764.3c9.2,764.3,7.9,766.0,6.5,768.0c4.2,771.4,3.0,773.7,3.0,774.9c3.0,775.2,2.9,775.9,2.7,776.5c2.5,777.1,2.3,778.1,2.3,778.8c2.2,779.4,2.0,781.2,1.9,782.7c1.7,784.7,1.6,812.7,1.7,881.8c1.8,984.3,1.7,978.6,2.8,982.2c2.9,982.8,3.0,983.4,3.0,983.6c3.0,984.3,3.8,986.4,4.5,987.6c4.9,988.2,5.1,988.9,5.1,989.1c5.1,989.7,6.4,991.4,6.8,991.4c7.0,991.4,7.6,992.1,8.2,993.0c9.0,994.1,9.4,994.5,10.0,994.5c10.4,994.5,10.8,994.7,11.0,995.0c11.2,995.3,11.5,995.5,11.7,995.5c11.9,995.6,12.3,995.8,12.5,996.1c12.8,996.4,13.5,996.6,14.6,996.6c15.5,996.6,16.4,996.7,16.5,996.9c16.8,997.3,22.0,997.4,46.4,997.5c57.2,997.5,68.8,997.4,72.0,997.2|m332.2,997.0c332.6,996.4,333.9,996.5,334.2,997.0c334.7,997.6,371.0,997.6,372.0,997.0c372.9,996.4,447.8,996.4,448.8,996.9c449.8,997.5,463.2,997.7,466.1,997.2c467.4,997.0,471.2,996.7,474.7,996.6c479.2,996.5,481.0,996.3,481.2,996.0c481.4,995.7,481.8,995.5,482.2,995.5c482.6,995.5,483.1,995.3,483.3,995.0c483.4,994.7,483.7,994.5,484.0,994.5c484.2,994.5,484.7,994.0,485.0,993.5c485.4,992.9,485.9,992.4,486.1,992.4c486.6,992.4,489.8,987.6,489.8,986.9c489.8,986.6,490.0,986.2,490.2,985.9c490.4,985.7,490.5,985.2,490.5,984.9c490.5,984.6,490.7,984.1,490.9,983.9c491.1,983.6,491.2,983.2,491.2,982.8c491.2,982.5,491.4,982.0,491.6,981.8c491.8,981.5,491.9,980.7,491.9,979.2c491.9,977.7,492.0,976.9,492.3,976.6c492.5,976.4,492.6,975.6,492.6,974.6c492.6,973.5,492.5,972.8,492.3,972.5c491.8,972.0,491.8,970.5,492.3,969.6c492.8,968.7,492.8,963.6,492.3,962.7c491.8,961.7,491.8,953.2,492.3,952.6c492.7,952.1,492.8,949.1,492.3,948.5c492.1,948.2,492.0,939.1,492.0,905.4c492.0,871.6,492.1,862.5,492.3,862.2c492.8,861.6,492.7,857.1,492.3,856.2c491.8,855.3,491.8,843.0,492.2,842.4c492.5,842.0,492.5,835.6,492.5,812.6c492.5,789.6,492.5,783.2,492.2,782.8c492.1,782.6,491.9,781.5,491.9,780.3c491.9,778.8,491.8,778.0,491.6,777.7c491.4,777.5,491.2,776.8,491.2,776.2c491.2,775.6,491.1,774.9,490.9,774.6c490.7,774.4,490.5,773.9,490.5,773.6c490.5,773.3,490.4,772.8,490.2,772.6c490.0,772.4,489.8,772.0,489.8,771.7c489.8,771.2,486.6,766.4,486.2,766.4c486.1,766.4,485.6,765.9,485.1,765.4c484.7,764.8,484.2,764.3,484.0,764.3c483.9,764.3,483.7,764.1,483.5,763.8c483.3,763.5,483.0,763.3,482.7,763.3c482.4,763.3,482.0,763.1,481.9,762.8c481.7,762.5,481.0,762.3,480.2,762.2c479.4,762.1,477.4,761.8,475.8,761.6c471.2,761.0,270.3,761.3,269.9,761.9c269.7,762.1,269.1,762.3,268.5,762.3c267.8,762.3,267.3,762.5,267.1,762.8c267.0,763.1,266.5,763.3,266.1,763.3c265.7,763.3,265.2,763.5,265.0,763.8c264.9,764.1,264.6,764.3,264.3,764.3c264.1,764.3,263.8,764.6,263.6,764.9c263.5,765.1,263.2,765.4,263.0,765.4c262.5,765.4,258.7,770.9,258.7,771.6c258.7,771.9,258.6,772.4,258.4,772.6c258.2,772.8,258.0,773.3,258.0,773.6c258.0,773.9,257.9,774.4,257.7,774.6c257.5,774.9,257.3,775.3,257.3,775.7c257.3,776.0,257.2,776.5,257.0,776.7c256.8,776.9,256.6,777.8,256.5,778.7c256.5,779.6,256.3,781.5,256.2,782.9c255.9,786.4,255.9,972.1,256.2,975.6c256.3,977.0,256.5,978.9,256.5,979.7c256.6,980.6,256.8,981.6,257.0,982.0c257.2,982.3,257.3,983.0,257.3,983.5c257.3,984.1,257.6,984.8,258.0,985.4c258.4,985.9,258.7,986.6,258.7,986.9c258.7,987.6,262.0,992.4,262.5,992.4c262.7,992.4,263.1,992.9,263.5,993.5c263.9,994.0,264.4,994.5,264.6,994.5c264.8,994.5,265.1,994.7,265.3,995.0c265.4,995.3,265.9,995.5,266.3,995.5c266.7,995.5,267.2,995.8,267.4,996.0c267.6,996.4,268.1,996.6,268.8,996.6c269.4,996.6,270.0,996.7,270.1,996.9c270.4,997.4,277.4,997.5,306.3,997.4c325.5,997.4,332.0,997.3,332.2,997.0|m548.8,997.0c549.2,996.4,553.3,996.4,553.6,997.0c553.9,997.3,554.9,997.4,557.1,997.4c559.3,997.4,560.3,997.3,560.5,997.0c560.7,996.8,561.0,996.6,561.3,996.6c561.6,996.6,561.9,996.8,562.1,997.0c562.3,997.3,568.9,997.4,593.7,997.4c618.4,997.4,625.1,997.3,625.3,997.0c625.7,996.4,628.8,996.4,629.6,997.1c630.0,997.4,630.7,997.6,631.2,997.6c631.7,997.6,632.5,997.4,632.8,997.1c633.7,996.4,645.3,996.3,645.8,997.0c646.0,997.3,647.5,997.4,651.3,997.4c655.2,997.4,656.7,997.3,656.9,997.0c657.3,996.3,664.5,996.4,665.1,997.1c665.4,997.4,665.8,997.6,666.1,997.6c666.4,997.6,666.8,997.4,667.0,997.1c667.6,996.4,678.6,996.3,679.4,997.0c679.7,997.3,681.0,997.4,683.6,997.4c686.2,997.4,687.3,997.3,687.5,997.0c687.7,996.7,688.9,996.6,691.7,996.6c694.5,996.6,695.7,996.7,695.9,997.0c696.1,997.3,699.7,997.4,712.5,997.4c725.3,997.4,728.9,997.3,729.2,997.0c729.3,996.8,730.0,996.6,730.8,996.6c731.6,996.6,732.3,996.4,732.5,996.1c732.8,995.8,733.3,995.6,733.7,995.5c734.1,995.5,734.6,995.3,734.7,995.0c734.9,994.7,735.2,994.5,735.4,994.5c735.7,994.5,736.0,994.3,736.1,994.0c736.3,993.7,736.6,993.5,736.8,993.5c737.3,993.5,741.3,987.6,741.3,986.9c741.3,986.6,741.4,986.2,741.6,985.9c741.8,985.7,742.0,985.2,742.0,984.9c742.0,984.6,742.1,984.1,742.3,983.9c742.5,983.6,742.7,983.1,742.7,982.7c742.7,982.2,742.8,981.3,743.0,980.6c743.4,979.6,743.4,967.5,743.4,879.2c743.4,790.9,743.3,778.8,743.0,778.0c742.8,777.4,742.7,776.8,742.7,776.5c742.7,776.3,742.5,775.9,742.3,775.7c742.1,775.4,742.0,774.8,742.0,774.2c742.0,773.4,741.8,772.8,741.4,772.2c741.1,771.8,740.8,771.2,740.8,771.0c740.8,770.3,738.2,766.4,737.8,766.4c737.6,766.4,737.1,765.9,736.7,765.4c736.4,764.8,735.9,764.3,735.7,764.3c735.4,764.3,735.1,764.1,735.0,763.8c734.8,763.5,734.5,763.3,734.3,763.3c734.0,763.3,733.7,763.1,733.6,762.8c733.4,762.4,732.8,762.3,731.8,762.3c731.0,762.3,730.3,762.1,730.1,761.9c729.9,761.5,708.6,761.4,625.1,761.4c541.7,761.4,520.4,761.5,520.2,761.9c520.0,762.1,519.4,762.3,518.7,762.3c517.9,762.3,517.4,762.5,517.2,762.8c517.0,763.1,516.8,763.3,516.6,763.3c516.4,763.3,516.2,763.5,516.0,763.8c515.9,764.1,515.5,764.3,515.3,764.3c515.1,764.3,514.8,764.6,514.6,764.9c514.5,765.1,514.2,765.4,513.9,765.4c513.5,765.4,509.5,771.0,509.5,771.7c509.5,771.9,509.2,772.6,508.8,773.1c508.2,773.8,508.1,774.4,508.1,775.4c508.1,776.1,507.9,776.8,507.7,777.1c507.5,777.3,507.4,778.1,507.4,779.1c507.4,780.0,507.2,780.9,507.1,781.1c506.8,781.5,506.8,801.7,506.8,879.9c506.8,958.2,506.8,978.4,507.1,978.8c507.2,979.0,507.4,979.9,507.4,980.8c507.4,981.8,507.5,982.6,507.7,982.8c507.9,983.1,508.1,983.5,508.1,983.9c508.1,984.2,508.2,984.6,508.4,984.9c508.6,985.1,508.8,985.6,508.8,985.9c508.8,986.6,513.4,993.5,513.9,993.5c514.2,993.5,514.5,993.7,514.6,994.0c514.8,994.3,515.1,994.5,515.3,994.5c515.5,994.5,515.9,994.7,516.0,995.0c516.2,995.3,516.5,995.5,516.7,995.5c516.9,995.6,517.3,995.8,517.5,996.1c517.8,996.4,518.5,996.6,519.6,996.6c520.6,996.6,521.4,996.7,521.5,996.9c521.9,997.4,525.1,997.5,537.4,997.4c545.6,997.4,548.6,997.3,548.8,997.0|m878.2,997.0c878.6,996.4,884.9,996.4,885.3,997.0c885.8,997.6,917.4,997.6,918.0,997.0c918.4,996.5,926.7,996.6,937.0,997.2c945.1,997.8,983.1,997.5,983.5,997.0c983.6,996.7,984.2,996.6,984.8,996.6c985.5,996.6,986.0,996.4,986.2,996.0c986.4,995.8,986.8,995.5,987.3,995.5c987.7,995.5,988.1,995.3,988.3,995.0c988.5,994.7,988.8,994.5,989.0,994.5c989.2,994.5,989.5,994.3,989.7,994.0c989.9,993.7,990.2,993.5,990.4,993.5c990.6,993.5,991.8,992.0,993.0,990.2c994.8,987.6,995.4,986.4,996.1,984.4c997.6,979.6,997.5,987.4,997.6,881.3c997.6,812.0,997.6,784.1,997.4,782.4c997.3,781.1,997.1,779.4,997.0,778.8c996.9,777.5,996.1,774.8,995.8,774.5c995.7,774.4,995.6,774.0,995.6,773.6c995.6,773.3,995.4,772.8,995.2,772.6c995.0,772.4,994.9,771.9,994.9,771.6c994.9,770.9,991.1,765.4,990.6,765.4c990.4,765.4,990.1,765.1,989.9,764.9c989.8,764.6,989.5,764.3,989.2,764.3c989.0,764.3,988.7,764.1,988.5,763.8c988.4,763.5,988.1,763.3,987.8,763.3c987.6,763.3,987.3,763.1,987.1,762.8c987.0,762.5,986.4,762.3,985.7,762.3c985.1,762.3,984.5,762.1,984.4,761.9c984.0,761.3,781.6,761.0,777.2,761.6c772.7,762.1,772.0,762.3,771.7,762.8c771.5,763.1,771.1,763.3,770.6,763.3c770.2,763.3,769.8,763.5,769.6,763.8c769.4,764.1,769.1,764.3,768.9,764.3c768.8,764.3,768.2,764.8,767.8,765.4c767.4,765.9,766.9,766.4,766.7,766.4c766.3,766.4,763.7,770.3,763.7,770.9c763.7,771.2,763.4,771.9,763.0,772.4c762.7,773.0,762.3,773.6,762.3,773.8c762.3,774.0,762.2,774.4,762.0,774.6c761.8,774.9,761.6,775.4,761.6,775.9c761.6,776.3,761.5,776.8,761.3,777.1c761.1,777.3,760.9,778.1,760.9,779.1c760.9,780.0,760.8,780.9,760.6,781.1c760.4,781.5,760.4,801.6,760.4,879.4c760.4,957.3,760.4,977.4,760.6,977.7c760.8,978.0,760.9,978.9,760.9,979.8c760.9,980.8,761.1,981.5,761.3,981.8c761.5,982.0,761.6,982.7,761.6,983.3c761.6,984.0,761.8,984.6,762.0,984.9c762.2,985.1,762.3,985.6,762.3,985.9c762.3,986.6,767.0,993.5,767.5,993.5c767.7,993.5,768.0,993.7,768.2,994.0c768.3,994.3,768.6,994.5,768.9,994.5c769.1,994.5,769.4,994.8,769.7,995.0c769.9,995.3,770.4,995.5,770.7,995.5c771.1,995.6,771.5,995.8,771.8,996.1c772.0,996.3,772.7,996.6,773.2,996.6c773.7,996.6,774.3,996.7,774.4,996.9c774.7,997.4,785.9,997.5,834.9,997.4c867.3,997.4,878.0,997.3,878.2,997.0|m12.6,989.8c12.3,989.7,11.8,989.5,11.6,989.4c11.3,989.2,11.0,989.0,10.8,988.9c10.6,988.8,10.3,988.5,10.1,988.4c9.9,988.2,9.2,987.7,8.5,987.2c7.8,986.7,7.3,986.1,7.3,985.7c7.2,985.4,7.0,984.7,6.7,984.2c6.4,983.7,5.9,982.7,5.7,982.0c5.3,980.7,5.3,979.1,5.3,954.9l5.3,929.3l5.9,928.3c6.8,927.0,6.8,925.3,5.9,923.3l5.3,921.8l5.3,895.1l5.3,868.3l5.9,866.6c6.7,864.5,6.7,863.1,5.9,861.0l5.3,859.3l5.3,835.1c5.3,818.1,5.4,810.7,5.5,810.3c5.7,810.1,5.9,809.3,5.9,808.6c6.1,806.9,8.2,804.1,9.7,803.4c10.8,802.9,14.3,802.8,45.3,802.9l79.7,803.0l80.6,804.3c81.1,805.0,81.7,805.6,82.0,805.6c82.2,805.6,82.8,805.0,83.3,804.3l84.2,803.0l119.2,803.0c157.9,803.0,154.6,802.8,156.4,805.4c157.3,806.5,157.5,806.7,157.8,806.4c158.1,806.2,158.3,805.7,158.4,805.2c158.4,804.8,158.9,804.1,159.3,803.7c160.1,803.0,160.1,803.0,195.1,803.0c222.8,803.0,230.2,803.1,230.4,803.4c230.6,803.7,230.9,803.8,231.1,803.8c231.8,803.8,234.6,808.6,234.6,809.6c234.6,810.1,234.8,810.8,235.0,811.2c235.5,812.2,235.5,859.0,235.0,860.0c234.8,860.4,234.6,860.9,234.6,861.2c234.6,861.5,234.4,862.1,234.0,862.6c233.3,863.6,233.3,864.0,234.0,865.0c234.4,865.5,234.6,866.2,234.6,866.9c234.6,867.4,234.8,868.2,235.0,868.6c235.5,869.6,235.5,921.2,235.0,922.2c234.8,922.6,234.6,923.1,234.6,923.4c234.6,923.7,234.4,924.3,234.0,924.8c233.3,925.8,233.3,926.2,234.0,927.2c234.4,927.6,234.6,928.2,234.6,928.5c234.6,928.8,234.8,929.4,235.0,929.7c235.5,930.7,235.5,977.5,235.0,978.5c234.8,978.9,234.6,979.7,234.6,980.3c234.6,980.9,234.5,981.6,234.3,981.8c234.1,982.0,233.9,982.4,233.9,982.7c233.9,983.7,232.2,986.9,231.7,986.9c231.6,986.9,231.1,987.4,230.8,988.0c230.3,988.7,229.9,989.0,229.4,989.0c229.0,989.0,228.5,989.2,228.3,989.4c228.1,989.8,221.1,989.9,194.9,989.9c168.6,989.9,161.6,989.8,161.4,989.4c161.2,989.2,160.9,989.0,160.7,989.0c160.5,989.0,159.7,988.0,158.9,986.9c157.4,984.7,157.4,984.7,156.8,985.2c156.4,985.5,156.1,986.1,156.0,986.6c155.9,987.1,155.6,987.6,155.4,987.8c155.1,988.1,154.7,988.4,154.6,988.6c154.4,988.8,154.1,989.0,153.8,989.0c153.5,989.0,153.2,989.2,153.0,989.4c152.8,989.8,145.8,989.9,119.5,989.9c93.3,989.9,86.3,989.8,86.0,989.4c85.9,989.2,85.6,989.0,85.4,989.0c85.1,989.0,84.8,988.8,84.7,988.5c84.5,988.2,84.2,988.0,84.0,988.0c83.8,988.0,83.2,987.3,82.7,986.4c81.7,984.7,81.4,984.7,80.8,986.8c80.6,987.6,80.3,988.0,80.0,988.0c79.8,988.0,79.5,988.2,79.3,988.5c79.1,988.8,78.8,989.0,78.6,989.0c78.4,989.0,78.1,989.2,77.9,989.4c77.7,989.8,70.9,989.9,45.4,989.9c27.7,989.9,13.0,989.9,12.6,989.8|m267.1,989.6c266.7,989.5,266.1,989.2,265.7,989.1c264.6,988.8,263.5,987.8,262.2,985.9c261.4,984.9,260.8,983.8,260.8,983.5c260.8,983.2,260.7,982.7,260.5,982.5c260.3,982.2,260.1,981.8,260.1,981.4c260.1,981.1,260.0,980.7,259.9,980.6c259.7,980.5,259.6,971.6,259.6,955.1c259.6,928.0,259.6,929.4,260.9,927.3c261.6,926.1,261.6,926.0,260.8,924.3c260.6,923.7,260.3,923.0,260.2,922.7c260.1,922.4,260.0,921.9,259.9,921.6c259.7,921.2,259.6,910.1,259.6,894.4c259.6,865.6,259.6,866.8,260.9,865.0c261.7,864.0,261.7,863.6,260.8,862.4c260.4,861.9,260.1,861.2,260.1,860.8c260.1,860.5,260.0,860.1,259.9,860.0c259.7,859.9,259.6,851.2,259.6,835.1c259.6,819.0,259.7,810.3,259.9,810.2c260.0,810.1,260.1,809.7,260.1,809.4c260.1,809.0,260.3,808.5,260.5,808.3c260.7,808.1,260.8,807.6,260.8,807.3c260.8,806.5,261.9,805.2,263.5,804.0l264.9,803.0l299.5,803.0l334.0,803.0l334.9,804.3c335.4,805.0,335.9,805.6,336.0,805.6c336.1,805.6,336.6,805.0,337.1,804.3l338.0,803.0l373.2,803.0l408.4,803.0l409.3,804.3c410.3,805.8,411.1,805.9,411.9,804.8c412.2,804.3,413.0,803.7,413.6,803.4c414.5,802.8,417.5,802.8,449.1,802.9l483.6,803.0l485.0,804.0c486.7,805.2,487.5,806.2,487.5,807.0c487.5,807.3,487.6,807.7,487.8,808.0c488.0,808.2,488.2,808.7,488.2,809.0c488.2,809.3,488.3,809.8,488.5,810.0c488.8,810.4,488.9,813.6,488.9,835.1c488.9,856.6,488.8,859.8,488.5,860.2c488.3,860.4,488.2,860.9,488.2,861.2c488.2,861.5,488.0,862.0,487.8,862.2c487.6,862.5,487.5,863.2,487.5,863.8c487.5,864.4,487.6,865.1,487.8,865.3c488.0,865.6,488.2,866.0,488.2,866.4c488.2,866.7,488.3,867.2,488.5,867.4c488.8,867.8,488.9,871.3,488.9,895.4l488.9,922.9l488.2,923.9c487.4,925.0,487.2,926.8,487.8,927.5c488.0,927.8,488.2,928.2,488.2,928.5c488.2,928.9,488.3,929.3,488.5,929.6c488.8,930.0,488.9,933.2,488.9,954.7c488.9,976.1,488.8,979.4,488.5,979.7c488.3,980.0,488.2,980.5,488.2,981.0c488.2,981.5,487.9,982.3,487.6,983.0c487.3,983.6,487.0,984.3,487.0,984.6c487.0,985.1,485.6,986.9,485.2,986.9c485.1,986.9,484.8,987.2,484.7,987.5c484.5,987.7,484.2,988.0,484.0,988.0c483.8,988.0,483.4,988.2,483.3,988.5c483.1,988.8,482.6,989.0,482.2,989.0c481.8,989.0,481.4,989.2,481.2,989.4c480.8,990.0,416.5,990.1,415.6,989.5c415.3,989.2,414.6,988.7,414.0,988.4c413.4,988.0,412.6,987.0,412.0,986.3l411.1,984.9l410.2,986.3c409.2,987.6,408.5,988.3,407.7,988.9c407.5,989.0,407.1,989.2,406.8,989.5c406.0,990.1,340.7,990.0,340.3,989.4c340.2,989.2,339.7,989.0,339.4,989.0c338.8,989.0,338.4,988.6,337.5,987.1c336.9,986.1,336.2,985.2,336.1,985.2c335.9,985.2,335.2,986.1,334.5,987.1c333.5,988.6,333.1,989.0,332.5,989.0c332.1,989.0,331.7,989.2,331.5,989.4c331.1,990.0,268.5,990.2,267.1,989.6|m518.2,989.8c517.9,989.7,517.4,989.5,517.3,989.3c517.2,989.1,516.8,989.0,516.4,989.0c515.9,989.0,515.5,988.8,515.3,988.5c515.2,988.2,514.9,988.0,514.7,988.0c514.1,988.0,511.1,983.1,511.1,982.1c511.1,981.6,511.0,981.1,510.8,980.8c510.6,980.5,510.5,974.8,510.5,954.7l510.5,928.9l511.2,927.9c511.9,926.8,512.0,925.1,511.5,924.4c511.3,924.2,511.1,923.7,511.1,923.4c511.1,923.1,511.0,922.7,510.8,922.4c510.6,922.1,510.5,916.0,510.5,894.4l510.5,866.8l511.2,865.8c511.6,865.2,511.8,864.4,511.8,863.8c511.8,863.2,511.6,862.4,511.2,861.8l510.5,860.8l510.5,835.3c510.5,813.4,510.6,809.7,510.9,808.8c511.4,807.2,513.5,803.8,513.9,803.8c514.1,803.8,514.4,803.7,514.6,803.4c514.8,803.1,522.2,803.0,549.4,802.9c581.1,802.8,584.1,802.8,585.0,803.4c585.6,803.7,586.4,804.3,586.7,804.8c587.4,805.8,587.5,805.8,588.3,804.8c588.6,804.3,589.4,803.7,589.9,803.4c590.9,802.8,593.9,802.8,625.5,802.9l660.1,803.0l661.0,804.3c661.5,805.0,662.1,805.6,662.3,805.6c662.6,805.6,663.2,805.0,663.7,804.3l664.6,803.0l699.5,802.9c739.2,802.8,735.5,802.5,737.8,805.9c738.9,807.4,739.2,808.0,739.2,808.8c739.2,809.4,739.3,810.1,739.5,810.3c739.7,810.7,739.8,816.2,739.8,835.6l739.8,860.5l739.1,861.5c738.6,862.2,738.5,862.8,738.5,863.9c738.5,864.7,738.6,865.4,738.7,865.5c738.8,865.6,739.1,866.3,739.4,867.0c739.7,868.2,739.8,870.1,739.8,895.4l739.8,922.6l739.1,923.8c738.7,924.6,738.5,925.5,738.5,926.2c738.5,926.9,738.7,927.6,739.1,928.3l739.8,929.3l739.8,954.7c739.8,974.5,739.7,980.1,739.5,980.5c739.3,980.7,739.2,981.2,739.2,981.5c739.2,981.8,739.0,982.2,738.8,982.5c738.6,982.7,738.5,983.2,738.5,983.5c738.5,984.1,736.6,986.9,736.2,986.9c736.1,986.9,735.6,987.4,735.2,987.9c734.7,988.5,734.1,989.0,733.7,989.1c733.3,989.2,732.4,989.5,731.8,989.7c729.9,990.3,666.8,990.0,666.4,989.4c666.2,989.2,665.9,989.0,665.7,989.0c665.5,989.0,665.2,988.8,665.0,988.5c664.9,988.2,664.5,988.0,664.3,988.0c664.1,988.0,663.7,987.6,663.5,987.1c662.9,985.9,662.0,985.1,661.6,985.6c661.5,985.8,661.3,986.3,661.2,986.7c661.2,987.1,661.0,987.5,660.8,987.7c660.5,987.8,660.2,988.1,659.9,988.3c659.7,988.5,659.4,988.8,659.2,988.9c659.0,989.0,658.6,989.2,658.3,989.5c657.4,990.1,591.7,990.0,591.3,989.4c591.1,989.2,590.9,989.0,590.6,989.0c590.4,989.0,589.7,988.1,588.9,986.9l587.5,984.9l586.1,986.9c585.2,988.2,584.4,989.0,584.0,989.1c583.6,989.2,582.8,989.5,582.2,989.7c581.2,990.0,519.8,990.1,518.2,989.8|m771.2,989.8c770.9,989.7,770.4,989.5,770.2,989.4c769.9,989.2,769.5,989.0,769.4,988.9c769.2,988.8,768.8,988.5,768.7,988.3c768.5,988.2,768.1,987.9,768.0,987.8c766.7,987.1,765.4,985.4,765.4,984.5c765.4,984.2,765.3,983.8,765.1,983.7c765.0,983.6,764.7,982.8,764.4,982.0c764.0,980.5,764.0,979.7,764.0,954.8l764.0,929.2l765.0,927.6l766.1,925.9l765.4,924.9c765.0,924.4,764.7,923.7,764.7,923.4c764.7,923.1,764.5,922.6,764.3,922.2c764.0,921.6,764.0,917.7,764.0,894.3l764.0,867.1l764.7,865.9c765.5,864.6,765.6,863.0,765.0,862.2c764.8,862.0,764.7,861.6,764.7,861.3c764.7,861.0,764.5,860.4,764.3,860.0c764.0,859.5,764.0,855.9,764.0,834.7c764.0,811.8,764.0,809.9,764.4,808.9c765.1,807.0,766.4,805.1,767.4,804.4c767.9,804.1,768.6,803.6,768.9,803.4c769.3,803.1,778.5,803.0,804.2,803.0l839.0,803.0l839.9,804.3c840.5,805.0,841.1,805.6,841.4,805.6c841.7,805.6,842.3,805.0,842.9,804.3l843.8,803.0l879.1,803.0c907.0,803.0,914.4,803.1,914.7,803.4c914.8,803.7,915.1,803.8,915.3,803.8c915.5,803.8,916.0,804.2,916.3,804.7c917.0,805.9,917.7,805.8,918.7,804.2c919.5,803.0,919.8,802.8,920.6,802.8c921.1,802.8,921.8,802.6,922.0,802.3c922.4,802.0,922.5,801.9,922.8,802.2c923.0,802.5,931.3,802.7,955.9,802.7c992.5,802.8,989.8,802.6,991.8,805.3c992.3,806.1,992.7,806.9,992.7,807.1c992.7,807.3,993.0,808.3,993.3,809.1l993.9,810.8l993.9,834.6c993.9,855.0,993.9,858.5,993.6,859.4c993.4,859.9,993.2,860.7,993.2,861.1c993.2,861.5,993.0,862.1,992.6,862.6c991.9,863.5,991.9,864.0,992.4,864.7c992.6,864.9,993.1,865.7,993.4,866.4l993.9,867.7l993.9,894.8c993.9,921.0,993.9,921.9,993.5,923.2c993.2,923.9,992.8,924.7,992.5,925.0c991.9,925.6,991.9,926.2,992.5,927.0c992.8,927.4,993.2,928.3,993.5,929.0c993.9,930.3,993.9,931.5,993.9,954.7c993.9,975.6,993.9,979.1,993.6,980.0c993.4,980.5,993.2,981.3,993.2,981.6c993.2,982.0,993.0,982.7,992.6,983.2c992.3,983.6,992.0,984.2,992.0,984.5c992.0,985.2,991.6,985.9,991.1,985.9c990.9,985.9,990.5,986.3,990.2,986.8c989.9,987.2,989.1,988.0,988.6,988.3c988.0,988.7,987.2,989.2,986.9,989.5c986.1,990.1,921.8,990.0,921.4,989.4c921.2,989.2,920.9,989.0,920.7,989.0c920.5,989.0,920.2,988.8,920.0,988.5c919.8,988.2,919.5,988.0,919.3,988.0c919.1,988.0,918.5,987.3,918.0,986.6c917.1,985.2,917.0,985.2,916.5,985.7c916.2,985.9,915.6,986.8,915.2,987.6c914.7,988.4,914.2,989.0,913.9,989.0c913.7,989.0,913.4,989.2,913.3,989.4c913.0,989.8,905.9,989.9,879.4,989.9c852.9,989.9,845.8,989.8,845.6,989.4c845.4,989.2,845.1,989.0,844.9,989.0c844.7,989.0,844.4,988.8,844.2,988.5c844.1,988.2,843.7,988.0,843.5,988.0c843.3,988.0,842.7,987.3,842.1,986.4c841.2,985.0,841.1,984.9,840.7,985.4c840.4,985.7,840.2,986.3,840.2,986.7c840.1,987.1,839.9,987.6,839.6,987.8c839.3,988.1,838.9,988.4,838.8,988.6c838.6,988.8,838.3,989.0,838.0,989.0c837.7,989.0,837.4,989.2,837.2,989.4c837.0,989.8,830.1,989.9,804.4,989.9c786.5,989.9,771.5,989.9,771.2,989.8|m63.2,987.8c63.6,987.2,63.7,987.2,64.1,987.8c64.6,988.5,70.0,988.6,70.7,987.8c71.1,987.4,72.0,987.3,74.5,987.3c77.2,987.3,77.9,987.2,78.1,986.8c78.3,986.5,78.6,986.3,78.8,986.3c79.3,986.3,79.8,985.6,79.8,984.9c79.8,984.5,79.9,984.1,80.1,983.9c80.3,983.6,80.5,983.2,80.5,982.8c80.5,982.5,80.6,982.0,80.8,981.8c81.3,981.2,81.3,977.4,80.8,976.5c80.3,975.5,80.3,947.4,80.8,945.6c81.3,943.8,81.3,932.8,80.8,931.8c80.6,931.4,80.5,930.9,80.5,930.6c80.5,930.3,80.1,929.4,79.6,928.6l78.6,927.2l76.2,927.0c74.9,926.9,59.3,926.8,41.5,926.9c14.3,927.0,9.1,927.1,8.7,927.5c8.3,927.7,7.9,928.1,7.7,928.2c7.6,928.3,7.3,928.6,7.2,928.9c6.4,931.4,6.4,930.9,6.4,955.4c6.4,974.1,6.5,979.4,6.7,979.8c6.9,980.0,7.0,980.5,7.0,980.8c7.0,981.1,7.2,981.6,7.4,981.8c7.6,982.0,7.7,982.5,7.7,982.8c7.7,983.5,8.9,985.2,9.4,985.2c9.6,985.2,9.9,985.5,10.1,985.7c10.2,986.0,10.5,986.3,10.7,986.3c10.9,986.3,11.2,986.5,11.5,986.8c12.0,987.2,15.8,987.3,36.9,987.4c56.4,987.4,61.8,987.6,62.0,987.9c62.4,988.5,62.7,988.4,63.2,987.8|m120.4,987.9c120.7,987.6,124.3,987.4,136.8,987.3l152.8,987.2l154.1,985.4c156.4,982.3,156.3,983.9,156.3,956.5c156.3,934.1,156.2,932.7,155.8,931.1c155.6,930.1,155.0,929.0,154.5,928.3c153.7,927.3,153.5,927.2,151.5,927.0c150.3,926.9,135.0,926.8,117.5,926.9c93.7,927.0,85.6,927.1,85.3,927.4c85.0,927.6,84.6,927.9,84.4,928.0c84.2,928.1,83.8,928.8,83.5,929.6c83.1,931.1,83.0,931.6,83.0,956.6c83.0,979.5,83.1,982.1,83.4,983.2c83.9,984.8,84.9,986.3,85.4,986.3c85.6,986.3,85.9,986.5,86.1,986.7c86.3,987.2,88.7,987.3,101.1,987.4c112.4,987.4,115.8,987.6,116.1,987.9c116.2,988.2,117.0,988.3,118.2,988.3c119.4,988.3,120.2,988.2,120.4,987.9|m522.3,987.9c522.5,987.6,529.0,987.4,552.7,987.4c572.5,987.3,583.0,987.1,583.4,986.9c583.7,986.7,584.5,985.9,585.1,985.0l586.1,983.5l586.2,962.4c586.3,946.2,586.4,941.2,586.6,940.9c587.0,940.3,587.0,937.1,586.6,936.5c586.4,936.2,586.4,936.0,586.6,935.7c587.0,935.1,587.0,931.8,586.5,931.3c586.4,931.1,586.2,930.6,586.2,930.2c586.2,929.9,585.8,929.1,585.2,928.4c584.4,927.3,584.2,927.2,582.1,927.0c581.0,926.9,565.2,926.8,547.1,926.9c521.1,927.0,514.1,927.1,513.9,927.4c513.7,927.7,513.4,927.9,513.2,927.9c512.7,927.9,512.3,928.6,511.9,930.2c511.5,931.8,511.4,978.2,511.8,978.5c511.9,978.6,512.0,979.3,512.0,980.0c512.0,981.1,512.2,981.5,513.8,983.8c514.8,985.1,515.7,986.3,515.9,986.3c516.1,986.3,516.3,986.5,516.5,986.8c516.7,987.1,517.2,987.3,517.9,987.3c518.6,987.3,519.1,987.5,519.3,987.8c519.7,988.4,521.9,988.5,522.3,987.9|m785.6,987.8c786.2,987.1,787.5,987.1,787.8,987.8c788.0,988.1,788.4,988.3,788.8,988.3c789.1,988.3,789.5,988.1,789.7,987.8c790.1,987.1,792.7,987.1,793.3,987.8c794.0,988.5,800.7,988.6,801.1,987.9c801.4,987.6,805.4,987.4,819.2,987.3l837.0,987.2l838.3,985.4c840.6,982.2,840.5,983.9,840.4,956.2c840.4,935.4,840.3,932.0,840.0,930.9c839.5,929.2,838.6,927.9,838.0,927.9c837.7,927.9,837.4,927.7,837.2,927.4c837.0,927.1,829.7,927.0,802.5,927.0c775.2,927.0,767.9,927.1,767.7,927.4c767.5,927.7,767.2,927.9,766.9,927.9c766.2,927.9,766.0,928.3,765.5,930.3c765.0,932.6,765.0,977.9,765.5,979.9c766.4,983.3,768.1,986.3,769.1,986.3c769.5,986.3,769.9,986.5,770.2,986.8c770.6,987.1,771.9,987.3,776.1,987.4c780.0,987.4,781.6,987.6,781.8,987.9c782.2,988.5,785.0,988.4,785.6,987.8|m228.2,986.8c228.5,986.5,229.0,986.3,229.2,986.3c229.5,986.3,229.8,986.0,229.9,985.7c230.1,985.5,230.3,985.2,230.5,985.2c230.9,985.2,232.5,982.9,233.0,981.7c233.2,981.0,233.4,979.7,233.5,978.7c233.6,977.7,233.8,976.7,233.9,976.5c234.3,976.0,234.2,942.2,233.9,941.7c233.7,941.4,233.6,940.2,233.6,938.2c233.6,936.2,233.7,935.0,233.9,934.7c234.7,933.5,233.8,929.9,232.2,928.1l231.3,927.0l196.5,927.0c168.9,927.0,161.6,927.1,161.4,927.4c161.2,927.7,160.9,927.9,160.6,927.9c159.9,927.9,158.8,929.6,158.8,930.7c158.8,931.2,158.7,932.0,158.5,932.5c158.2,933.4,158.1,936.7,158.1,956.0c158.1,975.3,158.2,978.7,158.5,979.5c158.7,980.1,158.8,981.1,158.8,981.9c158.8,983.1,159.0,983.5,159.8,984.8c160.4,985.6,160.9,986.3,161.1,986.3c161.2,986.3,161.7,986.5,162.0,986.8c162.6,987.2,166.8,987.3,195.1,987.3c223.4,987.3,227.6,987.2,228.2,986.8|m332.6,986.3c333.0,985.9,333.6,985.0,334.0,984.3l334.6,983.0l334.6,957.0c334.6,936.7,334.6,930.9,334.3,930.6c334.2,930.3,334.0,929.8,334.0,929.4c334.0,928.5,333.6,927.9,333.0,927.9c332.7,927.9,332.4,927.7,332.2,927.4c332.0,927.1,325.1,927.0,299.7,926.9c282.0,926.8,266.5,926.9,265.3,927.0c263.1,927.2,263.1,927.3,262.2,928.6c261.7,929.4,261.3,930.3,261.3,930.6c261.3,930.9,261.2,931.4,261.0,931.6c260.8,931.9,260.7,937.0,260.7,954.7c260.7,972.3,260.8,977.4,261.0,977.7c261.2,978.0,261.3,978.6,261.3,979.2c261.3,979.8,261.4,980.5,261.6,980.8c261.8,981.0,262.0,981.4,262.0,981.8c262.0,982.5,264.6,986.3,265.0,986.3c265.2,986.3,265.6,986.5,266.0,986.8c266.5,987.2,271.2,987.3,299.2,987.2l331.8,987.1l332.6,986.3|m406.6,986.8c407.0,986.5,407.4,986.3,407.6,986.3c407.9,986.3,409.1,984.5,409.1,983.9c409.1,983.6,409.3,983.0,409.5,982.7c410.0,981.7,410.0,931.2,409.5,930.6c409.3,930.4,409.1,929.8,409.1,929.3c409.0,928.8,408.8,928.3,408.7,928.2c408.5,928.1,408.0,927.7,407.6,927.5c407.1,927.1,401.2,927.0,373.1,927.0l339.2,927.0l338.3,928.4c337.7,929.1,337.3,930.0,337.3,930.3c337.3,930.6,337.2,931.1,337.0,931.3c336.4,931.9,336.4,979.9,337.0,980.9c337.2,981.3,337.3,982.0,337.3,982.5c337.3,983.0,337.6,984.0,338.1,984.8c339.7,987.5,336.6,987.3,373.2,987.3c401.8,987.3,406.0,987.2,406.6,986.8|m481.7,986.8c482.1,986.5,482.6,986.3,482.8,986.3c483.0,986.3,483.3,986.0,483.5,985.7c483.7,985.5,484.0,985.2,484.2,985.2c484.6,985.2,485.8,983.2,485.8,982.6c485.8,982.5,486.2,981.9,486.5,981.2c487.0,980.4,487.3,979.7,487.3,978.9c487.3,978.3,487.4,977.7,487.5,977.5c487.8,977.0,488.1,952.6,487.8,940.8l487.7,930.9l486.4,928.9l485.2,927.0l450.2,927.0c422.5,927.0,415.2,927.1,414.9,927.4c414.8,927.7,414.4,927.9,414.1,927.9c413.8,927.9,413.4,928.3,413.1,929.0l412.5,930.1l412.5,956.3c412.5,976.8,412.6,982.5,412.8,982.9c413.0,983.1,413.1,983.5,413.1,983.8c413.1,984.5,414.3,986.3,414.7,986.3c414.9,986.3,415.4,986.5,415.7,986.8c416.6,987.5,480.7,987.5,481.7,986.8|m658.7,986.3c659.1,985.9,659.7,985.0,660.1,984.3l660.7,983.0l660.7,956.5l660.7,929.9l659.7,928.5l658.7,927.0l625.2,927.0c598.6,927.0,591.5,927.1,591.3,927.4c591.1,927.7,590.8,927.9,590.5,927.9c590.2,927.9,589.8,928.3,589.4,929.0l588.8,930.2l588.8,956.7l588.8,983.2l589.7,984.7c591.5,987.5,588.2,987.3,625.0,987.2l657.9,987.1l658.7,986.3|m733.5,986.6c734.9,986.0,737.3,982.8,737.3,981.8c737.3,981.4,737.5,981.0,737.7,980.8c737.9,980.5,738.0,980.1,738.0,979.8c738.0,979.4,738.1,979.0,738.3,978.8c738.5,978.4,738.6,973.1,738.6,954.7l738.6,931.1l738.0,929.8c737.6,929.2,737.0,928.2,736.6,927.8l735.8,927.0l700.9,927.0l666.1,927.0l665.0,928.3c663.1,930.7,663.3,928.1,663.3,956.6c663.3,976.5,663.3,982.2,663.6,982.5c663.7,982.8,663.9,983.2,663.9,983.4c663.9,984.2,665.1,986.3,665.5,986.3c665.7,986.3,666.2,986.5,666.6,986.8c667.2,987.2,671.4,987.3,699.8,987.3c730.9,987.3,732.4,987.3,733.5,986.6|m912.8,987.0c913.8,986.4,915.1,984.5,915.1,983.7c915.1,983.2,915.2,982.8,915.3,982.7c915.5,982.5,915.6,973.3,915.6,956.1l915.6,929.7l914.9,928.8c914.5,928.3,914.1,927.9,913.9,927.9c913.7,927.9,913.4,927.7,913.3,927.4c913.0,927.1,905.9,927.0,879.1,927.0l845.3,927.0l844.5,927.8c844.1,928.3,843.4,929.3,843.0,930.0l842.3,931.4l842.3,956.0c842.3,977.1,842.4,980.7,842.7,981.6c842.9,982.1,843.0,982.8,843.0,983.0c843.0,983.2,843.2,983.6,843.4,983.8c843.6,984.1,843.7,984.6,843.8,985.0c843.9,985.7,844.0,985.8,845.4,986.7c846.1,987.2,849.8,987.3,879.2,987.3c899.1,987.3,912.5,987.2,912.8,987.0|m987.7,986.8c988.1,986.5,988.5,986.3,988.6,986.3c989.0,986.3,991.6,982.4,991.6,981.8c991.6,981.4,991.7,981.0,991.9,980.8c992.1,980.5,992.3,979.8,992.3,979.2c992.3,978.6,992.4,978.0,992.6,977.7c992.8,977.4,992.9,972.3,992.9,954.7c992.9,937.0,992.8,931.9,992.6,931.6c992.4,931.4,992.3,930.8,992.3,930.4c992.3,929.9,991.9,929.2,991.3,928.4c990.4,927.3,990.3,927.2,988.0,927.0c986.7,926.9,971.1,926.8,953.3,926.9l921.1,927.0l920.3,927.8c919.9,928.2,919.2,929.2,918.9,929.8l918.2,931.1l918.2,956.6c918.2,976.5,918.3,982.2,918.5,982.5c918.7,982.8,918.8,983.3,918.8,983.6c918.8,984.5,919.9,986.3,920.5,986.3c920.7,986.3,921.2,986.5,921.6,986.8c922.1,987.2,926.3,987.3,954.6,987.3c982.9,987.3,987.1,987.2,987.7,986.8|m77.9,924.5c78.1,924.3,78.4,924.1,78.7,924.1c79.5,924.1,80.5,922.4,80.5,921.0c80.5,920.3,80.6,919.6,80.8,919.3c81.0,919.0,81.1,916.1,81.1,907.4c81.1,898.7,81.0,895.8,80.8,895.5c80.5,895.2,80.5,893.3,80.5,888.6c80.5,883.0,80.5,882.0,80.9,881.4c81.2,880.9,81.2,880.7,81.0,880.3c80.7,879.9,80.7,879.6,80.9,879.1c81.3,878.0,81.2,870.4,80.8,869.6c80.6,869.2,80.5,868.6,80.5,868.2c80.5,867.3,79.3,865.7,78.7,865.7c78.4,865.7,78.1,865.5,77.9,865.3c77.7,864.9,70.5,864.8,43.4,864.8l9.2,864.8l8.5,865.6c8.1,866.1,7.4,867.0,7.1,867.7l6.4,868.9l6.4,891.6c6.3,904.1,6.3,915.9,6.4,917.8c6.6,921.1,6.6,921.3,7.4,922.6c7.8,923.4,8.5,924.1,8.9,924.3c9.4,924.4,10.0,924.7,10.3,924.8c10.6,924.9,25.9,925.0,44.3,925.0c70.6,925.0,77.7,924.8,77.9,924.5|m152.5,924.5c152.7,924.3,153.0,924.1,153.2,924.1c153.4,924.1,154.0,923.4,154.5,922.6c156.3,919.9,156.3,921.1,156.3,894.4c156.3,873.0,156.2,870.4,155.9,869.0c155.4,867.2,154.5,865.7,153.8,865.7c153.5,865.7,153.2,865.5,153.0,865.3c152.8,864.9,145.7,864.8,119.2,864.8l85.6,864.8l84.3,866.7l83.0,868.6l83.0,894.9l83.0,921.1l84.0,922.6c84.6,923.4,85.2,924.1,85.4,924.1c85.6,924.1,85.9,924.2,86.0,924.4c86.1,924.6,86.5,924.8,86.8,924.9c87.1,925.0,102.0,925.0,119.8,925.0c145.4,924.9,152.3,924.8,152.5,924.5|m231.1,924.5c231.3,924.3,231.6,924.1,231.8,924.1c232.3,924.1,233.3,922.5,233.8,920.8c234.1,919.6,234.2,917.4,234.1,895.1c234.0,868.9,234.0,868.5,232.8,866.6c231.6,864.8,232.9,864.8,195.9,864.8c168.8,864.8,161.6,864.9,161.4,865.3c161.2,865.5,160.9,865.7,160.6,865.7c160.0,865.7,159.5,866.3,159.5,867.0c159.5,867.2,159.2,868.0,158.9,868.7l158.2,869.9l158.2,894.1c158.1,915.2,158.2,918.4,158.5,919.4c158.7,919.9,158.8,920.6,158.8,920.8c158.8,921.4,160.8,924.1,161.2,924.1c161.4,924.1,161.6,924.2,161.8,924.4c161.9,924.6,162.3,924.8,162.6,924.9c162.9,925.0,178.4,925.0,197.0,925.0c223.7,924.9,230.9,924.8,231.1,924.5|m331.5,924.6c332.4,924.2,333.0,923.6,333.6,922.7l334.5,921.3l334.6,917.1c334.7,914.8,334.7,903.0,334.7,890.9l334.6,868.9l334.0,867.7c333.6,867.0,333.0,866.1,332.6,865.6l331.8,864.8l298.9,864.7c280.9,864.7,265.4,864.7,264.6,864.8c263.3,865.0,263.0,865.2,262.2,866.4c261.7,867.2,261.3,868.1,261.3,868.4c261.3,868.7,261.2,869.2,261.0,869.4c260.8,869.7,260.7,875.3,260.7,894.9c260.7,914.5,260.8,920.0,261.0,920.4c261.2,920.6,261.3,921.1,261.3,921.5c261.3,922.6,262.3,923.8,263.7,924.5c264.8,925.0,267.5,925.1,297.6,925.1c327.1,925.1,330.4,925.1,331.5,924.6|m406.8,924.5c407.0,924.3,407.3,924.1,407.5,924.1c407.7,924.1,408.3,923.4,408.9,922.5l409.8,921.0l409.8,894.9l409.8,868.9l408.6,866.9l407.3,864.8l373.6,864.8c347.0,864.8,339.8,864.9,339.6,865.3c339.5,865.5,339.2,865.7,338.9,865.7c338.5,865.7,337.3,867.4,337.3,868.1c337.3,868.4,337.2,868.9,337.0,869.1c336.7,869.5,336.6,872.8,336.6,894.9c336.6,917.0,336.7,920.3,337.0,920.6c337.2,920.9,337.3,921.3,337.3,921.6c337.3,922.3,338.5,924.1,338.9,924.1c339.2,924.1,339.4,924.2,339.5,924.4c339.7,924.6,340.0,924.8,340.4,924.9c340.7,925.0,355.7,925.0,373.7,925.0c399.6,924.9,406.6,924.8,406.8,924.5|m484.7,924.5c484.9,924.3,485.2,924.1,485.4,924.1c485.6,924.1,486.2,923.4,486.7,922.6l487.7,921.1l487.8,910.1c488.1,895.5,487.8,870.8,487.4,869.0c487.1,867.5,485.9,865.7,485.4,865.7c485.2,865.7,484.9,865.5,484.7,865.3c484.5,864.9,477.2,864.8,449.9,864.8l415.3,864.8l414.6,865.6c414.1,866.1,413.5,867.0,413.2,867.7l412.5,868.9l412.4,889.9c412.3,906.1,412.2,911.1,412.0,911.4c411.5,912.1,411.6,919.1,412.0,919.6c412.2,919.9,412.4,920.3,412.4,920.6c412.4,921.6,414.2,923.9,415.5,924.5c416.6,925.0,419.1,925.1,450.6,925.0c477.3,925.0,484.5,924.8,484.7,924.5|m583.0,924.5c583.9,924.1,584.6,923.5,585.2,922.6l586.1,921.3l586.2,897.1c586.3,878.4,586.4,872.8,586.6,872.5c587.0,871.9,587.0,870.7,586.5,870.1c586.4,869.9,586.2,869.2,586.2,868.6c586.2,867.4,585.2,865.7,584.4,865.7c584.2,865.7,583.8,865.5,583.7,865.3c583.4,864.9,576.1,864.8,548.7,864.8l514.1,864.8l512.8,866.8l511.6,868.8l511.6,894.1c511.6,914.1,511.7,919.7,511.9,920.7c512.2,922.2,513.4,924.1,513.9,924.1c514.1,924.1,514.4,924.2,514.5,924.4c514.6,924.6,515.0,924.8,515.3,924.9c515.6,924.9,530.7,925.0,548.8,925.1c579.3,925.1,581.7,925.1,583.0,924.5|m657.6,924.5c657.7,924.3,658.0,924.1,658.3,924.1c658.5,924.1,659.1,923.5,659.6,922.7l660.5,921.4l660.7,914.7c660.8,911.0,660.8,898.9,660.8,887.9l660.7,867.8l660.0,866.7c659.6,866.2,659.2,865.7,659.0,865.7c658.7,865.7,658.4,865.5,658.3,865.3c658.0,864.9,651.0,864.8,624.8,864.8c598.6,864.8,591.5,864.9,591.3,865.3c591.1,865.5,590.8,865.7,590.5,865.7c589.9,865.7,589.5,866.3,589.5,867.3c589.5,867.7,589.3,868.2,589.1,868.4c588.8,868.8,588.8,872.2,588.8,894.9l588.8,921.0l589.7,922.5c590.3,923.4,590.9,924.1,591.1,924.1c591.3,924.1,591.6,924.2,591.7,924.4c591.8,924.6,592.2,924.8,592.5,924.9c592.8,925.0,607.5,925.0,625.2,925.0c650.5,924.9,657.3,924.8,657.6,924.5|m735.5,924.6c736.3,924.2,737.0,923.6,737.6,922.7c738.4,921.4,738.5,921.1,738.6,918.8c738.7,917.5,738.7,905.7,738.7,892.6l738.6,868.9l738.0,867.7c737.6,867.0,737.0,866.1,736.6,865.6l735.8,864.8l700.9,864.8l666.1,864.8l665.0,866.1c663.1,868.5,663.3,866.3,663.2,891.6c663.2,904.1,663.2,915.9,663.3,917.8l663.4,921.4l664.4,922.7c664.9,923.5,665.5,924.1,665.7,924.1c665.9,924.1,666.2,924.2,666.3,924.4c666.4,924.6,666.8,924.8,667.1,924.9c667.5,924.9,682.7,925.0,701.0,925.1c731.0,925.1,734.3,925.1,735.5,924.6|m836.8,924.5c836.9,924.3,837.4,924.1,837.8,924.1c838.5,924.1,839.8,922.6,839.8,921.8c839.8,921.6,839.9,921.0,840.1,920.4c840.6,918.9,840.6,870.8,840.1,869.3c839.9,868.8,839.8,868.2,839.8,867.9c839.8,867.3,838.5,865.7,838.0,865.7c837.7,865.7,837.4,865.5,837.2,865.3c837.0,864.9,829.7,864.8,802.3,864.8l767.7,864.8l766.7,866.3c766.1,867.2,765.5,868.2,765.4,868.7c765.2,869.4,765.2,877.6,765.2,895.5l765.3,921.3l766.2,922.7c766.7,923.5,767.3,924.1,767.5,924.1c767.7,924.1,768.0,924.2,768.1,924.4c768.2,924.6,768.6,924.8,768.9,924.9c769.2,925.0,784.5,925.0,803.0,925.0c829.4,924.9,836.5,924.8,836.8,924.5|m912.4,924.9c913.1,924.7,913.6,924.2,914.4,923.0l915.6,921.4l915.6,895.1c915.6,875.8,915.5,868.6,915.3,868.0c915.1,867.6,914.9,867.0,914.9,866.7c914.8,866.5,914.6,866.1,914.4,866.0c914.2,865.9,913.7,865.6,913.4,865.3c912.8,864.9,907.0,864.8,879.0,864.8l845.3,864.8l844.5,865.6c844.1,866.1,843.4,867.1,843.0,867.8l842.3,869.2l842.3,894.3c842.3,915.9,842.4,919.6,842.7,920.4c842.9,921.0,843.0,921.6,843.0,921.8c843.0,922.4,844.3,924.1,844.7,924.1c844.9,924.1,845.2,924.2,845.3,924.4c845.4,924.6,845.8,924.8,846.1,924.9c847.0,925.1,911.4,925.1,912.4,924.9|m990.2,924.4c991.4,923.7,992.3,922.4,992.3,921.5c992.3,921.1,992.4,920.6,992.6,920.4c992.8,920.0,992.9,914.5,992.9,894.9c992.9,875.3,992.8,869.7,992.6,869.4c992.4,869.2,992.3,868.7,992.3,868.3c992.3,867.3,991.1,865.7,990.5,865.7c990.2,865.7,989.9,865.5,989.7,865.3c989.5,864.9,982.3,864.8,955.3,864.8l921.1,864.8l920.3,865.6c919.9,866.1,919.2,867.0,918.9,867.6l918.3,868.8l918.2,888.0c918.1,898.6,918.1,910.4,918.2,914.2l918.4,921.3l919.2,922.7c919.7,923.5,920.2,924.1,920.6,924.1c920.8,924.1,921.2,924.2,921.3,924.4c921.4,924.6,921.8,924.8,922.1,924.9c922.4,925.0,937.7,925.0,956.0,925.0c985.5,924.9,989.5,924.9,990.2,924.4|m76.7,862.7c78.6,862.5,78.7,862.4,79.6,861.1c80.1,860.4,80.5,859.6,80.5,859.3c80.5,859.1,80.6,858.4,80.8,857.9c81.3,856.5,81.3,841.9,80.8,840.5c80.4,839.3,80.4,837.8,80.8,837.2c81.2,836.6,81.2,809.6,80.8,808.9c80.6,808.7,80.5,808.3,80.5,807.9c80.5,807.6,80.0,806.7,79.4,806.0l78.4,804.6l64.6,804.4c45.5,804.0,11.9,804.4,10.7,805.0c9.7,805.5,7.0,809.2,7.0,810.0c7.0,810.3,6.9,810.8,6.7,811.0c6.5,811.3,6.4,816.2,6.4,832.1c6.3,843.5,6.3,854.2,6.4,856.0l6.6,859.2l7.8,860.9c8.9,862.4,9.1,862.6,10.3,862.7c12.7,862.9,74.7,862.9,76.7,862.7|m151.9,862.7c153.4,862.5,153.8,862.3,154.5,861.4c155.0,860.8,155.6,859.6,155.8,858.6c156.2,857.0,156.3,855.7,156.3,833.5c156.3,810.9,156.2,810.1,155.8,808.6c155.5,807.7,154.9,806.5,154.4,805.8l153.5,804.6l143.1,804.4c129.8,804.1,109.2,804.1,95.9,804.4l85.5,804.6l84.3,806.5l83.0,808.3l83.0,833.7l83.0,859.0l84.3,860.8c85.4,862.4,85.6,862.6,86.8,862.7c89.1,862.9,150.1,862.9,151.9,862.7|m232.2,861.7c232.7,861.1,233.1,860.4,233.2,860.2c234.2,857.6,234.2,858.3,234.2,835.1c234.2,816.3,234.1,812.7,233.8,811.9c233.6,811.3,233.2,810.2,233.0,809.3c232.5,807.6,230.8,805.2,230.1,805.2c230.0,805.2,229.7,805.0,229.5,804.8c229.3,804.5,222.2,804.4,195.8,804.4c161.3,804.4,161.2,804.4,160.1,805.7c159.7,806.1,158.8,808.7,158.8,809.6c158.8,810.0,158.7,810.7,158.5,811.3c158.2,812.1,158.1,815.5,158.1,834.6c158.1,853.7,158.2,857.1,158.5,857.9c158.7,858.4,158.8,859.2,158.8,859.5c158.8,860.3,160.0,861.9,160.6,861.9c160.9,861.9,161.2,862.0,161.3,862.2c161.4,862.4,162.0,862.6,162.7,862.7c163.3,862.8,179.0,862.8,197.6,862.8l231.3,862.8l232.2,861.7|m332.6,862.0c333.0,861.5,333.6,860.6,334.0,859.9l334.6,858.7l334.6,832.9l334.6,807.2l333.6,805.9l332.6,804.6l318.9,804.4c302.1,804.0,265.7,804.4,265.4,804.9c265.3,805.1,265.0,805.2,264.7,805.2c264.4,805.2,263.6,806.2,262.8,807.4c261.6,809.1,261.3,809.7,261.3,810.6c261.3,811.1,261.2,811.8,261.0,812.0c260.8,812.4,260.7,817.5,260.7,835.1c260.7,852.8,260.8,857.8,261.0,858.2c261.2,858.4,261.3,858.9,261.3,859.2c261.3,859.5,261.7,860.4,262.2,861.2c263.0,862.4,263.3,862.6,264.5,862.7c265.2,862.8,280.7,862.8,298.8,862.8l331.8,862.8l332.6,862.0|m407.3,862.3c407.4,862.1,407.8,861.9,408.1,861.9c408.7,861.9,409.1,861.3,409.1,860.3c409.1,859.9,409.3,859.4,409.5,859.2c409.8,858.8,409.8,855.5,409.8,833.7l409.8,808.6l408.4,806.5l407.0,804.4l373.3,804.4l339.5,804.4l338.7,805.3c338.2,805.8,337.6,807.0,337.2,808.0l336.6,809.9l336.6,834.0c336.6,854.9,336.7,858.1,337.0,858.5c337.2,858.7,337.3,859.2,337.3,859.5c337.3,859.8,337.7,860.6,338.2,861.3c338.9,862.4,339.2,862.6,340.4,862.7c341.1,862.8,356.3,862.8,374.3,862.8c400.1,862.8,407.1,862.7,407.3,862.3|m486.1,861.3c487.9,858.8,487.8,859.4,487.8,834.9c487.8,819.6,487.8,813.0,487.6,812.4c487.4,811.9,487.0,810.7,486.7,809.7c486.1,807.6,484.5,805.2,483.8,805.2c483.6,805.2,483.3,805.1,483.1,804.9c482.8,804.4,446.2,804.0,429.1,804.4l415.1,804.6l413.8,806.4l412.5,808.3l412.5,834.0l412.5,859.7l413.1,860.8c413.4,861.5,413.8,861.9,414.1,861.9c414.4,861.9,414.7,862.0,414.9,862.2c415.0,862.4,415.6,862.6,416.3,862.7c416.9,862.8,432.7,862.8,451.3,862.8l485.1,862.8l486.1,861.3|m583.7,862.3c583.8,862.1,584.2,861.9,584.5,861.9c584.8,861.9,585.2,861.5,585.5,860.8l586.1,859.7l586.2,836.8c586.3,819.1,586.4,813.7,586.6,813.4c587.0,812.8,587.0,810.2,586.5,809.7c586.4,809.5,586.2,808.8,586.2,808.3c586.2,807.6,585.9,807.0,585.2,806.0l584.2,804.6l570.2,804.4c554.2,804.1,516.5,804.4,516.2,804.8c516.0,805.0,515.6,805.2,515.3,805.3c514.5,805.6,512.0,809.4,512.0,810.3c512.0,810.7,511.9,811.1,511.8,811.2c511.7,811.4,511.6,819.7,511.6,835.1c511.6,850.5,511.7,858.8,511.8,859.0c511.9,859.1,512.0,859.5,512.0,859.9c512.0,860.8,512.7,861.9,513.2,861.9c513.4,861.9,513.7,862.0,513.8,862.2c513.9,862.4,514.6,862.6,515.3,862.7c516.0,862.8,531.6,862.8,550.0,862.8c576.4,862.8,583.4,862.7,583.7,862.3|m659.7,861.3l660.7,859.8l660.7,833.8l660.7,807.8l660.2,806.7c659.9,806.1,659.4,805.4,659.0,805.0c658.4,804.4,657.3,804.4,625.1,804.4c598.8,804.4,591.8,804.5,591.5,804.8c591.4,805.0,591.0,805.2,590.7,805.2c590.4,805.2,589.9,805.7,589.5,806.4l588.8,807.7l588.8,833.6l588.8,859.5l589.4,860.7c589.8,861.4,590.2,861.9,590.5,861.9c590.8,861.9,591.1,862.0,591.2,862.2c591.4,862.4,592.0,862.6,592.6,862.7c593.3,862.8,608.4,862.8,626.3,862.8l658.7,862.8l659.7,861.3|m736.9,861.4c737.5,860.7,738.1,859.7,738.3,859.2c738.7,858.0,738.8,811.7,738.3,811.0c738.1,810.8,738.0,810.3,738.0,810.1c738.0,809.3,735.2,805.2,734.6,805.2c734.3,805.2,734.0,805.1,733.9,804.9c733.6,804.4,697.0,804.0,679.9,804.4l665.9,804.6l664.6,806.4l663.3,808.2l663.3,833.5l663.3,858.8l664.5,860.7c665.7,862.4,665.9,862.6,667.1,862.7c667.8,862.8,683.6,862.8,702.1,862.8l735.8,862.8l736.9,861.4|m836.1,862.7c837.7,862.5,838.0,862.3,838.7,861.4c840.4,859.3,840.3,860.3,840.4,833.9c840.5,810.8,840.5,810.1,840.0,808.6c839.7,807.7,839.1,806.5,838.6,805.8l837.7,804.6l823.9,804.4c807.1,804.0,770.1,804.4,769.7,804.9c769.6,805.1,769.3,805.2,769.1,805.2c768.9,805.2,768.1,806.1,767.3,807.1c765.0,810.1,765.1,808.6,765.1,835.3c765.1,860.8,765.0,859.1,766.8,861.3c767.6,862.3,768.0,862.6,769.0,862.7c771.2,862.9,834.3,862.9,836.1,862.7|m913.3,862.3c913.4,862.1,913.7,861.9,913.9,861.9c914.1,861.9,914.5,861.5,914.9,861.0l915.6,860.1l915.6,833.7l915.6,807.3l914.6,806.0l913.7,804.6l899.5,804.4c891.7,804.2,876.2,804.2,865.1,804.3l845.0,804.5l843.7,806.4l842.5,808.3l842.4,833.3l842.3,858.2l842.9,859.5c843.8,861.5,844.9,862.5,846.2,862.7c846.8,862.8,862.1,862.8,880.2,862.8c906.1,862.8,913.0,862.7,913.3,862.3|m990.8,862.0c991.2,861.5,991.9,860.6,992.2,859.9l992.9,858.7l992.9,835.6c992.9,817.6,992.8,812.4,992.6,812.0c992.4,811.8,992.3,811.4,992.3,811.0c992.3,810.7,992.1,810.3,991.9,810.0c991.7,809.8,991.6,809.3,991.6,809.0c991.6,808.2,989.6,805.5,988.6,805.0c987.4,804.4,953.8,804.0,934.7,804.4l920.9,804.6l919.6,806.4l918.3,808.2l918.2,826.9c918.1,837.2,918.1,848.7,918.2,852.5l918.4,859.3l919.5,860.9c920.6,862.4,920.7,862.6,922.0,862.7c922.8,862.8,938.4,862.8,956.7,862.8l990.1,862.8l990.8,862.0|m57.8,782.9l57.8,769.5l63.5,769.6c67.7,769.6,69.3,769.8,69.5,770.1c69.7,770.3,70.3,770.5,70.9,770.5c71.6,770.5,72.1,770.7,72.3,771.0c72.4,771.3,72.8,771.6,73.0,771.6c73.6,771.6,74.3,772.8,75.2,775.5c76.1,778.1,76.2,779.1,75.6,780.4c75.0,782.0,73.4,784.3,73.0,784.3c72.7,784.3,72.4,784.5,72.3,784.8c72.1,785.1,71.7,785.3,71.4,785.3c71.0,785.3,70.5,785.6,70.3,785.9c70.0,786.5,70.0,786.6,71.0,788.3c71.6,789.3,72.0,790.2,72.0,790.3c72.0,790.5,72.8,791.7,73.7,793.0c75.4,795.5,75.7,796.3,74.8,796.3c74.2,796.3,72.3,793.7,72.3,792.8c72.3,792.5,71.3,790.9,70.2,789.3l68.0,786.3l63.8,786.3c60.8,786.3,59.4,786.4,59.2,786.7c59.0,787.0,58.9,788.6,58.9,791.7l58.9,796.3l58.4,796.3l57.8,796.3l57.8,782.9|m111.1,796.0c111.1,795.8,111.3,795.5,111.5,795.3c111.7,795.0,111.8,794.6,111.8,794.3c111.8,793.9,112.1,793.2,112.5,792.7c112.9,792.1,113.2,791.4,113.2,791.1c113.2,790.8,113.4,790.3,113.6,790.1c113.8,789.9,113.9,789.4,113.9,789.1c113.9,788.8,114.2,788.1,114.6,787.5c115.0,787.0,115.3,786.3,115.3,786.0c115.3,785.6,115.5,785.2,115.7,785.0c115.9,784.7,116.0,784.3,116.0,783.9c116.0,783.6,116.3,782.9,116.7,782.4c117.1,781.8,117.4,781.1,117.4,780.8c117.4,780.5,117.6,780.0,117.8,779.8c118.0,779.6,118.1,779.2,118.1,779.0c118.1,778.9,118.4,778.2,118.7,777.6c119.0,777.0,119.3,776.3,119.3,776.1c119.3,776.0,119.6,775.4,120.0,774.8c120.4,774.3,120.7,773.6,120.7,773.3c120.7,772.9,120.9,772.5,121.1,772.2c121.2,772.0,121.4,771.5,121.4,771.2c121.4,770.4,122.1,769.5,122.7,769.5c123.3,769.5,124.0,770.5,124.0,771.3c124.0,771.6,124.1,772.0,124.3,772.2c124.5,772.5,124.7,772.9,124.7,773.3c124.7,773.6,124.8,774.1,125.0,774.3c125.2,774.5,125.4,774.9,125.4,775.1c125.4,775.4,125.6,775.9,126.0,776.4c126.3,776.8,126.5,777.4,126.5,777.7c126.5,778.0,126.9,778.7,127.3,779.3c127.6,779.8,128.0,780.5,128.0,780.9c128.0,781.2,128.1,781.6,128.3,781.9c128.5,782.1,128.7,782.6,128.7,782.9c128.7,783.2,128.8,783.7,129.0,783.9c129.2,784.2,129.4,784.6,129.4,784.9c129.4,785.3,129.7,786.0,130.1,786.5c130.4,787.0,130.8,787.7,130.8,788.0c130.8,788.4,131.1,789.0,131.5,789.6c131.8,790.1,132.2,790.8,132.2,791.2c132.2,791.5,132.3,791.9,132.5,792.2c132.7,792.4,132.9,792.9,132.9,793.2c132.9,793.5,133.2,794.2,133.6,794.7c134.4,796.0,134.4,796.3,133.6,796.3c132.9,796.3,132.4,795.7,132.4,794.9c132.4,794.6,132.2,794.1,132.0,793.9c131.9,793.7,131.7,793.2,131.7,792.9c131.7,792.6,131.4,791.9,131.0,791.3c130.6,790.8,130.3,790.1,130.3,789.8c130.3,788.5,129.9,788.4,122.9,788.4l116.0,788.4l115.2,789.3c114.7,789.8,114.4,790.5,114.4,790.8c114.4,791.1,114.2,791.6,114.0,791.8c113.8,792.1,113.7,792.5,113.7,792.8c113.7,793.2,113.4,793.9,113.0,794.4c112.6,794.9,112.3,795.6,112.3,795.8c112.3,796.1,112.0,796.3,111.7,796.3c111.4,796.3,111.1,796.2,111.1,796.0|m177.5,782.9c177.5,775.4,177.6,769.5,177.7,769.5c177.9,769.5,178.1,769.8,178.3,770.1c178.7,770.9,178.7,787.1,178.3,787.8c178.1,788.0,178.0,789.5,178.0,792.2c178.0,794.7,177.9,796.3,177.8,796.3c177.6,796.3,177.5,791.6,177.5,782.9|m310.2,782.9l310.2,769.5l315.8,769.6c319.9,769.6,321.5,769.8,321.7,770.1c321.8,770.3,322.5,770.5,323.1,770.5c323.7,770.5,324.3,770.7,324.4,771.0c324.6,771.3,324.9,771.6,325.1,771.6c325.6,771.6,327.7,774.6,327.7,775.3c327.7,775.6,327.9,776.2,328.1,776.5c328.3,776.9,328.4,777.7,328.4,778.4c328.4,779.8,327.5,782.5,327.0,782.9c326.7,783.1,326.4,783.4,326.1,783.6c325.9,783.8,325.5,784.1,325.2,784.2c325.0,784.4,324.7,784.7,324.6,784.9c324.5,785.1,324.2,785.3,324.0,785.3c323.5,785.3,322.8,786.3,322.8,787.1c322.8,787.3,323.3,788.2,323.9,789.1c324.4,789.9,324.9,790.8,324.9,791.1c324.9,791.4,325.6,792.7,326.5,794.0c327.7,795.7,327.9,796.3,327.6,796.3c327.0,796.3,321.9,788.8,321.9,787.9c321.9,786.4,321.5,786.3,316.5,786.3c313.1,786.3,311.6,786.4,311.4,786.7c311.2,787.0,311.1,788.6,311.1,791.7c311.1,796.1,311.1,796.3,310.6,796.3c310.2,796.3,310.2,796.1,310.2,782.9|m364.2,795.5c364.4,795.1,364.7,794.5,364.7,794.2c364.7,793.9,364.8,793.4,365.0,793.2c365.2,793.0,365.4,792.5,365.4,792.2c365.4,791.9,365.7,791.2,366.1,790.6c366.5,790.1,366.8,789.4,366.8,789.1c366.8,788.7,366.9,788.3,367.1,788.0c367.3,787.8,367.5,787.4,367.5,787.0c367.5,786.7,367.8,786.0,368.2,785.5c368.6,784.9,368.9,784.2,368.9,783.9c368.9,783.6,369.0,783.1,369.2,782.9c369.4,782.7,369.6,782.3,369.6,782.1c369.6,781.8,369.9,781.2,370.3,780.7c370.7,780.1,371.0,779.4,371.0,779.1c371.0,778.8,371.3,778.2,371.6,777.7c371.9,777.3,372.2,776.7,372.2,776.3c372.2,776.0,372.3,775.6,372.5,775.3c372.7,775.1,372.9,774.6,372.9,774.3c372.9,774.0,373.2,773.3,373.6,772.8c374.0,772.2,374.3,771.5,374.3,771.2c374.3,770.4,375.0,769.5,375.6,769.5c376.0,769.5,376.1,769.7,376.1,770.1c376.1,770.5,376.3,771.0,376.5,771.2c376.7,771.4,376.8,771.9,376.8,772.2c376.8,772.5,377.2,773.2,377.5,773.8c377.9,774.3,378.2,775.0,378.2,775.2c378.2,775.4,378.4,775.8,378.6,776.0c378.8,776.3,378.9,776.7,378.9,777.0c378.9,777.4,379.2,778.0,379.5,778.4c379.9,778.9,380.1,779.4,380.1,779.7c380.1,779.9,380.4,780.6,380.8,781.2c381.1,781.9,381.7,783.2,382.0,784.3c382.4,785.3,382.9,786.5,383.1,786.8c383.4,787.2,383.6,787.7,383.6,788.1c383.6,788.4,383.8,788.8,384.0,789.1c384.2,789.3,384.3,789.8,384.3,790.1c384.3,790.4,384.6,791.1,385.0,791.7c385.4,792.2,385.7,792.9,385.7,793.2c385.7,793.5,385.9,794.0,386.1,794.2c386.6,794.8,386.7,796.3,386.2,796.3c385.7,796.3,385.3,795.6,385.3,795.0c385.3,794.7,385.0,794.1,384.7,793.6c384.5,793.2,383.9,791.9,383.5,790.7l382.8,788.6l375.8,788.5l368.9,788.4l368.1,789.3c367.6,789.8,367.3,790.4,367.3,790.7c367.3,791.0,366.9,791.8,366.5,792.5c366.2,793.2,365.8,793.9,365.8,794.1c365.8,794.7,364.6,796.3,364.1,796.3c363.7,796.3,363.7,796.3,364.2,795.5|m430.4,782.9c430.4,774.2,430.5,769.5,430.6,769.5c430.8,769.5,430.9,774.2,430.9,782.9c430.9,791.6,430.8,796.3,430.6,796.3c430.5,796.3,430.4,791.6,430.4,782.9|m559.5,782.9l559.5,769.4l565.3,769.6c569.4,769.6,571.1,769.8,571.3,770.1c571.4,770.3,572.0,770.5,572.6,770.5c573.3,770.5,573.9,770.7,574.0,771.0c574.2,771.3,574.5,771.6,574.7,771.6c575.2,771.6,577.1,774.3,577.1,775.0c577.1,775.3,577.2,775.8,577.4,776.0c577.6,776.3,577.8,777.0,577.8,777.9c577.8,778.8,577.6,779.5,577.4,779.8c577.2,780.0,577.1,780.5,577.1,780.8c577.1,781.5,575.2,784.3,574.7,784.3c574.5,784.3,574.2,784.5,574.0,784.8c573.9,785.1,573.4,785.3,573.0,785.3c572.6,785.3,572.1,785.5,571.9,785.8c571.7,786.2,571.8,786.6,572.4,787.7c572.8,788.4,573.1,789.2,573.1,789.4c573.1,789.6,574.0,791.1,575.1,792.8c576.2,794.5,577.1,796.0,577.1,796.1c577.1,796.2,576.8,796.3,576.6,796.3c576.0,796.3,574.0,793.7,574.0,793.0c574.0,792.8,573.1,791.2,571.9,789.5l569.7,786.3l565.5,786.3c562.5,786.3,561.2,786.4,561.0,786.7c560.8,787.0,560.7,788.6,560.7,791.7l560.7,796.3l560.1,796.3l559.5,796.3l559.5,782.9|m614.5,795.5c614.7,795.1,615.0,794.5,615.0,794.2c615.0,793.9,615.1,793.4,615.3,793.2c615.5,793.0,615.7,792.5,615.7,792.2c615.7,791.8,615.8,791.4,616.0,791.1c616.2,790.9,616.4,790.4,616.4,790.1c616.4,789.8,616.6,789.2,617.0,788.7c617.3,788.3,617.5,787.7,617.5,787.5c617.5,787.2,617.8,786.5,618.2,785.9c618.6,785.3,619.1,783.9,619.5,782.9c619.8,781.8,620.3,780.7,620.6,780.3c620.8,780.0,621.1,779.4,621.1,779.1c621.1,778.8,621.2,778.3,621.4,778.1c621.6,777.8,621.8,777.4,621.8,777.1c621.8,776.8,622.1,776.0,622.5,775.5c622.8,775.0,623.2,774.3,623.2,773.9c623.2,773.6,623.3,773.2,623.5,772.9c623.7,772.7,623.9,772.4,623.9,772.2c623.9,771.6,625.1,769.5,625.4,769.5c625.8,769.5,627.1,771.7,627.1,772.3c627.1,772.6,627.4,773.2,627.7,773.6c628.0,774.1,628.3,774.7,628.3,775.0c628.3,775.3,628.5,775.8,628.7,776.0c628.8,776.3,629.0,776.7,629.0,777.0c629.0,777.3,629.3,778.1,629.7,778.6c630.1,779.1,630.4,779.8,630.4,780.2c630.4,780.5,630.6,780.9,630.8,781.2c631.0,781.4,631.1,781.9,631.1,782.2c631.1,782.5,631.4,783.2,631.8,783.8c632.2,784.3,632.5,784.9,632.5,785.1c632.5,785.4,632.7,785.7,632.9,786.0c633.1,786.2,633.2,786.8,633.2,787.2c633.2,787.6,633.5,788.4,633.9,788.9c634.3,789.4,634.6,790.1,634.6,790.3c634.6,790.5,634.8,790.9,635.0,791.1c635.2,791.4,635.3,791.8,635.3,792.1c635.3,792.5,635.6,793.1,635.9,793.5c636.2,794.0,636.5,794.6,636.5,794.9c636.5,795.2,636.6,795.7,636.8,795.9c637.0,796.3,637.0,796.3,636.5,796.2c636.1,796.2,635.8,795.7,635.5,794.9c635.3,794.3,634.9,793.4,634.6,793.1c634.4,792.7,634.2,792.2,634.2,792.0c634.2,791.8,634.0,791.4,633.8,791.1c633.6,790.9,633.5,790.4,633.5,790.0c633.5,788.4,633.3,788.4,625.9,788.4l618.9,788.4l618.0,789.6c617.5,790.3,616.8,791.7,616.5,792.8c615.7,795.1,615.1,796.3,614.4,796.3c614.0,796.3,614.0,796.3,614.5,795.5|m680.5,783.4c680.6,770.6,680.7,769.5,681.4,769.5c681.5,769.5,681.6,775.4,681.6,782.9l681.6,796.3l681.0,796.3l680.4,796.3l680.5,783.4|m813.8,782.9l813.8,769.5l819.5,769.6c823.7,769.6,825.3,769.8,825.5,770.1c825.7,770.3,826.3,770.5,826.9,770.5c827.6,770.5,828.1,770.7,828.3,771.0c828.5,771.3,828.8,771.6,829.0,771.6c829.5,771.6,830.6,773.3,830.6,774.0c830.6,774.3,830.8,774.8,831.0,775.0c831.3,775.3,831.3,776.2,831.3,778.4l831.3,781.4l830.3,782.8c829.8,783.6,829.2,784.3,829.0,784.3c828.8,784.3,828.5,784.5,828.3,784.8c828.1,785.1,827.7,785.3,827.3,785.3c826.4,785.3,826.0,785.8,826.0,787.1c826.0,787.8,826.4,788.6,828.0,790.7c829.0,792.2,829.9,793.6,829.9,793.9c829.9,794.1,830.2,794.8,830.6,795.3c831.1,796.2,831.2,796.3,830.7,796.3c830.2,796.3,827.6,792.7,827.6,792.0c827.6,791.7,826.8,790.3,825.8,788.9l824.1,786.3l819.5,786.3c816.2,786.3,814.7,786.4,814.5,786.7c814.4,787.0,814.3,788.6,814.3,791.7c814.3,794.5,814.2,796.3,814.0,796.3c813.9,796.3,813.8,791.6,813.8,782.9|m868.5,795.4c868.5,795.0,868.7,794.4,868.9,794.2c869.1,794.0,869.2,793.6,869.2,793.3c869.2,793.0,869.6,792.2,869.9,791.6c870.3,791.0,870.6,790.2,870.6,790.0c870.6,789.7,870.9,789.2,871.1,788.9c871.4,788.5,871.9,787.3,872.3,786.1c872.7,785.0,873.2,783.8,873.4,783.4c873.7,783.1,873.9,782.5,873.9,782.2c873.9,781.9,874.1,781.4,874.3,781.2c874.5,780.9,874.6,780.5,874.6,780.2c874.6,779.8,874.9,779.1,875.3,778.6c875.7,778.1,876.0,777.4,876.0,777.1c876.0,776.7,876.3,776.0,876.7,775.5c877.1,775.0,877.4,774.3,877.4,773.9c877.4,773.6,877.6,773.2,877.8,772.9c878.0,772.7,878.1,772.3,878.1,772.1c878.1,771.9,878.5,771.2,878.9,770.5l879.8,769.4l880.5,770.4c880.9,770.9,881.2,771.6,881.2,771.9c881.2,772.2,881.5,772.9,881.9,773.4c882.3,774.0,882.6,774.7,882.6,775.0c882.6,775.3,882.9,776.0,883.3,776.5c883.7,777.1,884.0,777.8,884.0,778.1c884.0,778.4,884.1,778.9,884.3,779.1c884.5,779.3,884.7,779.7,884.7,779.9c884.7,780.1,885.0,780.8,885.4,781.5c885.8,782.2,886.1,783.0,886.1,783.3c886.1,783.6,886.2,784.0,886.4,784.3c886.6,784.5,886.8,784.9,886.8,785.1c886.8,785.3,887.1,786.0,887.5,786.5c887.9,787.0,888.2,787.8,888.2,788.2c888.2,788.7,888.3,789.2,888.5,789.4c888.7,789.7,888.9,790.0,888.9,790.3c888.9,790.5,889.2,791.0,889.5,791.5c889.8,791.9,890.1,792.5,890.1,792.9c890.1,793.2,890.4,793.9,890.8,794.4c891.6,795.6,891.7,796.3,890.9,796.3c890.3,796.3,889.8,795.7,889.8,794.9c889.8,794.6,889.5,793.9,889.1,793.4c888.7,792.8,888.4,792.2,888.4,792.0c888.4,791.7,888.3,791.4,888.1,791.1c887.9,790.9,887.7,790.4,887.7,790.0c887.7,788.4,887.6,788.4,879.8,788.4c872.1,788.4,871.8,788.4,871.8,789.8c871.8,790.1,871.7,790.6,871.5,790.8c871.3,791.0,871.1,791.5,871.1,791.8c871.1,792.2,871.0,792.6,870.8,792.9c870.6,793.1,870.4,793.5,870.4,793.8c870.4,794.6,869.2,796.3,868.8,796.3c868.5,796.3,868.4,796.1,868.5,795.4|m935.8,782.9c935.8,775.4,935.8,772.4,935.8,776.1c935.9,779.8,935.9,785.9,935.8,789.7c935.8,793.4,935.8,790.4,935.8,782.9|m128.6,786.9c128.9,786.4,129.0,786.3,128.6,785.7c128.4,785.4,128.2,784.8,128.2,784.5c128.2,784.2,128.0,783.8,127.8,783.6c127.6,783.3,127.5,782.9,127.5,782.6c127.5,782.2,127.2,781.6,126.9,781.2c126.6,780.7,126.3,780.2,126.3,780.0c126.3,779.7,126.2,779.3,126.0,779.1c125.8,778.9,125.6,778.5,125.6,778.2c125.6,777.9,125.3,777.1,124.9,776.4c124.5,775.6,124.2,774.9,124.2,774.8c124.2,774.6,123.9,774.0,123.5,773.4l122.7,772.2l121.9,773.3c121.5,773.9,121.2,774.6,121.2,774.8c121.2,774.9,120.9,775.6,120.5,776.4c120.1,777.1,119.8,777.8,119.8,777.9c119.8,778.0,119.5,778.7,119.1,779.5c118.7,780.2,118.4,780.9,118.4,781.1c118.4,781.7,117.7,783.5,117.1,784.3c116.4,785.1,116.3,786.6,116.8,787.3c117.0,787.6,118.4,787.7,122.6,787.6c127.5,787.5,128.2,787.5,128.6,786.9|m381.4,786.9c381.8,786.4,381.8,786.3,381.4,785.7c381.2,785.4,381.1,784.8,381.1,784.6c381.1,784.3,380.8,783.7,380.5,783.2c380.1,782.8,379.9,782.2,379.9,781.8c379.9,781.5,379.7,781.1,379.5,780.8c379.3,780.6,379.2,780.1,379.2,779.8c379.2,779.5,378.9,778.8,378.5,778.3c378.1,777.7,377.8,777.0,377.8,776.7c377.8,776.4,377.6,775.9,377.4,775.7c377.2,775.4,377.1,775.1,377.1,774.9c377.1,774.3,375.6,772.2,375.2,772.2c374.8,772.2,374.0,773.3,374.0,773.9c374.0,774.3,373.7,775.0,373.3,775.5c372.9,776.0,372.6,776.8,372.6,777.1c372.6,777.4,372.5,777.8,372.3,778.1c372.1,778.3,371.9,778.7,371.9,778.9c371.9,779.5,371.0,782.1,370.5,782.7c370.3,783.1,370.1,783.5,370.1,783.8c370.1,784.0,369.9,784.4,369.7,784.6c369.3,785.1,369.2,786.7,369.6,787.3c369.9,787.6,371.3,787.7,375.5,787.6c380.4,787.5,381.1,787.5,381.4,786.9|m631.7,786.9c632.1,786.4,632.1,786.3,631.7,785.7c631.5,785.4,631.3,784.8,631.3,784.6c631.3,784.3,631.0,783.6,630.6,783.1c630.3,782.5,629.9,781.9,629.9,781.7c629.9,781.4,629.8,781.1,629.6,780.8c629.4,780.6,629.2,780.1,629.2,779.8c629.2,779.5,629.0,778.9,628.7,778.4c628.3,778.0,628.1,777.4,628.1,777.2c628.1,777.0,627.8,776.3,627.4,775.7c627.1,775.1,626.7,774.1,626.4,773.5c625.9,771.8,624.3,771.9,624.3,773.6c624.3,773.9,624.0,774.6,623.6,775.2c623.2,775.7,622.9,776.4,622.9,776.7c622.9,777.1,622.8,777.5,622.6,777.7c622.4,778.0,622.2,778.4,622.2,778.7c622.2,779.1,621.9,779.8,621.5,780.3c621.1,780.9,620.8,781.6,620.8,781.9c620.8,782.2,620.7,782.7,620.5,782.9c620.3,783.1,620.1,783.5,620.1,783.8c620.1,784.0,619.9,784.7,619.7,785.2c619.3,786.2,619.3,786.3,619.8,787.0c620.2,787.7,620.4,787.7,625.8,787.6c630.7,787.5,631.4,787.5,631.7,786.9|m886.0,786.9c886.4,786.4,886.4,786.3,886.0,785.7c885.8,785.4,885.6,784.9,885.6,784.7c885.6,784.5,885.3,784.0,884.9,783.4c884.5,782.9,884.2,782.2,884.2,781.8c884.2,781.5,884.1,781.1,883.9,780.8c883.7,780.6,883.5,780.1,883.5,779.8c883.5,779.5,883.2,778.8,882.8,778.3c882.4,777.7,882.1,777.0,882.1,776.7c882.1,776.4,881.8,775.8,881.5,775.3c881.2,774.9,880.9,774.3,880.9,774.0c880.9,773.2,880.2,772.2,879.7,772.2c879.1,772.2,878.6,772.9,878.6,773.6c878.6,773.9,878.3,774.6,877.9,775.2c877.5,775.7,877.2,776.4,877.2,776.7c877.2,777.1,877.0,777.5,876.8,777.7c876.6,778.0,876.5,778.4,876.5,778.7c876.5,779.1,876.2,779.8,875.8,780.3c875.4,780.9,875.1,781.6,875.1,781.9c875.1,782.2,874.9,782.7,874.7,782.9c874.5,783.1,874.4,783.6,874.4,783.9c874.4,784.2,874.1,784.9,873.7,785.5c872.9,786.5,873.0,787.2,874.0,787.5c874.3,787.6,877.0,787.6,880.1,787.6c885.0,787.5,885.6,787.5,886.0,786.9|m68.3,785.1c68.5,784.8,69.0,784.6,70.1,784.6c71.0,784.6,71.6,784.4,71.8,784.1c72.0,783.8,72.3,783.6,72.6,783.5c72.9,783.4,73.3,782.7,74.0,780.8c74.5,779.4,74.9,778.1,74.9,777.9c74.9,776.6,72.6,772.2,71.9,772.2c71.8,772.2,71.3,772.0,71.0,771.7c70.1,771.1,59.7,771.0,59.2,771.6c58.8,772.2,58.8,784.6,59.2,785.2c59.4,785.5,60.8,785.6,63.8,785.6c67.3,785.6,68.1,785.5,68.3,785.1|m321.3,785.1c321.6,784.9,322.2,784.6,322.7,784.6c323.3,784.6,323.8,784.4,324.0,784.1c324.1,783.8,324.5,783.6,324.8,783.6c325.3,783.6,326.5,781.7,326.6,780.8c326.6,780.5,326.7,780.0,326.9,779.6c327.1,779.3,327.3,778.5,327.3,777.9c327.3,777.3,327.1,776.5,326.9,776.2c326.7,775.8,326.6,775.3,326.6,775.0c326.5,774.4,325.2,772.2,324.8,772.2c324.6,772.2,324.2,772.0,323.8,771.7c323.3,771.3,322.1,771.2,317.6,771.2c312.7,771.2,311.9,771.3,311.5,771.8c311.2,772.3,311.1,773.0,311.1,778.4c311.1,783.5,311.2,784.5,311.5,785.0c311.8,785.6,312.3,785.6,316.4,785.6c319.9,785.6,320.9,785.5,321.3,785.1|m570.1,785.1c570.3,784.8,570.8,784.6,571.8,784.6c572.8,784.6,573.4,784.5,573.6,784.1c573.7,783.8,574.0,783.6,574.3,783.6c574.7,783.6,575.9,781.8,575.9,781.1c575.9,780.8,576.1,780.4,576.3,780.1c576.5,779.9,576.6,779.1,576.6,778.0c576.6,776.3,576.5,776.1,575.3,774.2c574.5,773.1,573.8,772.2,573.7,772.2c573.5,772.2,573.1,772.0,572.7,771.7c572.2,771.3,571.1,771.2,567.5,771.2c563.7,771.2,562.8,771.1,562.6,770.7c562.2,770.1,561.4,770.0,561.0,770.6c560.8,770.9,560.7,772.8,560.7,777.2l560.7,783.4l561.4,784.5l562.2,785.6l566.0,785.6c569.1,785.6,569.8,785.5,570.1,785.1|m824.3,785.1c824.5,784.8,825.0,784.6,825.7,784.6c826.4,784.6,827.0,784.4,827.1,784.1c827.3,783.8,827.6,783.6,827.8,783.6c828.0,783.6,828.6,782.9,829.2,782.1l830.2,780.6l830.2,777.9l830.2,775.2l829.2,773.7c828.6,772.9,828.0,772.2,827.8,772.2c827.6,772.2,827.3,772.0,827.2,771.8c826.8,771.2,815.1,771.0,814.6,771.6c814.3,771.9,814.3,773.2,814.3,777.6l814.3,783.2l815.0,784.4l815.7,785.6l819.9,785.6c823.3,785.6,824.1,785.5,824.3,785.1|m17.0,748.0c16.7,747.9,16.4,747.6,16.3,747.5c16.1,747.3,15.1,747.2,14.0,747.2c12.5,747.2,11.9,747.0,11.7,746.7c11.5,746.4,11.2,746.1,11.0,746.1c10.8,746.1,10.5,745.9,10.3,745.6c10.1,745.3,9.8,745.1,9.6,745.1c9.4,745.1,9.0,744.9,8.9,744.6c8.7,744.3,8.4,744.1,8.2,744.1c8.0,744.1,7.5,743.6,7.1,743.0c6.8,742.5,6.3,742.0,6.1,742.0c5.6,742.0,4.4,740.2,4.4,739.5c4.4,739.2,4.0,738.5,3.5,737.7c3.0,737.0,2.6,736.1,2.6,735.8c2.6,735.5,2.4,735.0,2.2,734.8c2.0,734.6,1.9,733.9,1.9,733.3c1.9,732.6,1.7,731.9,1.5,731.7c1.3,731.5,1.2,730.8,1.2,730.2c1.2,729.6,1.0,728.9,0.9,728.7c0.4,728.0,0.4,526.5,0.9,525.9c1.0,525.6,1.2,525.0,1.2,524.5c1.2,524.0,1.3,523.4,1.5,523.2c1.7,523.0,1.9,522.5,1.9,522.2c1.9,521.8,2.0,521.4,2.2,521.1c2.4,520.9,2.6,520.5,2.6,520.3c2.6,519.2,3.5,517.3,5.3,514.5c6.5,512.9,7.5,511.5,7.7,511.5c8.0,511.5,8.3,511.3,8.4,511.0c8.6,510.7,8.9,510.5,9.1,510.5c9.4,510.5,9.6,510.3,9.7,510.2c10.0,509.5,11.4,508.7,13.1,508.2c14.5,507.8,29.8,507.7,120.0,507.7c228.8,507.8,227.9,507.8,228.8,509.1c229.0,509.3,229.3,509.4,229.5,509.4c229.7,509.4,230.0,509.7,230.2,510.0c230.3,510.2,230.7,510.5,230.9,510.5c231.1,510.5,231.4,510.7,231.6,511.0c231.7,511.3,232.0,511.5,232.3,511.5c232.5,511.5,233.0,512.0,233.3,512.5c233.7,513.1,234.1,513.6,234.2,513.6c234.6,513.6,236.0,515.4,236.0,516.0c236.0,516.3,236.3,517.0,236.7,517.5c237.1,518.1,237.4,518.8,237.4,519.1c237.4,519.4,237.6,519.9,237.8,520.1c238.0,520.3,238.1,520.8,238.1,521.1c238.1,521.5,238.3,521.9,238.5,522.2c238.7,522.4,238.8,522.8,238.8,523.0c238.8,523.3,239.0,523.9,239.2,524.4c239.4,525.0,239.5,526.0,239.5,526.6c239.5,527.3,239.7,528.1,239.8,528.3c240.1,528.6,240.1,549.1,240.1,628.5c240.1,707.8,240.1,728.3,239.8,728.7c239.7,728.9,239.5,729.6,239.5,730.1c239.5,730.7,239.4,731.6,239.2,732.2c239.0,732.7,238.8,733.4,238.8,733.6c238.8,733.8,238.7,734.2,238.5,734.5c238.3,734.7,238.1,735.1,238.1,735.5c238.1,735.8,237.8,736.5,237.4,737.0c237.0,737.6,236.7,738.3,236.7,738.5c236.7,739.1,234.9,742.0,234.5,742.0c234.4,742.0,233.7,742.7,233.1,743.6c232.4,744.4,231.8,745.1,231.6,745.1c231.5,745.1,231.3,745.3,231.1,745.6c231.0,745.9,230.5,746.1,230.1,746.1c229.6,746.1,229.2,746.4,229.0,746.7c228.8,747.0,228.2,747.2,226.9,747.2c225.6,747.2,225.0,747.3,224.8,747.7c224.4,748.4,222.9,748.3,222.0,747.7c221.4,747.2,220.2,747.2,213.6,747.3c209.4,747.4,205.1,747.6,204.0,747.8c201.3,748.3,161.8,748.3,158.9,747.8c157.8,747.6,154.9,747.4,152.5,747.3c148.9,747.2,148.2,747.2,147.7,747.7c147.0,748.3,145.2,748.4,144.8,747.8c144.6,747.4,141.1,747.3,129.5,747.2c116.6,747.2,114.2,747.2,112.9,747.7c110.7,748.4,100.5,748.4,99.3,747.7c98.6,747.3,97.3,747.2,93.0,747.2c88.7,747.2,87.4,747.3,86.7,747.7c85.5,748.4,77.8,748.4,76.5,747.7c75.8,747.2,74.6,747.2,69.8,747.3c66.3,747.3,63.6,747.5,63.0,747.8c61.6,748.4,48.6,748.3,47.4,747.7c46.0,747.0,39.6,747.0,39.0,747.7c38.6,748.0,37.9,748.2,36.6,748.2c35.3,748.2,34.6,748.0,34.3,747.7c33.7,747.0,29.9,747.0,29.5,747.6c29.3,747.9,27.7,748.0,23.3,748.1c20.1,748.1,17.2,748.1,17.0,748.0|m270.6,747.7c270.4,747.3,269.9,747.2,268.7,747.2c267.4,747.2,266.9,747.0,266.7,746.7c266.5,746.4,266.0,746.1,265.6,746.1c265.2,746.1,264.7,745.9,264.6,745.6c264.4,745.3,264.1,745.1,263.9,745.1c263.6,745.1,263.3,744.9,263.2,744.6c263.0,744.3,262.7,744.1,262.5,744.1c262.0,744.1,256.8,736.5,256.8,735.8c256.8,735.5,256.7,735.0,256.5,734.8c256.3,734.6,256.1,734.1,256.1,733.8c256.1,733.4,256.0,733.0,255.8,732.7c255.6,732.5,255.4,731.7,255.4,730.7c255.4,729.8,255.3,728.9,255.1,728.7c254.9,728.3,254.9,707.6,254.9,627.4c254.9,547.3,254.9,526.6,255.1,526.2c255.3,526.0,255.4,525.2,255.4,524.5c255.4,523.8,255.5,523.1,255.7,523.0c255.8,522.9,256.1,522.1,256.4,521.2c256.7,520.3,257.2,519.1,257.6,518.5c258.0,517.8,258.2,517.1,258.2,516.9c258.2,516.3,260.9,512.5,261.3,512.5c261.5,512.5,262.0,512.1,262.3,511.5c262.7,510.9,263.2,510.5,263.4,510.5c263.6,510.5,263.9,510.2,264.1,510.0c264.3,509.7,264.7,509.4,265.0,509.4c265.4,509.4,265.7,509.3,265.9,509.1c266.0,508.9,266.9,508.5,267.9,508.2c269.5,507.8,282.7,507.7,374.2,507.7c483.4,507.7,481.5,507.7,482.4,509.1c482.6,509.3,482.9,509.4,483.3,509.4c483.6,509.4,484.1,509.7,484.3,510.0c484.6,510.2,485.0,510.5,485.2,510.5c485.4,510.5,485.8,510.9,486.2,511.5c486.6,512.1,487.0,512.5,487.1,512.5c487.6,512.5,490.3,516.3,490.3,517.0c490.3,517.3,490.6,518.0,491.0,518.6c491.4,519.1,491.7,519.8,491.7,520.1c491.7,520.4,491.9,520.9,492.0,521.1c492.2,521.4,492.4,522.1,492.4,522.7c492.4,523.3,492.5,524.0,492.7,524.2c493.2,524.8,493.4,526.8,493.6,538.3c493.8,552.5,493.8,703.3,493.6,717.5c493.3,729.5,493.2,731.8,492.7,732.4c492.5,732.6,492.4,733.1,492.4,733.4c492.4,733.8,492.2,734.2,492.0,734.5c491.9,734.7,491.7,735.1,491.7,735.4c491.7,735.7,491.4,736.5,491.0,737.2c490.6,737.9,490.3,738.6,490.3,738.8c490.3,739.2,488.4,742.0,488.1,742.0c488.0,742.0,487.5,742.5,487.0,743.0c486.5,743.6,486.0,744.1,485.8,744.1c485.6,744.1,485.3,744.3,485.1,744.6c485.0,744.9,484.7,745.1,484.6,745.1c484.4,745.1,484.1,745.3,484.0,745.6c483.8,745.9,483.3,746.1,482.9,746.1c482.5,746.1,482.0,746.4,481.9,746.6c481.7,747.0,480.9,747.2,479.5,747.3c478.3,747.4,476.8,747.6,476.1,747.8c474.3,748.4,454.4,748.2,454.0,747.6c453.6,747.0,451.4,747.0,451.0,747.7c450.6,748.4,445.7,748.4,445.0,747.7c444.5,747.2,443.7,747.2,440.1,747.3c437.6,747.3,435.1,747.6,434.4,747.8c432.7,748.4,415.4,748.2,414.9,747.6c414.5,747.0,413.7,747.1,413.3,747.7c413.2,748.0,412.8,748.2,412.5,748.2c412.2,748.2,411.9,748.0,411.7,747.7c411.3,747.0,410.1,747.0,409.2,747.7c408.2,748.4,397.6,748.4,396.6,747.7c396.0,747.2,395.9,747.2,395.6,747.7c395.0,748.4,392.6,748.4,391.6,747.7c391.0,747.2,389.7,747.2,382.7,747.3c377.2,747.3,373.9,747.5,372.8,747.8c370.6,748.4,349.7,748.2,349.2,747.6c348.7,747.0,341.4,747.2,339.3,747.8c337.3,748.4,316.2,748.2,315.8,747.6c315.3,746.9,308.0,747.0,307.6,747.7c307.4,748.0,307.0,748.2,306.5,748.2c306.1,748.2,305.7,748.0,305.5,747.7c305.1,746.9,298.6,746.9,297.9,747.7c297.3,748.4,290.7,748.4,289.8,747.7c289.0,746.9,281.3,746.9,280.9,747.7c280.5,748.4,278.2,748.4,277.5,747.7c276.9,747.0,271.9,747.0,271.3,747.7c271.0,748.2,270.9,748.2,270.6,747.7|m521.5,748.0c521.3,747.9,521.0,747.6,520.8,747.5c520.7,747.3,520.0,747.2,519.2,747.2c518.2,747.2,517.6,747.0,517.4,746.7c517.3,746.4,516.8,746.1,516.4,746.1c516.0,746.1,515.5,745.9,515.3,745.6c515.2,745.3,514.9,745.1,514.7,745.1c514.6,745.1,514.3,744.9,514.2,744.6c514.0,744.3,513.7,744.1,513.5,744.1c513.0,744.1,508.3,737.2,508.3,736.5c508.3,736.2,508.0,735.5,507.6,735.0c507.2,734.4,506.9,733.7,506.9,733.4c506.9,733.1,506.8,732.6,506.6,732.4c506.1,731.8,506.0,729.4,505.7,712.8c505.5,692.9,505.5,561.9,505.7,541.7c505.9,525.9,506.0,523.8,506.6,523.2c506.8,522.9,506.9,522.5,506.9,522.2c506.9,521.8,507.1,521.4,507.3,521.1c507.4,520.9,507.6,520.4,507.6,520.1c507.6,519.8,507.8,519.3,508.0,519.1c508.1,518.8,508.3,518.4,508.3,518.1c508.3,517.4,512.3,511.5,512.8,511.5c513.0,511.5,513.3,511.3,513.5,511.0c513.6,510.7,513.9,510.5,514.2,510.5c514.4,510.5,514.7,510.2,514.9,510.0c515.0,509.7,515.3,509.4,515.5,509.4c515.8,509.4,516.0,509.3,516.2,509.1c517.1,507.7,515.2,507.7,625.1,507.7c717.2,507.7,730.5,507.8,732.1,508.2c733.1,508.5,734.0,508.9,734.1,509.1c734.3,509.3,734.6,509.4,735.0,509.4c735.3,509.4,735.7,509.7,735.9,510.0c736.1,510.2,736.4,510.5,736.6,510.5c736.8,510.5,737.3,510.9,737.7,511.5c738.0,512.1,738.5,512.5,738.7,512.5c739.2,512.5,741.1,515.3,741.1,516.0c741.1,516.3,741.4,517.0,741.8,517.5c742.1,518.1,742.5,518.7,742.5,518.9c742.5,519.2,742.8,519.9,743.2,520.6c743.5,521.2,743.9,522.1,743.9,522.6c743.9,523.1,744.0,523.6,744.2,523.9c744.4,524.1,744.6,524.9,744.6,525.9c744.6,526.8,744.7,527.7,744.9,527.9c745.1,528.3,745.1,548.8,745.1,628.3c745.1,707.8,745.1,728.3,744.9,728.7c744.7,728.9,744.6,729.8,744.6,730.7c744.6,731.7,744.4,732.5,744.2,732.7c744.0,733.0,743.9,733.4,743.9,733.8c743.9,734.1,743.7,734.6,743.5,734.8c743.3,735.0,743.2,735.5,743.2,735.8c743.2,736.1,742.8,736.8,742.5,737.4c742.1,737.9,741.8,738.6,741.8,738.9c741.8,739.6,740.1,742.0,739.6,742.0c739.4,742.0,739.0,742.5,738.6,743.0c738.2,743.6,737.7,744.1,737.5,744.1c737.3,744.1,737.0,744.3,736.8,744.6c736.7,744.9,736.4,745.1,736.1,745.1c735.9,745.1,735.6,745.3,735.4,745.6c735.3,745.9,735.0,746.1,734.8,746.1c734.5,746.1,734.2,746.3,734.1,746.6c733.9,746.9,732.1,747.1,727.6,747.2c724.3,747.3,720.4,747.6,718.9,747.8c715.4,748.3,667.2,748.3,663.7,747.8c660.1,747.3,647.0,747.3,644.2,747.8c641.0,748.4,605.3,748.2,604.9,747.6c604.5,747.0,602.8,747.1,602.0,747.7c601.4,748.1,600.3,748.2,596.4,748.2c592.5,748.2,591.3,748.1,590.8,747.7c589.9,747.0,588.7,747.0,588.3,747.7c587.9,748.4,583.3,748.4,582.5,747.7c581.6,747.0,570.6,747.0,569.2,747.7c567.9,748.4,556.1,748.4,554.5,747.7c552.9,747.0,538.3,746.9,537.5,747.6c537.1,747.9,535.0,748.0,529.5,748.1c525.4,748.1,521.8,748.1,521.5,748.0|m775.9,748.0c775.6,747.9,775.2,747.7,775.1,747.5c775.0,747.3,774.1,747.2,773.1,747.2c771.8,747.2,771.2,747.0,771.0,746.7c770.8,746.4,770.4,746.1,769.9,746.1c769.5,746.1,769.0,745.9,768.9,745.6c768.7,745.3,768.5,745.1,768.3,745.1c768.1,745.1,767.9,744.9,767.7,744.6c767.6,744.3,767.3,744.1,767.1,744.1c766.9,744.1,766.2,743.4,765.6,742.5c765.0,741.7,764.3,741.0,764.1,741.0c763.7,741.0,762.6,739.2,762.6,738.5c762.6,738.3,762.3,737.6,761.9,737.0c761.5,736.5,761.2,735.8,761.2,735.5c761.2,735.1,761.0,734.7,760.8,734.5c760.6,734.2,760.5,733.8,760.5,733.4c760.5,733.1,760.3,732.6,760.1,732.4c760.0,732.2,759.7,731.4,759.7,730.6c759.0,724.2,759.0,531.2,759.6,526.0c759.8,524.6,760.1,523.3,760.2,523.1c760.4,522.9,760.5,522.4,760.5,522.1c760.5,521.8,760.6,521.4,760.8,521.1c761.0,520.9,761.2,520.4,761.2,520.1c761.2,519.8,761.5,519.1,761.9,518.6c762.3,518.0,762.6,517.4,762.6,517.1c762.6,516.6,765.1,512.9,765.7,512.5c766.0,512.3,766.4,512.0,766.6,511.9c766.8,511.7,767.2,511.4,767.4,511.2c767.7,511.0,768.0,510.7,768.2,510.6c768.4,510.5,768.7,510.3,768.9,510.1c769.1,509.9,769.4,509.7,769.6,509.6c769.8,509.5,770.1,509.3,770.4,509.1c770.6,508.9,771.5,508.5,772.4,508.2c774.9,507.5,983.6,507.5,986.2,508.2c987.9,508.7,989.3,509.5,989.6,510.2c989.7,510.3,989.9,510.5,990.1,510.5c990.4,510.5,990.9,510.9,991.2,511.5c991.6,512.1,992.1,512.5,992.3,512.5c992.7,512.5,996.0,517.3,996.0,517.8c996.0,518.0,996.3,518.9,996.7,519.8c997.1,520.7,997.4,521.8,997.4,522.1c997.4,522.5,997.6,523.0,997.8,523.2c998.0,523.4,998.1,524.0,998.1,524.5c998.1,525.0,998.3,525.6,998.4,525.9c998.7,526.2,998.7,547.1,998.7,627.8c998.7,708.5,998.7,729.4,998.4,729.7c998.3,729.9,998.1,730.6,998.1,731.2c998.1,731.8,998.0,732.5,997.8,732.7c997.6,733.0,997.4,733.3,997.4,733.6c997.4,733.8,997.1,735.0,996.6,736.3c995.7,738.9,993.2,743.0,992.5,743.0c992.3,743.0,991.8,743.5,991.5,744.1c991.0,744.8,990.6,745.1,990.0,745.1c989.6,745.1,989.2,745.3,989.0,745.6c988.8,745.9,988.5,746.1,988.3,746.1c988.1,746.1,987.8,746.4,987.6,746.7c987.4,747.1,986.7,747.2,984.0,747.2c981.5,747.2,980.5,747.3,980.0,747.7c979.0,748.4,967.9,748.4,966.6,747.7c965.9,747.2,964.7,747.2,959.8,747.3c956.5,747.4,952.7,747.6,951.3,747.8c947.8,748.4,908.2,748.2,907.8,747.6c907.6,747.3,906.8,747.2,905.4,747.2c904.0,747.2,903.2,747.3,903.0,747.6c902.7,747.9,900.5,748.0,893.5,748.0c886.4,748.0,884.2,747.9,883.9,747.6c883.8,747.4,883.3,747.2,882.8,747.2c882.3,747.2,881.8,747.4,881.7,747.6c881.4,747.9,872.9,748.0,840.7,748.0c808.5,748.0,800.0,747.9,799.7,747.6c799.5,747.3,798.7,747.2,797.3,747.2c795.9,747.2,795.1,747.3,794.9,747.6c794.7,747.9,792.4,748.0,785.5,748.1c780.6,748.1,776.2,748.0,775.9,748.0|m224.8,745.1c228.1,744.7,229.0,744.4,229.3,743.9c229.4,743.6,229.8,743.4,230.2,743.4c230.5,743.4,231.0,743.0,231.3,742.5c231.6,742.1,232.1,741.7,232.3,741.7c232.7,741.7,236.3,736.5,236.3,735.8c236.3,735.5,236.4,735.0,236.6,734.8c236.8,734.6,237.0,734.1,237.0,733.8c237.0,733.4,237.1,733.0,237.3,732.7c237.5,732.5,237.7,731.8,237.7,731.2c237.7,730.6,237.8,729.9,238.0,729.7c238.2,729.4,238.2,708.5,238.2,628.0c238.2,547.4,238.2,526.6,238.0,526.2c237.8,526.0,237.7,525.5,237.7,525.1c237.7,524.6,237.5,524.1,237.3,523.9c237.1,523.6,237.0,523.2,237.0,522.8c237.0,522.5,236.8,522.0,236.6,521.8c236.4,521.6,236.3,521.1,236.3,520.8c236.3,520.1,231.6,513.2,231.1,513.2c230.9,513.2,230.4,512.8,230.1,512.2c229.6,511.5,229.2,511.2,228.7,511.2c228.3,511.2,227.8,511.0,227.6,510.8c227.5,510.5,226.8,510.2,226.0,510.0c223.3,509.4,197.9,509.2,119.6,509.2c44.5,509.2,16.0,509.4,13.6,510.0c13.1,510.1,12.5,510.4,12.4,510.7c12.2,510.9,11.8,511.2,11.4,511.2c10.8,511.2,10.4,511.5,9.9,512.2c9.6,512.8,9.1,513.2,8.9,513.2c8.7,513.2,7.6,514.6,6.5,516.2c4.9,518.7,4.3,519.8,3.5,522.5c2.9,524.3,2.3,526.3,2.3,527.0c2.2,527.6,2.0,529.3,1.9,530.6c1.6,533.9,1.6,722.0,1.9,725.4c2.0,726.7,2.2,728.3,2.3,729.0c2.4,730.5,3.7,734.3,4.5,735.8c4.9,736.4,5.1,737.1,5.1,737.3c5.1,738.4,8.5,742.4,9.5,742.4c9.6,742.4,9.9,742.6,10.1,742.9c10.2,743.2,10.5,743.4,10.8,743.4c11.0,743.4,11.3,743.6,11.4,743.9c11.7,744.4,12.6,744.6,15.6,745.1c18.1,745.4,222.0,745.5,224.8,745.1|m478.4,745.1c481.6,744.7,482.5,744.4,482.8,743.9c483.0,743.6,483.3,743.4,483.6,743.4c484.5,743.4,486.1,741.9,487.6,739.8c488.4,738.6,489.1,737.4,489.1,737.2c489.1,737.0,489.4,736.2,489.8,735.5c490.2,734.8,490.5,734.0,490.5,733.7c490.5,733.4,490.7,733.0,490.9,732.7c491.1,732.5,491.2,731.9,491.2,731.4c491.2,730.8,491.4,730.2,491.6,730.0c491.8,729.7,491.9,729.0,491.9,727.9c491.9,726.9,492.1,726.1,492.3,725.9c492.5,725.6,492.6,725.2,492.6,724.8c492.6,724.5,492.5,724.0,492.3,723.8c491.8,723.2,491.8,721.3,492.3,720.7c492.7,720.2,492.7,719.8,492.2,712.5c491.8,707.0,491.9,582.8,492.3,582.2c492.7,581.6,492.7,579.7,492.3,579.2c491.8,578.6,491.8,569.9,492.2,569.3c492.4,568.9,492.5,564.5,492.5,549.6c492.5,534.7,492.4,530.3,492.2,530.0c492.1,529.8,491.9,528.9,491.9,528.0c491.9,527.0,491.8,526.2,491.6,525.9c491.4,525.7,491.2,525.0,491.2,524.4c491.2,523.8,491.1,523.1,490.9,522.8c490.7,522.6,490.5,522.2,490.5,521.8c490.5,521.5,490.2,520.8,489.8,520.3c489.4,519.7,489.1,519.0,489.1,518.8c489.1,518.1,486.5,514.3,486.1,514.3c485.9,514.3,485.4,513.8,485.0,513.2c484.7,512.7,484.2,512.2,484.0,512.2c483.7,512.2,483.4,512.0,483.3,511.7c483.1,511.4,482.8,511.2,482.6,511.2c482.4,511.2,482.1,511.0,481.9,510.7c481.4,510.0,478.4,509.8,463.0,509.4c439.7,508.9,270.5,509.2,270.1,509.7c270.0,510.0,269.2,510.1,268.4,510.1c267.4,510.1,266.9,510.3,266.7,510.6c266.5,510.9,266.2,511.2,266.0,511.2c265.7,511.2,265.4,511.4,265.3,511.7c265.1,512.0,264.8,512.2,264.6,512.2c264.4,512.2,263.9,512.7,263.5,513.2c263.1,513.8,262.7,514.3,262.5,514.3c262.0,514.3,258.7,519.1,258.7,519.8c258.7,520.1,258.6,520.5,258.4,520.8c258.2,521.0,258.0,521.5,258.0,521.8c258.0,522.1,257.9,522.6,257.7,522.8c257.5,523.1,257.3,523.5,257.3,523.9c257.3,524.2,257.2,524.7,257.0,524.9c256.8,525.1,256.6,526.0,256.5,526.9c256.5,527.8,256.3,529.7,256.2,531.1c255.8,534.6,255.9,720.3,256.2,723.8c256.3,725.2,256.5,727.3,256.5,728.5c256.6,729.7,256.8,730.8,257.0,731.0c257.2,731.3,257.3,731.7,257.3,732.1c257.3,732.4,257.5,732.8,257.7,733.1c257.9,733.3,258.0,733.8,258.0,734.1c258.0,734.4,258.3,735.0,258.6,735.5c258.9,735.9,259.2,736.5,259.2,736.8c259.2,737.4,261.0,740.2,261.6,740.5c261.9,740.6,262.3,741.0,262.6,741.4c263.2,742.1,264.8,743.4,265.2,743.4c265.3,743.4,265.6,743.6,265.7,743.9c265.9,744.2,266.4,744.4,266.8,744.4c267.2,744.4,267.6,744.6,267.7,744.7c267.9,744.9,268.8,745.1,269.8,745.2c274.1,745.5,476.3,745.4,478.4,745.1|m732.2,744.8c732.4,744.6,732.8,744.4,733.2,744.4c733.6,744.4,734.1,744.2,734.4,743.9c734.6,743.6,735.1,743.4,735.4,743.4c735.8,743.4,736.3,743.1,736.5,742.7c736.8,742.3,737.3,741.8,737.7,741.5c738.5,741.0,740.8,737.5,740.8,736.8c740.8,736.5,741.1,735.9,741.4,735.5c741.7,735.0,742.0,734.4,742.0,734.1c742.0,733.8,742.1,733.3,742.3,733.1c742.5,732.8,742.7,732.2,742.7,731.6c742.7,731.0,742.9,730.1,743.0,729.6c743.6,728.3,743.6,527.9,743.0,526.1c742.8,525.4,742.7,524.5,742.7,524.0c742.7,523.6,742.5,523.1,742.3,522.8c742.1,522.6,742.0,522.2,742.0,521.8c742.0,521.5,741.6,520.7,741.1,519.9c740.5,519.2,740.1,518.3,740.1,518.1c740.1,517.4,738.0,514.3,737.5,514.3c737.3,514.3,736.9,513.8,736.5,513.2c736.1,512.7,735.6,512.2,735.4,512.2c735.2,512.2,734.9,512.0,734.7,511.7c734.6,511.4,734.3,511.2,734.0,511.2c733.8,511.2,733.5,510.9,733.3,510.6c733.1,510.3,732.6,510.1,731.6,510.1c730.8,510.1,730.0,510.0,729.9,509.7c729.5,509.2,559.6,508.9,535.8,509.4c520.6,509.7,517.9,509.9,517.4,510.8c517.2,511.0,516.9,511.2,516.7,511.2c516.5,511.2,516.2,511.4,516.0,511.7c515.9,512.0,515.5,512.2,515.3,512.2c515.1,512.2,514.8,512.4,514.6,512.7c514.5,513.0,514.2,513.2,513.9,513.2c513.4,513.2,509.5,519.1,509.5,519.8c509.5,520.1,509.3,520.5,509.1,520.8c508.9,521.0,508.8,521.5,508.8,521.8c508.8,522.1,508.6,522.6,508.4,522.8c508.2,523.1,508.1,523.5,508.1,523.9c508.1,524.2,507.9,524.7,507.7,524.9c507.5,525.2,507.4,525.9,507.4,526.9c507.4,527.8,507.2,528.7,507.1,529.0c506.8,529.3,506.8,549.5,506.8,627.8c506.8,706.0,506.8,726.3,507.1,726.6c507.2,726.8,507.4,727.8,507.4,728.6c507.4,729.7,507.5,730.4,507.7,730.7c507.9,730.9,508.1,731.4,508.1,731.7c508.1,732.0,508.2,732.5,508.4,732.7c508.6,733.0,508.8,733.4,508.8,733.7c508.8,734.1,509.1,734.8,509.5,735.3c509.9,735.9,510.2,736.6,510.2,736.9c510.2,737.5,512.2,740.6,512.6,740.6c512.7,740.6,513.1,741.0,513.5,741.4c513.9,741.8,514.7,742.5,515.2,742.9c515.7,743.2,516.3,743.7,516.5,743.9c516.9,744.4,518.0,744.7,520.7,745.1c521.8,745.2,569.8,745.3,627.3,745.3c710.7,745.3,732.0,745.2,732.2,744.8|m984.1,745.1c987.4,744.7,988.3,744.4,988.6,743.9c988.7,743.6,989.0,743.4,989.2,743.4c989.5,743.4,989.8,743.2,989.9,742.9c990.1,742.6,990.4,742.4,990.6,742.4c991.1,742.4,995.6,735.8,995.6,735.1c995.6,734.8,995.7,734.3,995.9,734.1c996.1,733.9,996.3,733.3,996.3,732.8c996.3,732.3,996.4,731.6,996.6,731.2c996.8,730.8,997.0,729.9,997.0,729.1c997.1,728.4,997.3,726.7,997.4,725.4c997.6,723.6,997.6,696.1,997.6,625.7c997.5,522.3,997.6,528.1,996.5,524.5c996.4,523.9,996.3,523.2,996.3,523.0c996.3,522.7,995.9,521.9,995.6,521.2c995.2,520.6,994.9,519.9,994.9,519.7c994.9,519.0,991.5,514.3,991.1,514.3c990.9,514.3,990.4,513.8,990.1,513.2c989.7,512.7,989.3,512.2,989.1,512.2c989.0,512.2,988.7,512.0,988.5,511.7c988.4,511.4,988.0,511.2,987.7,511.2c987.4,511.2,987.1,510.9,986.9,510.6c986.7,510.3,986.2,510.1,985.5,510.1c984.9,510.1,984.3,509.9,984.1,509.7c983.8,509.2,813.4,508.9,789.8,509.4c774.9,509.7,772.2,509.9,771.6,510.8c771.5,511.0,771.1,511.2,770.7,511.2c770.4,511.2,770.0,511.4,769.8,511.7c769.7,512.0,769.4,512.2,769.1,512.2c768.9,512.2,768.2,512.9,767.6,513.7c766.9,514.6,766.2,515.3,766.0,515.3c765.6,515.3,763.7,518.1,763.7,518.8c763.7,519.0,763.4,519.7,763.0,520.3c762.7,520.8,762.3,521.5,762.3,521.8c762.3,522.2,762.2,522.6,762.0,522.8c761.8,523.1,761.6,523.5,761.6,523.9c761.6,524.2,761.5,524.7,761.3,524.9c761.1,525.2,760.9,525.9,760.9,526.9c760.9,527.8,760.8,528.7,760.6,529.0c760.4,529.3,760.4,549.4,760.4,627.3c760.4,705.1,760.4,725.2,760.6,725.6c760.8,725.8,760.9,726.9,760.9,728.1c760.9,729.6,761.0,730.4,761.3,730.7c761.5,730.9,761.6,731.4,761.6,731.7c761.6,732.0,761.8,732.5,762.0,732.7c762.2,733.0,762.3,733.4,762.3,733.8c762.3,734.1,762.5,734.6,762.7,734.8c762.9,735.0,763.0,735.5,763.0,735.8c763.0,736.4,766.5,741.7,766.9,741.7c767.3,741.7,769.5,743.3,770.1,743.9c770.5,744.4,771.6,744.7,774.3,745.1c777.1,745.4,981.4,745.4,984.1,745.1|m19.8,740.1c13.5,740.0,11.9,739.8,11.3,739.4c10.9,739.1,10.5,738.8,10.4,738.6c10.3,738.4,10.1,738.2,9.9,738.2c9.6,738.2,8.7,737.1,7.8,735.7c6.6,733.9,6.1,732.9,5.9,732.1c5.9,731.4,5.7,730.6,5.5,730.4c5.4,730.1,5.3,722.2,5.3,704.8c5.3,681.1,5.3,679.6,5.7,678.3c5.9,677.5,6.4,676.5,6.7,676.0l7.3,675.0l6.3,673.5l5.3,671.9l5.3,644.5l5.3,617.1l5.9,615.5c6.7,613.4,6.7,613.3,5.9,611.2l5.3,609.6l5.3,584.6c5.3,567.2,5.4,559.5,5.5,559.2c5.7,559.0,5.9,558.3,5.9,557.7c6.1,556.6,8.2,553.2,9.0,552.7c9.3,552.5,9.6,552.3,9.8,552.1c11.3,550.8,10.4,550.8,45.2,550.8l78.8,550.8l79.5,551.8c79.8,552.3,80.3,552.7,80.5,552.7c80.8,552.7,80.9,553.0,80.9,553.4c80.9,553.7,81.1,554.2,81.3,554.5c81.6,554.8,81.8,554.7,82.4,553.8c82.8,553.2,83.3,552.7,83.5,552.7c83.8,552.7,84.1,552.5,84.2,552.2c84.4,551.9,84.7,551.7,84.9,551.7c85.1,551.7,85.4,551.5,85.6,551.3c85.8,550.9,92.9,550.8,119.5,550.8c154.3,550.8,153.4,550.8,154.9,552.1c155.0,552.3,155.4,552.5,155.6,552.6c155.8,552.7,156.0,553.0,156.0,553.2c156.0,553.8,156.8,554.8,157.2,554.8c157.4,554.8,158.1,554.1,158.7,553.3c159.4,552.5,160.2,551.6,160.6,551.4c161.2,550.9,165.6,550.8,195.2,550.8c222.1,550.8,229.3,550.9,229.5,551.3c229.7,551.5,230.0,551.7,230.2,551.7c230.4,551.7,230.7,551.9,230.9,552.2c231.0,552.5,231.3,552.7,231.6,552.7c232.1,552.7,233.9,555.5,233.9,556.2c233.9,556.5,234.1,557.0,234.3,557.2c234.5,557.4,234.6,557.9,234.6,558.2c234.6,558.5,234.8,559.0,235.0,559.4c235.3,560.0,235.3,563.5,235.3,584.2c235.3,604.8,235.3,608.3,235.0,608.9c234.8,609.3,234.6,609.8,234.6,610.1c234.6,610.5,234.5,610.9,234.3,611.1c233.8,611.7,233.8,614.0,234.3,614.6c234.5,614.8,234.6,615.3,234.6,615.8c234.6,616.2,234.8,617.0,235.0,617.5c235.3,618.4,235.3,622.1,235.3,644.4c235.3,672.7,235.4,671.1,234.0,673.9l233.4,675.0l234.0,676.2c234.3,676.9,234.6,677.6,234.6,677.8c234.6,678.1,234.8,678.6,235.0,679.0c235.5,680.0,235.5,727.5,235.0,728.5c234.8,728.8,234.6,729.6,234.6,730.2c234.6,730.8,234.5,731.5,234.3,731.7c234.1,731.9,233.9,732.3,233.9,732.6c233.9,733.5,232.8,736.0,232.4,736.1c232.1,736.2,231.6,736.7,231.2,737.2c230.9,737.8,230.4,738.2,230.2,738.2c229.9,738.2,229.6,738.5,229.5,738.7c229.3,739.0,229.0,739.3,228.8,739.3c228.6,739.3,228.3,739.5,228.1,739.7c227.7,740.3,162.2,740.3,161.4,739.7c161.1,739.5,160.7,739.2,160.5,739.1c159.2,738.4,158.6,737.5,158.3,736.1c158.0,734.7,157.4,735.0,156.0,737.1c155.3,738.3,154.5,739.3,154.3,739.3c154.2,739.3,153.9,739.5,153.7,739.7c153.5,740.0,146.4,740.1,119.6,740.1c92.9,740.1,85.8,740.0,85.6,739.7c85.4,739.5,85.1,739.3,84.9,739.3c84.7,739.3,84.1,738.6,83.5,737.7c82.5,736.2,81.7,735.8,81.2,736.6c81.1,736.8,80.9,737.3,80.9,737.6c80.9,738.0,80.8,738.2,80.5,738.2c80.3,738.2,79.9,738.6,79.5,739.1l78.9,740.0l53.2,740.1c39.1,740.1,24.0,740.1,19.8,740.1|m274.5,740.1c269.9,740.0,266.7,739.8,266.6,739.6c266.4,739.4,266.1,739.3,265.8,739.3c265.5,739.3,264.9,739.0,264.5,738.7c263.4,737.8,260.8,734.1,260.8,733.4c260.8,733.1,260.7,732.6,260.5,732.4c260.3,732.2,260.1,731.5,260.1,731.0c260.1,730.5,260.0,729.9,259.9,729.8c259.7,729.7,259.6,720.8,259.6,704.2c259.6,687.7,259.7,678.8,259.9,678.6c260.0,678.5,260.1,678.2,260.1,677.9c260.1,677.5,260.5,676.8,260.9,676.2l261.6,675.0l260.9,673.9c260.5,673.3,260.1,672.5,260.1,672.2c260.1,671.9,260.0,671.5,259.9,671.4c259.7,671.3,259.6,661.9,259.6,644.5c259.6,627.0,259.7,617.6,259.9,617.5c260.0,617.4,260.1,617.0,260.1,616.6c260.1,616.3,260.3,615.8,260.5,615.6c260.7,615.4,260.8,614.9,260.8,614.6c260.8,614.3,261.0,613.8,261.2,613.5c261.6,612.9,261.6,612.8,260.9,611.7c260.5,611.1,260.1,610.3,260.1,610.0c260.1,609.7,260.0,609.4,259.9,609.2c259.5,608.9,259.6,559.8,259.9,558.8c260.1,558.4,260.3,557.8,260.4,557.5c260.5,557.3,260.7,556.7,260.8,556.3c261.2,555.0,263.1,552.6,264.3,551.9c264.5,551.7,264.9,551.5,265.2,551.2c265.7,550.9,274.4,550.8,299.4,550.8l333.1,550.8l333.7,551.8c334.1,552.3,334.6,552.7,334.7,552.7c334.9,552.7,335.2,553.0,335.5,553.3c335.9,553.8,335.9,553.8,336.3,553.3c336.6,553.0,336.9,552.7,337.1,552.7c337.3,552.7,337.7,552.3,338.1,551.8l338.7,550.8l373.2,550.8c400.5,550.8,407.8,550.9,408.0,551.3c408.1,551.5,408.4,551.7,408.6,551.7c408.8,551.7,409.5,552.4,410.1,553.3l411.2,554.9l412.3,553.4c414.3,550.6,410.9,550.8,449.1,550.8c476.3,550.8,483.5,550.9,483.8,551.3c483.9,551.5,484.2,551.7,484.4,551.7c484.7,551.7,485.1,552.2,485.5,552.7c485.9,553.3,486.4,553.8,486.6,553.8c486.8,553.8,487.0,554.0,487.0,554.4c487.0,554.7,487.3,555.4,487.6,555.8c487.9,556.3,488.2,557.0,488.2,557.5c488.2,558.0,488.4,558.7,488.5,559.1c489.1,560.1,489.1,609.5,488.5,610.1c488.3,610.3,488.2,610.7,488.2,611.0c488.2,611.2,488.0,611.9,487.8,612.5c487.4,613.4,487.4,613.5,487.8,614.1c488.0,614.5,488.2,615.0,488.2,615.3c488.2,615.5,488.4,616.1,488.5,616.4c489.1,617.4,489.1,671.5,488.5,672.5c488.4,672.8,488.2,673.4,488.2,673.6c488.2,673.9,488.0,674.4,487.8,674.8c487.5,675.3,487.4,675.5,487.7,676.0c487.8,676.3,488.0,676.8,488.1,677.1c488.2,677.4,488.4,678.0,488.6,678.5c489.1,679.9,489.1,730.1,488.5,730.7c488.3,730.9,488.2,731.4,488.2,731.7c488.2,732.0,488.0,732.5,487.8,732.7c487.6,733.0,487.5,733.4,487.5,733.7c487.5,734.4,485.6,737.2,485.1,737.2c484.9,737.2,484.5,737.7,484.1,738.2c483.6,738.9,483.2,739.3,482.7,739.3c482.3,739.3,481.8,739.5,481.7,739.7c481.4,740.0,474.4,740.1,448.1,740.1c410.8,740.1,414.1,740.4,412.3,737.6c411.8,736.8,411.3,736.2,411.2,736.2c411.0,736.2,410.5,736.8,410.1,737.5c409.6,738.3,408.8,739.1,408.3,739.5c407.4,740.1,405.9,740.1,373.4,740.1c346.5,740.1,339.4,740.0,339.1,739.7c339.0,739.5,338.7,739.3,338.5,739.3c338.3,739.3,337.6,738.5,337.0,737.6l335.9,736.0l334.5,738.0l333.2,740.0l307.7,740.1c293.7,740.1,278.8,740.1,274.5,740.1|m524.9,740.1c520.2,740.0,517.0,739.8,516.9,739.6c516.7,739.4,516.5,739.3,516.2,739.3c516.0,739.3,515.7,739.0,515.6,738.7c515.4,738.5,515.1,738.2,514.9,738.2c514.4,738.2,511.1,733.4,511.1,732.7c511.1,732.4,511.0,732.0,510.8,731.8c510.6,731.4,510.5,725.7,510.5,705.3c510.5,676.8,510.4,678.5,511.9,676.1l512.6,675.0l511.6,673.6l510.5,672.2l510.5,644.6c510.5,616.3,510.5,616.7,511.4,614.6c511.8,613.5,511.9,613.2,511.7,612.8c511.6,612.5,511.5,612.1,511.4,611.8c510.5,609.7,510.5,610.0,510.5,584.2c510.5,558.4,510.5,558.6,511.4,556.5c511.5,556.2,511.6,555.8,511.7,555.5c512.0,554.3,512.2,553.9,512.7,553.8c512.9,553.8,513.4,553.3,513.8,552.7c514.2,552.2,514.6,551.7,514.9,551.7c515.1,551.7,515.4,551.5,515.5,551.3c515.8,550.9,523.0,550.8,550.3,550.8l584.8,550.8l585.4,551.8c585.8,552.3,586.3,552.7,586.5,552.7c586.7,552.7,587.0,553.0,587.1,553.2c587.6,554.1,588.1,553.9,589.2,552.3l590.2,550.8l624.7,550.8c651.9,550.8,659.2,550.9,659.5,551.3c659.6,551.5,659.9,551.7,660.1,551.7c660.3,551.7,660.8,552.2,661.2,552.7c661.5,553.3,662.1,553.8,662.3,553.8c662.6,553.8,663.1,553.3,663.5,552.7c663.9,552.2,664.4,551.7,664.6,551.7c664.8,551.7,665.1,551.5,665.2,551.3c665.6,550.7,733.9,550.6,734.8,551.2c735.1,551.5,735.5,551.7,735.7,551.9c736.9,552.6,738.2,554.2,738.5,555.3c738.6,555.7,738.8,556.2,738.9,556.5c739.8,558.6,739.8,558.4,739.8,584.4c739.8,604.2,739.7,609.8,739.5,610.2c739.3,610.4,739.2,610.8,739.2,611.2c739.2,611.5,739.0,611.9,738.8,612.2c738.6,612.4,738.5,612.9,738.5,613.4c738.5,613.8,738.6,614.3,738.8,614.6c739.0,614.8,739.2,615.3,739.2,615.6c739.2,615.9,739.3,616.3,739.5,616.6c739.7,616.9,739.8,623.0,739.8,644.4l739.8,671.9l739.1,672.9c738.4,674.0,738.2,676.0,738.8,676.7c739.0,677.0,739.2,677.4,739.2,677.7c739.2,678.1,739.3,678.5,739.5,678.8c739.7,679.1,739.8,684.7,739.8,704.5c739.8,728.1,739.7,729.9,739.4,731.1c739.1,731.8,738.8,732.5,738.7,732.6c738.6,732.7,738.5,733.0,738.5,733.4c738.5,734.4,735.6,738.3,734.3,739.1c734.1,739.2,733.7,739.5,733.4,739.7c732.5,740.3,666.3,740.3,665.9,739.7c665.8,739.5,665.5,739.3,665.3,739.3c665.1,739.3,664.4,738.6,663.9,737.7c663.3,736.9,662.6,736.2,662.3,736.2c662.1,736.2,661.4,736.9,660.8,737.7c660.3,738.6,659.6,739.3,659.4,739.3c659.2,739.3,658.9,739.5,658.7,739.7c658.3,740.4,591.8,740.3,590.6,739.6c590.2,739.4,589.3,738.5,588.7,737.6c587.8,736.3,587.5,736.1,587.2,736.4c587.0,736.6,586.7,737.1,586.7,737.5c586.7,737.9,586.5,738.2,586.4,738.2c586.2,738.2,585.8,738.6,585.5,739.1l584.9,740.0l558.8,740.1c544.5,740.1,529.2,740.1,524.9,740.1|m778.4,740.1c773.7,740.0,770.6,739.8,770.4,739.6c770.3,739.4,770.0,739.3,769.8,739.3c769.6,739.3,769.3,739.0,769.1,738.7c769.0,738.5,768.7,738.2,768.4,738.2c768.2,738.2,767.7,737.8,767.4,737.2c767.0,736.6,766.6,736.2,766.4,736.2c766.2,736.2,766.1,736.0,766.1,735.7c766.1,735.5,765.8,734.8,765.4,734.3c764.9,733.6,764.7,733.0,764.7,732.2c764.7,731.7,764.5,730.9,764.3,730.5c764.0,730.0,764.0,726.3,764.0,704.7c764.0,683.2,764.0,679.5,764.3,679.0c764.5,678.6,764.7,678.1,764.7,677.8c764.7,677.5,765.0,676.8,765.4,676.2l766.2,675.0l765.5,673.9c763.9,671.4,764.0,673.0,764.0,643.8l764.0,617.4l765.0,615.5c765.6,614.5,766.1,613.4,766.1,613.2c766.1,612.9,765.6,612.0,765.0,611.1l764.0,609.4l764.0,584.2c764.0,562.6,764.0,559.0,764.3,558.4c764.5,558.0,764.7,557.5,764.7,557.2c764.7,556.5,767.3,552.7,767.7,552.7c768.0,552.7,768.3,552.5,768.4,552.2c768.6,551.9,768.9,551.7,769.1,551.7c769.3,551.7,769.6,551.5,769.8,551.3c770.0,550.9,777.2,550.8,804.2,550.8c831.2,550.8,838.4,550.9,838.6,551.3c838.8,551.5,839.1,551.7,839.3,551.7c839.5,551.7,840.0,552.2,840.4,552.7c841.2,554.0,841.5,554.0,842.5,552.8c844.4,550.7,841.6,550.8,879.4,550.8c906.9,550.8,914.2,550.9,914.4,551.3c914.6,551.5,914.9,551.7,915.1,551.7c915.3,551.7,915.8,552.2,916.1,552.7c917.0,554.0,917.6,554.0,918.5,552.7c918.8,552.2,919.3,551.7,919.5,551.7c919.7,551.7,920.0,551.5,920.2,551.3c920.4,550.9,927.6,550.8,954.5,550.8c991.6,550.8,988.8,550.7,990.7,552.8c991.1,553.3,991.6,553.8,991.8,553.8c991.9,553.8,992.0,554.0,992.0,554.2c992.0,554.5,992.3,555.0,992.5,555.3c992.8,555.6,993.2,556.6,993.4,557.4c993.9,558.8,993.9,559.4,993.9,584.4l993.9,610.0l993.3,610.8c992.9,611.3,992.7,612.0,992.7,612.7c992.7,613.3,993.0,614.5,993.3,615.4l993.9,617.0l993.9,643.9c993.9,673.3,994.0,671.8,992.6,674.1l992.0,675.0l992.6,676.0c994.0,678.2,993.9,676.9,993.9,704.2c993.9,725.7,993.9,729.4,993.6,730.2c993.4,730.7,993.2,731.4,993.2,731.7c993.2,732.0,993.0,732.6,992.6,733.1c992.3,733.5,992.0,734.1,992.0,734.4c992.0,735.2,990.6,737.2,990.1,737.2c989.9,737.2,989.7,737.4,989.6,737.6c989.5,737.8,989.2,738.1,988.9,738.3c988.6,738.4,988.3,738.7,988.1,738.9c986.6,740.2,987.4,740.1,953.8,740.1c928.0,740.1,921.1,740.0,920.9,739.7c920.7,739.5,920.4,739.3,920.2,739.3c920.0,739.3,919.4,738.6,918.8,737.7c918.3,736.9,917.6,736.2,917.3,736.2c917.0,736.2,916.4,736.9,915.8,737.7c915.2,738.6,914.6,739.3,914.4,739.3c914.2,739.3,913.9,739.5,913.7,739.7c913.5,740.0,906.2,740.1,879.1,740.1l844.7,740.1l844.0,739.2c843.7,738.7,843.2,738.2,843.0,738.2c842.7,738.2,842.6,738.0,842.6,737.6c842.6,736.7,842.1,736.2,841.4,736.2c841.0,736.2,840.5,736.6,839.9,737.7c839.4,738.6,838.9,739.3,838.6,739.3c838.4,739.3,838.1,739.4,838.0,739.6c837.7,740.0,793.9,740.3,778.4,740.1|m77.0,738.0c77.2,737.7,77.5,737.5,77.8,737.5c78.3,737.5,80.5,734.5,80.5,733.7c80.5,733.4,80.6,733.0,80.8,732.7c81.3,732.1,81.3,726.5,80.8,725.9c80.3,725.2,80.3,711.6,80.8,710.6c81.3,709.7,81.3,700.9,80.9,699.9c80.6,699.4,80.6,699.2,80.9,698.4c81.3,697.1,81.3,683.1,80.8,681.8c80.6,681.2,80.5,680.6,80.5,680.3c80.5,680.1,80.0,679.3,79.4,678.5l78.4,677.2l68.4,676.9c62.9,676.8,47.2,676.7,33.5,676.8l8.7,677.0l7.9,677.9c7.4,678.4,7.0,679.1,7.0,679.4c7.0,679.8,6.9,680.2,6.7,680.5c6.3,681.1,6.3,728.0,6.7,728.7c6.9,728.9,7.0,729.6,7.0,730.2c7.0,731.1,7.3,731.7,8.8,733.9c9.8,735.3,10.8,736.5,11.0,736.5c11.2,736.5,11.5,736.7,11.7,737.0c11.9,737.3,12.3,737.5,12.7,737.5c13.1,737.5,13.6,737.7,13.7,737.9c14.1,738.4,17.4,738.5,47.9,738.4c70.6,738.4,76.8,738.3,77.0,738.0|m151.6,738.0c151.8,737.7,152.2,737.5,152.6,737.5c153.1,737.5,153.7,737.1,154.3,736.3c156.2,733.9,156.1,735.5,156.1,706.6l156.1,681.0l155.5,679.7c155.1,679.1,154.5,678.2,154.1,677.7l153.4,677.0l128.9,676.8c115.5,676.7,100.0,676.8,94.7,676.9l84.9,677.2l83.9,678.5l83.0,679.9l83.0,706.8l83.0,733.6l84.4,735.6c85.1,736.7,86.0,737.5,86.2,737.5c86.5,737.5,86.8,737.7,86.9,737.9c87.3,738.4,90.6,738.5,121.8,738.4c145.1,738.4,151.4,738.3,151.6,738.0|m226.0,738.0c226.2,737.7,226.8,737.5,227.4,737.5c228.0,737.5,228.7,737.3,228.9,737.0c229.2,736.8,229.5,736.5,229.7,736.5c230.2,736.5,232.6,732.8,233.0,731.4c234.0,728.3,234.0,727.2,234.0,704.2c234.0,680.1,234.0,679.8,232.7,677.9l232.1,677.0l206.6,676.8c192.6,676.7,176.6,676.8,170.9,676.9l160.6,677.2l159.7,678.5c159.2,679.3,158.8,680.1,158.8,680.4c158.8,680.6,158.7,681.2,158.5,681.8c158.0,683.3,158.0,729.0,158.5,730.5c158.7,731.0,158.8,731.8,158.8,732.2c158.8,733.2,159.8,735.9,160.2,736.2c160.4,736.3,160.7,736.6,160.9,736.7c161.1,736.8,161.4,737.0,161.6,737.2c162.6,738.0,163.4,738.2,165.6,738.3c167.0,738.4,181.0,738.4,196.9,738.4c219.6,738.4,225.8,738.3,226.0,738.0|m331.5,738.0c331.7,737.7,332.0,737.5,332.2,737.5c332.4,737.5,333.0,736.8,333.6,736.0l334.6,734.4l334.6,707.1l334.6,679.8l333.6,678.5l332.7,677.2l325.2,677.0c315.6,676.7,279.7,676.7,270.1,677.0l262.7,677.2l262.0,678.1c261.4,678.9,261.3,679.4,261.3,680.6c261.3,681.4,261.2,682.3,261.0,682.5c260.8,682.9,260.7,687.7,260.7,704.6c260.7,721.4,260.8,726.3,261.0,726.6c261.2,726.8,261.3,727.8,261.3,728.6c261.3,729.7,261.4,730.4,261.6,730.7c261.8,730.9,262.0,731.4,262.0,731.7c262.0,732.5,264.7,736.5,265.2,736.5c265.5,736.5,265.8,736.7,266.0,737.0c266.1,737.3,266.6,737.5,267.0,737.5c267.4,737.5,267.8,737.7,268.0,737.9c268.3,738.4,271.5,738.5,302.2,738.4c325.1,738.4,331.3,738.3,331.5,738.0|m406.0,738.0c406.2,737.8,406.9,737.4,407.4,737.0c408.6,736.2,409.1,735.5,409.1,734.8c409.1,734.5,409.3,734.0,409.5,733.8c409.8,733.4,409.8,730.0,409.8,706.9c409.8,681.0,409.8,680.4,409.4,679.3c409.1,678.7,408.6,677.9,408.2,677.6c407.6,676.9,406.3,676.9,373.5,676.9l339.5,676.9l338.6,678.0c338.1,678.5,337.6,679.2,337.5,679.5c337.5,679.8,337.2,680.5,337.0,681.2c336.6,682.2,336.6,684.6,336.6,706.7c336.6,727.7,336.7,731.3,337.0,731.9c337.2,732.2,337.3,733.0,337.3,733.6c337.3,735.2,339.1,737.5,340.2,737.5c340.6,737.5,341.1,737.7,341.2,737.9c341.5,738.4,344.9,738.5,376.0,738.4c397.0,738.4,405.6,738.3,406.0,738.0|m480.5,738.0c480.7,737.7,481.1,737.5,481.4,737.5c481.7,737.5,482.2,737.3,482.5,737.0c482.7,736.8,483.1,736.5,483.3,736.5c483.7,736.5,486.5,732.4,486.5,731.7c486.5,731.5,486.7,731.0,486.9,730.7c487.8,729.1,487.8,728.0,487.8,703.7l487.8,680.4l487.3,679.3c487.0,678.7,486.5,677.9,486.1,677.6c485.5,676.9,484.4,676.9,450.0,676.9l414.5,676.9l413.5,678.4l412.5,679.8l412.4,705.0c412.4,718.8,412.4,731.0,412.5,732.0c412.7,733.7,412.8,734.0,414.0,735.7c414.7,736.7,415.5,737.5,415.7,737.5c415.9,737.5,416.1,737.7,416.3,737.9c416.6,738.4,419.9,738.5,450.9,738.4c474.0,738.4,480.3,738.3,480.5,738.0|m583.0,738.0c583.1,737.7,583.4,737.5,583.6,737.5c584.1,737.5,586.2,734.7,586.2,733.9c586.2,733.5,586.4,733.0,586.5,732.7c587.1,732.1,587.1,714.7,586.5,713.7c586.3,713.2,586.2,712.0,586.2,709.2c586.2,706.4,586.3,705.2,586.5,704.7c587.1,703.7,587.1,685.9,586.6,684.4c586.4,683.9,586.2,682.7,586.2,681.7c586.2,680.1,586.1,679.9,585.1,678.4l584.1,676.9l582.0,676.8c580.8,676.7,579.8,676.5,579.5,676.2c579.0,675.7,578.9,675.7,578.4,676.2c577.9,676.6,573.9,676.7,545.8,676.8l513.8,676.9l513.0,677.7c512.6,678.1,512.2,678.9,512.1,679.4c512.0,679.9,511.9,680.5,511.8,680.7c511.5,681.3,511.7,728.1,512.0,729.9c512.2,731.1,512.6,732.0,513.9,734.0c514.9,735.4,515.8,736.5,516.0,736.5c516.2,736.5,516.6,736.8,516.8,737.0c517.1,737.3,517.6,737.5,517.9,737.5c518.2,737.5,518.6,737.7,518.7,737.9c519.1,738.4,522.4,738.5,553.4,738.4c576.5,738.4,582.7,738.3,583.0,738.0|m657.6,738.0c657.7,737.7,658.1,737.5,658.3,737.5c658.5,737.5,659.1,736.8,659.6,736.0l660.5,734.4l660.7,727.8c660.8,724.1,660.8,712.0,660.8,700.7c660.7,680.4,660.7,680.3,660.2,679.3c659.9,678.7,659.4,677.9,659.0,677.6c658.4,676.9,657.3,676.9,624.7,676.9c592.3,676.9,591.0,676.9,590.4,677.6c590.0,677.9,589.5,678.7,589.2,679.3c588.8,680.4,588.8,681.0,588.8,706.9c588.8,730.0,588.8,733.4,589.1,733.8c589.3,734.0,589.5,734.4,589.5,734.7c589.5,735.5,590.2,736.5,590.7,736.5c590.9,736.5,591.2,736.7,591.3,737.0c591.5,737.3,591.8,737.5,592.0,737.5c592.2,737.5,592.5,737.7,592.6,737.9c593.0,738.4,596.3,738.5,627.6,738.4c651.0,738.4,657.3,738.3,657.6,738.0|m731.3,738.0c731.4,737.7,731.9,737.5,732.3,737.5c732.7,737.5,733.2,737.3,733.3,737.0c733.5,736.7,733.8,736.5,734.0,736.5c734.3,736.5,734.6,736.3,734.7,736.0c734.9,735.7,735.2,735.5,735.4,735.5c735.9,735.5,736.6,734.5,736.6,733.8c736.6,733.5,736.9,732.8,737.3,732.2c737.8,731.5,738.0,730.9,738.0,730.2c738.0,729.6,738.1,728.9,738.3,728.7c738.5,728.3,738.6,722.9,738.6,704.0l738.6,679.8l737.6,678.5l736.6,677.2l729.1,677.0c724.9,676.8,712.3,676.7,700.9,676.7c689.6,676.7,677.0,676.8,672.8,677.0l665.2,677.2l664.3,678.5l663.3,679.8l663.3,706.6l663.3,733.4l664.7,735.5c665.4,736.6,666.2,737.5,666.4,737.5c666.6,737.5,666.9,737.7,667.0,737.9c667.4,738.4,670.7,738.5,701.7,738.4c724.8,738.4,731.0,738.3,731.3,738.0|m836.5,738.0c836.7,737.7,837.0,737.5,837.2,737.5c837.9,737.5,840.2,734.0,840.3,732.7c840.4,732.1,840.5,720.2,840.4,706.3l840.4,681.0l839.7,679.7c839.4,679.1,838.7,678.2,838.3,677.7l837.5,676.9l802.5,676.9l767.4,676.9l766.6,677.7c765.1,679.3,765.1,678.4,765.1,704.0c765.1,724.1,765.2,727.5,765.5,729.4c765.7,730.6,766.1,731.9,766.4,732.3c766.6,732.7,767.0,733.5,767.2,734.2c767.4,734.8,767.8,735.4,768.1,735.4c768.4,735.5,768.7,735.7,768.9,736.0c769.1,736.3,769.4,736.5,769.6,736.5c769.8,736.5,770.1,736.8,770.4,737.0c770.6,737.3,771.2,737.5,771.6,737.5c772.0,737.5,772.4,737.7,772.5,737.9c772.9,738.4,776.1,738.5,806.9,738.4c830.0,738.4,836.3,738.3,836.5,738.0|m911.6,738.0c911.8,737.7,912.1,737.5,912.4,737.5c912.7,737.5,913.1,737.3,913.2,737.0c913.4,736.7,913.7,736.5,913.9,736.5c914.4,736.5,915.1,735.5,915.1,734.8c915.1,734.4,915.2,734.1,915.3,733.9c915.5,733.8,915.6,733.3,915.6,732.8c915.6,732.3,915.7,731.5,915.9,731.2c916.3,730.4,916.4,728.2,916.0,727.6c915.8,727.3,915.7,724.2,915.7,715.2c915.7,706.3,915.8,703.1,916.0,702.8c916.2,702.5,916.3,699.6,916.3,691.5c916.3,682.2,916.2,680.5,915.9,680.2c915.7,679.9,915.6,679.5,915.6,679.1c915.6,678.8,915.2,678.1,914.8,677.7l914.0,676.9l881.2,676.8c851.2,676.7,848.2,676.7,847.4,676.1c846.6,675.6,846.5,675.6,845.8,676.2c845.4,676.5,845.0,676.7,844.8,676.7c844.5,676.7,843.0,678.8,843.0,679.3c843.0,679.6,842.9,680.2,842.7,680.7c842.2,682.2,842.2,731.6,842.7,732.6c842.9,733.0,843.0,733.5,843.0,733.8c843.0,734.4,845.2,737.5,845.6,737.5c845.8,737.5,846.1,737.7,846.2,737.9c846.6,738.4,849.9,738.5,881.5,738.4c905.0,738.4,911.4,738.3,911.6,738.0|m985.5,738.0c985.7,737.7,986.2,737.5,986.6,737.5c987.0,737.5,987.4,737.3,987.6,737.0c987.8,736.7,988.1,736.5,988.3,736.5c988.8,736.5,991.6,732.6,991.6,731.9c991.6,731.7,991.7,731.3,991.9,731.0c992.1,730.8,992.3,730.3,992.3,729.8c992.3,729.4,992.4,728.9,992.6,728.7c992.8,728.3,992.9,723.0,992.9,704.6c992.9,686.1,992.8,680.8,992.6,680.5c992.4,680.2,992.3,679.8,992.3,679.4c992.3,679.1,991.9,678.4,991.4,677.9l990.6,676.9l958.5,676.7c932.9,676.6,926.2,676.4,925.5,676.1c924.6,675.7,924.4,675.7,923.7,676.2c923.3,676.5,922.4,676.7,921.7,676.7c920.7,676.7,920.4,676.9,919.7,677.8c919.2,678.4,918.8,679.1,918.8,679.5c918.8,679.8,918.7,680.2,918.5,680.5c918.3,680.8,918.2,686.5,918.2,706.6c918.2,726.8,918.3,732.5,918.5,732.8c918.7,733.0,918.8,733.5,918.8,733.7c918.8,734.5,921.0,737.5,921.5,737.5c921.8,737.5,922.1,737.7,922.2,737.9c922.6,738.4,925.8,738.5,956.3,738.4c979.1,738.4,985.3,738.3,985.5,738.0|m79.4,672.6c80.4,671.2,80.5,671.0,80.5,669.0c80.5,667.8,80.6,666.7,80.8,666.5c81.0,666.2,81.1,662.7,81.1,651.5c81.1,640.3,81.0,636.8,80.8,636.5c80.3,635.9,80.4,631.1,80.8,630.2c81.1,629.7,81.2,628.4,81.2,624.3l81.2,619.0l79.8,616.9l78.4,614.7l43.4,614.7l8.5,614.7l7.7,615.7c7.3,616.3,7.0,617.0,7.0,617.3c7.0,617.6,6.9,618.1,6.7,618.3c6.5,618.6,6.4,624.3,6.4,644.5l6.4,670.2l7.5,671.7c8.0,672.6,8.7,673.3,8.9,673.3c9.1,673.3,9.4,673.5,9.5,673.6c9.8,674.1,15.3,674.2,48.2,674.2l78.3,674.2l79.4,672.6|m147.5,674.1l153.7,673.9l154.5,672.8c156.2,670.7,156.1,671.9,156.1,643.9l156.1,618.8l155.5,617.6c155.1,616.9,154.5,616.0,154.1,615.5l153.3,614.7l124.8,614.6c109.1,614.6,93.7,614.6,90.6,614.7l84.9,615.0l84.0,616.4l83.0,617.7l83.0,644.1l83.0,670.4l84.3,672.2l85.5,674.0l89.7,674.1c98.8,674.3,141.7,674.3,147.5,674.1|m230.9,673.7c231.1,673.5,231.4,673.3,231.7,673.3c232.6,673.3,233.4,671.6,233.5,669.6c233.6,668.5,233.8,667.5,233.9,667.3c234.1,667.1,234.2,659.2,234.2,643.7c234.2,618.4,234.2,620.5,232.9,616.3l232.4,614.7l202.4,614.6c186.0,614.6,169.8,614.6,166.6,614.8l160.6,615.0l159.7,616.4c159.2,617.1,158.8,617.9,158.8,618.2c158.8,618.4,158.7,619.1,158.5,619.6c158.0,621.1,158.0,667.8,158.5,669.3c158.7,669.9,158.8,670.6,158.8,670.9c158.8,671.6,159.3,672.3,159.7,672.3c159.9,672.3,160.4,672.7,160.8,673.1c161.5,673.9,161.7,674.0,165.7,674.1c168.1,674.2,183.6,674.2,200.3,674.2c224.2,674.2,230.7,674.1,230.9,673.7|m332.4,673.7c332.7,673.4,333.1,673.1,333.3,673.0c333.5,672.8,333.7,672.5,333.8,672.3c334.6,669.8,334.6,670.3,334.6,643.7l334.6,617.7l333.6,616.2l332.6,614.7l297.8,614.7l263.0,614.7l262.1,615.7c261.7,616.2,261.3,616.9,261.3,617.3c261.3,617.6,261.2,618.1,261.0,618.3c260.8,618.6,260.7,624.2,260.7,643.9c260.7,663.7,260.8,669.2,261.0,669.6c261.2,669.8,261.3,670.3,261.3,670.6c261.3,670.9,261.8,671.8,262.4,672.6l263.4,674.0l267.6,674.1c269.8,674.2,285.2,674.2,301.8,674.2c326.8,674.2,331.9,674.1,332.4,673.7|m407.3,673.7c407.4,673.5,407.7,673.3,407.9,673.3c408.1,673.3,408.6,672.8,409.1,672.2l409.8,671.1l409.8,644.7c409.8,618.6,409.8,618.2,409.3,617.1c408.6,615.4,407.5,614.6,406.1,614.6c405.4,614.6,404.7,614.3,404.2,614.0c403.6,613.4,403.4,613.4,402.5,613.9c401.7,614.3,396.2,614.4,370.5,614.5l339.5,614.7l338.6,615.8c338.1,616.4,337.6,617.1,337.5,617.3c337.5,617.6,337.2,618.3,337.0,619.0c336.6,620.0,336.6,622.4,336.6,644.6c336.6,665.5,336.7,669.1,337.0,669.7c337.2,670.0,337.3,670.6,337.3,670.9c337.3,671.3,337.7,672.1,338.3,672.8l339.3,674.0l343.4,674.1c345.6,674.2,360.9,674.2,377.2,674.2c400.7,674.2,407.1,674.1,407.3,673.7|m484.5,673.7c484.6,673.5,485.0,673.3,485.3,673.3c485.6,673.3,486.2,672.7,486.7,671.8l487.7,670.2l487.8,659.0c488.0,646.5,487.8,619.1,487.5,618.5c487.4,618.3,487.2,617.8,487.2,617.3c487.1,616.7,486.7,616.0,486.3,615.5l485.5,614.7l450.0,614.7l414.5,614.7l413.5,616.2l412.5,617.7l412.4,642.3c412.4,655.9,412.4,667.8,412.5,668.8c412.7,670.4,412.8,670.9,413.8,672.3l414.9,674.0l419.2,674.1c421.6,674.2,437.2,674.2,453.8,674.2c477.8,674.2,484.2,674.1,484.5,673.7|m583.7,673.7c583.8,673.5,584.1,673.3,584.3,673.3c584.9,673.3,586.2,671.2,586.2,670.2c586.2,669.7,586.4,669.0,586.5,668.7c587.0,667.7,587.0,661.4,586.6,660.0c586.1,658.6,586.1,640.8,586.6,638.8c587.0,636.8,587.0,626.3,586.6,625.4c586.3,624.9,586.2,623.7,586.2,621.2l586.2,617.8l585.1,616.3l584.1,614.7l548.9,614.7l513.8,614.7l513.0,615.5c512.6,616.0,512.2,616.8,512.1,617.4c512.0,617.9,511.9,618.4,511.8,618.5c511.7,618.6,511.6,630.2,511.6,644.5l511.6,670.3l512.8,672.1l514.1,674.0l518.3,674.1c520.6,674.2,536.2,674.2,552.9,674.2c576.9,674.2,583.4,674.1,583.7,673.7|m658.0,673.7c658.2,673.5,658.6,673.3,658.9,673.3c659.2,673.3,659.6,672.8,660.0,672.0l660.7,670.8l660.8,649.8c660.8,632.5,660.9,628.7,661.2,628.2c661.6,627.3,661.6,625.1,661.2,624.6c661.0,624.3,660.8,623.2,660.8,620.9l660.7,617.7l659.7,616.2c658.8,614.8,658.7,614.8,657.0,614.6c656.1,614.6,655.0,614.3,654.5,614.0c653.8,613.5,653.6,613.5,652.8,613.9c652.0,614.3,645.7,614.4,621.4,614.5c592.3,614.7,591.0,614.8,590.4,615.4c590.0,615.7,589.5,616.5,589.2,617.1c588.8,618.2,588.8,618.8,588.8,644.6l588.8,670.9l589.5,672.1c589.9,672.8,590.4,673.3,590.6,673.3c590.8,673.3,591.1,673.5,591.2,673.6c591.6,674.1,596.8,674.2,628.6,674.2c651.6,674.2,657.8,674.1,658.0,673.7|m737.2,672.2l738.6,670.2l738.6,644.5c738.6,624.3,738.5,618.6,738.3,618.3c738.1,618.1,738.0,617.6,738.0,617.3c738.0,616.9,737.6,616.2,737.2,615.7l736.3,614.7l706.7,614.6c690.4,614.6,674.4,614.6,671.2,614.7l665.3,615.0l664.3,616.3l663.3,617.6l663.3,643.9l663.3,670.3l664.6,672.1l666.0,674.0l670.2,674.1c672.6,674.2,688.3,674.2,705.2,674.2l735.9,674.2l737.2,672.2|m831.5,674.1l837.9,673.9l838.7,672.8c840.4,670.7,840.3,671.8,840.4,644.1l840.5,619.3l839.9,618.0c839.6,617.3,838.9,616.2,838.4,615.7l837.6,614.7l802.5,614.7l767.4,614.7l766.7,615.5c766.2,615.9,765.8,616.9,765.6,617.9c765.2,619.5,765.1,621.7,765.1,644.7l765.1,669.8l765.8,671.2c767.2,673.9,767.4,674.0,772.1,674.1c781.1,674.3,825.6,674.3,831.5,674.1|m913.3,673.7c913.4,673.5,913.7,673.3,913.9,673.3c914.4,673.3,915.6,671.6,915.6,670.9c915.6,670.6,915.7,670.1,915.9,669.9c916.2,669.5,916.3,666.2,916.3,644.5c916.3,622.7,916.2,619.4,915.9,619.0c915.7,618.8,915.6,618.3,915.6,618.0c915.6,617.6,915.1,616.8,914.6,616.2l913.7,615.0l908.0,614.7c904.9,614.6,889.3,614.6,873.4,614.6l844.5,614.7l843.8,615.7c843.4,616.3,843.0,617.0,843.0,617.3c843.0,617.6,842.9,618.1,842.7,618.5c842.4,619.1,842.3,622.7,842.3,644.5l842.3,669.8l843.0,671.2c844.4,673.9,844.6,674.0,849.2,674.1c851.4,674.2,866.7,674.2,883.1,674.2c906.7,674.2,913.0,674.1,913.3,673.7|m991.5,672.2l992.9,670.2l992.9,644.5c992.9,624.3,992.8,618.6,992.6,618.3c992.4,618.1,992.3,617.6,992.3,617.3c992.3,616.9,991.9,616.2,991.4,615.7l990.6,614.7l955.4,614.7l920.3,614.7l919.5,615.7c919.2,616.3,918.8,617.0,918.8,617.3c918.8,617.6,918.7,618.1,918.5,618.3c918.3,618.6,918.2,624.3,918.2,644.5l918.2,670.2l919.5,672.1l920.8,674.0l925.0,674.1c927.3,674.2,942.9,674.2,959.7,674.2l990.2,674.2l991.5,672.2|m79.4,610.4c80.1,609.5,80.5,608.7,80.5,608.3c80.5,607.8,80.6,607.3,80.8,607.1c81.0,606.7,81.1,601.7,81.1,585.1c81.2,573.2,81.1,562.1,81.0,560.3l80.9,557.1l79.6,555.2c78.9,554.2,78.2,553.4,77.9,553.4c77.7,553.4,77.4,553.2,77.2,553.0c77.0,552.6,70.2,552.6,44.8,552.6c19.4,552.6,12.6,552.6,12.4,553.0c12.2,553.2,11.7,553.4,11.3,553.4c10.7,553.4,10.2,553.9,8.8,555.9c7.6,557.5,7.0,558.6,7.0,559.1c7.0,559.5,6.9,560.0,6.7,560.2c6.3,560.9,6.3,607.5,6.7,608.1c6.9,608.3,7.0,608.8,7.0,609.2c7.0,609.6,7.4,610.3,7.8,610.9l8.5,611.8l43.4,611.8l78.2,611.8l79.4,610.4|m154.5,610.5c156.3,607.9,156.3,608.9,156.3,582.6c156.3,556.6,156.3,557.6,154.5,554.9c154.0,554.1,153.4,553.4,153.1,553.4c152.8,553.4,152.5,553.2,152.3,553.0c152.1,552.6,145.2,552.6,119.5,552.6c93.9,552.6,87.0,552.6,86.7,553.0c86.6,553.2,86.3,553.4,86.1,553.4c85.9,553.4,85.1,554.3,84.4,555.4l83.0,557.4l83.0,583.2l83.0,608.9l83.6,609.7c83.9,610.1,84.5,610.8,84.9,611.1c85.7,611.7,87.4,611.7,119.6,611.8l153.5,611.8l154.5,610.5|m232.4,610.4c233.0,609.6,233.5,608.7,233.5,608.3c233.5,607.9,233.6,607.1,233.8,606.5c234.3,605.1,234.3,588.1,233.8,587.0c233.5,586.3,233.5,586.1,233.8,585.5c234.1,585.0,234.1,582.9,234.1,573.7c234.1,566.7,234.1,562.4,233.9,562.1c233.8,562.0,233.6,561.0,233.5,560.1c233.4,558.6,233.2,558.1,231.7,555.9c230.4,553.9,229.9,553.4,229.4,553.4c229.0,553.4,228.5,553.2,228.3,553.0c228.1,552.6,221.2,552.6,195.2,552.6c169.2,552.6,162.3,552.6,162.1,553.0c161.9,553.2,161.6,553.4,161.3,553.4c160.7,553.4,158.8,556.1,158.8,556.9c158.8,557.2,158.7,557.9,158.5,558.4c158.2,559.3,158.1,562.7,158.1,582.8c158.1,602.8,158.2,606.3,158.5,607.1c158.7,607.7,158.8,608.3,158.8,608.5c158.8,608.8,159.3,609.6,159.9,610.4l160.9,611.8l196.1,611.8l231.4,611.8l232.4,610.4|m332.3,611.3c332.5,611.0,332.9,610.8,333.1,610.8c333.4,610.8,333.8,610.3,334.1,609.7l334.6,608.6l334.7,586.6c334.7,574.5,334.7,562.7,334.6,560.3l334.5,556.1l333.5,554.8c333.0,554.0,332.4,553.4,332.2,553.4c332.0,553.4,331.7,553.2,331.5,553.0c331.3,552.6,324.5,552.6,299.1,552.6c273.7,552.6,266.9,552.6,266.6,553.0c266.5,553.2,265.9,553.4,265.5,553.4c264.7,553.4,264.4,553.7,262.9,556.0c261.7,557.9,261.3,558.9,261.3,559.6c261.3,560.1,261.2,560.7,261.0,560.9c260.6,561.5,260.6,607.2,261.0,608.4c261.1,608.9,261.3,609.5,261.4,609.8c261.5,610.2,261.7,610.5,261.9,610.6c262.2,610.8,262.7,611.0,263.0,611.3c264.1,612.0,331.6,612.0,332.3,611.3|m408.8,610.3l409.8,608.8l409.8,582.7l409.8,556.7l408.9,555.0c408.3,554.0,407.7,553.4,407.4,553.4c407.1,553.4,406.7,553.2,406.6,553.0c406.4,552.6,399.4,552.6,373.5,552.6c347.5,552.6,340.5,552.6,340.3,553.0c340.2,553.2,339.9,553.4,339.7,553.4c339.2,553.4,337.3,556.2,337.3,556.9c337.3,557.2,337.2,557.6,337.0,557.9c336.7,558.3,336.6,561.4,336.6,582.4l336.6,606.5l337.2,608.3c337.6,609.4,338.2,610.5,338.7,611.0l339.5,611.8l373.7,611.8l407.8,611.8l408.8,610.3|m486.4,610.8c486.9,610.2,487.3,609.4,487.3,609.1c487.3,608.8,487.4,608.3,487.5,608.1c487.8,607.8,487.8,602.5,487.8,584.2c487.8,565.8,487.8,560.6,487.5,560.2c487.4,560.0,487.3,559.5,487.3,559.2c487.3,558.9,487.1,558.5,486.9,558.2c486.7,558.0,486.5,557.6,486.5,557.3c486.5,556.5,485.9,555.5,485.4,555.5c485.2,555.5,484.7,555.0,484.3,554.4c483.9,553.7,483.4,553.4,482.9,553.4c482.5,553.4,482.1,553.2,481.9,553.0c481.5,552.4,416.1,552.4,415.6,553.0c415.5,553.2,415.1,553.4,414.9,553.4c414.2,553.4,413.1,555.1,413.1,556.0c413.1,556.4,413.0,556.9,412.8,557.1c412.4,557.7,412.4,607.2,412.8,608.4c412.9,608.9,413.1,609.5,413.2,609.8c413.3,610.2,413.6,610.6,414.0,610.8c414.3,611.0,414.8,611.3,415.0,611.5c415.2,611.7,428.9,611.8,450.5,611.8l485.6,611.8l486.4,610.8|m585.2,610.4c585.7,609.6,586.2,608.7,586.2,608.4c586.2,608.0,586.4,607.6,586.5,607.4c587.0,606.8,587.0,601.9,586.6,601.2c586.2,600.6,586.1,576.7,586.5,574.4c586.6,573.5,586.8,569.9,586.8,565.9c586.9,560.0,586.9,558.8,586.6,558.1c586.4,557.7,586.2,557.1,586.2,556.8c586.2,556.1,584.3,553.4,583.7,553.4c583.5,553.4,583.1,553.2,583.0,553.0c582.7,552.6,575.8,552.6,549.8,552.6c523.9,552.6,516.9,552.6,516.7,553.0c516.5,553.2,516.2,553.4,516.0,553.4c515.8,553.4,515.5,553.6,515.3,553.9c515.2,554.2,514.9,554.4,514.7,554.4c514.2,554.4,512.7,556.5,512.7,557.2c512.7,557.5,512.6,557.9,512.5,558.1c511.6,559.4,511.6,560.6,511.6,584.6c511.6,599.8,511.7,608.1,511.8,608.2c511.9,608.3,512.0,608.7,512.0,609.1c512.0,609.4,512.4,610.2,512.9,610.8l513.7,611.8l548.9,611.8l584.1,611.8l585.2,610.4|m658.3,611.3c658.6,611.0,659.0,610.8,659.2,610.8c659.4,610.8,659.9,610.3,660.2,609.7l660.7,608.6l660.7,582.6l660.7,556.6l659.8,555.2c659.4,554.3,658.7,553.4,658.4,553.1c657.9,552.6,655.0,552.6,625.1,552.6c599.2,552.6,592.2,552.6,592.0,553.0c591.9,553.2,591.5,553.4,591.2,553.4c590.9,553.4,590.3,554.0,589.7,555.0l588.8,556.7l588.8,582.8l588.8,608.8l589.8,610.3l590.9,611.8l624.4,611.8c653.5,611.8,658.0,611.7,658.3,611.3|m737.0,611.1c737.4,610.7,737.9,610.2,737.9,609.8c738.0,609.5,738.2,608.9,738.3,608.4c738.7,607.2,738.7,560.5,738.3,559.9c738.1,559.7,738.0,559.1,738.0,558.6c738.0,557.9,737.6,557.0,736.7,555.5c735.6,553.7,735.3,553.4,734.5,553.4c734.1,553.4,733.5,553.2,733.4,553.0c733.1,552.6,726.1,552.6,699.9,552.6c673.6,552.6,666.6,552.6,666.4,553.0c666.2,553.2,665.9,553.4,665.8,553.4c665.3,553.4,663.9,555.5,663.9,556.2c663.9,556.5,663.7,556.9,663.6,557.1c663.3,557.5,663.3,563.1,663.3,582.7c663.3,607.6,663.3,607.9,663.8,609.1c664.0,609.8,664.7,610.6,665.3,611.0l666.3,611.8l701.3,611.8c735.9,611.8,736.3,611.8,737.0,611.1|m839.0,609.9l840.4,608.1l840.3,582.9c840.3,560.8,840.3,557.6,840.0,556.4c839.5,554.7,838.6,553.4,838.0,553.4c837.7,553.4,837.4,553.2,837.2,553.0c837.0,552.6,830.1,552.6,804.1,552.6c778.1,552.6,771.2,552.6,771.0,553.0c770.8,553.2,770.3,553.4,769.9,553.4c769.5,553.4,769.0,553.6,768.9,553.9c768.7,554.2,768.4,554.4,768.2,554.4c767.6,554.4,766.7,556.1,765.9,558.4l765.3,560.5l765.2,583.7c765.1,605.4,765.2,607.1,765.6,608.6c765.9,610.0,766.2,610.4,767.0,611.0l768.1,611.8l802.9,611.8l837.7,611.8l839.0,609.9|m914.1,611.1c914.5,610.7,915.2,609.8,915.5,609.1l916.3,607.8l916.3,582.7c916.3,558.5,916.2,557.6,915.8,556.4c915.2,554.7,914.4,553.4,913.9,553.4c913.7,553.4,913.4,553.2,913.3,553.0c913.0,552.6,905.9,552.6,879.4,552.6c852.9,552.6,845.8,552.6,845.6,553.0c845.4,553.2,845.1,553.4,844.8,553.4c844.2,553.4,843.0,555.1,843.0,555.9c843.0,556.3,842.9,556.9,842.7,557.3c842.4,558.0,842.3,561.2,842.4,583.1l842.5,608.1l843.8,609.9l845.1,611.8l879.2,611.8c913.2,611.8,913.3,611.8,914.1,611.1|m991.5,610.9c992.0,610.4,992.3,609.8,992.3,609.3c992.3,608.9,992.4,608.3,992.6,608.1c992.8,607.8,992.9,602.5,992.9,584.2c992.9,565.8,992.8,560.6,992.6,560.2c992.4,560.0,992.3,559.5,992.3,559.1c992.3,558.7,991.6,557.4,990.6,555.9c989.1,553.8,988.8,553.4,988.1,553.4c987.6,553.4,987.1,553.2,986.9,553.0c986.7,552.7,980.3,552.5,956.7,552.4c940.2,552.4,925.5,552.4,924.0,552.6l921.3,552.8l919.9,554.9l918.4,557.0l918.3,562.0c918.1,568.5,918.1,596.8,918.3,603.2l918.4,608.2l919.7,610.0l921.0,611.8l955.8,611.8l990.7,611.8l991.5,610.9|m57.8,531.1l57.8,517.7l63.6,517.7c68.5,517.7,69.5,517.8,69.7,518.2c69.9,518.5,70.3,518.7,70.8,518.7c71.2,518.7,71.7,519.0,71.8,519.2c72.0,519.5,72.2,519.8,72.4,519.8c72.5,519.8,73.3,520.5,74.0,521.5l75.3,523.2l75.3,525.7c75.3,528.1,75.0,529.8,74.2,531.3c73.8,531.9,72.0,533.2,71.4,533.2c70.7,533.2,69.9,534.1,69.9,535.0c69.9,535.5,70.6,536.7,71.9,538.6c73.0,540.2,73.9,541.7,73.9,542.0c73.9,542.2,74.2,542.8,74.5,543.4c75.1,544.4,75.1,544.5,74.7,544.5c74.2,544.5,71.6,540.8,71.6,540.0c71.6,539.7,70.8,538.3,69.8,536.9l68.1,534.4l63.6,534.2c57.9,534.1,58.2,533.7,58.2,539.9c58.2,542.7,58.2,544.5,58.0,544.5c57.9,544.5,57.8,539.8,57.8,531.1|m109.9,544.0c109.9,543.8,110.2,543.2,110.5,542.8c110.8,542.3,111.1,541.7,111.1,541.4c111.1,541.1,111.3,540.6,111.5,540.4c111.7,540.1,111.8,539.7,111.8,539.4c111.8,539.0,112.1,538.3,112.5,537.8c112.9,537.2,113.2,536.5,113.2,536.2c113.2,535.9,113.5,535.2,113.9,534.7c114.3,534.2,114.6,533.4,114.6,533.1c114.6,532.8,114.8,532.4,115.0,532.1c115.2,531.9,115.3,531.4,115.3,531.1c115.3,530.8,115.5,530.3,115.7,530.1c115.9,529.8,116.0,529.4,116.0,529.1c116.0,528.7,116.3,528.0,116.7,527.5c117.1,526.9,117.4,526.2,117.4,525.9c117.4,525.6,117.7,524.9,118.1,524.4c118.5,523.8,118.8,523.1,118.8,522.8c118.8,522.5,119.1,521.9,119.4,521.5c119.7,521.0,120.0,520.4,120.0,520.1c120.0,519.8,120.2,519.3,120.4,519.1c120.5,518.8,120.7,518.4,120.7,518.2c120.7,517.6,121.9,517.5,122.3,518.1c122.4,518.3,122.6,518.8,122.6,519.1c122.6,519.4,122.9,520.1,123.3,520.6c123.7,521.2,124.0,521.9,124.0,522.2c124.0,522.5,124.1,523.0,124.3,523.2c124.5,523.4,124.7,523.9,124.7,524.2c124.7,524.5,125.0,525.2,125.4,525.8c125.8,526.3,126.1,527.0,126.1,527.3c126.1,527.6,126.3,528.2,126.5,528.5c126.8,528.9,127.3,530.0,127.6,531.0c127.9,531.9,128.3,532.9,128.4,533.0c128.5,533.1,128.7,533.4,128.7,533.7c128.7,534.0,129.0,534.8,129.4,535.6c129.7,536.3,130.1,537.0,130.1,537.2c130.1,537.4,130.2,537.7,130.4,538.0c130.6,538.2,130.8,538.6,130.8,538.9c130.8,539.2,131.1,540.0,131.5,540.7c131.8,541.4,132.2,542.2,132.2,542.3c132.2,542.5,132.3,542.9,132.5,543.1c133.1,543.8,132.9,544.5,132.3,544.5c132.0,544.5,131.7,544.3,131.7,544.1c131.7,543.9,131.4,543.1,131.0,542.4c130.6,541.7,130.3,540.9,130.3,540.6c130.3,540.3,130.1,539.9,129.9,539.7c129.7,539.4,129.6,539.1,129.6,538.8c129.6,538.6,129.3,538.0,128.9,537.4l128.2,536.4l121.3,536.3c114.0,536.2,113.7,536.2,113.7,537.8c113.7,538.2,113.4,539.0,113.0,539.5c112.6,540.0,112.3,540.7,112.3,541.1c112.3,541.4,112.0,542.1,111.6,542.6c111.2,543.1,110.9,543.8,110.9,544.0c110.9,544.3,110.7,544.5,110.4,544.5c110.2,544.5,109.9,544.3,109.9,544.0|m176.1,531.1c176.1,523.6,176.2,517.7,176.3,517.7c176.5,517.7,176.7,517.9,176.9,518.3c177.1,518.7,177.2,521.2,177.2,531.1c177.2,541.0,177.1,543.5,176.9,543.9c176.7,544.2,176.5,544.5,176.3,544.5c176.2,544.5,176.1,538.5,176.1,531.1|m311.3,531.1l311.3,517.7l317.2,517.7c322.1,517.7,323.0,517.8,323.3,518.2c323.4,518.5,323.9,518.7,324.3,518.7c324.7,518.7,325.2,519.0,325.4,519.2c325.5,519.5,325.8,519.8,326.1,519.8c326.3,519.8,326.6,519.9,326.7,520.1c326.9,520.3,327.2,520.7,327.5,520.9c328.8,521.9,329.5,526.1,328.8,528.5c328.2,530.6,328.1,530.9,327.7,531.1c326.3,532.2,324.7,533.1,324.1,533.3c323.6,533.4,323.2,533.8,323.0,534.1c322.8,534.5,323.1,535.1,324.9,537.7c326.1,539.5,327.0,541.1,327.0,541.4c327.0,541.7,327.4,542.5,327.9,543.2c328.6,544.3,328.7,544.5,328.3,544.5c327.7,544.5,324.4,539.7,324.4,538.9c324.4,538.6,323.9,537.5,323.1,536.5c321.6,534.2,321.5,534.2,316.4,534.2c311.6,534.2,311.8,533.8,311.8,540.0c311.8,542.7,311.7,544.5,311.6,544.5c311.4,544.5,311.3,539.8,311.3,531.1|m364.9,543.7c365.2,543.3,365.4,542.7,365.4,542.4c365.4,542.1,365.5,541.6,365.7,541.4c365.9,541.2,366.1,540.7,366.1,540.4c366.1,540.0,366.2,539.6,366.4,539.3c366.6,539.1,366.8,538.6,366.8,538.3c366.8,538.0,367.1,537.3,367.5,536.8c367.9,536.2,368.2,535.5,368.2,535.2c368.2,534.9,368.5,534.2,368.9,533.7c369.3,533.1,369.6,532.4,369.6,532.1c369.6,531.8,369.7,531.3,369.9,531.1c370.1,530.9,370.3,530.4,370.3,530.1c370.3,529.8,370.6,529.1,371.0,528.5c371.4,528.0,371.7,527.3,371.7,527.0c371.7,526.7,372.0,526.0,372.3,525.6c372.6,525.1,372.9,524.5,372.9,524.2c372.9,523.9,373.0,523.4,373.2,523.2c373.4,523.0,373.6,522.5,373.6,522.2c373.6,521.9,373.9,521.2,374.3,520.6c374.7,520.1,375.0,519.4,375.0,519.2c375.0,518.6,375.8,517.7,376.3,517.7c376.6,517.7,376.8,517.9,376.8,518.2c376.8,518.4,377.0,518.8,377.2,519.1c377.4,519.3,377.5,519.8,377.5,520.1c377.5,520.4,377.9,521.1,378.2,521.6c378.6,522.2,378.9,522.8,378.9,523.0c378.9,523.6,379.8,525.9,380.3,526.8c380.5,527.2,381.0,528.3,381.3,529.2c381.6,530.1,382.0,531.2,382.2,531.6c383.0,532.8,384.3,535.9,384.3,536.4c384.3,536.6,384.5,537.0,384.7,537.3c384.9,537.5,385.0,538.0,385.0,538.3c385.0,538.6,385.3,539.2,385.6,539.7c386.0,540.2,386.3,540.8,386.5,541.2c386.6,541.6,386.8,542.1,386.9,542.4c387.6,544.3,387.6,544.5,387.2,544.5c386.7,544.5,386.0,543.5,386.0,543.0c386.0,542.8,385.7,542.1,385.3,541.4c385.0,540.8,384.5,539.6,384.2,538.8c384.0,538.1,383.7,537.2,383.6,536.9c383.5,536.5,382.4,536.4,376.4,536.4l369.4,536.4l368.3,537.9c367.7,538.8,367.3,539.7,367.3,540.1c367.3,540.4,367.1,540.8,366.9,541.1c366.7,541.3,366.5,541.7,366.5,542.0c366.5,542.8,365.4,544.5,364.8,544.5c364.4,544.5,364.4,544.5,364.9,543.7|m431.1,531.1c431.1,522.4,431.2,517.7,431.3,517.7c431.5,517.7,431.6,522.4,431.6,531.1c431.6,539.8,431.5,544.5,431.3,544.5c431.2,544.5,431.1,539.8,431.1,531.1|m559.6,531.7c559.6,521.4,559.7,518.7,560.0,518.3c560.3,517.8,561.0,517.7,566.1,517.7c570.9,517.7,571.9,517.8,572.2,518.2c572.3,518.5,572.8,518.7,573.2,518.7c573.6,518.7,574.1,519.0,574.3,519.2c574.4,519.5,574.7,519.8,574.8,519.8c575.2,519.8,577.1,522.6,577.1,523.1c577.1,523.3,577.2,523.6,577.4,523.9c577.6,524.1,577.8,524.9,577.8,525.9c577.8,527.0,577.6,527.7,577.4,528.0c577.2,528.2,577.1,528.7,577.1,529.0c577.1,530.3,574.4,533.2,573.2,533.2c572.9,533.2,572.4,533.4,572.1,533.8l571.6,534.5l572.7,536.1c573.3,537.1,573.8,538.0,573.8,538.3c573.8,538.6,574.5,539.9,575.4,541.2c576.3,542.5,577.1,543.8,577.1,544.0c577.1,544.3,576.8,544.5,576.5,544.5c576.1,544.5,575.9,544.3,575.9,543.9c575.9,543.5,574.5,541.3,572.9,538.8l569.8,534.4l565.6,534.2c562.5,534.1,561.3,534.2,561.0,534.5c560.8,534.9,560.7,535.9,560.7,539.7l560.7,544.5l560.1,544.5l559.5,544.5l559.6,531.7|m614.3,543.5c614.7,543.0,615.0,542.3,615.0,542.0c615.0,541.7,615.1,541.3,615.3,541.1c615.5,540.8,615.7,540.5,615.7,540.3c615.7,540.1,615.9,539.5,616.2,538.9c616.5,538.3,617.1,536.9,617.4,535.8c617.8,534.7,618.1,533.8,618.3,533.6c618.6,533.3,619.6,530.8,619.6,530.3c619.6,530.0,620.0,529.4,620.4,528.9c620.7,528.3,621.1,527.6,621.1,527.3c621.1,527.0,621.2,526.5,621.4,526.3c621.6,526.0,621.8,525.6,621.8,525.3c621.8,525.0,622.1,524.2,622.5,523.7c622.8,523.2,623.2,522.5,623.2,522.2c623.2,521.9,623.5,521.2,623.9,520.6c624.2,520.1,624.6,519.4,624.6,519.1c624.6,518.2,625.0,517.7,625.8,517.7c626.3,517.7,626.4,517.9,626.4,518.3c626.4,518.7,626.7,519.3,627.0,519.8c627.6,520.6,628.3,522.3,628.3,522.9c628.3,523.1,628.6,523.8,629.0,524.6c629.4,525.3,629.7,526.0,629.7,526.1c629.7,526.2,630.0,526.9,630.4,527.7c630.8,528.4,631.1,529.1,631.1,529.3c631.1,529.5,631.3,529.8,631.5,530.1c631.7,530.3,631.8,530.8,631.8,531.1c631.8,531.4,632.0,531.9,632.2,532.1c632.4,532.4,632.5,532.8,632.5,533.1c632.5,533.4,632.8,534.2,633.2,534.7c633.6,535.2,633.9,535.9,633.9,536.2c633.9,536.5,634.2,537.2,634.6,537.8c635.0,538.3,635.3,539.0,635.3,539.4c635.3,539.7,635.5,540.1,635.7,540.4c635.9,540.6,636.0,541.1,636.0,541.4c636.0,541.7,636.3,542.3,636.6,542.8c636.9,543.2,637.2,543.8,637.2,544.1c637.2,544.7,636.0,544.5,635.8,543.7c635.6,543.4,635.5,542.8,635.3,542.5c635.2,542.2,634.9,541.4,634.8,540.9c634.6,540.3,634.2,539.6,634.0,539.2c633.7,538.8,633.5,538.2,633.5,537.8c633.5,536.2,633.2,536.2,625.8,536.3l618.9,536.4l618.2,537.7c616.6,540.3,616.1,541.3,616.1,541.8c616.1,542.5,614.7,544.5,614.2,544.5c613.8,544.5,613.8,544.4,614.3,543.5|m681.2,539.9c681.2,536.8,681.1,535.2,680.9,534.9c680.7,534.6,680.7,534.4,680.9,534.1c681.1,533.8,681.2,531.5,681.2,525.7c681.2,520.6,681.3,517.7,681.4,517.7c681.6,517.7,681.6,522.4,681.6,531.1c681.6,539.8,681.6,544.5,681.4,544.5c681.3,544.5,681.2,542.7,681.2,539.9|m813.8,531.1l813.8,517.7l819.6,517.7c824.5,517.7,825.5,517.8,825.7,518.2c825.9,518.5,826.4,518.7,826.8,518.7c827.2,518.7,827.7,519.0,827.8,519.2c828.0,519.5,828.4,519.8,828.8,519.8c829.4,519.8,830.6,521.3,830.6,522.0c830.6,522.3,830.8,522.6,831.0,522.8c831.3,523.2,831.3,524.0,831.3,525.9c831.3,527.9,831.3,528.7,831.0,529.0c830.8,529.3,830.6,529.7,830.6,530.0c830.6,531.1,828.6,533.2,827.5,533.2c826.8,533.2,826.0,534.1,826.0,535.0c826.0,535.5,826.7,536.7,828.0,538.6c829.0,540.2,829.9,541.7,829.9,542.0c829.9,542.2,830.2,542.8,830.5,543.4c831.1,544.4,831.1,544.5,830.7,544.5c830.2,544.5,827.6,540.8,827.6,540.0c827.6,539.7,826.8,538.3,825.8,536.9l824.1,534.4l819.7,534.4c815.6,534.4,815.2,534.4,814.8,535.0c814.3,535.6,814.3,535.7,814.6,536.2c814.9,536.7,815.0,537.6,815.0,540.1c815.0,542.8,814.9,543.4,814.5,543.9c814.3,544.2,814.0,544.5,814.0,544.5c813.9,544.5,813.8,538.5,813.8,531.1|m868.6,543.5c869.0,543.0,869.2,542.3,869.2,542.0c869.2,541.7,869.4,541.3,869.6,541.1c869.8,540.8,869.9,540.4,869.9,540.0c869.9,539.7,870.3,539.0,870.6,538.5c871.0,537.9,871.3,537.2,871.3,536.9c871.3,536.6,871.5,536.1,871.7,535.9c871.9,535.7,872.0,535.2,872.0,534.9c872.0,534.6,872.4,533.9,872.7,533.3c873.1,532.8,873.5,532.2,873.5,531.9c873.5,531.2,874.1,529.5,874.7,528.7c875.1,528.2,875.3,527.6,875.3,527.3c875.3,527.0,875.6,526.3,876.0,525.8c876.4,525.2,876.7,524.5,876.7,524.2c876.7,523.9,876.9,523.4,877.1,523.2c877.3,523.0,877.4,522.5,877.4,522.2c877.4,521.9,877.7,521.2,878.1,520.6c878.5,520.1,878.8,519.4,878.8,519.1c878.8,517.5,880.4,517.2,880.9,518.6c881.0,519.1,881.2,519.7,881.2,519.9c881.2,520.0,881.5,520.8,881.9,521.5c882.3,522.2,882.6,522.9,882.6,523.1c882.6,523.3,882.9,523.8,883.3,524.4c883.7,524.9,884.0,525.6,884.0,526.0c884.0,526.3,884.1,526.7,884.3,527.0c884.5,527.2,884.7,527.7,884.7,528.0c884.7,528.3,885.0,529.0,885.4,529.5c885.8,530.1,886.1,530.8,886.1,531.1c886.1,531.4,886.2,531.9,886.4,532.1c886.6,532.4,886.8,532.8,886.8,533.1c886.8,533.4,887.1,534.2,887.5,534.7c887.9,535.2,888.2,535.9,888.2,536.2c888.2,536.5,888.5,537.2,888.9,537.8c889.3,538.3,889.6,539.0,889.6,539.4c889.6,539.7,889.7,540.1,889.8,540.2c890.0,540.3,890.1,540.7,890.1,541.0c890.1,541.3,890.4,542.1,890.8,542.6c891.6,543.8,891.7,544.5,890.9,544.5c890.3,544.5,889.8,543.9,889.8,543.1c889.8,542.8,889.7,542.3,889.5,542.1c889.3,541.8,889.1,541.4,889.1,541.1c889.1,540.8,888.8,540.0,888.4,539.5c888.0,539.0,887.7,538.2,887.7,537.8c887.7,536.3,887.5,536.2,880.9,536.2c877.5,536.2,874.3,536.3,873.9,536.5c872.9,536.7,871.1,538.7,871.1,539.7c871.1,540.0,871.0,540.5,870.8,540.7c870.6,540.9,870.4,541.4,870.4,541.7c870.4,542.5,869.0,544.5,868.4,544.5c868.0,544.5,868.1,544.4,868.6,543.5|m935.7,531.1c935.7,517.9,935.7,517.7,936.1,517.7c936.6,517.7,936.6,517.9,936.6,531.1c936.6,544.3,936.6,544.5,936.1,544.5c935.7,544.5,935.7,544.3,935.7,531.1|m127.2,535.1c127.5,534.6,127.6,533.3,127.3,533.0c127.1,532.9,127.0,532.5,127.0,532.2c127.0,531.8,126.7,531.1,126.3,530.6c125.9,530.0,125.6,529.3,125.6,529.0c125.6,528.7,125.5,528.2,125.3,528.0c125.1,527.8,124.9,527.3,124.9,527.0c124.9,526.7,124.6,526.0,124.2,525.4c123.8,524.9,123.5,524.2,123.5,523.9c123.5,523.5,123.4,523.1,123.2,522.8c123.0,522.6,122.8,522.2,122.8,521.8c122.8,521.1,122.3,520.4,121.8,520.4c121.3,520.4,119.8,522.4,119.8,523.0c119.8,523.3,119.6,523.6,119.4,523.9c119.2,524.1,119.1,524.6,119.1,524.9c119.1,525.2,118.8,525.8,118.5,526.3c118.2,526.7,117.9,527.3,117.9,527.6c117.9,528.0,117.6,528.7,117.2,529.2c116.8,529.7,116.5,530.4,116.5,530.8c116.5,531.1,116.3,531.5,116.1,531.8c115.9,532.0,115.8,532.4,115.8,532.7c115.8,533.0,115.6,533.5,115.4,533.9c115.1,534.4,115.1,534.6,115.3,535.0c115.6,535.5,116.5,535.6,121.3,535.6c125.4,535.6,127.0,535.4,127.2,535.1|m382.2,535.1c382.5,534.6,381.9,532.6,381.1,531.3c380.6,530.5,379.9,528.4,379.9,527.8c379.9,527.6,379.6,527.0,379.2,526.5c378.8,525.9,378.5,525.2,378.5,524.9c378.5,524.6,378.3,524.1,378.1,523.9c377.9,523.6,377.8,523.2,377.8,522.9c377.8,522.3,376.6,520.4,376.2,520.4c375.9,520.4,374.0,523.4,374.0,523.9c374.0,524.1,373.7,524.8,373.3,525.5c372.9,526.1,372.6,526.8,372.6,527.1c372.6,527.3,372.4,527.8,372.1,528.2c371.6,528.9,370.8,531.3,370.8,532.0c370.8,532.2,370.6,532.6,370.4,532.8c370.0,533.3,370.0,534.6,370.3,535.1c370.8,535.8,381.8,535.7,382.2,535.1|m631.8,535.1c632.2,534.4,632.1,533.3,631.3,532.3c631.0,531.7,630.6,531.1,630.6,530.7c630.6,530.4,630.3,529.7,629.9,529.2c629.6,528.7,629.2,528.0,629.2,527.7c629.2,527.4,628.8,526.3,628.3,525.2c627.8,524.1,627.4,523.1,627.4,522.9c627.4,522.8,627.0,522.1,626.6,521.5l625.7,520.3l625.0,521.3c624.6,521.8,624.3,522.5,624.3,522.8c624.3,523.2,624.0,523.8,623.6,524.4c623.2,524.9,622.9,525.5,622.9,525.7c622.9,525.9,622.6,526.6,622.2,527.3c621.8,528.0,621.5,528.7,621.5,528.9c621.5,529.0,621.2,529.7,620.8,530.4c620.4,531.1,620.1,531.9,620.1,532.1c620.1,532.2,619.9,532.9,619.7,533.4c619.4,534.3,619.4,534.5,619.6,535.0c619.9,535.5,620.7,535.6,625.7,535.6c629.9,535.6,631.6,535.4,631.8,535.1|m886.1,535.0c886.3,534.6,886.3,534.4,886.0,533.9c885.8,533.5,885.6,533.0,885.6,532.7c885.6,532.4,885.5,532.0,885.3,531.8c885.1,531.5,884.9,531.1,884.9,530.8c884.9,530.4,884.6,529.7,884.2,529.2c883.8,528.7,883.5,528.0,883.5,527.6c883.5,527.3,883.2,526.7,882.9,526.3c882.3,525.5,881.6,523.7,881.6,523.1c881.6,522.6,880.4,520.4,880.1,520.4c879.7,520.4,877.9,523.3,877.9,523.9c877.9,524.2,877.6,524.9,877.2,525.4c876.8,526.0,876.5,526.7,876.5,527.0c876.5,527.3,876.3,527.8,876.1,528.0c875.9,528.2,875.8,528.6,875.8,528.8c875.8,528.9,875.5,529.7,875.1,530.4c874.7,531.1,874.4,531.9,874.4,532.2c874.4,532.5,874.2,532.9,874.0,533.2c873.6,533.7,873.6,534.6,874.0,535.1c874.2,535.4,875.8,535.6,880.0,535.6c884.9,535.6,885.8,535.5,886.1,535.0|m68.4,533.2c68.5,533.0,69.0,532.8,69.4,532.8c69.9,532.8,70.6,532.6,71.0,532.3c71.3,532.0,71.8,531.8,71.9,531.8c72.1,531.8,72.6,531.1,73.2,530.3l74.2,528.8l74.2,526.2c74.2,523.6,74.1,523.4,73.3,522.0c72.8,521.1,72.2,520.4,72.0,520.4c71.8,520.4,71.5,520.2,71.3,519.9c71.2,519.6,70.6,519.4,69.9,519.4c69.2,519.4,68.7,519.2,68.5,518.9c68.3,518.5,67.6,518.4,65.0,518.4c62.5,518.4,61.8,518.5,61.5,518.9c61.4,519.2,60.8,519.4,60.4,519.4c59.9,519.4,59.4,519.6,59.2,519.8c59.0,520.1,58.9,522.1,58.9,526.5c58.9,530.8,59.0,532.8,59.2,533.1c59.6,533.6,68.2,533.7,68.4,533.2|m319.9,533.2c320.0,533.0,321.1,532.8,322.3,532.7c323.5,532.7,324.6,532.4,324.7,532.2c324.9,532.0,325.2,531.8,325.4,531.8c326.3,531.8,328.0,527.7,328.0,525.4c328.0,524.7,327.7,523.6,327.5,523.1c327.0,522.0,325.8,520.4,325.4,520.4c325.3,520.4,325.1,520.2,324.9,519.9c324.8,519.6,324.3,519.4,323.9,519.4c323.4,519.4,323.0,519.2,322.8,518.9c322.6,518.5,321.7,518.4,317.9,518.4l313.3,518.4l312.6,519.4l311.9,520.5l311.9,525.9l311.9,531.4l312.6,532.4l313.3,533.5l316.5,533.5c318.2,533.5,319.8,533.4,319.9,533.2|m569.5,533.2c569.5,533.0,570.4,532.8,571.5,532.7c573.1,532.6,573.4,532.5,574.0,531.7c574.4,531.2,574.8,530.7,575.0,530.7c575.5,530.7,575.9,530.1,575.9,529.3c575.9,529.0,576.1,528.6,576.3,528.3c576.5,528.1,576.6,527.3,576.6,526.1c576.6,524.9,576.5,524.2,576.3,523.9c576.1,523.6,575.9,523.2,575.9,522.9c575.9,522.2,574.7,520.4,574.3,520.4c574.0,520.4,573.7,520.2,573.6,519.9c573.4,519.6,572.9,519.4,572.2,519.4c571.5,519.4,570.9,519.2,570.8,518.9c570.5,518.5,569.7,518.4,566.4,518.4l562.2,518.4l561.5,519.5l560.7,520.6l560.7,526.3c560.7,530.3,560.8,532.1,561.0,532.4c561.2,532.7,562.2,532.8,564.1,532.8c565.8,532.8,567.1,533.0,567.1,533.2c567.3,533.6,569.3,533.6,569.5,533.2|m823.7,533.2c823.8,533.0,824.4,532.8,825.1,532.8c825.8,532.8,826.6,532.6,827.0,532.3c827.4,532.0,827.8,531.8,827.9,531.8c828.1,531.8,828.6,531.1,829.2,530.3l830.2,528.8l830.2,526.1l830.2,523.4l829.2,521.9c828.6,521.1,828.1,520.4,827.9,520.4c827.8,520.4,827.5,520.2,827.4,519.9c827.2,519.6,826.7,519.4,826.2,519.4c825.7,519.4,825.2,519.2,825.0,518.9c824.8,518.5,823.9,518.4,820.1,518.4c816.9,518.4,815.5,518.5,815.3,518.8c815.1,519.1,815.0,521.2,815.0,525.9c815.0,530.7,815.1,532.8,815.3,533.1c815.6,533.6,823.5,533.7,823.7,533.2|m32.4,493.9c21.8,493.8,12.7,493.6,12.0,493.5c11.3,493.3,10.7,493.0,10.5,492.8c10.4,492.5,10.1,492.3,9.8,492.3c9.6,492.3,9.3,492.0,9.1,491.8c9.0,491.5,8.7,491.2,8.4,491.2c7.6,491.2,1.9,481.9,1.9,480.4c1.9,480.2,1.7,479.8,1.5,479.6c1.3,479.3,1.2,478.6,1.2,477.7c1.2,476.9,1.0,476.1,0.9,475.8c0.4,475.2,0.4,273.7,0.9,273.1c1.0,272.8,1.2,272.1,1.2,271.5c1.2,270.9,1.3,270.2,1.5,270.0c1.7,269.8,1.9,269.3,1.9,269.0c1.9,268.6,2.0,268.2,2.2,267.9c2.4,267.7,2.6,267.3,2.6,267.0c2.6,266.2,3.7,264.0,5.4,261.3c6.4,259.9,7.3,258.7,7.5,258.7c7.7,258.7,8.2,258.2,8.5,257.6c9.0,256.9,9.4,256.6,10.0,256.6c10.4,256.6,10.8,256.4,11.0,256.1c11.2,255.8,11.6,255.6,12.0,255.6c12.4,255.6,12.9,255.4,13.1,255.2c13.3,254.8,35.0,254.7,120.2,254.7c205.4,254.7,227.2,254.8,227.4,255.2c227.6,255.4,228.0,255.6,228.4,255.6c228.8,255.6,229.3,255.8,229.5,256.1c229.6,256.4,229.9,256.6,230.2,256.6c230.4,256.6,230.7,256.8,230.9,257.1c231.0,257.4,231.3,257.6,231.6,257.6c231.8,257.6,232.3,258.1,232.6,258.7c233.0,259.2,233.5,259.7,233.7,259.7c234.2,259.7,236.7,263.5,236.7,264.2c236.7,264.5,237.0,265.2,237.4,265.7c237.8,266.3,238.1,266.9,238.1,267.2c238.1,267.5,238.3,268.1,238.5,268.4c238.7,268.8,238.8,269.5,238.8,269.9c238.8,270.3,239.0,271.1,239.2,271.6c239.4,272.1,239.5,273.1,239.5,273.6c239.5,274.2,239.7,274.9,239.8,275.1c240.1,275.5,240.1,295.8,240.1,374.8c240.1,453.7,240.1,474.1,239.8,474.5c239.7,474.7,239.5,475.4,239.5,476.1c239.5,476.8,239.4,477.8,239.2,478.3c239.0,478.9,238.8,479.5,238.8,479.7c238.8,480.0,238.7,480.4,238.5,480.6c238.3,480.8,238.1,481.3,238.1,481.6c238.1,482.0,238.0,482.4,237.8,482.7c237.6,482.9,237.4,483.3,237.4,483.6c237.4,484.4,233.5,490.2,233.0,490.2c232.7,490.2,232.4,490.4,232.3,490.7c232.1,491.0,231.8,491.2,231.6,491.2c231.4,491.2,231.0,491.5,230.9,491.8c230.7,492.0,230.4,492.3,230.2,492.3c229.9,492.3,229.6,492.5,229.5,492.8c229.3,493.0,228.8,493.3,228.2,493.5c225.4,494.2,81.5,494.5,32.4,493.9|m287.3,493.9c276.8,493.8,267.6,493.6,266.9,493.5c266.1,493.3,265.4,493.0,265.2,492.8c265.1,492.5,264.8,492.3,264.6,492.3c264.3,492.3,264.0,492.0,263.9,491.8c263.7,491.5,263.4,491.2,263.3,491.2c263.1,491.2,262.9,491.0,262.7,490.7c262.5,490.4,262.2,490.2,262.0,490.2c261.4,490.2,257.7,484.4,257.1,482.6c256.8,481.7,256.5,480.9,256.4,480.8c256.2,480.6,256.1,480.3,256.1,479.9c256.1,479.6,256.0,479.1,255.8,478.9c255.6,478.6,255.4,477.8,255.4,476.8c255.4,476.0,255.3,475.0,255.1,474.8c254.9,474.5,254.9,453.8,254.9,373.9c254.9,294.0,254.9,273.4,255.1,273.1c255.3,272.8,255.4,272.1,255.4,271.5c255.4,270.9,255.6,270.2,255.8,270.0c256.0,269.8,256.1,269.3,256.1,269.0c256.1,268.6,256.3,268.2,256.5,267.9c256.7,267.7,256.8,267.3,256.8,266.9c256.8,266.6,257.0,266.1,257.2,265.9c257.4,265.7,257.5,265.3,257.5,265.1c257.5,264.5,261.5,258.7,261.9,258.7c262.0,258.7,262.3,258.4,262.5,258.2c262.6,257.9,262.9,257.6,263.2,257.6c263.4,257.6,263.7,257.4,263.9,257.1c264.0,256.8,264.3,256.6,264.6,256.6c264.8,256.6,265.1,256.4,265.3,256.1c265.4,255.8,265.9,255.6,266.3,255.6c266.7,255.6,267.2,255.4,267.3,255.2c267.7,254.6,449.0,254.3,468.5,254.9c481.5,255.2,482.8,255.3,483.3,256.1c483.4,256.4,483.7,256.6,483.9,256.6c484.0,256.6,484.3,256.8,484.4,257.1c484.6,257.4,484.9,257.6,485.1,257.6c485.3,257.6,485.8,258.1,486.2,258.7c486.6,259.2,487.0,259.7,487.2,259.7c487.7,259.7,490.3,263.5,490.3,264.2c490.3,264.5,490.6,265.2,491.0,265.7c491.4,266.3,491.7,267.0,491.7,267.3c491.7,267.6,491.9,268.1,492.0,268.3c492.2,268.5,492.4,269.2,492.4,269.8c492.4,270.5,492.5,271.1,492.7,271.4c493.3,272.0,493.4,273.7,493.6,288.0c493.9,309.3,493.8,473.9,493.4,474.5c493.2,474.7,493.1,475.6,493.1,476.5c493.1,477.5,493.0,478.3,492.7,478.5c492.6,478.8,492.4,479.5,492.4,480.1c492.4,480.7,492.2,481.4,492.0,481.6c491.9,481.9,491.7,482.3,491.7,482.6c491.7,482.9,491.4,483.7,491.0,484.2c490.6,484.7,490.3,485.4,490.3,485.7c490.3,486.4,489.1,488.1,488.7,488.1c488.5,488.1,487.8,488.8,487.3,489.7c486.7,490.5,486.0,491.2,485.8,491.2c485.6,491.2,485.3,491.5,485.1,491.8c485.0,492.0,484.5,492.3,484.1,492.3c483.7,492.3,483.2,492.5,483.1,492.8c482.9,493.0,482.3,493.3,481.8,493.5c478.9,494.2,335.6,494.5,287.3,493.9|m537.4,494.0c526.9,493.8,517.9,493.6,517.4,493.5c516.9,493.3,516.4,493.0,516.2,492.7c516.1,492.5,515.6,492.3,515.2,492.3c514.8,492.3,514.3,492.0,514.2,491.8c514.0,491.5,513.7,491.2,513.5,491.2c513.3,491.2,512.6,490.5,512.0,489.7c511.5,488.8,510.8,488.1,510.6,488.1c510.2,488.1,509.0,486.4,509.0,485.7c509.0,485.4,508.7,484.7,508.3,484.2c507.9,483.7,507.6,482.9,507.6,482.6c507.6,482.3,507.4,481.9,507.3,481.6c507.1,481.4,506.9,480.7,506.9,480.1c506.9,479.5,506.8,478.8,506.6,478.6c506.0,477.9,505.9,475.8,505.7,460.0c505.5,440.1,505.5,308.8,505.7,288.9c505.9,273.1,506.0,271.0,506.6,270.3c506.8,270.1,506.9,269.7,506.9,269.3c506.9,269.0,507.1,268.5,507.3,268.3c507.4,268.1,507.6,267.6,507.6,267.3c507.6,266.9,507.8,266.5,508.0,266.2c508.1,266.0,508.3,265.6,508.3,265.3c508.3,264.5,512.3,258.7,512.8,258.7c513.0,258.7,513.3,258.4,513.5,258.2c513.6,257.9,513.9,257.6,514.2,257.6c514.4,257.6,514.7,257.4,514.9,257.1c515.0,256.8,515.3,256.6,515.6,256.6c515.8,256.6,516.1,256.4,516.3,256.1c516.4,255.8,516.8,255.6,517.2,255.6c517.5,255.6,517.9,255.4,518.1,255.2c518.3,254.8,540.1,254.7,625.4,254.7c710.7,254.7,732.4,254.8,732.7,255.2c732.8,255.4,733.3,255.6,733.7,255.6c734.1,255.6,734.6,255.8,734.7,256.1c734.9,256.4,735.2,256.6,735.4,256.6c735.7,256.6,736.0,256.8,736.1,257.1c736.3,257.4,736.5,257.6,736.7,257.6c736.8,257.6,737.3,258.1,737.8,258.7c738.3,259.2,738.8,259.7,738.9,259.7c739.2,259.7,741.1,262.5,741.1,262.9c741.1,263.2,741.4,263.8,741.8,264.3c742.1,264.9,742.5,265.6,742.5,265.9c742.5,266.2,742.6,266.7,742.8,266.9c743.0,267.2,743.2,267.6,743.2,267.9c743.2,268.3,743.3,268.7,743.5,269.0c743.7,269.2,743.9,269.7,743.9,270.0c743.9,270.3,744.0,270.8,744.2,271.0c744.4,271.3,744.6,272.1,744.6,273.1c744.6,274.0,744.7,274.9,744.9,275.1c745.1,275.5,745.1,295.9,745.1,375.0c745.1,454.0,745.1,474.5,744.9,474.8c744.7,475.0,744.6,476.0,744.6,476.8c744.6,477.8,744.4,478.6,744.2,478.9c744.0,479.1,743.9,479.6,743.9,479.9c743.9,480.3,743.8,480.6,743.6,480.8c743.5,480.9,743.2,481.7,742.9,482.6c742.3,484.4,738.6,490.2,738.0,490.2c737.8,490.2,737.5,490.4,737.3,490.7c737.1,491.0,736.9,491.2,736.7,491.2c736.6,491.2,736.3,491.5,736.1,491.8c736.0,492.0,735.7,492.3,735.4,492.3c735.2,492.3,734.9,492.5,734.8,492.8c734.6,493.0,734.0,493.3,733.5,493.5c730.7,494.2,588.2,494.5,537.4,494.0|m791.8,493.9c781.3,493.8,772.1,493.6,771.4,493.5c770.7,493.3,770.0,493.0,769.8,492.8c769.7,492.5,769.3,492.3,769.1,492.3c768.9,492.3,768.6,492.0,768.4,491.8c768.3,491.5,767.9,491.2,767.7,491.2c767.5,491.2,767.2,491.0,767.0,490.7c766.9,490.4,766.6,490.2,766.3,490.2c765.8,490.2,761.9,484.4,761.9,483.6c761.9,483.3,761.7,482.9,761.5,482.7c761.3,482.4,761.2,482.0,761.2,481.6c761.2,481.3,761.0,480.8,760.8,480.6c760.6,480.4,760.5,479.9,760.5,479.7c760.5,479.4,760.3,478.9,760.1,478.4c759.2,476.2,759.2,476.9,759.2,374.6c759.2,272.2,759.2,272.0,760.2,270.3c760.3,270.0,760.5,269.4,760.5,268.9c760.5,268.4,760.8,267.5,761.2,266.8c761.6,266.2,761.9,265.4,761.9,265.2c761.9,264.5,765.9,258.7,766.3,258.7c766.6,258.7,766.9,258.4,767.0,258.2c767.2,257.9,767.5,257.6,767.7,257.6c767.9,257.6,768.3,257.4,768.4,257.1c768.6,256.8,768.9,256.6,769.1,256.6c769.3,256.6,769.7,256.4,769.8,256.1c770.0,255.8,770.5,255.6,770.9,255.6c771.3,255.6,771.7,255.4,771.9,255.2c772.1,254.8,793.9,254.7,879.1,254.7c964.3,254.7,986.0,254.8,986.2,255.2c986.4,255.4,986.9,255.6,987.3,255.6c987.7,255.6,988.1,255.8,988.3,256.1c988.5,256.4,988.9,256.6,989.2,256.6c989.5,256.6,990.2,257.1,990.6,257.6c991.1,258.2,991.7,258.7,991.9,258.7c992.5,258.7,995.8,263.9,996.6,266.4c997.1,267.7,997.4,269.0,997.4,269.2c997.4,269.4,997.6,269.8,997.8,270.0c998.0,270.2,998.1,270.9,998.1,271.5c998.1,272.1,998.3,272.8,998.4,273.1c998.7,273.4,998.7,294.2,998.7,375.0c998.7,455.7,998.7,476.5,998.4,476.9c998.3,477.1,998.1,477.8,998.1,478.4c998.1,479.0,998.0,479.7,997.8,479.9c997.6,480.1,997.4,480.5,997.4,480.8c997.4,481.1,997.2,481.9,996.8,482.7c996.5,483.4,996.3,484.2,996.3,484.4c996.3,484.9,993.5,489.2,993.2,489.2c993.0,489.2,992.5,489.6,992.0,490.2c991.6,490.8,991.0,491.2,990.8,491.2c990.6,491.2,990.3,491.5,990.2,491.8c990.0,492.0,989.6,492.3,989.2,492.3c988.9,492.3,988.5,492.5,988.3,492.8c988.2,493.0,987.6,493.3,987.1,493.5c984.2,494.2,840.3,494.5,791.8,493.9|m225.5,492.0c225.7,491.8,226.4,491.6,227.3,491.6c228.3,491.6,228.8,491.4,229.0,491.1c229.2,490.8,229.5,490.6,229.7,490.6c229.9,490.6,230.2,490.3,230.4,490.0c230.6,489.8,230.9,489.5,231.1,489.5c231.6,489.5,236.3,482.7,236.3,481.9c236.3,481.6,236.6,481.0,237.0,480.4c237.4,479.7,237.7,479.1,237.7,478.4c237.7,477.8,237.8,477.1,238.0,476.9c238.4,476.2,238.4,274.7,238.0,274.1c237.8,273.8,237.7,273.2,237.7,272.6c237.7,272.0,237.5,271.3,237.3,271.0c237.1,270.8,237.0,270.3,237.0,270.0c237.0,269.7,236.8,269.2,236.6,269.0c236.4,268.7,236.3,268.3,236.3,267.9c236.3,267.6,236.1,267.2,235.9,266.9c235.7,266.7,235.6,266.2,235.6,265.9c235.6,265.3,233.0,261.4,232.6,261.4c232.4,261.4,231.9,261.0,231.5,260.4c231.1,259.8,230.5,259.4,230.3,259.4c230.2,259.4,229.9,259.1,229.7,258.8c229.5,258.6,229.2,258.3,229.0,258.3c228.8,258.3,228.5,258.1,228.3,257.8c227.5,256.3,221.1,256.3,115.5,256.4c35.7,256.4,15.2,256.5,14.9,256.9c14.8,257.1,14.2,257.3,13.5,257.3c12.9,257.3,12.3,257.5,12.2,257.8c12.0,258.1,11.7,258.3,11.5,258.3c11.2,258.3,10.9,258.6,10.8,258.8c10.6,259.1,10.3,259.4,10.1,259.4c9.8,259.4,9.5,259.6,9.4,259.9c9.2,260.2,8.9,260.4,8.7,260.4c7.7,260.4,3.0,269.1,3.0,270.9c3.0,271.1,2.9,271.5,2.7,271.7c2.5,271.9,2.3,272.9,2.3,273.9c2.2,274.9,2.0,276.6,1.9,277.7c1.6,280.5,1.6,469.4,1.9,472.2c2.0,473.3,2.2,475.0,2.3,476.0c2.3,476.9,2.5,477.9,2.7,478.2c2.8,478.5,3.2,479.3,3.4,480.1c3.6,480.8,4.1,482.0,4.5,482.6c4.8,483.2,5.1,483.9,5.1,484.1c5.1,484.7,7.0,487.5,7.4,487.5c7.5,487.5,7.9,487.9,8.3,488.5c8.7,489.1,9.2,489.5,9.5,489.5c9.8,489.5,10.1,489.8,10.3,490.0c10.5,490.3,10.9,490.6,11.2,490.6c11.6,490.6,12.0,490.8,12.2,491.1c12.3,491.4,12.8,491.6,13.3,491.6c13.8,491.6,14.3,491.7,14.4,491.9c14.8,492.4,20.6,492.5,126.2,492.5c205.1,492.4,225.3,492.4,225.5,492.0|m479.1,492.0c479.3,491.8,480.0,491.6,480.8,491.6c481.8,491.6,482.4,491.4,482.6,491.1c482.7,490.8,483.0,490.6,483.3,490.6c483.5,490.6,483.8,490.3,484.0,490.0c484.1,489.8,484.4,489.5,484.7,489.5c484.9,489.5,485.4,489.1,485.7,488.5c486.1,487.9,486.6,487.5,486.8,487.5c487.3,487.5,488.4,485.7,488.4,485.0c488.4,484.7,488.9,483.8,489.5,483.0c490.1,482.2,490.5,481.2,490.5,480.9c490.5,480.6,490.7,480.1,490.9,479.9c491.1,479.7,491.2,479.0,491.2,478.4c491.2,477.8,491.4,477.1,491.5,476.9c491.8,476.5,491.8,455.7,491.8,375.0c491.8,294.2,491.8,273.4,491.5,273.1c491.4,272.8,491.2,272.1,491.2,271.5c491.2,270.9,491.1,270.2,490.9,270.0c490.7,269.8,490.5,269.3,490.5,269.0c490.5,268.7,490.2,268.0,489.8,267.4c489.4,266.9,489.1,266.2,489.1,265.9c489.1,265.2,486.3,261.1,485.8,261.1c485.6,261.1,485.2,260.7,484.9,260.2c484.6,259.7,484.2,259.4,484.1,259.4c483.9,259.4,483.7,259.1,483.5,258.8c483.3,258.6,483.0,258.3,482.8,258.3c482.6,258.3,482.3,258.1,482.1,257.8c481.3,256.3,475.7,256.3,369.8,256.4c289.9,256.4,269.4,256.5,269.2,256.9c269.0,257.1,268.4,257.3,267.8,257.3c267.1,257.3,266.6,257.5,266.4,257.8c266.3,258.1,266.0,258.3,265.7,258.3c265.5,258.3,265.2,258.6,265.0,258.8c264.9,259.1,264.6,259.4,264.3,259.4c264.1,259.4,263.8,259.6,263.6,259.9c263.5,260.2,263.2,260.4,262.9,260.4c262.5,260.4,258.7,266.0,258.7,266.7c258.7,267.0,258.6,267.4,258.4,267.6c258.2,267.8,258.0,268.3,258.0,268.6c258.0,269.0,257.9,269.4,257.7,269.7c257.5,269.9,257.3,270.4,257.3,270.7c257.3,271.0,257.2,271.5,257.0,271.7c256.8,271.9,256.6,273.0,256.5,274.2c256.5,275.4,256.3,277.6,256.2,279.1c255.9,282.9,255.9,467.1,256.2,470.6c256.3,472.0,256.5,474.0,256.5,475.0c256.6,476.0,256.8,477.0,257.0,477.2c257.2,477.4,257.3,478.0,257.3,478.4c257.3,478.9,257.6,479.9,258.0,480.6c258.4,481.3,258.7,482.1,258.7,482.3c258.7,482.8,262.7,488.5,263.0,488.5c263.2,488.5,263.5,488.7,263.6,489.0c263.8,489.3,264.1,489.5,264.3,489.5c264.6,489.5,264.9,489.8,265.0,490.0c265.2,490.3,265.5,490.6,265.7,490.6c266.0,490.6,266.3,490.8,266.4,491.1c266.6,491.4,267.1,491.6,267.9,491.6c268.6,491.6,269.2,491.7,269.4,491.9c269.7,492.4,275.4,492.5,380.4,492.5c458.8,492.4,478.9,492.4,479.1,492.0|m723.4,492.2c731.9,491.9,733.7,491.7,734.1,491.0c734.2,490.8,734.6,490.6,734.9,490.6c735.1,490.6,735.5,490.3,735.7,490.0c735.8,489.8,736.1,489.5,736.3,489.5c736.8,489.5,741.3,482.7,741.3,482.0c741.3,481.7,741.6,481.0,742.0,480.4c742.4,479.9,742.7,479.1,742.7,478.7c742.7,478.3,742.8,477.4,743.0,476.7c743.6,474.9,743.6,274.4,743.0,273.1c742.9,272.6,742.7,271.8,742.7,271.2c742.7,270.6,742.5,269.9,742.3,269.7c742.1,269.4,742.0,269.0,742.0,268.7c742.0,268.4,741.6,267.6,741.1,266.8c740.5,266.1,740.1,265.3,740.1,265.1c740.1,264.4,738.4,261.7,737.7,261.3c737.3,261.0,736.8,260.5,736.5,260.1c736.3,259.7,735.9,259.4,735.7,259.4c735.4,259.4,735.1,259.1,735.0,258.8c734.8,258.6,734.3,258.3,733.9,258.3c733.5,258.3,733.0,258.1,732.9,257.8c732.7,257.5,732.2,257.3,731.5,257.3c730.9,257.3,730.3,257.1,730.1,256.9c729.9,256.5,708.6,256.4,625.1,256.4c541.7,256.4,520.4,256.5,520.2,256.9c520.0,257.1,519.4,257.3,518.7,257.3c517.9,257.3,517.4,257.5,517.2,257.8c517.0,258.1,516.8,258.3,516.6,258.3c516.4,258.3,516.2,258.6,516.0,258.8c515.9,259.1,515.5,259.4,515.3,259.4c515.1,259.4,514.8,259.6,514.6,259.9c514.5,260.2,514.2,260.4,513.9,260.4c513.4,260.4,509.5,266.2,509.5,267.0c509.5,267.3,509.3,267.7,509.1,267.9c508.9,268.2,508.8,268.6,508.8,269.0c508.8,269.3,508.6,269.8,508.4,270.0c508.2,270.2,508.1,270.7,508.1,271.0c508.1,271.4,507.9,271.8,507.7,272.1c507.5,272.3,507.4,273.1,507.4,274.1c507.4,275.0,507.2,275.9,507.1,276.1c506.8,276.5,506.8,296.7,506.8,375.0c506.8,453.2,506.8,473.4,507.1,473.8c507.2,474.0,507.4,474.9,507.4,475.8c507.4,476.8,507.5,477.6,507.7,477.8c507.9,478.1,508.1,478.5,508.1,478.9c508.1,479.2,508.2,479.7,508.4,479.9c508.6,480.1,508.8,480.6,508.8,480.9c508.8,481.2,509.1,481.9,509.5,482.5c509.9,483.0,510.2,483.7,510.2,484.0c510.2,484.7,512.1,487.5,512.5,487.5c512.7,487.5,513.2,487.9,513.6,488.5c513.9,489.1,514.4,489.5,514.6,489.5c514.9,489.5,515.2,489.8,515.3,490.0c515.5,490.3,515.8,490.6,516.0,490.6c516.2,490.6,516.6,490.8,516.7,491.1c516.9,491.4,517.4,491.6,518.1,491.6c518.7,491.6,519.3,491.7,519.4,491.9c519.6,492.1,522.2,492.3,526.0,492.4c541.7,492.6,716.9,492.5,723.4,492.2|m985.1,492.0c985.2,491.8,985.8,491.6,986.5,491.6c987.1,491.6,987.7,491.4,987.8,491.1c988.0,490.8,988.3,490.6,988.5,490.6c988.8,490.6,989.1,490.3,989.2,490.0c989.4,489.8,989.7,489.5,989.9,489.5c990.1,489.5,990.6,489.1,991.0,488.5c991.4,487.9,991.8,487.5,992.1,487.5c992.5,487.5,994.9,483.7,994.9,483.0c994.9,482.8,995.2,482.1,995.6,481.5c995.9,480.9,996.3,480.0,996.3,479.7c996.3,479.3,996.4,478.7,996.6,478.3c996.7,478.0,997.0,476.9,997.0,476.0c997.1,475.0,997.3,473.4,997.4,472.3c997.7,469.8,997.7,279.7,997.4,277.2c997.3,276.2,997.1,274.6,997.0,273.7c997.0,272.8,996.8,271.9,996.6,271.7c996.4,271.5,996.3,271.0,996.3,270.7c996.3,270.4,996.1,269.9,995.9,269.7c995.7,269.4,995.6,269.0,995.6,268.6c995.6,268.3,995.4,267.8,995.2,267.6c995.0,267.4,994.9,267.0,994.9,266.8c994.9,266.1,991.1,260.4,990.7,260.4c990.4,260.4,990.1,260.2,989.9,259.9c989.8,259.6,989.5,259.4,989.2,259.4c989.0,259.4,988.7,259.1,988.5,258.8c988.4,258.6,988.1,258.3,987.8,258.3c987.6,258.3,987.3,258.1,987.1,257.8c987.0,257.5,986.4,257.3,985.7,257.3c985.1,257.3,984.5,257.1,984.4,256.9c984.1,256.5,962.8,256.4,879.1,256.4c795.4,256.4,774.0,256.5,773.8,256.9c773.6,257.1,773.0,257.3,772.4,257.3c771.7,257.3,771.2,257.5,771.0,257.8c770.8,258.1,770.5,258.3,770.3,258.3c770.1,258.3,769.8,258.6,769.6,258.8c769.4,259.1,769.1,259.4,768.9,259.4c768.7,259.4,768.3,259.6,768.2,259.9c768.0,260.2,767.7,260.4,767.5,260.4c767.0,260.4,763.0,266.2,763.0,266.9c763.0,267.2,762.7,267.9,762.3,268.5c761.8,269.2,761.6,269.8,761.6,270.5c761.6,271.2,761.5,271.8,761.3,272.1c761.1,272.3,760.9,273.1,760.9,274.1c760.9,275.0,760.8,275.9,760.6,276.1c760.4,276.5,760.4,296.6,760.4,374.4c760.4,452.3,760.4,472.4,760.6,472.7c760.8,473.0,760.9,474.1,760.9,475.3c760.9,476.8,761.0,477.5,761.3,477.8c761.5,478.1,761.6,478.5,761.6,478.9c761.6,479.2,761.8,479.7,762.0,479.9c762.2,480.1,762.3,480.6,762.3,480.9c762.3,481.6,767.7,489.5,768.2,489.5c768.4,489.5,768.7,489.8,768.9,490.0c769.0,490.3,769.4,490.6,769.6,490.6c769.8,490.6,770.1,490.8,770.3,491.1c770.5,491.4,771.0,491.6,771.7,491.6c772.3,491.6,772.9,491.7,773.0,491.9c773.4,492.4,779.2,492.5,885.3,492.5c964.6,492.4,984.8,492.4,985.1,492.0|m13.1,486.9c12.8,486.8,12.4,486.6,12.3,486.4c12.2,486.2,11.7,486.1,11.3,486.1c10.9,486.1,10.5,485.9,10.3,485.6c10.1,485.3,9.8,485.1,9.6,485.1c9.0,485.1,6.9,481.6,6.1,479.1l5.3,476.7l5.3,451.1l5.3,425.5l5.9,423.8c6.3,422.8,6.5,421.9,6.5,421.7c6.5,421.4,6.3,420.5,5.9,419.6l5.3,417.9l5.3,391.0l5.3,364.2l5.9,363.2c6.7,361.9,6.7,360.3,5.9,358.1l5.3,356.4l5.3,331.6c5.3,314.5,5.4,306.7,5.5,306.4c5.7,306.1,5.9,305.4,5.9,304.7c6.2,302.9,9.0,298.9,9.9,298.9c10.3,298.9,10.8,298.7,11.0,298.4c11.2,298.1,18.3,298.0,45.0,298.0l78.7,298.0l79.6,299.0c80.1,299.5,80.5,299.9,80.7,299.9c80.8,299.9,80.9,300.1,80.9,300.4c80.9,300.6,81.1,301.1,81.4,301.4c81.8,301.9,81.8,301.9,82.4,301.1c82.7,300.6,83.1,300.0,83.4,299.9c83.6,299.7,84.0,299.4,84.2,299.3c85.7,298.0,84.8,298.0,119.7,298.0c146.4,298.0,153.5,298.1,153.7,298.4c153.9,298.7,154.2,298.9,154.4,298.9c154.5,298.9,155.2,299.6,155.8,300.4c156.4,301.3,157.1,302.0,157.2,302.0c157.3,302.0,158.0,301.3,158.6,300.4c159.2,299.6,159.8,298.9,160.0,298.9c160.2,298.9,160.5,298.7,160.7,298.4c160.9,298.1,168.1,298.0,195.2,298.0c222.3,298.0,229.5,298.1,229.7,298.4c229.9,298.7,230.3,298.9,230.6,298.9c231.3,298.9,233.9,302.3,233.9,303.1c233.9,303.4,234.1,303.8,234.3,304.0c234.5,304.3,234.6,304.6,234.6,304.9c234.6,305.1,234.8,305.8,235.0,306.3c235.5,307.8,235.5,355.1,235.0,356.1c234.8,356.5,234.6,357.0,234.6,357.3c234.6,357.6,234.5,358.1,234.3,358.3c233.8,358.9,233.8,361.8,234.3,362.4c234.5,362.7,234.6,363.1,234.6,363.4c234.6,363.7,234.8,364.3,235.0,364.6c235.5,365.6,235.5,416.0,235.0,417.5c234.8,418.0,234.6,418.8,234.6,419.3c234.6,419.7,234.5,420.2,234.3,420.5c234.1,420.7,233.9,421.4,233.9,422.0c233.9,422.6,234.1,423.3,234.3,423.6c234.5,423.8,234.6,424.2,234.6,424.6c234.6,424.9,234.8,425.4,235.0,425.8c235.5,426.8,235.5,474.6,235.0,475.6c234.8,476.0,234.6,476.8,234.6,477.4c234.6,478.0,234.5,478.6,234.3,478.9c234.1,479.1,233.9,479.6,233.9,479.9c233.9,480.6,230.8,485.1,230.3,485.1c230.1,485.1,229.9,485.3,229.7,485.6c229.5,485.9,229.1,486.1,228.7,486.1c228.3,486.1,227.8,486.3,227.6,486.5c227.4,486.9,220.5,486.9,194.5,486.9c168.5,486.9,161.6,486.9,161.4,486.5c161.2,486.3,160.9,486.1,160.7,486.1c160.5,486.1,159.8,485.3,159.2,484.3c157.6,482.0,157.3,481.8,156.6,482.4c156.3,482.7,156.0,483.3,156.0,483.7c155.9,484.1,155.7,484.6,155.5,484.8c155.3,484.9,154.9,485.2,154.7,485.4c154.5,485.6,154.1,485.8,153.9,485.9c153.7,486.1,153.3,486.3,153.0,486.5c152.6,486.8,144.0,486.9,119.5,486.9c85.5,486.9,86.4,487.0,84.9,485.7c84.7,485.5,84.4,485.3,84.2,485.2c84.0,485.0,83.5,484.5,83.0,484.0c82.5,483.4,82.1,483.0,81.9,483.0c81.8,483.0,81.3,483.7,80.7,484.5c80.1,485.4,79.5,486.1,79.3,486.1c79.1,486.1,78.8,486.3,78.6,486.5c78.4,486.9,71.5,487.0,46.0,487.0c28.2,487.0,13.4,487.0,13.1,486.9|m267.5,486.9c267.1,486.8,266.7,486.6,266.6,486.4c266.4,486.2,266.0,486.1,265.6,486.1c265.2,486.1,264.7,485.9,264.6,485.6c264.4,485.3,264.1,485.1,263.9,485.1c263.4,485.1,260.8,481.3,260.8,480.5c260.8,480.2,260.7,479.8,260.5,479.6c260.3,479.3,260.1,478.6,260.1,478.0c260.1,477.4,260.0,476.8,259.9,476.6c259.7,476.5,259.6,467.7,259.6,451.2c259.6,434.8,259.7,425.9,259.9,425.8c260.0,425.7,260.1,425.3,260.1,425.0c260.1,424.7,260.5,424.0,260.9,423.3c261.6,422.3,261.6,422.2,261.2,421.6c261.0,421.2,260.8,420.7,260.8,420.4c260.8,420.1,260.7,419.7,260.5,419.4c260.3,419.2,260.1,418.7,260.1,418.4c260.1,418.0,260.0,417.7,259.9,417.6c259.5,417.2,259.6,365.0,259.9,364.0c260.1,363.6,260.5,362.7,260.9,362.0c261.7,360.5,261.7,359.7,260.9,358.6c259.6,356.8,259.6,357.9,259.6,331.1c259.6,315.1,259.7,306.4,259.9,306.3c260.0,306.1,260.1,305.8,260.1,305.4c260.1,305.1,260.3,304.6,260.5,304.4c260.7,304.1,260.8,303.7,260.8,303.4c260.8,302.7,262.7,299.9,263.2,299.9c263.4,299.9,263.7,299.7,263.9,299.4c264.0,299.1,264.3,298.9,264.5,298.9c264.8,298.9,265.1,298.7,265.2,298.4c265.5,298.1,272.5,298.0,298.9,298.0c336.3,298.0,332.9,297.8,335.0,300.6l336.1,301.9l337.0,300.5c338.8,297.8,335.4,298.0,373.6,298.0c400.6,298.0,407.8,298.1,408.0,298.4c408.1,298.7,408.4,298.9,408.7,298.9c408.9,298.9,409.5,299.6,410.1,300.4l411.1,302.0l412.2,300.4c412.8,299.6,413.4,298.9,413.6,298.9c413.8,298.9,414.1,298.7,414.2,298.4c414.5,298.1,421.7,298.0,448.8,298.0c475.9,298.0,483.1,298.1,483.3,298.4c483.5,298.7,483.9,298.9,484.2,298.9c484.9,298.9,487.7,302.6,488.4,304.7c488.9,306.1,488.9,306.2,488.9,331.5c488.9,353.6,488.8,356.9,488.5,357.3c488.3,357.5,488.2,358.0,488.2,358.3c488.2,358.6,488.0,359.1,487.8,359.3c487.6,359.6,487.5,360.0,487.5,360.4c487.5,360.7,487.6,361.2,487.8,361.4c488.0,361.6,488.2,362.1,488.2,362.4c488.2,362.8,488.3,363.2,488.5,363.4c488.8,363.8,488.9,367.3,488.9,390.9c488.9,414.6,488.8,418.0,488.5,418.4c488.3,418.6,488.2,419.2,488.2,419.6c488.2,420.0,488.0,420.6,487.8,420.8c487.6,421.1,487.5,421.4,487.5,421.7c487.5,421.9,487.6,422.3,487.8,422.5c488.0,422.8,488.2,423.2,488.2,423.6c488.2,423.9,488.3,424.4,488.5,424.6c488.8,425.0,488.9,428.4,488.9,451.2c488.9,474.1,488.8,477.5,488.5,477.8c488.3,478.1,488.2,478.5,488.2,478.9c488.2,479.2,488.0,479.7,487.8,479.9c487.6,480.1,487.5,480.6,487.5,480.9c487.5,481.6,485.1,485.1,484.6,485.1c484.4,485.1,484.1,485.3,484.0,485.6c483.8,485.9,483.4,486.1,482.9,486.1c482.5,486.1,482.1,486.3,481.9,486.5c481.7,486.9,474.7,486.9,448.6,486.9c414.4,486.9,415.2,487.0,413.8,485.7c413.6,485.5,413.3,485.3,413.0,485.2c412.8,485.1,412.6,484.8,412.6,484.6c412.6,484.0,411.9,483.0,411.5,483.0c411.3,483.0,410.7,483.7,410.1,484.5c409.4,485.5,408.7,486.1,408.4,486.1c408.1,486.1,407.7,486.3,407.5,486.5c407.3,486.9,400.2,486.9,373.7,486.9c339.1,486.9,339.9,487.0,338.5,485.7c338.3,485.5,337.9,485.3,337.7,485.1c337.4,484.9,337.0,484.5,336.7,484.1c336.1,483.1,335.9,483.1,334.9,484.7c334.4,485.5,333.8,486.1,333.6,486.1c333.4,486.1,333.1,486.3,332.9,486.5c332.7,486.9,325.8,487.0,300.4,487.0c282.7,487.0,267.9,487.0,267.5,486.9|m518.2,486.9c517.9,486.8,517.4,486.6,517.3,486.4c517.2,486.2,516.8,486.1,516.4,486.1c515.9,486.1,515.5,485.9,515.3,485.6c515.2,485.3,514.9,485.1,514.7,485.1c514.3,485.1,511.8,481.4,511.8,480.8c511.8,480.5,511.7,480.1,511.5,479.9c511.3,479.7,511.1,479.0,511.1,478.4c511.1,477.8,511.0,477.1,510.8,476.9c510.6,476.5,510.5,470.8,510.5,450.7l510.5,425.0l511.2,424.0c511.9,422.9,512.0,421.9,511.5,420.5c510.5,417.7,510.5,418.9,510.5,390.9c510.5,363.5,510.5,363.9,511.4,361.7c511.8,360.6,511.9,360.2,511.6,359.7c511.5,359.4,511.3,358.9,511.2,358.6c511.1,358.4,510.9,357.8,510.8,357.3c510.6,356.7,510.5,349.6,510.5,331.0c510.5,303.2,510.4,305.5,511.9,302.5c512.8,300.7,514.4,298.9,515.1,298.9c515.4,298.9,515.8,298.7,516.0,298.4c516.2,298.1,523.4,298.0,550.5,298.0l584.8,298.0l585.4,299.0c585.8,299.5,586.2,299.9,586.4,299.9c586.5,299.9,586.7,300.1,586.7,300.4c586.7,300.6,586.9,301.1,587.1,301.4c587.5,301.9,587.6,301.9,588.5,300.4c589.1,299.6,589.7,298.9,589.9,298.9c590.1,298.9,590.4,298.7,590.6,298.4c590.8,298.1,598.0,298.0,625.0,298.0l659.1,298.0l659.9,299.0c660.4,299.5,660.9,299.9,661.0,299.9c661.1,299.9,661.3,300.2,661.4,300.6c661.8,301.8,662.1,301.7,663.2,300.3c665.2,297.8,661.9,298.0,700.0,298.0c727.3,298.0,734.5,298.1,734.8,298.4c734.9,298.7,735.2,298.9,735.5,298.9c735.7,298.9,736.0,299.1,736.1,299.4c736.3,299.7,736.6,299.9,736.8,299.9c737.3,299.9,738.5,301.6,738.5,302.4c738.5,302.7,738.6,303.1,738.8,303.3c739.0,303.6,739.2,304.0,739.2,304.3c739.2,304.7,739.3,305.1,739.5,305.3c739.7,305.7,739.8,311.4,739.8,331.7l739.8,357.6l739.1,358.6c738.4,359.6,738.3,360.7,738.8,361.4c739.0,361.6,739.2,362.2,739.2,362.6c739.2,363.0,739.3,363.5,739.5,363.7c739.7,364.1,739.8,370.1,739.8,391.6l739.8,419.1l739.1,420.0c738.3,421.4,738.3,423.0,739.1,424.3l739.8,425.3l739.8,451.2c739.8,471.5,739.7,477.2,739.5,477.6c739.3,477.8,739.2,478.4,739.2,479.0c739.2,479.9,738.8,480.6,737.5,482.6c736.6,483.9,735.6,485.1,735.4,485.1c735.2,485.1,734.9,485.3,734.7,485.6c734.6,485.9,734.1,486.1,733.7,486.1c733.3,486.1,732.8,486.3,732.7,486.5c732.4,486.9,725.4,486.9,699.2,486.9c672.9,486.9,665.9,486.9,665.7,486.5c665.5,486.3,665.3,486.1,665.1,486.1c664.9,486.1,664.3,485.4,663.7,484.5c663.1,483.7,662.5,483.0,662.4,483.0c662.2,483.0,661.6,483.7,660.9,484.5c660.3,485.3,659.5,486.2,659.1,486.4c658.5,486.9,654.1,486.9,625.0,486.9c598.6,486.9,591.5,486.9,591.3,486.5c591.1,486.3,590.8,486.1,590.6,486.1c590.4,486.1,590.1,485.9,589.9,485.6c589.8,485.3,589.5,485.1,589.3,485.1c589.0,485.1,588.6,484.6,588.2,484.0l587.5,483.0l586.4,484.5c585.8,485.4,585.2,486.1,585.0,486.1c584.8,486.1,584.5,486.3,584.4,486.5c584.1,486.9,577.2,487.0,551.5,487.0c533.6,487.0,518.6,487.0,518.2,486.9|m771.8,486.9c771.4,486.8,771.0,486.6,770.9,486.4c770.8,486.2,770.3,486.1,769.9,486.1c769.5,486.1,769.0,485.9,768.9,485.6c768.7,485.3,768.5,485.1,768.3,485.1c768.0,485.1,765.6,481.7,765.4,480.8c765.2,480.4,765.1,479.8,764.9,479.6c763.9,477.2,764.0,477.9,764.0,450.8l764.1,425.0l765.1,423.6l766.2,422.3l765.4,421.1c765.0,420.4,764.7,419.7,764.7,419.4c764.7,419.2,764.5,418.6,764.3,418.3c764.0,417.7,764.0,413.9,764.0,391.0c764.0,362.8,763.9,364.3,764.9,361.7c765.4,360.6,765.4,360.2,765.2,359.7c765.0,359.4,764.8,358.9,764.8,358.6c764.7,358.4,764.5,357.7,764.3,357.2c763.8,355.8,763.8,306.5,764.3,305.5c764.5,305.2,764.7,304.6,764.7,304.3c764.7,304.0,764.8,303.6,765.0,303.3c765.2,303.1,765.4,302.6,765.4,302.2c765.5,301.8,765.7,301.3,766.0,301.1c766.2,300.9,766.8,300.3,767.3,299.8c767.8,299.3,768.3,298.9,768.5,298.9c768.6,298.9,768.9,298.7,769.1,298.4c769.3,298.1,776.6,298.0,803.9,298.0c831.1,298.0,838.4,298.1,838.6,298.4c838.8,298.7,839.1,298.9,839.3,298.9c839.5,298.9,840.0,299.3,840.4,299.9c841.2,301.2,841.6,301.2,842.5,299.9c842.8,299.3,843.3,298.9,843.5,298.9c843.7,298.9,844.0,298.7,844.2,298.4c844.4,298.1,851.7,298.0,879.3,298.0l914.1,298.0l915.0,299.0c915.5,299.6,916.1,300.4,916.4,300.9l916.9,301.7l918.0,300.4c918.7,299.6,919.5,298.8,919.9,298.5c920.4,298.1,925.3,298.0,954.3,298.0c981.0,298.0,988.1,298.1,988.3,298.4c988.5,298.7,989.0,298.9,989.4,298.9c989.9,298.9,990.4,299.3,991.6,301.2c994.1,305.0,993.9,302.2,993.9,331.3l993.9,356.7l993.3,357.8c992.7,359.0,992.6,360.3,993.0,361.3c994.0,364.0,993.9,362.9,993.9,391.1l993.9,418.0l993.3,419.6c993.0,420.5,992.7,421.6,992.7,422.2c992.7,422.7,993.0,423.8,993.3,424.7l993.9,426.4l993.9,451.2c993.9,472.6,993.9,476.2,993.6,477.0c993.4,477.6,993.2,478.3,993.2,478.7c993.2,479.1,993.0,479.8,992.6,480.2c992.3,480.7,992.0,481.3,992.0,481.6c992.0,482.3,990.9,484.0,990.4,484.0c990.2,484.0,989.7,484.5,989.4,485.1c988.9,485.8,988.5,486.1,988.0,486.1c987.6,486.1,987.1,486.3,986.9,486.5c986.7,486.9,979.8,486.9,953.8,486.9c927.8,486.9,920.9,486.9,920.7,486.5c920.5,486.3,920.2,486.1,920.0,486.1c919.8,486.1,919.1,485.2,918.3,484.1l917.0,482.2l916.0,483.4c915.5,484.1,914.9,485.0,914.7,485.4c914.5,485.8,914.2,486.1,914.0,486.1c913.7,486.1,913.4,486.3,913.3,486.5c913.0,486.9,905.9,486.9,879.1,486.9c852.3,486.9,845.1,486.9,844.9,486.5c844.7,486.3,844.4,486.1,844.2,486.1c844.0,486.1,843.4,485.4,842.8,484.5c842.2,483.7,841.6,483.0,841.5,483.0c841.3,483.0,840.8,483.5,840.4,484.0c839.9,484.6,839.4,485.1,839.2,485.1c839.0,485.1,838.8,485.3,838.6,485.6c838.4,485.9,838.1,486.1,837.9,486.1c837.7,486.1,837.4,486.3,837.2,486.5c837.0,486.9,830.2,487.0,804.7,487.0c787.0,487.0,772.2,487.0,771.8,486.9|m76.6,484.9c76.9,484.6,77.5,484.4,77.9,484.4c78.3,484.4,78.7,484.0,79.1,483.4c80.5,481.3,80.5,481.2,80.5,475.1c80.5,470.7,80.6,469.3,80.8,468.8c81.3,467.8,81.3,459.7,80.8,458.8c80.3,457.8,80.3,440.5,80.8,439.6c81.1,439.0,81.2,437.7,81.2,433.7c81.2,429.7,81.1,428.4,80.8,427.8c80.6,427.5,80.5,426.9,80.5,426.6c80.5,426.4,80.0,425.4,79.4,424.6l78.3,423.1l43.7,423.1l9.1,423.1l7.8,425.0l6.4,427.0l6.4,451.2c6.4,470.1,6.5,475.5,6.7,475.8c6.9,476.1,7.0,476.7,7.0,477.3c7.0,478.1,7.4,478.8,8.7,480.8c9.6,482.2,10.6,483.3,10.8,483.3c11.0,483.3,11.3,483.6,11.5,483.9c11.6,484.1,12.0,484.4,12.3,484.4c12.6,484.4,13.2,484.6,13.6,484.9c14.8,485.6,75.6,485.6,76.6,484.9|m149.6,484.9c150.1,484.6,151.0,484.4,151.7,484.4c152.5,484.4,153.0,484.2,153.2,483.9c153.4,483.6,153.7,483.3,153.9,483.3c154.4,483.3,155.6,481.6,155.6,480.7c155.6,480.3,155.7,479.4,155.9,478.7c156.2,477.7,156.3,474.2,156.2,452.9c156.1,425.4,156.2,426.5,154.5,424.4l153.7,423.3l149.6,423.1c147.4,422.9,132.1,422.9,115.6,422.9c92.0,423.0,85.6,423.1,85.3,423.5c85.2,423.7,84.9,423.9,84.7,423.9c84.5,423.9,84.0,424.3,83.7,424.9l83.0,425.8l83.0,452.5c83.0,482.1,82.9,479.8,84.7,482.9c85.2,484.0,85.7,484.4,86.1,484.4c86.4,484.4,87.1,484.6,87.5,484.9c88.7,485.6,148.4,485.7,149.6,484.9|m225.6,484.9c226.0,484.6,226.7,484.4,227.2,484.4c227.9,484.4,228.4,484.2,228.5,483.9c228.7,483.6,229.0,483.3,229.2,483.3c229.4,483.3,230.2,482.4,231.0,481.2c232.5,479.1,233.4,476.9,233.5,475.6c233.5,475.2,233.6,474.5,233.8,473.9c234.1,473.1,234.2,469.8,234.2,450.7c234.2,430.6,234.1,428.3,233.8,427.3c233.5,426.7,233.3,425.9,233.2,425.6c233.1,425.4,232.7,424.7,232.2,424.1l231.3,423.1l200.0,422.9c182.8,422.9,167.0,422.9,164.8,423.1l160.7,423.3l159.8,424.5c159.3,425.1,158.8,426.0,158.8,426.3c158.8,426.6,158.7,427.4,158.5,427.9c158.0,429.4,158.0,476.1,158.5,477.6c158.7,478.2,158.8,479.0,158.8,479.5c158.8,480.7,161.3,484.4,162.0,484.4c162.3,484.4,162.9,484.6,163.3,484.9c164.5,485.6,224.6,485.6,225.6,484.9|m331.7,484.8c333.1,484.0,334.0,482.8,334.0,481.8c334.0,481.4,334.2,480.9,334.3,480.6c334.6,480.3,334.6,474.4,334.6,453.7l334.6,427.1l334.0,425.9c333.6,425.2,333.0,424.3,332.6,423.8l331.8,423.1l297.6,423.1l263.4,423.1l262.3,424.6c261.8,425.4,261.3,426.4,261.3,426.7c261.3,427.0,261.2,427.4,261.0,427.6c260.8,428.0,260.7,433.2,260.7,451.2c260.7,469.3,260.8,474.5,261.0,474.8c261.2,475.0,261.3,475.7,261.3,476.3c261.3,476.9,261.4,477.6,261.6,477.8c261.8,478.1,262.0,478.5,262.0,478.8c262.0,479.5,264.6,483.3,265.1,483.3c265.3,483.3,265.6,483.6,265.7,483.9c265.9,484.1,266.4,484.4,266.9,484.4c267.4,484.4,268.1,484.6,268.6,484.9c269.2,485.3,273.6,485.4,299.9,485.4c329.0,485.4,330.5,485.4,331.7,484.8|m374.6,484.9c375.2,484.2,376.6,484.2,377.2,484.9c377.6,485.3,379.5,485.4,389.6,485.4c398.8,485.4,401.6,485.3,401.8,485.0c402.0,484.7,403.1,484.5,404.7,484.4l407.2,484.3l408.5,482.3l409.8,480.3l409.8,453.2l409.8,426.1l408.9,424.7l408.0,423.3l403.9,423.1c401.7,422.9,386.2,422.9,369.5,422.9l339.2,423.1l338.3,424.4c337.7,425.2,337.3,426.0,337.3,426.3c337.3,426.7,337.2,427.1,337.0,427.3c336.4,428.0,336.4,478.0,337.0,479.0c337.2,479.4,337.3,480.1,337.3,480.5c337.3,481.6,338.2,483.3,338.7,483.3c338.9,483.3,339.3,483.6,339.5,483.8c339.8,484.1,340.4,484.4,340.9,484.4c341.5,484.4,342.1,484.6,342.4,484.9c343.0,485.6,374.0,485.7,374.6,484.9|m479.7,484.9c480.1,484.6,480.8,484.4,481.2,484.4c481.5,484.4,481.9,484.1,482.1,483.9c482.3,483.6,482.5,483.3,482.7,483.3c483.1,483.3,484.7,482.0,485.4,481.0c485.8,480.5,486.4,479.2,486.7,478.2c487.0,477.1,487.4,475.9,487.6,475.5c487.8,474.9,487.8,467.8,487.8,451.1l487.8,427.5l487.2,426.2c486.8,425.5,486.2,424.5,485.7,424.0l484.8,423.1l450.0,423.1c422.5,423.1,415.2,423.1,414.9,423.5c414.8,423.7,414.5,423.9,414.3,423.9c414.1,423.9,413.6,424.4,413.2,425.0l412.5,426.0l412.5,453.1c412.5,480.8,412.5,480.2,413.3,482.7c413.4,482.9,413.7,483.2,414.0,483.3c414.3,483.3,414.6,483.6,414.7,483.9c414.9,484.1,415.2,484.4,415.4,484.4c415.6,484.4,416.1,484.6,416.4,484.9c417.3,485.6,478.4,485.6,479.7,484.9|m582.4,484.9c582.8,484.6,583.4,484.4,583.7,484.4c584.3,484.4,585.5,482.7,585.5,482.0c585.5,481.7,585.6,481.2,585.8,481.0c586.0,480.7,586.1,477.6,586.2,468.9c586.3,460.2,586.4,457.2,586.6,456.8c586.8,456.5,586.9,455.2,586.9,452.8c586.9,450.3,586.8,449.0,586.6,448.7c586.4,448.4,586.3,445.4,586.2,437.2c586.1,425.1,586.1,425.1,584.6,423.7c584.0,423.1,582.5,423.0,553.1,422.9c536.1,422.9,520.4,422.9,518.1,423.1l514.1,423.3l512.8,425.1l511.6,427.0l511.6,451.2c511.6,467.0,511.7,475.5,511.8,475.6c511.9,475.7,512.0,476.4,512.0,477.0c512.0,478.1,512.3,478.6,513.7,480.8c514.6,482.2,515.6,483.3,515.8,483.3c516.0,483.3,516.3,483.6,516.5,483.9c516.7,484.2,517.2,484.4,517.9,484.4c518.5,484.4,519.2,484.6,519.5,484.9c520.4,485.6,581.1,485.6,582.4,484.9|m598.4,484.9c598.7,484.2,599.5,484.2,600.1,484.9c600.8,485.7,626.1,485.6,627.0,484.9c627.4,484.6,628.3,484.4,629.2,484.4c630.1,484.4,631.0,484.6,631.4,484.9c632.3,485.5,635.3,485.6,635.8,485.0c636.0,484.6,638.7,484.5,647.4,484.4l658.7,484.3l659.6,483.0l660.5,481.7l660.7,476.8c660.9,470.4,660.9,437.2,660.7,430.8l660.5,425.9l659.6,424.5l658.8,423.1l628.7,422.9c612.2,422.9,596.9,422.9,594.7,423.1l590.6,423.3l589.7,424.7l588.8,426.1l588.8,453.0c588.8,477.3,588.8,480.1,589.2,481.1c589.4,481.6,589.6,482.4,589.7,482.7c589.8,482.9,590.1,483.2,590.4,483.3c590.6,483.3,591.0,483.6,591.1,483.9c591.3,484.1,591.7,484.4,592.0,484.4c592.4,484.4,592.9,484.6,593.1,484.9c593.8,485.6,598.0,485.6,598.4,484.9|m730.0,484.9c730.4,484.6,731.4,484.4,732.0,484.4c732.9,484.4,733.4,484.2,733.6,483.9c733.7,483.6,734.0,483.3,734.2,483.3c734.7,483.3,737.3,479.6,737.3,478.8c737.3,478.5,737.5,478.1,737.7,477.8c737.9,477.6,738.0,477.2,738.0,476.8c738.0,476.5,738.1,476.1,738.3,475.8c738.5,475.5,738.6,470.1,738.6,451.3c738.6,424.3,738.8,426.8,736.8,424.3l735.8,423.1l704.9,422.9c687.9,422.9,672.2,422.9,670.0,423.1l665.9,423.3l664.6,425.1l663.3,426.9l663.2,450.2c663.2,463.1,663.2,475.2,663.3,477.1l663.4,480.7l664.7,482.5c665.6,483.8,666.2,484.4,666.6,484.4c667.0,484.4,667.5,484.6,667.8,484.9c668.7,485.6,728.7,485.6,730.0,484.9|m836.6,484.9c836.9,484.6,837.4,484.4,837.5,484.4c838.0,484.4,839.8,481.5,839.8,480.7c839.8,480.3,839.9,479.4,840.1,478.7c840.4,477.7,840.5,474.2,840.4,452.9c840.3,425.4,840.4,426.5,838.7,424.4l837.9,423.3l833.8,423.1c831.6,422.9,815.9,422.9,798.9,422.9l768.0,423.1l767.2,424.0c766.7,424.6,766.0,425.6,765.7,426.3l765.1,427.6l765.2,451.4c765.3,468.4,765.4,475.8,765.6,477.0c765.8,478.5,766.1,479.0,767.5,481.0c768.5,482.3,769.4,483.3,769.5,483.3c769.6,483.3,769.9,483.6,770.1,483.9c770.2,484.2,770.7,484.4,771.3,484.4c771.9,484.4,772.7,484.6,773.1,484.9c774.3,485.6,835.6,485.6,836.6,484.9|m878.9,485.0c879.7,484.3,887.3,484.4,887.8,485.0c888.1,485.4,888.3,485.4,888.6,484.9c889.0,484.4,889.1,484.4,889.4,484.9c889.8,485.6,909.8,485.6,910.5,484.9c910.8,484.6,911.4,484.4,912.0,484.4c913.0,484.4,913.2,484.2,914.3,482.6c915.2,481.4,915.6,480.5,915.6,479.9c915.6,479.4,915.7,478.6,915.9,478.1c916.4,476.6,916.4,429.2,915.9,428.2c915.7,427.9,915.6,427.2,915.6,426.7c915.6,426.1,915.2,425.3,914.6,424.4l913.7,423.1l879.5,423.1l845.3,423.1l844.5,423.9c844.1,424.3,843.4,425.3,843.0,426.1l842.3,427.4l842.3,453.1c842.3,475.1,842.4,478.8,842.7,479.7c842.9,480.2,843.0,480.9,843.0,481.1c843.0,481.3,843.5,482.1,844.0,482.9c844.9,484.1,845.2,484.4,846.0,484.4c846.5,484.4,847.2,484.6,847.5,484.9c848.3,485.6,878.1,485.6,878.9,485.0|m927.7,485.0c928.1,484.3,939.9,484.4,940.4,485.0c940.7,485.3,940.9,485.3,941.5,484.8c942.1,484.2,942.2,484.2,943.0,484.8c943.8,485.4,945.4,485.4,963.8,485.4c980.6,485.4,983.8,485.3,984.3,484.9c984.6,484.6,985.3,484.4,985.9,484.4c986.4,484.4,987.0,484.2,987.1,483.9c987.3,483.6,987.5,483.3,987.7,483.3c988.7,483.3,991.6,480.0,991.6,478.8c991.6,478.5,991.7,478.1,991.9,477.8c992.1,477.6,992.3,476.9,992.3,476.3c992.3,475.7,992.4,475.0,992.6,474.8c992.8,474.5,992.9,469.3,992.9,451.2c992.9,433.2,992.8,428.0,992.6,427.6c992.4,427.4,992.3,426.9,992.3,426.6c992.3,426.3,991.9,425.4,991.4,424.7l990.5,423.3l986.4,423.1c984.2,422.9,968.5,422.9,951.7,422.9l921.0,423.1l920.0,424.3c918.1,426.8,918.2,424.1,918.2,453.2c918.2,473.5,918.3,479.3,918.5,479.6c918.7,479.8,918.8,480.4,918.8,480.7c918.8,481.6,920.6,484.4,921.2,484.4c921.4,484.4,921.7,484.6,921.9,484.9c922.3,485.6,927.2,485.6,927.7,485.0|m79.6,419.1l80.4,418.1l80.5,397.1c80.6,381.1,80.7,375.8,80.9,375.2c81.3,374.1,81.3,367.1,80.8,366.5c80.6,366.3,80.5,365.8,80.5,365.3c80.5,364.8,80.1,364.1,79.5,363.3c78.7,362.3,78.3,362.1,77.1,361.9c76.3,361.8,60.6,361.7,42.1,361.8c10.1,361.9,8.5,361.9,7.9,362.5c7.6,362.9,7.1,363.6,6.9,364.1c6.5,364.9,6.4,366.4,6.4,390.3c6.4,409.2,6.5,415.8,6.7,416.4c6.9,416.8,7.0,417.5,7.1,417.9c7.1,418.3,7.5,418.9,7.9,419.3l8.7,420.1l43.8,420.1l78.8,420.1l79.6,419.1|m154.8,419.2c156.3,417.1,156.3,417.7,156.3,391.5c156.3,369.0,156.2,367.7,155.8,366.0c155.2,363.8,154.0,362.2,152.6,361.9c151.2,361.7,87.4,361.7,86.0,361.9c85.2,362.1,84.6,362.5,84.0,363.3l83.0,364.5l83.0,390.9l83.0,417.3l84.1,418.7l85.1,420.1l119.6,420.1l154.1,420.1l154.8,419.2|m232.7,419.3c234.0,417.6,234.0,417.4,234.1,390.5l234.2,365.8l232.9,364.0c231.9,362.5,231.5,362.2,230.5,362.0c229.1,361.7,163.2,361.7,161.8,361.9c160.6,362.2,158.8,364.1,158.8,365.2c158.8,365.5,158.7,366.2,158.5,366.8c158.2,367.6,158.1,371.0,158.1,391.1c158.1,411.2,158.2,414.6,158.5,415.4c158.7,416.0,158.8,416.6,158.8,416.9c158.8,417.1,159.3,417.9,159.9,418.7l160.9,420.1l196.5,420.1l232.0,420.1l232.7,419.3|m333.6,418.8l334.6,417.5l334.6,391.2c334.6,366.4,334.6,364.9,334.2,364.1c334.0,363.6,333.5,362.9,333.1,362.5c332.5,361.9,331.0,361.9,297.6,361.9l262.7,361.9l262.0,362.9c261.6,363.5,261.3,364.2,261.3,364.5c261.3,364.8,261.2,365.2,261.0,365.5c260.6,366.1,260.6,414.5,261.0,415.7c261.1,416.2,261.3,417.0,261.3,417.5c261.4,418.3,261.6,418.8,262.2,419.3l263.0,420.1l297.8,420.1l332.6,420.1l333.6,418.8|m408.8,418.6l409.8,417.1l409.8,391.1l409.8,365.0l408.9,363.4l408.0,361.9l373.2,361.8c347.3,361.7,338.3,361.8,338.1,362.1c337.9,362.3,337.8,362.8,337.8,363.3c337.8,363.7,337.5,364.4,337.2,364.8l336.6,365.6l336.6,390.8l336.6,416.1l337.2,417.3c337.6,417.9,338.2,418.8,338.7,419.3l339.5,420.1l373.7,420.1l407.8,420.1l408.8,418.6|m486.7,418.6l487.8,417.1l487.8,391.7c487.8,371.8,487.8,366.1,487.5,365.8c487.4,365.6,487.3,365.0,487.3,364.6c487.3,364.2,486.9,363.5,486.5,362.9l485.8,361.9l450.2,361.9c416.2,361.9,414.6,361.9,414.0,362.5c413.6,362.9,413.2,363.6,412.9,364.1c412.5,364.9,412.5,366.4,412.5,391.2l412.5,417.5l413.5,418.8l414.6,420.1l450.1,420.1l485.6,420.1l486.7,418.6|m585.1,418.8l586.1,417.5l586.2,397.2c586.3,381.6,586.4,376.8,586.6,376.5c587.0,375.8,587.0,369.0,586.5,368.1c586.4,367.7,586.2,366.8,586.2,366.0c586.2,364.7,586.1,364.4,585.2,363.3c584.4,362.3,584.0,362.1,582.8,361.9c582.1,361.8,566.1,361.7,547.4,361.8l513.4,361.9l512.7,363.0c512.4,363.6,512.0,364.4,512.0,364.8c512.0,365.2,511.9,365.6,511.8,365.7c511.7,365.8,511.6,374.7,511.6,391.1c511.6,407.5,511.7,416.4,511.8,416.5c511.9,416.6,512.0,417.0,512.0,417.4c512.0,417.7,512.4,418.5,512.9,419.1l513.7,420.1l548.9,420.1l584.0,420.1l585.1,418.8|m658.9,419.6c659.3,419.3,659.9,418.6,660.2,418.0l660.7,416.9l660.7,390.9l660.7,364.8l659.7,363.4l658.7,361.9l626.1,361.8c608.2,361.7,592.9,361.8,592.1,361.9c590.7,362.1,590.5,362.3,589.7,363.5l588.8,364.9l588.8,391.0l588.8,417.2l589.8,418.6l590.9,420.1l624.6,420.1c653.9,420.1,658.4,420.1,658.9,419.6|m736.8,419.6c737.1,419.4,737.7,418.8,738.0,418.2l738.6,417.3l738.6,391.6c738.6,371.5,738.5,365.8,738.3,365.5c738.1,365.2,738.0,364.8,738.0,364.5c738.0,364.2,737.7,363.5,737.3,362.9l736.6,361.9l701.4,361.9c672.2,361.9,666.2,362.0,665.6,362.4c665.2,362.6,664.8,362.9,664.6,363.1c664.4,363.2,664.2,363.5,664.1,363.8c663.3,366.3,663.3,365.8,663.3,391.8c663.3,416.8,663.3,417.3,663.7,418.1c664.0,418.5,664.5,419.1,664.9,419.5c665.6,420.1,667.0,420.1,700.9,420.1c730.7,420.1,736.3,420.1,736.8,419.6|m839.0,418.3l840.4,416.4l840.3,391.7c840.3,364.2,840.4,365.4,838.7,363.2c838.0,362.3,837.6,362.1,836.4,361.9c835.6,361.8,819.8,361.7,801.2,361.8l767.4,361.9l766.6,362.7c765.1,364.3,765.1,364.1,765.2,392.2l765.3,417.4l766.2,418.8l767.2,420.1l802.5,420.1l837.7,420.1l839.0,418.3|m914.1,419.4c914.5,419.0,915.2,418.1,915.5,417.4l916.3,416.1l916.3,391.6c916.3,367.8,916.2,367.1,915.8,365.7c915.5,364.9,915.0,363.7,914.5,363.1l913.7,361.9l879.1,361.9c845.9,361.9,844.5,361.9,843.9,362.5c843.6,362.9,843.1,363.7,842.8,364.3c842.3,365.4,842.3,365.8,842.4,391.5l842.5,417.5l843.5,418.8l844.5,420.1l878.9,420.1c913.2,420.1,913.3,420.1,914.1,419.4|m991.4,419.3c991.8,418.9,992.2,418.3,992.2,417.9c992.3,417.5,992.4,416.8,992.6,416.4c992.8,415.8,992.9,409.3,992.9,390.8l992.9,366.0l992.2,364.7c991.9,364.1,991.2,363.1,990.8,362.7l990.1,361.9l955.2,361.9l920.3,361.9l919.5,362.9c919.2,363.5,918.8,364.2,918.8,364.5c918.8,364.8,918.7,365.2,918.5,365.5c918.3,365.8,918.2,371.4,918.2,391.4c918.2,416.1,918.3,416.9,918.7,417.9c919.0,418.4,919.5,419.1,919.9,419.5c920.6,420.1,921.9,420.1,955.6,420.1l990.6,420.1l991.4,419.3|m77.5,358.8c78.8,358.5,80.5,356.6,80.5,355.4c80.5,355.0,80.6,354.4,80.8,354.2c81.0,353.9,81.2,353.2,81.2,352.3c81.2,351.4,81.0,350.7,80.8,350.4c80.5,350.0,80.5,348.7,80.5,342.3c80.5,335.9,80.5,334.6,80.8,334.2c81.3,333.6,81.3,329.0,80.8,328.4c80.4,327.9,80.4,325.4,80.8,324.1c81.3,322.7,81.3,313.4,80.8,312.4c80.5,311.8,80.6,311.7,80.9,311.2c81.2,310.7,81.2,310.5,80.9,310.0c80.7,309.6,80.7,309.4,80.9,309.1c81.3,308.5,81.2,304.5,80.8,304.0c80.6,303.8,80.5,303.3,80.5,303.0c80.5,302.1,79.3,300.8,78.0,300.1c76.9,299.6,74.5,299.6,44.6,299.6c19.2,299.7,12.4,299.8,12.1,300.2c12.0,300.4,11.5,300.6,11.1,300.6c10.7,300.6,10.2,300.9,9.9,301.3c9.7,301.7,9.1,302.2,8.7,302.5c8.3,302.7,7.9,303.2,7.8,303.6c7.6,304.5,7.5,304.8,7.3,305.4c7.2,305.7,6.9,306.3,6.8,306.8c6.5,307.5,6.4,311.4,6.4,328.8c6.3,340.4,6.3,351.3,6.4,353.1c6.6,356.1,6.6,356.3,7.4,357.4c7.9,358.2,8.5,358.6,8.9,358.7c10.2,359.0,76.3,359.0,77.5,358.8|m154.3,357.8c154.8,357.2,155.4,356.1,155.7,355.3c156.1,354.0,156.1,353.3,156.1,329.8l156.1,305.6l155.4,303.2c154.9,301.9,154.4,300.8,154.2,300.7c154.0,300.6,153.6,300.4,153.3,300.1c153.0,299.8,144.7,299.7,120.0,299.6c89.9,299.5,87.0,299.6,86.1,300.1c84.8,300.8,84.1,301.7,83.5,303.5c83.1,304.8,83.0,305.9,83.0,329.8c83.0,354.2,83.1,354.8,83.5,356.2c83.8,357.0,84.2,357.7,84.4,357.8c84.6,357.9,85.0,358.1,85.3,358.3c85.5,358.5,85.9,358.7,86.2,358.8c86.5,358.8,101.7,358.9,120.0,358.9l153.4,358.8l154.3,357.8|m232.8,358.0c233.2,357.5,233.5,356.7,233.6,356.2c233.7,355.7,233.8,355.1,233.9,355.0c234.1,354.9,234.2,345.6,234.2,332.0c234.2,312.6,234.1,309.1,233.8,308.0c233.6,307.3,233.5,306.5,233.5,306.1c233.5,305.1,230.2,300.6,229.6,300.6c229.3,300.6,228.7,300.4,228.2,300.1c227.5,299.6,223.2,299.6,194.9,299.6c174.1,299.6,162.2,299.7,161.8,299.9c161.0,300.3,158.8,303.3,158.8,303.9c158.8,304.1,158.7,304.7,158.5,305.3c158.2,306.1,158.1,309.6,158.1,329.6c158.1,349.7,158.2,353.1,158.5,354.0c158.7,354.5,158.8,355.2,158.8,355.6c158.8,356.4,160.6,358.6,161.4,358.7c161.7,358.8,177.8,358.9,197.1,358.8l232.2,358.8l232.8,358.0|m333.1,358.2c333.5,357.8,334.0,357.1,334.2,356.6c334.6,355.8,334.6,354.3,334.6,329.8l334.6,303.8l334.0,302.6c333.6,301.9,333.0,301.0,332.6,300.5l331.8,299.7l299.7,299.6c271.5,299.6,267.5,299.6,266.8,300.1c266.3,300.4,265.6,300.6,265.3,300.6c264.8,300.6,264.3,301.1,263.3,302.6c262.6,303.7,262.0,304.8,262.0,305.1c262.0,305.4,261.8,305.8,261.6,306.1c261.4,306.3,261.3,307.0,261.3,307.6c261.3,308.2,261.2,308.9,261.0,309.1c260.8,309.5,260.7,314.4,260.7,331.7c260.7,348.9,260.8,353.9,261.0,354.2c261.2,354.5,261.3,354.9,261.3,355.2c261.3,356.2,263.0,358.6,263.9,358.7c264.3,358.8,279.9,358.9,298.6,358.8c331.0,358.8,332.5,358.8,333.1,358.2|m408.9,357.3l409.8,355.7l409.8,329.7l409.8,303.6l408.6,301.7l407.3,299.7l374.5,299.6c356.4,299.6,341.2,299.6,340.6,299.7c339.7,299.9,339.3,300.3,338.1,302.2l336.6,304.5l336.6,329.3c336.6,350.9,336.7,354.1,337.0,354.5c337.2,354.8,337.3,355.2,337.3,355.5c337.3,356.4,339.0,358.6,339.8,358.7c340.2,358.8,355.7,358.9,374.2,358.8l408.0,358.8l408.9,357.3|m486.8,357.4l487.7,355.9l487.8,345.7c488.0,334.1,487.8,308.1,487.5,307.2c487.4,306.9,487.1,305.9,486.8,305.0c486.1,302.7,484.3,300.6,483.0,300.6c482.8,300.6,482.3,300.4,481.8,300.1c481.1,299.6,476.9,299.6,448.8,299.6c418.0,299.6,416.7,299.6,415.5,300.2c414.8,300.6,413.8,301.4,413.4,302.1l412.5,303.3l412.5,328.7c412.5,349.7,412.6,354.3,412.8,355.5c413.3,357.5,413.5,358.0,414.1,358.0c414.4,358.0,414.7,358.1,414.9,358.3c415.0,358.4,415.4,358.7,415.7,358.7c416.0,358.8,431.9,358.9,451.1,358.9l485.9,358.8l486.8,357.4|m583.4,358.8c583.9,358.6,584.7,358.0,585.3,357.4c586.0,356.4,586.2,355.9,586.2,355.0c586.2,354.4,586.4,353.7,586.5,353.5c587.0,353.0,587.0,350.7,586.6,350.1c586.4,349.8,586.3,345.1,586.3,329.3c586.3,313.4,586.4,308.8,586.6,308.4c587.0,307.8,587.0,305.6,586.5,305.0c586.4,304.8,586.2,304.3,586.2,304.0c586.2,303.1,583.7,300.0,582.9,299.7c582.4,299.6,567.5,299.6,549.6,299.6l517.1,299.7l515.6,300.8c513.9,302.0,513.1,303.1,512.4,305.2c512.2,306.0,511.9,306.9,511.8,307.2c511.7,307.5,511.6,318.3,511.6,331.1c511.6,355.9,511.6,356.0,512.7,357.8c513.0,358.2,513.6,358.7,514.0,358.7c515.2,359.0,582.5,359.0,583.4,358.8|m659.7,357.3l660.7,355.9l660.8,331.7c660.9,311.4,660.9,307.4,661.2,307.1c661.6,306.6,661.6,305.6,661.2,305.0c661.0,304.8,660.8,304.2,660.8,303.7c660.8,302.3,659.7,300.8,658.3,300.1c657.1,299.6,654.1,299.6,624.6,299.6c588.3,299.6,591.5,299.3,589.7,302.2l588.8,303.7l588.8,329.7l588.8,355.8l589.7,357.2c590.2,358.0,590.9,358.7,591.3,358.7c591.6,358.8,607.0,358.9,625.3,358.8l658.7,358.8l659.7,357.3|m737.1,358.2c737.5,357.8,737.9,357.1,738.2,356.6c738.6,355.8,738.6,354.3,738.6,331.1c738.6,311.8,738.5,306.4,738.3,306.0c738.1,305.8,738.0,305.4,738.0,305.1c738.0,304.1,735.4,300.6,734.7,300.6c734.4,300.6,733.7,300.4,733.3,300.1c732.5,299.6,728.3,299.6,699.9,299.6c663.6,299.5,666.2,299.4,664.3,302.0c663.5,303.1,663.5,303.4,663.3,305.9c663.1,309.4,663.1,349.1,663.3,352.6c663.5,355.3,663.5,355.3,664.6,357.0c665.4,358.0,666.1,358.7,666.5,358.7c666.9,358.8,682.8,358.9,701.9,358.8c734.9,358.8,736.5,358.8,737.1,358.2|m838.5,357.8c839.4,356.7,839.5,356.5,840.1,354.5c840.4,353.4,840.5,350.4,840.5,329.2c840.5,308.6,840.4,305.1,840.1,304.2c839.9,303.7,839.8,303.1,839.8,302.8c839.8,302.3,838.5,300.6,838.1,300.6c837.9,300.6,837.6,300.4,837.5,300.2c837.2,299.8,830.2,299.7,803.9,299.7l770.6,299.7l769.1,300.8c767.2,302.2,766.0,304.0,765.6,306.1c765.4,307.2,765.3,313.3,765.2,330.8c765.1,352.3,765.2,354.1,765.6,355.7c765.8,356.6,766.1,357.5,766.3,357.6c767.2,358.2,767.9,358.6,768.4,358.8c768.7,358.8,784.4,358.9,803.3,358.9l837.6,358.8l838.5,357.8|m914.3,358.1c914.7,357.7,915.3,356.5,915.6,355.5l916.3,353.6l916.3,329.7l916.3,305.8l915.7,304.2c915.4,303.3,915.1,302.3,915.1,302.0c915.1,301.2,914.8,300.9,913.3,300.1c912.2,299.6,909.8,299.6,878.9,299.6c852.7,299.7,845.6,299.8,845.3,300.2c845.2,300.4,844.9,300.6,844.7,300.6c844.5,300.6,843.9,301.2,843.4,302.0l842.5,303.4l842.4,328.8c842.3,353.5,842.3,354.3,842.8,355.3c843.5,357.0,844.7,358.6,845.5,358.7c845.9,358.8,861.4,358.9,879.9,358.8l913.6,358.8l914.3,358.1|m990.8,358.0c991.2,357.6,991.9,356.7,992.2,356.0l992.9,354.7l992.9,331.1c992.9,312.7,992.8,307.4,992.6,307.1c992.4,306.8,992.3,306.4,992.3,306.1c992.3,305.7,992.1,305.3,991.9,305.0c991.7,304.8,991.6,304.4,991.6,304.0c991.6,303.3,990.6,302.0,989.4,301.1c988.8,300.8,988.2,300.3,988.0,300.1c987.6,299.8,978.8,299.7,955.0,299.6c924.8,299.6,922.4,299.6,921.3,300.1c919.9,300.8,918.8,302.1,918.8,303.2c918.8,303.6,918.7,304.1,918.5,304.3c918.2,304.8,918.0,338.0,918.2,348.5l918.4,355.3l919.5,357.0c920.2,357.9,920.9,358.6,921.3,358.7c921.7,358.8,937.3,358.9,956.0,358.8l990.1,358.8l990.8,358.0|m57.8,278.1l57.8,264.9l63.6,264.9c67.0,264.9,69.5,265.0,69.6,265.2c69.7,265.4,70.2,265.6,70.8,265.7c71.4,265.8,72.1,266.1,72.3,266.2c72.6,266.4,72.9,266.6,73.0,266.6c73.5,266.6,75.3,269.4,75.3,270.1c75.3,270.5,75.5,271.3,75.7,271.9c76.0,273.0,76.0,273.2,75.7,274.3c75.5,274.9,75.3,275.7,75.3,276.1c75.3,277.4,73.0,280.3,72.0,280.3c71.4,280.3,70.6,281.3,70.6,282.0c70.6,282.3,71.0,283.0,71.3,283.8c71.7,284.5,72.0,285.2,72.0,285.4c72.0,285.6,72.9,287.0,73.9,288.5l75.8,291.3l74.9,291.3c74.1,291.3,73.8,291.1,73.1,289.8c72.7,289.0,72.3,288.1,72.3,287.8c72.3,287.3,69.3,282.9,68.3,281.9c67.8,281.4,67.0,281.3,63.6,281.3c60.7,281.3,59.4,281.5,59.2,281.8c59.0,282.0,58.9,283.6,58.9,286.7l58.9,291.3l58.4,291.3l57.8,291.3l57.8,278.1|m111.1,291.0c111.1,290.9,111.4,290.3,111.8,289.8c112.2,289.2,112.5,288.5,112.5,288.2c112.5,287.9,112.7,287.4,112.9,287.2c113.1,287.0,113.2,286.5,113.2,286.2c113.2,285.9,113.5,285.2,113.9,284.6c114.3,284.1,114.6,283.4,114.6,283.0c114.6,282.7,114.8,282.3,115.0,282.0c115.2,281.8,115.3,281.3,115.3,281.0c115.3,280.7,115.5,280.2,115.7,280.0c115.9,279.7,116.0,279.4,116.0,279.2c116.0,279.0,116.3,278.3,116.7,277.6c117.1,276.9,117.4,276.1,117.4,275.9c117.4,275.8,117.6,275.3,117.9,275.0c118.4,274.3,119.3,271.9,119.3,271.2c119.3,271.0,119.6,270.4,120.0,269.8c120.4,269.3,120.7,268.6,120.7,268.3c120.7,268.0,120.9,267.5,121.1,267.3c121.2,267.0,121.4,266.6,121.4,266.3c121.4,265.9,121.5,265.5,121.7,265.3c122.1,264.7,123.3,264.7,123.3,265.3c123.3,265.6,123.6,266.2,124.0,266.7c124.4,267.3,124.7,268.0,124.7,268.3c124.7,268.6,125.0,269.3,125.4,269.8c125.8,270.4,126.1,271.0,126.1,271.2c126.1,271.9,127.0,274.3,127.5,275.0c127.7,275.3,128.0,275.8,128.0,276.0c128.0,276.3,128.1,276.6,128.3,276.9c128.5,277.1,128.7,277.6,128.7,277.9c128.7,278.2,128.8,278.7,129.0,278.9c129.2,279.2,129.4,279.6,129.4,280.0c129.4,280.3,129.7,281.0,130.1,281.5c130.4,282.1,130.8,282.8,130.8,283.1c130.8,283.4,131.1,284.1,131.5,284.6c131.8,285.2,132.2,285.9,132.2,286.2c132.2,286.5,132.3,287.0,132.5,287.2c132.7,287.4,132.9,287.9,132.9,288.2c132.9,288.5,133.2,289.2,133.6,289.8c134.4,291.0,134.4,291.3,133.6,291.3c132.9,291.3,132.4,290.8,132.4,289.9c132.4,289.6,132.2,289.1,132.0,288.9c131.9,288.7,131.7,288.2,131.7,287.9c131.7,287.5,131.5,287.1,131.3,286.8c131.2,286.6,131.0,286.1,131.0,285.8c131.0,285.5,130.6,284.8,130.2,284.3l129.4,283.4l122.7,283.4l116.0,283.4l115.2,284.3c114.7,284.8,114.4,285.5,114.4,285.8c114.4,286.1,114.2,286.6,114.0,286.8c113.8,287.1,113.7,287.5,113.7,287.9c113.7,288.2,113.4,288.9,113.0,289.4c112.6,290.0,112.3,290.6,112.3,290.9c112.3,291.1,112.0,291.3,111.7,291.3c111.4,291.3,111.1,291.2,111.1,291.0|m177.5,278.1c177.5,265.6,177.6,264.8,178.0,264.9c178.3,265.0,178.4,265.6,178.6,267.8c178.8,271.5,178.6,283.4,178.3,283.9c178.1,284.1,178.0,285.6,178.0,287.8c178.0,289.9,177.9,291.3,177.8,291.3c177.6,291.3,177.5,286.7,177.5,278.1|m310.9,278.6c310.9,271.7,310.9,265.7,311.0,265.4c311.1,264.9,311.9,264.9,316.7,264.9c320.0,264.9,322.4,265.0,322.4,265.2c322.5,265.4,323.1,265.6,323.7,265.7c324.3,265.8,325.0,266.1,325.2,266.2c325.4,266.4,325.7,266.6,325.9,266.6c326.3,266.6,328.4,269.7,328.4,270.2c328.4,270.4,328.6,271.1,328.8,271.6c329.0,272.1,329.1,273.0,329.1,273.6c329.1,275.4,327.6,279.3,326.8,279.3c326.6,279.3,326.2,279.5,326.1,279.8c325.9,280.1,325.5,280.3,325.0,280.3c324.3,280.3,323.5,281.2,323.5,282.1c323.5,282.4,324.0,283.3,324.6,284.1c325.1,284.9,325.6,285.8,325.6,286.1c325.6,286.4,326.3,287.7,327.2,289.0c328.7,291.2,328.7,291.3,328.1,291.3c327.7,291.3,327.3,290.9,326.7,290.0c326.3,289.3,325.2,287.5,324.2,286.0c323.2,284.4,322.3,283.0,322.3,282.7c322.3,281.5,321.9,281.3,317.1,281.3c313.7,281.3,312.3,281.5,312.1,281.8c311.9,282.0,311.8,283.6,311.8,286.7c311.8,291.1,311.8,291.3,311.3,291.3c310.9,291.3,310.9,291.1,310.9,278.6|m364.7,291.0c364.7,290.8,364.8,290.5,365.0,290.3c365.2,290.0,365.4,289.6,365.4,289.2c365.4,288.9,365.5,288.5,365.7,288.2c365.9,288.0,366.1,287.5,366.1,287.2c366.1,286.9,366.4,286.2,366.8,285.6c367.2,285.1,367.5,284.5,367.5,284.3c367.5,284.2,367.8,283.4,368.2,282.7c368.6,282.0,368.9,281.3,368.9,281.1c368.9,280.9,369.0,280.6,369.2,280.3c369.4,280.1,369.6,279.6,369.6,279.3c369.6,279.0,369.9,278.3,370.3,277.7c370.7,277.2,371.0,276.5,371.0,276.2c371.0,275.9,371.2,275.4,371.3,275.2c371.5,274.9,371.7,274.5,371.7,274.2c371.7,273.8,372.0,273.2,372.3,272.8c372.6,272.3,372.9,271.7,372.9,271.4c372.9,271.0,373.0,270.6,373.2,270.4c373.4,270.1,373.6,269.7,373.6,269.3c373.6,269.0,373.9,268.3,374.3,267.8c374.7,267.2,375.0,266.5,375.0,266.2c375.0,265.9,375.1,265.5,375.3,265.3c375.6,264.7,376.8,264.7,376.8,265.3c376.8,265.6,377.2,266.2,377.5,266.7c377.9,267.3,378.2,268.0,378.2,268.3c378.2,268.7,378.4,269.0,378.5,269.2c378.7,269.4,379.6,272.1,379.6,272.6c379.6,272.8,379.9,273.3,380.2,273.8c380.5,274.3,381.1,275.4,381.4,276.4c381.7,277.3,382.2,278.4,382.4,278.8c382.7,279.1,382.9,279.6,382.9,279.8c382.9,280.0,383.2,280.9,383.6,281.6c384.0,282.4,384.3,283.2,384.3,283.4c384.3,283.5,384.5,283.9,384.7,284.1c384.9,284.3,385.0,284.8,385.0,285.1c385.0,285.4,385.3,286.1,385.7,286.7c386.1,287.2,386.4,287.9,386.4,288.2c386.4,288.6,386.6,289.0,386.8,289.2c387.3,289.8,387.4,291.3,386.9,291.3c386.4,291.3,386.0,290.6,386.0,289.9c386.0,289.6,385.6,288.9,385.3,288.4c384.9,287.8,384.6,287.2,384.6,287.0c384.6,286.8,384.3,285.9,384.0,285.1l383.5,283.6l376.5,283.5l369.6,283.4l368.8,284.3c368.3,284.8,368.0,285.4,368.0,285.7c368.0,286.0,367.6,286.8,367.3,287.5c366.9,288.2,366.5,289.0,366.5,289.3c366.5,290.1,365.7,291.3,365.2,291.3c364.9,291.3,364.7,291.2,364.7,291.0|m431.1,278.1c431.1,265.6,431.1,264.8,431.5,264.9c432.1,265.1,432.2,267.2,432.3,280.1l432.3,291.3l431.7,291.3l431.1,291.3l431.1,278.1|m559.5,279.5c559.6,273.1,559.6,267.2,559.7,266.4l559.9,265.0l565.5,264.9c568.8,264.9,571.2,265.0,571.3,265.2c571.5,265.4,572.1,265.6,572.6,265.7c573.2,265.9,574.1,266.2,574.5,266.5c575.5,267.1,577.1,269.3,577.1,270.0c577.1,270.4,577.2,270.8,577.4,271.0c577.8,271.5,577.9,274.5,577.5,275.1c577.2,275.5,576.7,276.8,576.5,277.7c576.4,278.0,576.2,278.3,576.1,278.3c576.0,278.3,575.6,278.7,575.1,279.3c574.6,279.9,574.1,280.3,573.6,280.3c572.2,280.3,571.9,282.3,573.1,283.9c573.5,284.5,573.8,285.1,573.8,285.4c573.8,285.6,574.6,287.1,575.6,288.6l577.4,291.3l576.6,291.3c575.7,291.3,574.7,290.2,574.7,289.2c574.7,288.9,573.6,287.0,572.2,285.0l569.7,281.3l565.5,281.3c562.5,281.3,561.2,281.5,561.0,281.8c560.8,282.0,560.7,283.6,560.7,286.7l560.7,291.3l560.1,291.3l559.5,291.3l559.5,279.5|m614.3,291.0c614.3,290.8,614.4,290.5,614.6,290.3c614.8,290.0,615.0,289.6,615.0,289.2c615.0,288.9,615.1,288.5,615.3,288.2c615.5,288.0,615.7,287.5,615.7,287.2c615.7,286.9,615.9,286.3,616.2,286.0c616.4,285.6,617.0,284.4,617.3,283.2c617.7,282.1,618.2,280.8,618.5,280.5c618.7,280.1,618.9,279.7,618.9,279.4c618.9,279.2,619.2,278.5,619.6,277.8c619.9,277.2,620.4,276.1,620.7,275.3c620.9,274.6,621.4,273.4,621.8,272.7c622.2,272.0,622.5,271.3,622.5,271.1c622.5,270.9,622.6,270.6,622.8,270.4c623.0,270.1,623.2,269.7,623.2,269.4c623.2,269.1,623.5,268.3,623.8,267.7c624.2,267.0,624.5,266.1,624.6,265.7c624.7,264.6,625.7,264.6,626.5,265.8c626.8,266.3,627.1,267.0,627.1,267.3c627.1,267.6,627.4,268.2,627.7,268.6c628.0,269.1,628.3,269.7,628.3,270.0c628.3,270.3,628.5,270.8,628.7,271.0c628.8,271.3,629.0,271.7,629.0,272.0c629.0,272.4,629.3,273.1,629.7,273.6c630.1,274.2,630.4,274.9,630.4,275.2c630.4,275.5,630.7,276.2,631.1,276.7c631.5,277.3,631.8,278.0,631.8,278.3c631.8,278.6,632.0,279.1,632.2,279.3c632.4,279.5,632.5,280.0,632.5,280.3c632.5,280.6,632.8,281.3,633.2,281.9c633.6,282.4,633.9,283.1,633.9,283.4c633.9,283.7,634.1,284.2,634.3,284.4c634.5,284.7,634.6,285.0,634.6,285.2c634.6,285.4,634.9,286.1,635.3,286.7c635.7,287.4,636.0,288.1,636.0,288.4c636.0,288.7,636.2,289.4,636.5,290.1l637.0,291.4l636.3,291.2c635.9,291.2,635.7,290.9,635.6,290.4c635.6,290.0,635.2,289.2,634.8,288.7c634.5,288.2,634.2,287.5,634.2,287.2c634.2,286.8,634.0,286.4,633.8,286.2c633.6,285.9,633.5,285.4,633.5,285.0c633.5,283.4,633.3,283.4,625.9,283.4l619.0,283.4l618.3,284.3c617.9,284.8,617.5,285.4,617.5,285.7c617.5,285.9,617.3,286.6,616.9,287.3c616.5,287.9,616.0,289.0,615.8,289.8c615.4,290.9,615.2,291.3,614.8,291.3c614.5,291.3,614.3,291.2,614.3,291.0|m681.2,286.7c681.2,283.5,681.1,282.0,680.9,281.7c680.7,281.4,680.6,280.1,680.6,277.4c680.6,274.7,680.7,273.3,680.9,273.1c681.1,272.8,681.2,271.4,681.2,268.7c681.2,266.4,681.3,264.9,681.4,264.9c681.6,264.9,681.6,269.5,681.6,278.1c681.6,286.7,681.6,291.3,681.4,291.3c681.3,291.3,681.2,289.6,681.2,286.7|m813.8,278.1l813.8,264.9l819.3,264.9c822.5,264.9,824.8,265.0,824.9,265.2c825.0,265.4,825.5,265.6,826.1,265.7c826.8,265.8,827.4,266.1,827.7,266.2c827.9,266.4,828.2,266.6,828.4,266.6c828.5,266.6,829.3,267.5,830.0,268.6l831.3,270.5l831.3,273.5l831.3,276.4l830.4,277.8c829.8,278.5,828.9,279.4,828.4,279.8c827.2,280.7,826.0,282.0,826.0,282.5c826.0,282.7,826.5,283.7,827.2,284.6c827.8,285.6,828.5,286.8,828.6,287.4c828.8,287.9,829.4,289.0,830.0,289.8c830.9,291.1,831.0,291.3,830.6,291.3c830.0,291.3,824.8,283.6,824.8,282.7c824.8,281.5,824.3,281.3,819.5,281.3c816.2,281.3,814.7,281.5,814.5,281.8c814.4,282.0,814.3,283.6,814.3,286.7c814.3,289.6,814.2,291.3,814.0,291.3c813.9,291.3,813.8,286.7,813.8,278.1|m868.5,290.5c868.5,290.1,868.8,289.4,869.1,288.9c869.4,288.4,869.9,287.2,870.3,286.1c870.6,285.1,871.1,283.9,871.5,283.4c871.8,283.0,872.0,282.3,872.0,282.0c872.0,281.7,872.2,281.2,872.4,281.0c872.6,280.8,872.7,280.3,872.7,280.0c872.7,279.7,873.0,279.0,873.3,278.6c873.7,278.2,873.9,277.5,873.9,277.2c873.9,276.9,874.1,276.4,874.3,276.2c874.5,276.0,874.6,275.6,874.6,275.4c874.6,275.2,874.9,274.5,875.3,273.8c875.7,273.1,876.0,272.3,876.0,272.0c876.0,271.7,876.2,271.3,876.4,271.0c876.6,270.8,876.7,270.5,876.7,270.3c876.7,270.1,877.0,269.4,877.4,268.6c877.8,267.9,878.1,267.2,878.1,267.1c878.1,266.5,879.4,264.9,879.8,264.9c880.2,264.9,881.2,266.3,881.2,267.0c881.2,267.2,881.5,267.9,881.9,268.5c882.3,269.0,882.6,269.7,882.6,270.0c882.6,270.4,882.7,270.8,882.9,271.0c883.1,271.3,883.3,271.7,883.3,272.0c883.3,272.4,883.6,273.1,884.0,273.6c884.4,274.2,884.7,274.9,884.7,275.2c884.7,275.5,884.8,276.0,885.0,276.2c885.2,276.4,885.4,276.9,885.4,277.2c885.4,277.5,885.7,278.2,886.1,278.8c886.5,279.3,886.8,280.0,886.8,280.3c886.8,280.7,886.9,281.1,887.1,281.3c887.3,281.6,887.5,282.0,887.5,282.4c887.5,282.7,887.8,283.4,888.2,283.9c888.6,284.5,888.9,285.1,888.9,285.3c888.9,285.5,889.2,286.1,889.5,286.5c889.8,286.9,890.1,287.5,890.1,287.8c890.1,288.0,890.3,289.0,890.6,289.8l891.2,291.4l890.7,291.2c890.4,291.2,890.1,290.8,889.9,290.3c889.8,289.9,889.4,289.1,889.0,288.6c888.7,288.1,888.4,287.4,888.4,287.1c888.4,286.8,888.3,286.4,888.1,286.2c887.9,285.9,887.7,285.4,887.7,285.0c887.7,283.4,887.6,283.4,879.8,283.4c872.1,283.4,871.8,283.5,871.8,284.8c871.8,285.1,871.7,285.6,871.5,285.8c871.3,286.0,871.1,286.5,871.1,286.8c871.1,287.1,870.8,287.8,870.4,288.4c870.0,288.9,869.7,289.6,869.7,289.9c869.7,290.7,869.3,291.3,868.7,291.3c868.5,291.3,868.4,291.1,868.5,290.5|m935.8,278.1c935.8,270.7,935.8,267.7,935.8,271.5c935.9,275.2,935.9,281.3,935.8,284.9c935.8,288.5,935.8,285.5,935.8,278.1|m128.6,282.3c129.1,281.6,128.9,280.2,128.2,279.1c127.8,278.6,127.5,278.0,127.5,277.8c127.5,277.6,127.2,277.0,126.9,276.3c126.6,275.7,126.3,275.1,126.3,274.9c126.3,274.7,126.2,274.4,126.0,274.1c125.8,273.9,125.6,273.4,125.6,273.1c125.6,272.8,125.3,272.1,124.9,271.6c124.5,271.0,124.2,270.3,124.2,270.0c124.2,269.8,123.9,269.0,123.5,268.4l122.7,267.3l121.9,268.4c121.5,269.0,121.2,269.7,121.2,270.0c121.2,270.3,120.9,271.0,120.5,271.6c120.1,272.1,119.8,272.8,119.8,273.1c119.8,273.4,119.6,273.9,119.4,274.1c119.2,274.4,119.1,274.7,119.1,274.9c119.1,275.1,118.8,275.7,118.5,276.3c118.2,277.0,117.9,277.6,117.9,277.7c117.9,277.9,117.6,278.6,117.2,279.3c116.4,280.7,116.3,281.6,116.8,282.3c117.0,282.6,118.6,282.7,122.7,282.7c126.8,282.7,128.4,282.6,128.6,282.3|m382.1,282.0c382.5,281.4,382.5,281.3,382.1,280.7c381.9,280.4,381.8,279.9,381.8,279.6c381.8,279.3,381.6,278.8,381.4,278.6c381.2,278.4,381.1,278.0,381.1,277.8c381.1,277.5,380.8,277.0,380.5,276.5c380.1,276.1,379.9,275.5,379.9,275.2c379.9,275.0,379.6,274.2,379.2,273.4c378.8,272.7,378.5,272.0,378.5,271.8c378.5,271.6,378.3,271.3,378.1,271.0c377.9,270.8,377.8,270.4,377.8,270.0c377.8,269.7,377.4,269.0,377.0,268.3l376.2,267.2l375.1,269.0c374.5,269.9,374.0,270.8,374.0,271.1c374.0,271.3,373.7,272.0,373.3,272.6c372.9,273.3,372.6,274.0,372.6,274.3c372.6,274.5,372.5,274.9,372.3,275.2c372.1,275.4,371.9,275.9,371.9,276.2c371.9,276.5,371.7,277.1,371.3,277.6c371.0,278.0,370.8,278.6,370.8,279.0c370.8,279.3,370.6,279.7,370.4,280.0c370.0,280.5,370.0,281.7,370.3,282.3c370.5,282.6,372.2,282.7,376.2,282.7c381.4,282.7,381.7,282.7,382.1,282.0|m631.7,282.1c632.0,281.5,632.0,281.4,631.7,281.0c631.5,280.8,631.3,280.3,631.3,280.0c631.3,279.7,631.0,279.0,630.6,278.4c630.3,277.9,629.9,277.2,629.9,276.9c629.9,276.5,629.8,276.1,629.6,275.9c629.4,275.6,629.2,275.2,629.2,275.0c629.2,274.3,628.5,272.3,627.9,271.4c627.7,270.9,627.4,270.2,627.3,269.8c627.2,269.4,626.8,268.6,626.4,268.1l625.7,267.1l624.7,268.8c624.1,269.7,623.6,270.7,623.6,270.9c623.6,271.1,623.3,271.7,622.9,272.2c622.5,272.8,622.2,273.5,622.2,273.8c622.2,274.1,622.1,274.6,621.9,274.8c621.7,275.1,621.5,275.5,621.5,275.8c621.5,276.1,621.2,276.9,620.8,277.4c620.4,277.9,620.1,278.6,620.1,278.9c620.1,279.2,619.9,279.8,619.8,280.1c619.6,280.5,619.4,281.0,619.4,281.3c619.4,282.6,619.8,282.7,625.6,282.7c630.8,282.7,631.3,282.7,631.7,282.1|m885.9,282.1c886.3,281.5,886.3,281.4,886.0,281.0c885.8,280.8,885.6,280.3,885.6,280.0c885.6,279.7,885.3,279.0,884.9,278.4c884.5,277.9,884.2,277.2,884.2,276.9c884.2,276.5,884.1,276.1,883.9,275.9c883.7,275.6,883.5,275.2,883.5,274.8c883.5,274.5,883.2,273.8,882.8,273.3c882.4,272.7,882.1,272.0,882.1,271.7c882.1,271.4,881.8,270.8,881.5,270.4c881.2,269.9,880.9,269.3,880.9,269.0c880.9,268.3,880.2,267.3,879.8,267.3c879.4,267.3,878.6,268.2,878.6,268.8c878.6,269.0,878.3,269.6,877.9,270.2c877.5,270.7,877.2,271.5,877.2,271.9c877.2,272.3,877.0,272.9,876.8,273.1c876.6,273.3,876.5,273.7,876.5,273.9c876.5,274.2,876.2,274.8,875.8,275.3c875.4,275.9,875.1,276.6,875.1,276.9c875.1,277.2,874.9,277.7,874.7,277.9c874.5,278.1,874.4,278.6,874.4,278.9c874.4,279.2,874.1,279.9,873.7,280.5c873.0,281.4,873.0,281.5,873.4,282.1c873.7,282.7,874.2,282.7,879.6,282.7c885.1,282.7,885.6,282.7,885.9,282.1|m69.7,280.1c69.9,279.9,70.4,279.6,70.9,279.6c71.4,279.6,71.9,279.4,72.0,279.1c72.2,278.8,72.5,278.6,72.6,278.6c73.0,278.6,73.9,277.2,74.4,275.7c74.9,274.1,75.0,272.3,74.5,271.7c74.3,271.5,74.2,271.1,74.2,270.8c74.2,270.0,72.3,267.3,71.8,267.3c71.6,267.3,71.3,267.1,71.1,266.8c70.9,266.5,69.4,266.4,65.3,266.3c60.4,266.2,59.8,266.2,59.4,266.8c59.0,267.3,58.9,267.9,58.9,273.6c58.9,278.0,59.0,280.0,59.2,280.2c59.4,280.5,60.9,280.7,64.5,280.7c68.6,280.7,69.5,280.6,69.7,280.1|m322.7,280.1c322.9,279.9,323.6,279.6,324.2,279.6c325.2,279.6,325.4,279.5,326.2,278.2c327.6,276.0,328.0,275.2,328.0,273.7c328.0,272.0,327.0,268.9,326.2,268.0c325.8,267.6,325.3,267.3,324.9,267.3c324.6,267.3,324.2,267.1,324.0,266.8c323.8,266.5,322.2,266.4,318.2,266.3c313.3,266.2,312.7,266.2,312.3,266.8c311.9,267.3,311.8,267.9,311.8,273.6c311.8,278.0,311.9,280.0,312.1,280.2c312.5,280.9,322.1,280.8,322.7,280.1|m571.5,280.1c571.6,279.8,572.2,279.6,572.8,279.6c573.8,279.6,574.0,279.5,574.9,278.2c575.5,277.3,575.9,276.4,575.9,276.1c575.9,275.8,576.1,275.4,576.3,275.2c576.5,274.9,576.6,274.1,576.6,273.0c576.6,271.3,576.5,271.1,575.3,269.2c574.5,268.2,573.8,267.3,573.6,267.3c573.4,267.3,573.1,267.1,572.9,266.8c572.5,266.2,561.5,266.0,561.0,266.6c560.6,267.1,560.5,279.6,561.0,280.2c561.2,280.5,562.7,280.7,566.2,280.7c570.3,280.7,571.2,280.6,571.5,280.1|m825.0,280.1c825.2,279.8,825.7,279.6,826.4,279.6c827.4,279.6,827.6,279.5,828.8,277.6l830.2,275.7l830.2,272.9l830.2,270.2l829.2,268.7c828.6,267.9,828.0,267.3,827.8,267.3c827.6,267.3,827.3,267.1,827.2,266.8c826.8,266.2,815.1,266.0,814.6,266.6c814.3,266.9,814.3,268.1,814.3,272.6l814.3,278.2l815.0,279.4l815.7,280.7l820.2,280.7c824.0,280.7,824.8,280.6,825.0,280.1|m13.1,239.8c11.0,239.2,10.5,239.0,10.4,238.7c10.3,238.5,10.1,238.4,9.8,238.4c9.6,238.4,9.3,238.2,9.1,237.9c9.0,237.6,8.7,237.4,8.4,237.4c8.2,237.4,7.7,236.9,7.4,236.3c7.0,235.8,6.5,235.3,6.3,235.3c5.9,235.3,4.0,232.6,4.0,232.0c4.0,231.8,3.7,231.0,3.3,230.4c2.9,229.7,2.6,229.0,2.6,228.7c2.6,228.4,2.4,228.0,2.2,227.8c2.0,227.5,1.9,227.1,1.9,226.7c1.9,226.4,1.7,225.9,1.5,225.7c1.3,225.5,1.2,224.9,1.2,224.3c1.2,223.8,1.0,223.2,0.9,223.0c0.4,222.4,0.4,19.8,0.9,19.2c1.0,18.9,1.2,18.3,1.2,17.7c1.2,17.1,1.3,16.4,1.5,16.1c1.7,15.9,1.9,15.4,1.9,15.1c1.9,14.8,2.0,14.3,2.2,14.1c2.4,13.8,2.6,13.5,2.6,13.3c2.6,11.8,5.9,5.8,6.7,5.8c6.9,5.8,7.4,5.4,7.8,4.8c8.2,4.2,8.8,3.8,8.9,3.8c9.1,3.8,9.4,3.5,9.6,3.3c9.8,3.0,10.1,2.7,10.3,2.7c10.5,2.7,10.8,2.5,11.0,2.2c11.2,1.9,11.6,1.7,12.0,1.7c12.4,1.7,12.9,1.5,13.1,1.3c13.5,0.7,227.2,0.7,227.6,1.3c227.8,1.5,228.3,1.7,228.7,1.7c229.1,1.7,229.5,1.9,229.7,2.2c229.9,2.5,230.2,2.7,230.4,2.7c230.6,2.7,231.0,3.0,231.1,3.3c231.3,3.5,231.6,3.8,231.8,3.8c232.0,3.8,232.5,4.2,232.9,4.8c233.2,5.4,233.7,5.8,233.8,5.8c234.1,5.8,236.7,9.7,236.7,10.1c236.7,10.3,237.0,10.9,237.4,11.6c238.3,13.4,238.8,14.9,238.8,15.7c238.8,16.1,239.0,16.9,239.2,17.4c239.4,17.9,239.5,18.9,239.5,19.6c239.5,20.3,239.7,21.0,239.8,21.2c240.1,21.6,240.1,42.1,240.1,121.4c240.1,200.8,240.1,221.3,239.8,221.6c239.7,221.9,239.5,222.5,239.5,223.0c239.5,223.4,239.4,224.1,239.2,224.5c239.0,224.9,238.8,225.6,238.8,226.1c238.8,226.6,238.5,227.5,238.1,228.2c237.7,228.9,237.4,229.5,237.4,229.6c237.4,229.8,237.1,230.5,236.7,231.2c236.3,231.9,236.0,232.6,236.0,232.8c236.0,233.2,234.5,235.3,234.2,235.3c234.1,235.3,233.7,235.8,233.3,236.3c233.0,236.9,232.5,237.4,232.3,237.4c232.0,237.4,231.7,237.6,231.6,237.9c231.4,238.2,231.1,238.4,230.9,238.4c230.7,238.4,230.4,238.5,230.3,238.7c230.2,238.8,229.7,239.1,229.1,239.4c228.1,239.9,215.0,239.9,121.1,240.0c62.3,240.0,13.7,239.9,13.1,239.8|m268.0,239.9c265.7,239.3,264.9,238.9,264.7,238.7c264.6,238.5,264.3,238.4,264.1,238.4c263.9,238.4,263.6,238.2,263.4,237.9c263.2,237.6,262.9,237.4,262.7,237.4c262.5,237.4,262.0,236.9,261.6,236.3c261.3,235.8,260.8,235.3,260.6,235.3c260.2,235.3,258.2,232.6,258.2,232.0c258.2,231.8,257.9,231.0,257.5,230.4c257.2,229.7,256.8,229.0,256.8,228.7c256.8,228.4,256.7,228.1,256.6,227.9c256.3,227.6,255.4,224.8,255.4,223.9c255.4,223.5,255.3,222.9,255.1,222.7c254.9,222.3,254.9,201.5,254.9,120.9c254.9,40.3,254.9,19.5,255.1,19.2c255.3,18.9,255.4,18.3,255.4,17.7c255.4,17.1,255.6,16.4,255.8,16.1c256.0,15.9,256.1,15.4,256.1,15.1c256.1,14.8,256.3,14.3,256.5,14.1c256.7,13.8,256.8,13.4,256.8,13.1c256.8,12.7,257.0,12.3,257.2,12.0c257.4,11.8,257.5,11.3,257.5,11.0c257.5,10.3,261.3,4.8,261.8,4.8c262.0,4.8,262.3,4.6,262.5,4.3c262.6,4.0,262.9,3.8,263.2,3.8c263.4,3.8,263.7,3.5,263.9,3.3c264.0,3.0,264.3,2.7,264.6,2.7c264.8,2.7,265.1,2.5,265.3,2.2c265.4,1.9,265.9,1.7,266.3,1.7c266.7,1.7,267.2,1.5,267.3,1.3c267.8,0.7,480.8,0.7,481.2,1.3c481.4,1.5,481.8,1.7,482.2,1.7c482.6,1.7,483.1,1.9,483.3,2.2c483.4,2.5,483.8,2.7,484.0,2.7c484.2,2.7,484.5,3.0,484.7,3.3c484.8,3.5,485.1,3.8,485.2,3.8c485.3,3.8,485.8,4.2,486.3,4.8c486.8,5.4,487.3,5.8,487.4,5.8c487.7,5.8,490.3,9.7,490.3,10.2c490.3,10.4,490.6,11.0,491.0,11.5c491.4,12.1,491.7,12.8,491.7,13.1c491.7,13.4,491.9,13.8,492.0,14.1c492.2,14.3,492.4,15.0,492.4,15.6c492.4,16.2,492.5,16.9,492.7,17.1c493.2,17.8,493.4,21.3,493.6,32.3c493.8,46.7,493.8,196.8,493.5,210.6c493.3,222.7,493.2,225.1,492.7,225.7c492.5,225.9,492.4,226.4,492.4,226.7c492.4,227.1,492.2,227.5,492.0,227.8c491.9,228.0,491.7,228.4,491.7,228.8c491.7,229.1,491.4,229.8,491.0,230.3c490.6,230.9,490.3,231.6,490.3,231.9c490.3,232.5,488.3,235.3,487.8,235.3c487.7,235.3,487.3,235.8,486.9,236.3c486.5,236.9,486.1,237.4,485.8,237.4c485.6,237.4,485.3,237.6,485.1,237.9c485.0,238.2,484.7,238.4,484.5,238.4c484.2,238.4,484.0,238.5,483.9,238.7c483.8,238.8,483.2,239.1,482.6,239.4c481.7,239.9,468.7,239.9,375.0,240.0c316.4,240.0,268.2,240.0,268.0,239.9|m518.7,239.9c516.5,239.3,515.6,238.9,515.5,238.7c515.3,238.5,514.9,238.4,514.6,238.4c514.2,238.4,513.6,237.9,513.0,237.2c512.4,236.5,511.9,236.0,511.8,236.0c511.5,236.0,508.3,231.3,508.3,230.8c508.3,230.6,508.0,229.8,507.6,229.1c507.2,228.4,506.9,227.4,506.9,227.0c506.9,226.5,506.8,225.9,506.6,225.7c506.0,225.1,505.9,223.0,505.7,206.8c505.5,186.7,505.5,55.5,505.7,35.0c505.9,19.0,506.0,17.1,506.6,16.5c506.8,16.2,506.9,15.8,506.9,15.5c506.9,15.1,507.1,14.7,507.3,14.4c507.4,14.2,507.6,13.7,507.6,13.2c507.6,12.8,507.8,12.3,508.0,12.0c508.1,11.8,508.3,11.4,508.3,11.2c508.3,10.8,511.6,5.8,511.9,5.8c512.0,5.8,512.5,5.4,513.0,4.8c513.5,4.2,514.0,3.8,514.1,3.8c514.2,3.8,514.5,3.5,514.6,3.3c514.8,3.0,515.1,2.7,515.3,2.7c515.5,2.7,515.9,2.5,516.0,2.2c516.2,1.9,516.6,1.7,517.1,1.7c517.5,1.7,517.9,1.5,518.1,1.3c518.5,0.7,731.8,0.7,732.2,1.3c732.4,1.5,732.9,1.7,733.5,1.7c734.1,1.7,734.6,1.9,734.7,2.2c734.9,2.5,735.2,2.7,735.4,2.7c735.7,2.7,736.0,3.0,736.1,3.3c736.3,3.5,736.6,3.8,736.8,3.8c737.0,3.8,737.5,4.2,737.9,4.8c738.4,5.4,738.9,5.8,739.0,5.8c739.4,5.8,741.8,9.4,741.8,10.0c741.8,10.3,742.1,11.0,742.5,11.5c742.8,12.1,743.2,12.8,743.2,13.1c743.2,13.4,743.3,13.8,743.5,14.1c743.7,14.3,743.9,14.8,743.9,15.1c743.9,15.4,744.0,15.9,744.2,16.1c744.4,16.4,744.6,17.2,744.6,18.2c744.6,19.1,744.7,20.0,744.9,20.2c745.1,20.6,745.1,41.1,745.1,120.6c745.1,200.1,745.1,220.6,744.9,220.9c744.7,221.2,744.6,222.0,744.6,222.8c744.6,223.7,744.4,224.4,744.2,224.7c744.0,224.9,743.9,225.6,743.9,226.2c743.9,226.8,743.7,227.5,743.5,227.8c743.3,228.0,743.2,228.4,743.2,228.8c743.2,229.1,742.7,230.0,742.1,230.8c741.5,231.7,741.1,232.6,741.1,232.9c741.1,233.6,740.6,234.3,740.1,234.3c739.9,234.3,739.3,235.0,738.7,235.8c738.1,236.7,737.5,237.4,737.3,237.4c737.1,237.4,736.8,237.6,736.6,237.9c736.4,238.2,736.1,238.4,735.9,238.4c735.7,238.4,735.4,238.5,735.3,238.7c735.3,238.8,734.7,239.1,734.1,239.4c733.1,239.9,720.1,239.9,626.1,240.0c567.3,240.0,519.0,240.0,518.7,239.9|m772.4,239.9c771.0,239.6,769.2,239.0,769.0,238.7c768.9,238.5,768.6,238.4,768.4,238.4c768.2,238.4,767.8,238.1,767.6,237.7c767.3,237.3,766.8,236.6,766.3,236.2c765.4,235.3,761.9,230.2,761.9,229.7c761.9,229.5,761.6,228.9,761.2,228.2c760.8,227.5,760.5,226.7,760.5,226.1c760.5,225.6,760.4,225.0,760.2,224.8c760.1,224.6,759.8,223.3,759.6,221.9c758.9,216.3,759.0,25.7,759.7,19.4c759.9,18.3,760.1,17.3,760.2,17.1c760.4,16.9,760.5,16.3,760.5,15.8c760.5,15.3,760.6,14.7,760.8,14.4c761.0,14.2,761.2,13.8,761.2,13.5c761.2,13.2,761.5,12.4,761.9,11.7c762.3,11.0,762.6,10.3,762.6,10.1c762.6,9.7,765.2,5.8,765.5,5.8c765.6,5.8,766.1,5.4,766.5,4.8c767.0,4.2,767.5,3.8,767.7,3.8c767.8,3.8,768.0,3.5,768.2,3.3c768.3,3.0,768.7,2.7,768.9,2.7c769.1,2.7,769.4,2.5,769.6,2.2c769.8,1.9,770.2,1.7,770.6,1.7c771.0,1.7,771.5,1.5,771.7,1.3c772.1,0.7,985.8,0.7,986.2,1.3c986.4,1.5,986.9,1.7,987.3,1.7c987.7,1.7,988.1,1.9,988.3,2.2c988.5,2.5,988.8,2.7,989.0,2.7c989.2,2.7,989.5,3.0,989.7,3.3c989.9,3.5,990.2,3.8,990.4,3.8c990.6,3.8,991.0,4.0,991.1,4.3c991.3,4.6,991.6,4.8,991.8,4.8c992.2,4.8,996.0,10.3,996.0,10.9c996.0,11.1,996.3,11.8,996.7,12.5c997.1,13.1,997.4,13.9,997.4,14.2c997.4,14.5,997.6,14.9,997.8,15.1c998.0,15.4,998.1,16.0,998.1,16.6c998.1,17.2,998.3,17.9,998.4,18.2c998.7,18.5,998.7,39.5,998.7,120.9c998.7,202.3,998.7,223.3,998.4,223.7c998.3,223.9,998.1,224.6,998.1,225.2c998.1,225.8,998.0,226.5,997.8,226.7c997.6,227.0,997.4,227.4,997.4,227.7c997.4,228.0,997.1,228.7,996.7,229.4c996.3,230.0,996.0,230.7,996.0,231.0c996.0,231.5,992.9,236.0,992.6,236.0c992.4,236.0,991.9,236.5,991.4,237.2c990.9,237.9,990.3,238.4,990.2,238.4c990.1,238.4,989.8,238.5,989.5,238.7c987.8,240.0,991.8,240.0,880.2,240.0c821.2,240.0,772.7,240.0,772.4,239.9|m226.9,237.9c228.8,237.2,230.1,236.5,230.3,236.0c230.4,235.8,230.6,235.7,230.8,235.7c231.0,235.7,231.6,235.2,232.0,234.6c232.5,234.1,233.1,233.6,233.3,233.6c233.7,233.6,235.6,230.8,235.6,230.1c235.6,229.8,235.9,229.2,236.3,228.6c236.6,228.1,237.0,227.4,237.0,227.0c237.0,226.7,237.1,226.3,237.3,226.0c237.5,225.8,237.7,225.1,237.7,224.3c237.7,223.7,237.8,222.9,238.0,222.7c238.4,222.0,238.4,19.8,238.0,19.2c237.8,18.9,237.7,18.4,237.7,18.0c237.7,17.6,237.5,17.1,237.3,16.8c237.1,16.6,237.0,16.0,237.0,15.5c237.0,14.9,236.6,14.0,235.9,12.8c235.3,11.8,234.9,10.9,234.9,10.7c234.9,10.3,232.8,7.2,232.5,7.2c232.4,7.2,231.7,6.6,230.9,5.8c230.2,5.1,229.4,4.5,229.2,4.5c229.0,4.5,228.7,4.2,228.5,4.0c228.4,3.6,227.8,3.4,227.2,3.4c226.6,3.4,225.9,3.2,225.8,3.0c225.4,2.4,19.8,2.2,16.7,2.8c15.5,3.0,14.1,3.2,13.5,3.3c12.9,3.4,12.3,3.7,12.1,4.0c12.0,4.2,11.7,4.5,11.6,4.5c10.7,4.5,8.1,6.8,6.5,9.2c5.0,11.4,4.5,12.4,3.5,15.3c2.9,17.2,2.3,19.3,2.3,19.9c2.2,20.6,2.0,22.2,1.9,23.5c1.6,26.9,1.6,215.0,1.9,218.3c2.0,219.6,2.2,221.3,2.3,221.9c2.3,222.6,2.9,224.6,3.5,226.4c4.3,228.9,4.9,230.2,6.2,232.1c7.1,233.5,8.0,234.6,8.2,234.6c8.4,234.6,8.8,235.0,9.0,235.3c9.6,236.2,11.1,237.4,11.8,237.4c12.0,237.4,12.4,237.6,12.7,237.8c13.5,238.5,39.0,238.6,136.6,238.6c220.1,238.5,225.2,238.5,226.9,237.9|m480.5,237.9c481.4,237.6,482.4,237.2,482.7,237.0c482.9,236.9,483.5,236.6,483.9,236.5c484.3,236.4,484.9,235.9,485.2,235.5c485.5,235.0,485.9,234.6,486.1,234.6c486.5,234.6,489.1,230.8,489.1,230.1c489.1,229.8,489.4,229.2,489.8,228.6c490.2,228.1,490.5,227.4,490.5,227.0c490.5,226.7,490.7,226.3,490.9,226.1c491.9,224.8,491.9,218.1,491.9,115.9c491.8,39.4,491.8,19.5,491.5,19.2c491.4,18.9,491.2,18.2,491.2,17.5c491.2,16.8,491.1,16.0,490.9,15.8c490.7,15.6,490.5,15.1,490.5,14.8c490.5,14.5,490.2,13.8,489.8,13.2c489.4,12.7,489.1,12.0,489.1,11.7c489.1,11.0,485.8,6.2,485.4,6.2c485.2,6.2,484.8,5.8,484.3,5.3c483.9,4.9,483.4,4.5,483.1,4.5c482.9,4.5,482.5,4.3,482.2,4.0c481.8,3.5,481.4,3.4,477.8,2.8c475.2,2.3,273.0,2.3,270.6,2.8c269.7,3.0,268.4,3.2,267.8,3.3c267.2,3.4,266.6,3.7,266.4,4.0c266.3,4.2,266.0,4.5,265.9,4.5c265.7,4.5,264.9,5.0,264.1,5.5c262.5,6.7,258.7,11.7,258.7,12.7c258.7,13.0,258.4,13.7,258.0,14.3c257.5,14.9,257.3,15.6,257.3,16.3c257.3,16.9,257.2,17.6,257.0,17.8c256.8,18.1,256.6,19.0,256.5,19.9c256.5,20.7,256.3,22.2,256.2,23.0c255.8,25.2,255.8,109.6,256.2,111.5c256.6,114.1,256.7,114.7,256.3,115.3c256.1,115.8,256.0,124.3,256.0,166.4c255.9,202.5,256.0,217.4,256.2,218.6c256.3,219.6,256.5,221.1,256.5,222.0c256.6,222.9,256.8,223.8,257.0,224.0c257.2,224.2,257.3,224.7,257.3,225.0c257.3,225.3,257.5,225.8,257.7,226.0c257.9,226.3,258.0,226.7,258.0,227.1c258.0,227.4,258.2,227.9,258.4,228.1c258.6,228.3,258.7,228.8,258.7,229.1c258.7,229.8,262.0,234.6,262.5,234.6c262.7,234.6,263.1,235.0,263.4,235.5c263.7,236.0,264.3,236.4,264.8,236.6c265.3,236.7,265.8,236.9,265.9,237.1c265.9,237.2,266.3,237.4,266.6,237.4c266.9,237.4,267.4,237.6,267.7,237.8c268.5,238.5,293.8,238.6,390.8,238.6c473.4,238.5,478.8,238.5,480.5,237.9|m732.0,237.9c732.7,237.6,733.6,237.4,733.9,237.4c734.6,237.4,736.1,236.2,736.7,235.3c736.9,235.0,737.3,234.6,737.5,234.6c738.0,234.6,740.8,230.5,740.8,229.8c740.8,229.5,741.1,228.9,741.4,228.4c741.7,228.0,742.0,227.4,742.0,227.1c742.0,226.7,742.1,226.3,742.3,226.0c742.5,225.8,742.7,225.3,742.7,224.8c742.7,224.4,742.8,223.5,743.0,222.9c743.3,221.9,743.4,209.0,743.4,131.6c743.5,60.2,743.6,41.5,743.8,41.2c744.3,40.5,744.2,31.3,743.7,30.0c743.5,29.3,743.4,27.8,743.4,24.2c743.4,20.3,743.3,19.2,743.0,18.9c742.8,18.7,742.7,18.0,742.7,17.3c742.7,16.7,742.5,16.0,742.3,15.8c742.1,15.6,742.0,15.1,742.0,14.8c742.0,14.5,741.7,13.8,741.4,13.4c741.1,13.0,740.8,12.4,740.8,12.1c740.8,11.3,738.0,7.2,737.5,7.2c737.3,7.2,736.9,6.9,736.7,6.5c736.2,5.7,734.6,4.5,734.1,4.5c734.0,4.5,733.7,4.2,733.6,4.0c733.4,3.7,732.8,3.4,732.2,3.3c731.6,3.2,730.3,3.0,729.2,2.8c726.7,2.3,524.0,2.3,521.6,2.8c520.7,3.0,519.4,3.2,518.7,3.3c518.1,3.4,517.4,3.7,517.2,3.9c516.8,4.3,516.4,4.6,514.5,5.8c513.2,6.7,509.5,11.8,509.5,12.7c509.5,13.0,509.3,13.5,509.1,13.7c508.9,14.0,508.8,14.4,508.8,14.8c508.8,15.1,508.6,15.6,508.4,15.8c508.2,16.0,508.1,16.6,508.1,17.0c508.1,17.4,507.9,18.0,507.7,18.2c507.5,18.5,507.4,19.2,507.4,20.2c507.4,21.1,507.2,22.0,507.1,22.3c506.8,22.6,506.8,42.9,506.8,121.6c506.8,200.3,506.8,220.6,507.1,220.9c507.2,221.2,507.4,221.9,507.4,222.5c507.4,223.1,507.5,223.7,507.7,224.0c507.9,224.2,508.1,224.9,508.1,225.5c508.1,226.3,508.3,226.9,508.8,227.6c509.2,228.1,509.5,228.8,509.5,229.1c509.5,229.8,512.7,234.6,513.2,234.6c513.4,234.6,513.9,235.1,514.3,235.7c514.7,236.2,515.3,236.7,515.4,236.7c515.6,236.7,516.0,236.8,516.2,237.0c516.4,237.2,517.2,237.5,518.0,237.8c520.2,238.5,544.8,238.6,642.2,238.6c722.3,238.5,730.8,238.4,732.0,237.9|m985.7,238.1c986.3,237.8,987.1,237.6,987.5,237.5c987.9,237.4,988.6,236.9,989.2,236.5c989.8,236.0,990.4,235.7,990.5,235.7c990.7,235.7,991.8,234.1,993.1,232.1c995.6,228.4,996.8,225.6,997.1,222.6c997.2,221.8,997.3,220.3,997.4,219.3c997.7,216.9,997.7,24.7,997.4,22.3c997.3,21.3,997.1,19.7,997.0,18.8c997.0,17.9,996.8,17.0,996.6,16.8c996.4,16.6,996.3,16.1,996.3,15.8c996.3,15.5,996.1,15.0,995.9,14.8c995.7,14.5,995.6,14.1,995.6,13.8c995.6,13.1,990.9,6.2,990.4,6.2c990.2,6.2,989.8,5.8,989.5,5.3c989.2,4.8,988.7,4.5,988.3,4.5c988.0,4.5,987.5,4.3,987.2,4.0c987.0,3.7,986.3,3.4,985.7,3.3c985.2,3.2,983.8,3.0,982.6,2.8c979.5,2.2,774.6,2.4,774.2,3.0c774.1,3.2,773.5,3.4,772.9,3.4c772.3,3.5,771.6,3.7,771.4,4.0c771.1,4.2,770.7,4.5,770.5,4.5c770.0,4.5,768.4,5.7,767.9,6.5c767.6,6.9,767.2,7.2,767.0,7.2c766.5,7.2,763.7,11.2,763.7,12.0c763.7,12.3,763.4,13.0,763.0,13.6c762.7,14.1,762.3,14.8,762.3,15.1c762.3,15.5,762.2,15.9,762.0,16.1c761.8,16.4,761.6,17.1,761.6,17.7c761.6,18.3,761.5,18.9,761.3,19.2c761.1,19.5,761.1,40.3,761.1,120.9c761.1,201.5,761.1,222.3,761.3,222.7c761.5,222.9,761.6,223.7,761.6,224.3c761.6,225.1,761.8,225.8,762.0,226.0c762.2,226.3,762.3,226.7,762.3,227.0c762.3,227.3,762.9,228.4,763.6,229.5c764.4,230.6,765.1,231.8,765.2,232.2c765.4,232.7,765.7,233.2,766.0,233.4c766.2,233.6,766.8,234.2,767.3,234.7c767.8,235.2,768.3,235.7,768.5,235.7c768.7,235.7,768.9,235.8,769.0,236.0c769.2,236.4,770.3,237.1,771.7,237.7c773.4,238.5,799.5,238.6,896.1,238.5c959.9,238.5,985.0,238.3,985.7,238.1|m15.0,233.0c13.6,232.9,12.4,232.7,12.3,232.6c12.2,232.4,11.7,232.2,11.3,232.2c10.9,232.2,10.5,232.0,10.3,231.7c10.1,231.4,9.8,231.2,9.6,231.2c9.0,231.2,6.1,226.6,5.9,225.3c5.8,224.7,5.7,223.9,5.5,223.7c5.4,223.4,5.3,215.4,5.3,197.8l5.3,172.5l6.3,171.0c7.4,169.3,7.4,169.0,6.8,168.1c6.5,167.8,6.0,166.8,5.8,165.9c5.3,164.4,5.3,164.2,5.3,137.7l5.3,111.0l5.9,110.0c6.7,108.8,6.7,107.4,5.9,105.3l5.3,103.6l5.3,78.3l5.3,53.1l5.9,51.4c6.3,50.5,6.5,49.5,6.5,49.3c6.5,48.2,9.6,45.0,10.5,45.0c10.8,45.0,11.2,44.8,11.6,44.5c12.6,43.7,77.6,43.7,78.6,44.4c80.2,45.7,81.7,46.7,82.0,46.7c82.3,46.7,83.7,45.7,85.4,44.4c85.9,44.0,91.3,44.0,119.2,44.0c148.1,44.0,152.4,44.0,153.1,44.5c153.6,44.8,154.2,45.0,154.4,45.0c154.6,45.0,155.2,45.6,155.7,46.4c156.9,48.2,157.5,48.2,158.7,46.4c159.2,45.6,159.9,45.0,160.1,45.0c160.4,45.0,160.9,44.8,161.3,44.5c161.9,44.0,166.2,44.0,195.4,44.0c231.5,44.0,228.7,43.8,231.3,45.6c232.4,46.4,233.9,48.4,233.9,49.2c233.9,49.5,234.1,49.9,234.3,50.2c234.5,50.4,234.6,50.8,234.6,51.1c234.6,51.4,234.8,52.0,235.0,52.4c235.3,52.9,235.3,56.5,235.3,77.6c235.3,103.3,235.3,102.8,234.4,105.1c234.2,105.4,234.1,105.9,234.0,106.1c233.9,106.4,233.8,106.9,233.7,107.3c233.5,107.8,233.6,108.2,234.0,109.0c235.4,111.8,235.3,110.2,235.3,138.7c235.3,161.1,235.3,164.9,235.0,165.4c234.8,165.8,234.6,166.3,234.6,166.6c234.6,166.9,234.4,167.5,234.0,168.0c233.3,169.0,233.3,169.4,234.0,170.4c234.4,170.9,234.6,171.6,234.6,172.3c234.6,172.8,234.8,173.6,235.0,174.0c235.5,175.0,235.5,220.2,235.0,221.7c234.8,222.2,234.6,223.0,234.6,223.5c234.6,223.9,234.5,224.4,234.3,224.7c234.1,224.9,233.9,225.3,233.9,225.5c233.9,226.9,232.3,230.2,231.6,230.2c231.4,230.2,230.9,230.6,230.5,231.2c230.1,231.8,229.6,232.2,229.2,232.2c228.9,232.2,228.5,232.4,228.3,232.7c228.1,233.0,221.1,233.1,195.0,233.1c160.8,233.1,161.7,233.1,160.2,231.8c160.0,231.7,159.7,231.4,159.5,231.3c158.7,230.9,158.5,230.6,158.4,230.0c158.3,229.0,157.7,228.1,157.2,228.1c156.7,228.1,156.0,229.2,156.0,229.9c156.0,230.5,154.8,232.2,154.4,232.2c154.2,232.2,153.9,232.4,153.7,232.7c153.5,233.0,146.4,233.1,119.6,233.1c92.9,233.1,85.8,233.0,85.6,232.7c85.4,232.4,85.1,232.2,84.9,232.2c84.7,232.2,84.4,232.0,84.2,231.7c84.1,231.4,83.8,231.2,83.5,231.2c83.3,231.2,82.8,230.7,82.4,230.1l81.6,229.0l80.2,231.0l78.8,233.1l48.1,233.1c31.2,233.1,16.3,233.1,15.0,233.0|m268.7,233.0c266.5,232.9,265.8,232.7,264.8,231.8c264.6,231.7,264.2,231.4,264.0,231.2c263.3,230.8,260.8,227.1,260.8,226.6c260.8,226.3,260.7,225.9,260.5,225.7c260.3,225.5,260.1,224.8,260.1,224.1c260.1,223.5,260.0,222.9,259.9,222.8c259.7,222.6,259.6,214.0,259.6,197.9c259.6,171.2,259.6,172.2,260.9,170.4c261.7,169.3,261.7,168.0,260.9,166.9c259.6,165.1,259.6,166.3,259.6,137.9c259.6,120.8,259.7,111.6,259.9,111.5c260.0,111.4,260.1,111.0,260.1,110.7c260.1,110.4,260.5,109.6,260.9,109.0c261.6,107.9,261.6,107.8,261.2,107.2c261.0,106.9,260.8,106.4,260.8,106.1c260.8,105.8,260.7,105.4,260.5,105.1c260.3,104.9,260.1,104.4,260.1,104.1c260.1,103.7,260.0,103.3,259.9,103.2c259.7,103.1,259.6,94.2,259.6,77.8c259.6,61.4,259.7,52.5,259.9,52.4c260.0,52.3,260.1,51.9,260.1,51.6c260.1,51.2,260.3,50.7,260.5,50.5c260.7,50.3,260.8,49.8,260.8,49.5c260.8,48.2,263.7,45.0,264.9,45.0c265.2,45.0,265.6,44.8,266.0,44.5c266.5,44.1,271.4,44.0,299.3,44.0c336.1,44.0,332.9,43.7,334.9,46.5l335.9,47.8l337.0,46.4c337.6,45.6,338.3,45.0,338.5,45.0c338.7,45.0,339.3,44.8,339.7,44.5c340.5,44.0,344.8,44.0,373.9,44.0c406.3,44.0,407.3,44.0,408.3,44.6c408.8,45.0,409.6,45.8,410.0,46.5c411.1,48.1,411.8,48.1,412.9,46.5c413.3,45.9,414.1,45.0,414.7,44.6c415.7,44.0,416.6,44.0,449.2,44.0c477.8,44.0,482.8,44.1,483.3,44.5c483.6,44.8,484.1,45.0,484.5,45.0c484.9,45.0,485.5,45.7,486.6,47.3c487.9,49.2,488.2,49.9,488.2,50.7c488.2,51.3,488.3,52.0,488.5,52.2c488.8,52.6,488.9,55.9,488.9,78.6l488.9,104.5l488.2,105.8c487.8,106.5,487.5,107.4,487.5,107.9c487.5,108.3,487.8,109.2,488.2,109.9l488.9,111.2l488.9,138.7l488.9,166.1l488.0,167.5c487.4,168.2,487.0,169.0,487.0,169.2c487.0,169.4,487.3,169.9,487.6,170.4c487.9,170.8,488.2,171.5,488.2,171.8c488.2,172.1,488.3,172.6,488.5,172.8c489.1,173.4,489.1,222.8,488.5,223.8c488.4,224.2,488.2,224.9,488.2,225.3c488.2,226.3,485.0,231.2,484.4,231.2c484.2,231.2,483.9,231.3,483.9,231.5c483.8,231.7,483.3,232.1,482.9,232.5c482.0,233.0,480.1,233.1,448.6,233.1c422.2,233.1,415.2,233.0,414.9,232.7c414.8,232.4,414.5,232.2,414.3,232.2c414.2,232.2,413.4,231.3,412.6,230.2c411.2,228.2,411.1,228.1,410.7,228.7c410.5,229.0,410.3,229.5,410.3,229.8c410.3,230.5,409.8,231.2,409.4,231.2c409.2,231.2,408.7,231.6,408.4,232.1l407.7,233.1l373.9,233.1c347.2,233.1,340.1,233.0,339.8,232.7c339.7,232.4,339.4,232.2,339.2,232.2c338.9,232.2,338.6,232.0,338.5,231.7c338.3,231.4,338.0,231.2,337.8,231.2c337.6,231.2,337.1,230.7,336.7,230.1l335.9,229.0l334.5,231.0l333.1,233.1l302.0,233.1c285.0,233.1,269.9,233.1,268.7,233.0|m519.5,233.0c517.2,232.9,515.8,232.4,515.4,231.5c515.4,231.3,515.1,231.2,514.9,231.2c514.7,231.2,513.7,230.1,512.8,228.7c511.6,226.9,511.1,226.0,511.1,225.3c511.1,224.9,511.0,224.3,510.8,224.0c510.6,223.7,510.5,218.1,510.5,198.4c510.5,178.7,510.6,173.1,510.8,172.7c511.0,172.5,511.1,172.1,511.1,171.8c511.1,171.5,511.4,170.8,511.8,170.2l512.5,169.2l511.8,168.2c511.4,167.6,511.1,166.9,511.1,166.6c511.1,166.3,511.0,165.9,510.8,165.6c510.6,165.3,510.5,159.3,510.5,138.1l510.5,111.0l511.6,109.4l512.6,107.8l511.9,106.9c511.4,106.4,511.1,105.7,511.1,105.4c511.1,105.2,511.0,104.7,510.8,104.5c510.4,103.9,510.4,52.8,510.8,52.2c511.0,51.9,511.1,51.3,511.1,50.8c511.1,49.0,514.2,45.0,515.7,45.0c515.9,45.0,516.4,44.8,516.7,44.5c517.2,44.1,522.2,44.0,550.4,44.0c582.7,44.0,583.6,44.0,584.6,44.6c585.2,45.0,586.0,45.9,586.4,46.5c587.3,47.9,587.6,48.0,588.2,47.1c588.4,46.7,589.4,45.8,590.3,45.2l592.1,44.0l625.1,44.0c653.9,44.0,658.2,44.0,658.8,44.5c659.2,44.8,659.6,45.0,659.7,45.0c659.9,45.0,660.4,45.6,660.9,46.4c662.0,47.9,662.9,48.1,663.3,46.8c663.5,46.1,664.0,45.7,665.8,44.5c666.5,44.0,669.8,44.0,700.0,44.0c728.6,44.0,733.5,44.1,734.0,44.5c734.4,44.8,734.9,45.0,735.2,45.0c735.6,45.0,736.1,45.4,736.4,45.9c736.7,46.3,737.1,46.7,737.4,46.7c737.6,46.7,737.8,47.0,737.8,47.3c737.8,47.7,738.1,48.4,738.5,49.0c738.9,49.5,739.2,50.2,739.2,50.5c739.2,50.8,739.3,51.2,739.5,51.5c739.7,51.8,739.8,57.5,739.8,77.8c739.8,98.1,739.7,103.8,739.5,104.1c739.3,104.4,739.2,104.8,739.2,105.1c739.2,105.5,739.0,105.9,738.8,106.1c738.2,106.9,738.4,108.9,739.1,110.0l739.8,111.0l739.8,138.4l739.8,165.9l738.8,167.4c738.2,168.2,737.8,169.0,737.8,169.2c737.8,169.4,738.0,170.0,738.4,170.4c739.8,172.4,739.8,171.2,739.8,199.0c739.8,218.8,739.7,224.4,739.5,224.7c739.3,225.0,739.2,225.4,739.2,225.7c739.2,225.9,738.9,226.6,738.6,227.1c738.2,227.6,737.8,228.4,737.7,228.8c737.4,229.5,736.5,230.5,735.7,231.0c735.5,231.2,735.2,231.3,735.1,231.4c735.0,231.5,734.7,231.7,734.5,231.8c733.0,233.1,733.9,233.1,699.5,233.1c673.2,233.1,666.2,233.0,665.9,232.7c665.8,232.4,665.5,232.2,665.3,232.2c665.1,232.2,664.4,231.5,663.9,230.7c663.3,229.8,662.6,229.1,662.3,229.1c662.1,229.1,661.4,229.8,660.8,230.7c660.3,231.5,659.6,232.2,659.4,232.2c659.2,232.2,658.9,232.4,658.7,232.7c658.5,233.0,651.4,233.1,624.7,233.1l590.9,233.1l590.2,232.1c589.9,231.6,589.4,231.2,589.2,231.2c589.1,231.2,588.6,230.7,588.1,230.1l587.4,229.0l586.4,230.6c585.9,231.5,585.3,232.2,585.1,232.2c584.8,232.2,584.5,232.4,584.4,232.7c584.1,233.0,577.5,233.1,553.0,233.1c536.0,233.1,520.9,233.1,519.5,233.0|m773.8,233.0c772.5,232.9,771.2,232.7,771.1,232.6c771.0,232.4,770.6,232.2,770.2,232.2c769.7,232.2,769.3,232.0,769.1,231.7c769.0,231.4,768.7,231.2,768.4,231.2c767.9,231.2,765.4,227.4,765.4,226.7c765.4,226.4,765.2,225.9,765.0,225.7c764.8,225.5,764.7,224.9,764.7,224.5c764.7,224.1,764.5,223.3,764.3,222.7c763.8,221.3,763.8,174.0,764.3,172.9c764.5,172.6,764.7,172.0,764.7,171.7c764.7,171.4,765.0,170.8,765.4,170.2c765.8,169.7,766.1,169.0,766.1,168.7c766.1,168.4,765.8,167.7,765.4,167.1c765.0,166.6,764.7,165.9,764.7,165.6c764.7,165.3,764.5,164.8,764.3,164.4c763.8,163.4,763.8,114.0,764.3,112.6c764.5,112.0,764.7,111.2,764.7,110.8c764.7,110.5,765.0,109.6,765.4,109.0c766.1,108.0,766.1,107.8,765.8,107.3c765.5,106.7,765.0,105.5,764.8,104.8c764.7,104.5,764.5,103.8,764.3,103.3c763.8,102.0,763.8,54.4,764.3,53.4c764.5,53.0,764.7,52.4,764.7,51.9c764.7,51.5,765.0,50.5,765.4,49.8c765.8,49.1,766.1,48.3,766.1,47.9c766.1,47.6,766.4,47.2,766.8,46.9c767.3,46.6,767.8,46.1,768.1,45.7c768.3,45.3,768.8,45.0,769.1,45.0c769.4,45.0,770.0,44.8,770.3,44.5c770.8,44.1,775.8,44.0,804.4,44.0c837.0,44.0,837.9,44.0,838.9,44.6c839.4,45.0,840.2,45.8,840.7,46.5c841.1,47.2,841.6,47.7,841.8,47.7c841.9,47.7,842.4,47.1,842.9,46.4c843.4,45.6,844.1,45.0,844.3,45.0c844.6,45.0,845.2,44.8,845.5,44.5c846.1,44.0,850.4,44.0,879.6,44.0c908.9,44.0,913.2,44.0,913.8,44.5c914.1,44.8,914.6,45.0,914.7,45.0c914.9,45.0,915.4,45.6,915.9,46.4c916.4,47.1,917.0,47.7,917.3,47.7c917.6,47.7,918.2,47.1,918.7,46.4c919.2,45.6,919.8,45.0,920.0,45.0c920.2,45.0,920.6,44.8,920.8,44.5c921.5,43.7,987.4,43.7,988.4,44.5c988.8,44.8,989.3,45.0,989.6,45.0c989.9,45.0,990.3,45.4,990.6,45.9c990.9,46.3,991.4,46.7,991.6,46.7c992.0,46.7,992.7,47.7,992.7,48.3c992.7,48.5,993.0,49.4,993.3,50.3l993.9,51.9l993.9,78.5l993.9,105.0l993.3,105.8c992.9,106.4,992.7,107.0,992.7,107.9c992.7,108.8,992.9,109.4,993.3,109.9l993.9,110.7l993.9,137.9l993.9,165.1l993.3,166.7c993.0,167.6,992.7,168.8,992.7,169.2c992.7,169.7,993.0,170.6,993.3,171.2l993.9,172.3l993.9,197.8l993.9,223.3l993.3,224.9c993.0,225.8,992.7,226.7,992.7,226.9c992.7,227.4,990.3,230.8,989.6,231.2c989.3,231.4,989.0,231.7,988.8,231.8c987.3,233.1,988.2,233.1,954.1,233.1c928.1,233.1,921.1,233.0,920.9,232.7c920.7,232.4,920.4,232.2,920.2,232.2c920.0,232.2,919.4,231.5,918.8,230.7c918.3,229.8,917.6,229.1,917.3,229.1c917.0,229.1,916.4,229.8,915.8,230.7c915.2,231.5,914.6,232.2,914.4,232.2c914.2,232.2,913.9,232.4,913.7,232.7c913.5,233.0,906.3,233.1,879.3,233.1c852.3,233.1,845.1,233.0,844.9,232.7c844.7,232.4,844.4,232.2,844.2,232.2c844.0,232.2,843.4,231.5,842.8,230.6l841.9,229.0l840.8,230.6c840.1,231.5,839.5,232.2,839.3,232.2c839.1,232.2,838.8,232.4,838.6,232.7c838.4,233.0,831.8,233.1,807.3,233.1c790.2,233.1,775.2,233.1,773.8,233.0|m76.7,231.3c77.8,231.1,78.1,230.8,79.2,229.4c80.0,228.3,80.5,227.4,80.5,226.9c80.5,226.5,80.6,226.0,80.8,225.7c81.2,225.1,81.2,175.4,80.8,174.8c80.6,174.6,80.5,174.0,80.5,173.6c80.5,172.8,79.1,170.9,78.2,170.4c77.9,170.2,64.1,170.0,43.7,170.0c14.0,170.0,9.6,170.1,9.0,170.6c8.7,170.8,8.2,171.1,8.0,171.1c7.4,171.1,7.0,171.8,7.0,172.6c7.0,173.0,6.9,173.5,6.7,173.8c6.3,174.4,6.3,222.0,6.7,222.7c6.9,222.9,7.0,223.4,7.0,223.8c7.0,224.2,7.8,225.7,9.1,227.5c10.9,230.2,11.2,230.5,11.9,230.5c12.4,230.5,12.9,230.6,13.0,230.8c13.1,231.0,13.5,231.2,13.9,231.3c15.1,231.5,75.3,231.5,76.7,231.3|m152.3,230.9c152.5,230.7,152.8,230.5,153.1,230.5c153.7,230.5,155.6,227.8,155.6,226.9c155.6,226.5,155.7,225.6,155.9,224.9c156.2,223.8,156.3,220.4,156.2,199.3c156.1,175.8,156.1,175.0,155.7,173.7c155.4,172.9,154.8,171.9,154.3,171.3l153.4,170.2l119.5,170.2c92.7,170.2,85.6,170.3,85.3,170.6c85.2,170.9,84.9,171.1,84.7,171.1c84.5,171.1,84.0,171.5,83.7,172.0l83.0,173.0l83.0,199.6c83.0,225.8,83.0,226.3,83.5,227.7c83.8,228.5,84.2,229.2,84.4,229.3c84.6,229.4,85.0,229.7,85.1,229.8c85.3,230.0,85.7,230.3,85.8,230.4c86.0,230.5,86.4,230.7,86.7,230.9c86.9,231.0,87.5,231.2,87.8,231.3c88.2,231.4,102.8,231.4,120.3,231.4c145.3,231.4,152.1,231.3,152.3,230.9|m226.9,230.9c227.1,230.7,227.6,230.5,228.0,230.5c228.4,230.5,228.8,230.3,229.0,230.0c229.2,229.7,229.5,229.5,229.7,229.5c230.2,229.5,232.6,225.8,233.1,224.3c233.2,223.7,233.5,222.2,233.6,221.1c233.6,219.9,233.8,218.9,233.9,218.7c234.1,218.5,234.2,210.2,234.2,197.0c234.2,176.6,234.1,175.6,233.7,174.1c233.4,173.3,232.9,172.1,232.4,171.4l231.6,170.2l196.3,170.2l161.0,170.2l160.1,171.3c159.2,172.4,159.1,172.5,158.5,174.6c158.2,175.7,158.1,178.6,158.1,199.3c158.1,219.5,158.2,222.9,158.5,223.8c158.7,224.3,158.8,225.2,158.8,225.7c158.8,226.2,159.0,226.8,159.2,227.1c159.4,227.3,159.5,227.8,159.5,228.1c159.5,228.4,159.7,228.8,159.8,229.1c160.0,229.3,160.3,229.5,160.5,229.5c160.7,229.5,161.0,229.7,161.2,230.0c161.3,230.3,161.7,230.5,162.0,230.5c162.3,230.5,162.6,230.6,162.7,230.8c162.8,231.0,163.2,231.2,163.6,231.3c164.0,231.4,178.3,231.4,195.5,231.4c220.1,231.4,226.7,231.3,226.9,230.9|m332.6,230.6c333.0,230.1,333.6,229.2,334.0,228.5l334.6,227.3l334.6,200.7c334.6,180.0,334.6,174.1,334.3,173.8c334.2,173.5,334.0,173.0,334.0,172.6c334.0,171.8,333.6,171.1,333.1,171.1c332.9,171.1,332.4,170.8,332.0,170.6c331.4,170.1,327.1,170.0,298.0,170.0c279.6,170.0,264.3,170.1,263.9,170.3c262.9,170.5,261.3,172.6,261.3,173.6c261.3,174.0,261.2,174.6,261.0,174.8c260.8,175.1,260.7,180.2,260.7,197.9c260.7,215.5,260.8,220.6,261.0,220.9c261.2,221.2,261.3,221.9,261.3,222.5c261.3,223.1,261.4,223.7,261.6,224.0c261.8,224.2,262.0,224.7,262.0,225.0c262.0,225.7,264.6,229.5,265.1,229.5c265.3,229.5,265.6,229.7,265.7,230.0c265.9,230.3,266.3,230.5,266.5,230.5c266.8,230.5,267.1,230.6,267.3,230.8c267.4,231.0,267.8,231.2,268.2,231.3c268.6,231.4,283.0,231.4,300.4,231.4l331.8,231.4l332.6,230.6|m406.8,230.9c407.0,230.7,407.3,230.5,407.5,230.5c407.9,230.5,409.1,228.8,409.1,228.1c409.1,227.8,409.3,227.3,409.5,226.9c410.0,225.9,410.0,174.9,409.5,173.5c409.3,173.0,409.1,172.3,409.0,172.0c409.0,171.7,408.7,171.3,408.5,171.2c408.3,171.1,407.9,170.8,407.6,170.6c407.3,170.3,398.9,170.2,374.0,170.1c355.8,170.1,340.5,170.1,339.9,170.2c338.8,170.5,337.3,172.3,337.3,173.4c337.3,173.8,337.2,174.3,337.0,174.5c336.4,175.1,336.4,224.1,337.0,225.2c337.2,225.5,337.3,226.2,337.3,226.7c337.3,227.7,339.0,230.5,339.7,230.5c339.9,230.5,340.1,230.6,340.2,230.8c340.4,231.0,340.8,231.2,341.3,231.3c341.7,231.4,356.6,231.4,374.3,231.4c399.7,231.4,406.6,231.3,406.8,230.9|m480.5,230.9c480.7,230.7,481.2,230.5,481.7,230.5c482.1,230.5,482.6,230.3,482.8,230.0c483.0,229.7,483.2,229.5,483.4,229.5c483.9,229.5,486.3,225.8,486.8,224.1c487.1,223.2,487.4,222.2,487.5,221.8c487.8,220.9,488.0,195.2,487.8,184.0l487.7,174.0l486.4,172.1l485.2,170.2l450.2,170.1c411.4,170.0,414.2,169.9,413.0,172.2l412.5,173.3l412.5,199.8c412.5,220.6,412.6,226.4,412.8,226.8c413.0,227.0,413.1,227.5,413.1,227.9c413.1,228.8,413.5,229.5,414.1,229.5c414.3,229.5,414.6,229.7,414.7,230.0c414.9,230.3,415.3,230.5,415.5,230.5c415.8,230.5,416.1,230.6,416.3,230.8c416.4,231.0,416.8,231.2,417.2,231.3c417.6,231.4,431.9,231.4,449.1,231.4c473.6,231.4,480.3,231.3,480.5,230.9|m583.0,230.9c583.1,230.7,583.5,230.5,583.8,230.5c584.5,230.5,585.9,228.0,586.1,226.3c586.2,225.5,586.2,213.2,586.2,199.1c586.1,173.3,586.1,173.3,585.6,172.3c585.2,171.5,584.7,171.1,583.7,170.6c582.4,170.0,580.5,170.0,548.2,170.1l514.1,170.2l512.9,172.2l511.6,174.1l511.6,197.8c511.6,213.3,511.7,221.6,511.8,221.7c511.9,221.9,512.0,222.5,512.0,223.1c512.0,223.9,512.3,224.5,512.7,225.2c513.1,225.7,513.5,226.4,513.5,226.7c513.5,227.4,514.1,228.4,514.6,228.4c514.8,228.4,515.3,228.9,515.7,229.5c516.1,230.2,516.6,230.5,517.1,230.5c517.5,230.5,517.9,230.6,518.0,230.8c518.1,231.0,518.6,231.2,519.1,231.3c519.5,231.4,534.0,231.4,551.3,231.4c576.1,231.4,582.7,231.3,583.0,230.9|m657.6,230.9c657.7,230.7,658.0,230.5,658.2,230.5c658.4,230.5,659.1,229.8,659.7,228.9l660.7,227.4l660.7,200.3c660.7,174.8,660.7,173.3,660.3,172.4c660.0,171.9,659.6,171.2,659.2,170.8c658.6,170.2,657.1,170.2,625.5,170.1c594.9,170.0,592.3,170.1,591.2,170.6c590.6,170.9,589.8,171.7,589.4,172.3l588.8,173.3l588.8,200.3l588.8,227.2l589.7,228.9c590.3,229.8,590.9,230.5,591.1,230.5c591.3,230.5,591.6,230.6,591.7,230.8c591.8,231.0,592.3,231.2,592.7,231.3c593.2,231.4,607.9,231.4,625.4,231.4c650.6,231.4,657.3,231.3,657.6,230.9|m732.2,230.9c732.4,230.7,732.8,230.5,733.2,230.5c733.7,230.5,734.2,230.2,734.6,229.5c735.0,228.9,735.5,228.4,735.7,228.4c736.1,228.4,736.6,227.8,736.6,227.1c736.6,226.9,736.9,226.1,737.3,225.5c737.7,224.8,738.0,223.9,738.0,223.3c738.0,222.8,738.1,222.2,738.3,222.0c738.5,221.6,738.6,216.4,738.6,197.9l738.6,174.3l738.0,173.0c737.6,172.4,737.0,171.5,736.6,171.0l735.8,170.2l700.9,170.2l666.1,170.2l665.3,171.0c664.9,171.5,664.3,172.4,663.9,173.0l663.3,174.3l663.2,197.0c663.2,209.5,663.2,221.3,663.3,223.2l663.4,226.8l664.8,228.7c665.5,229.7,666.2,230.5,666.4,230.5c666.6,230.5,666.9,230.6,667.0,230.8c667.2,231.0,667.6,231.2,668.0,231.3c668.3,231.4,682.9,231.4,700.3,231.4c725.2,231.4,732.0,231.3,732.2,230.9|m837.2,230.9c837.4,230.7,837.7,230.5,838.0,230.5c838.5,230.5,839.3,229.4,840.1,227.8c840.4,227.0,840.5,224.5,840.5,200.8l840.5,174.6l839.8,173.2c839.4,172.5,838.8,171.5,838.3,171.0l837.5,170.2l802.6,170.2l767.7,170.2l766.8,171.6c765.1,174.0,765.1,173.3,765.2,198.7c765.3,215.7,765.4,221.8,765.6,222.9c765.8,224.1,766.3,225.1,767.5,227.0c768.5,228.4,769.4,229.5,769.6,229.5c769.8,229.5,770.1,229.7,770.3,230.0c770.5,230.3,770.8,230.5,771.0,230.5c771.2,230.5,771.5,230.6,771.6,230.8c771.7,231.0,772.2,231.2,772.6,231.3c773.1,231.4,787.7,231.4,805.2,231.4c830.3,231.4,837.0,231.3,837.2,230.9|m912.5,230.9c912.7,230.7,913.0,230.5,913.2,230.5c913.8,230.5,915.0,228.7,915.7,226.9l916.3,225.2l916.3,199.7l916.3,174.1l915.4,172.6c914.9,171.7,914.3,171.1,914.0,171.1c913.8,171.1,913.4,170.9,913.3,170.6c913.0,170.3,905.8,170.2,879.0,170.2l844.9,170.2l844.3,171.1c844.0,171.5,843.4,172.5,843.0,173.3l842.3,174.6l842.3,199.7c842.3,221.3,842.4,225.0,842.7,225.5c842.9,225.9,843.0,226.5,843.0,226.9c843.0,227.8,844.9,230.5,845.5,230.5c845.8,230.5,846.1,230.6,846.2,230.8c846.3,231.0,846.8,231.2,847.3,231.3c847.7,231.4,862.5,231.4,880.2,231.4c905.5,231.4,912.3,231.3,912.5,230.9|m986.2,230.9c986.4,230.7,986.8,230.5,987.0,230.5c987.3,230.5,987.7,230.3,987.8,230.0c988.0,229.7,988.3,229.5,988.5,229.5c989.0,229.5,991.6,225.7,991.6,225.0c991.6,224.7,991.7,224.2,991.9,224.0c992.1,223.7,992.3,223.2,992.3,222.8c992.3,222.4,992.4,221.9,992.6,221.6c992.8,221.3,992.9,216.0,992.9,197.7l992.9,174.3l992.2,173.0c991.9,172.4,991.2,171.5,990.8,171.0l990.1,170.2l955.6,170.2l921.1,170.2l920.3,171.0c919.9,171.5,919.2,172.4,918.9,173.0l918.2,174.3l918.2,199.8c918.2,219.8,918.3,225.4,918.5,225.7c918.7,226.0,918.8,226.4,918.8,226.7c918.8,227.6,920.7,230.5,921.3,230.5c921.5,230.5,921.9,230.6,922.0,230.8c922.1,231.0,922.5,231.2,922.9,231.3c923.3,231.4,937.6,231.4,954.8,231.4c979.4,231.4,986.0,231.3,986.2,230.9|m72.5,167.8c72.7,167.4,73.4,167.3,76.0,167.3c79.3,167.3,79.8,167.1,79.8,165.9c79.8,165.6,79.9,165.1,80.1,164.9c80.3,164.7,80.5,164.1,80.5,163.7c80.5,163.3,80.6,162.7,80.8,162.5c81.1,162.2,81.2,161.3,81.2,159.1c81.2,156.8,81.1,155.9,80.8,155.6c80.4,155.1,80.4,153.2,80.8,152.4c81.3,151.4,81.3,141.1,80.8,139.7c80.3,138.3,80.3,133.4,80.8,132.0c81.1,131.1,81.2,129.6,81.1,122.3c81.1,116.0,81.0,113.6,80.8,113.3c80.6,113.1,80.5,112.6,80.5,112.3c80.5,112.0,80.0,111.1,79.4,110.4l78.4,109.0l70.1,108.8c59.5,108.5,27.7,108.5,17.2,108.8l9.1,109.0l7.7,110.8l6.4,112.6l6.4,137.9c6.4,157.6,6.5,163.2,6.7,163.6c6.9,163.8,7.0,164.2,7.0,164.6c7.0,164.9,7.3,165.6,7.7,166.1l8.5,167.1l38.2,167.3c61.6,167.4,68.1,167.6,68.3,167.9c68.8,168.5,72.1,168.5,72.5,167.8|m107.9,167.8c108.9,167.1,116.3,167.1,116.7,167.8c117.1,168.5,119.3,168.5,119.7,167.9c120.0,167.6,123.9,167.4,137.0,167.3c154.0,167.1,154.0,167.1,154.7,166.4c155.2,165.9,155.6,165.0,155.8,163.9c156.2,162.4,156.3,160.2,156.3,138.6c156.3,111.8,156.3,112.9,154.4,110.2l153.4,108.7l119.8,108.7c91.8,108.7,86.0,108.8,85.5,109.2c85.1,109.5,84.6,109.8,84.4,109.9c84.3,110.0,83.9,110.8,83.6,111.5l83.1,112.8l83.1,138.6l83.0,164.4l84.0,165.9c85.0,167.2,85.1,167.3,86.4,167.3c87.1,167.3,88.0,167.5,88.3,167.8c89.3,168.6,106.9,168.6,107.9,167.8|m163.5,167.9c163.7,167.6,171.1,167.4,198.0,167.3c231.5,167.1,232.2,167.1,232.7,166.5c233.0,166.1,233.4,165.1,233.7,164.3c234.1,162.8,234.2,162.0,234.1,138.3c234.0,110.9,234.1,112.3,232.3,110.0l231.3,108.7l196.1,108.7l161.0,108.7l159.9,110.3c159.3,111.1,158.8,112.0,158.8,112.2c158.8,112.4,158.7,113.0,158.5,113.6c158.2,114.4,158.1,117.9,158.1,138.1c158.1,158.3,158.2,161.8,158.5,162.6c158.7,163.2,158.8,163.8,158.8,164.0c158.8,164.6,160.8,167.3,161.2,167.3c161.4,167.3,161.7,167.5,161.9,167.8c162.2,168.4,163.1,168.5,163.5,167.9|m307.0,167.8c308.0,167.1,324.7,167.1,325.7,167.8c326.6,168.5,327.8,168.5,328.2,167.8c328.4,167.4,329.0,167.3,330.5,167.3l332.6,167.3l333.5,166.0l334.5,164.6l334.6,160.4c334.7,158.0,334.7,146.4,334.7,134.4c334.6,117.6,334.6,112.6,334.3,112.3c334.2,112.0,334.0,111.6,334.0,111.3c334.0,110.6,333.3,109.6,332.8,109.6c332.5,109.6,332.1,109.4,332.0,109.2c331.7,108.7,289.8,108.4,274.3,108.7l263.4,109.0l262.3,110.3c261.8,111.1,261.3,112.0,261.3,112.3c261.3,112.6,261.2,113.1,261.0,113.3c260.8,113.6,260.7,119.0,260.7,137.9c260.7,156.8,260.8,162.2,261.0,162.5c261.2,162.8,261.3,163.4,261.3,164.0c261.3,164.8,261.5,165.4,262.0,166.1l262.7,167.1l284.0,167.3c300.5,167.4,305.3,167.6,305.5,167.9c305.9,168.5,306.2,168.4,307.0,167.8|m347.8,167.9c348.0,167.6,354.5,167.4,378.1,167.3l408.0,167.1l408.9,165.6l409.8,164.0l409.8,138.0l409.8,111.9l408.8,110.3l407.8,108.7l373.6,108.7l339.5,108.7l338.6,109.8c338.1,110.3,337.6,111.0,337.5,111.3c337.5,111.6,337.2,112.3,337.0,113.0c336.6,114.0,336.6,116.4,336.6,138.8c336.6,160.3,336.7,163.5,337.0,163.9c337.2,164.1,337.3,164.5,337.3,164.9c337.3,165.6,337.8,166.3,338.3,166.3c338.5,166.3,338.8,166.5,338.9,166.8c339.1,167.1,339.7,167.3,340.7,167.3c341.7,167.3,342.3,167.5,342.5,167.8c342.8,168.5,347.4,168.6,347.8,167.9|m421.0,167.9c421.2,167.6,428.2,167.4,453.6,167.3l485.9,167.1l486.8,165.7l487.7,164.2l487.8,153.3c487.9,147.3,487.9,135.8,487.9,127.6l487.7,112.9l487.1,111.8c486.8,111.1,486.2,110.2,485.7,109.7l484.8,108.7l450.0,108.7l415.2,108.7l413.9,110.7l412.5,112.7l412.4,136.8c412.4,150.1,412.4,161.7,412.5,162.7c412.7,164.8,413.9,167.3,414.8,167.3c415.1,167.3,415.5,167.5,415.7,167.8c416.1,168.5,420.6,168.6,421.0,167.9|m527.0,167.9c527.2,167.6,533.4,167.4,555.6,167.3l584.0,167.1l584.7,166.4c586.3,164.7,586.2,166.0,586.1,137.4l586.1,111.7l585.1,110.2l584.1,108.8l560.3,108.6c547.2,108.5,531.4,108.6,525.3,108.7l514.1,109.0l512.8,110.8l511.6,112.6l511.6,137.7c511.6,165.1,511.5,164.2,512.9,166.4c513.5,167.2,513.7,167.3,515.6,167.3c517.0,167.3,517.7,167.4,518.0,167.8c518.6,168.5,526.5,168.6,527.0,167.9|m602.3,167.8c603.2,167.1,613.0,167.1,613.7,167.8c614.3,168.4,617.6,168.5,618.0,167.9c618.2,167.6,622.8,167.4,638.5,167.3l658.7,167.1l659.7,165.7l660.7,164.2l660.7,138.2l660.7,112.2l660.2,111.1c659.0,108.6,661.0,108.8,635.3,108.6c622.7,108.5,607.5,108.6,601.6,108.7l590.9,109.0l589.8,110.3c589.2,111.1,588.8,112.0,588.8,112.3c588.8,112.7,588.6,113.1,588.4,113.4c588.0,113.9,588.0,116.1,588.4,116.7c588.6,117.1,588.7,122.5,588.8,140.7l588.9,164.2l589.8,165.7l590.7,167.3l592.5,167.3c593.8,167.3,594.4,167.4,594.6,167.8c595.0,168.6,601.3,168.6,602.3,167.8|m669.2,167.9c669.4,167.6,676.6,167.4,703.0,167.3l736.6,167.1l737.3,166.1c737.7,165.6,738.0,164.9,738.0,164.6c738.0,164.2,738.1,163.8,738.3,163.6c738.5,163.2,738.6,157.6,738.6,137.9l738.6,112.6l737.3,110.8l736.0,109.0l727.7,108.8c717.0,108.5,684.9,108.5,674.2,108.8l665.9,109.0l664.6,110.8l663.3,112.6l663.3,138.4l663.3,164.2l664.3,165.7c665.2,167.1,665.5,167.3,666.3,167.3c666.9,167.3,667.4,167.5,667.6,167.8c668.0,168.4,668.8,168.5,669.2,167.9|m837.4,167.8c837.6,167.5,837.9,167.3,838.1,167.3c838.6,167.3,840.2,164.8,840.4,163.7c840.4,163.3,840.5,151.7,840.4,137.8l840.4,112.7l839.0,110.7l837.7,108.7l802.9,108.7l768.1,108.7l767.0,110.0c765.1,112.4,765.1,111.6,765.1,138.2c765.1,164.1,765.1,163.3,766.8,165.8l767.7,167.1l802.0,167.3c828.9,167.4,836.3,167.6,836.5,167.9c836.9,168.5,837.1,168.4,837.4,167.8|m914.8,166.5c915.1,166.1,915.5,165.2,915.8,164.4c916.2,163.0,916.3,162.4,916.3,137.8l916.3,112.7l915.0,110.8l913.8,109.0l902.8,108.7c896.8,108.6,881.3,108.5,868.5,108.6l845.1,108.8l844.1,110.3c843.5,111.1,843.0,112.0,843.0,112.2c843.0,112.4,842.9,113.0,842.7,113.6c842.2,115.0,842.2,162.4,842.7,163.4c842.9,163.7,843.0,164.4,843.0,164.8c843.0,165.7,844.1,166.9,845.2,167.0c845.6,167.1,861.3,167.2,880.2,167.2c913.3,167.1,914.4,167.1,914.8,166.5|m991.5,166.3c992.0,165.8,992.3,165.2,992.3,164.8c992.3,164.3,992.4,163.8,992.6,163.6c992.8,163.2,992.9,157.6,992.9,137.9l992.9,112.6l991.6,110.8l990.2,109.0l982.1,108.8c971.6,108.5,939.5,108.5,929.0,108.8l920.9,109.0l919.6,110.8l918.2,112.6l918.2,137.9c918.2,157.6,918.3,163.2,918.5,163.6c918.7,163.8,918.8,164.2,918.8,164.6c918.8,165.4,920.0,166.9,920.9,167.0c921.4,167.1,937.3,167.2,956.3,167.2l990.8,167.1l991.5,166.3|m77.8,106.7c78.0,106.4,78.4,106.2,78.6,106.2c79.1,106.1,80.5,104.1,80.5,103.4c80.5,103.1,80.6,102.6,80.8,102.4c81.0,102.1,81.2,101.4,81.2,100.8c81.2,100.2,81.0,99.5,80.8,99.3c80.4,98.7,80.3,95.1,80.8,94.5c81.2,93.9,81.2,70.1,80.8,69.3c80.5,68.9,80.5,68.7,80.8,68.4c81.3,67.8,81.3,65.8,80.8,65.3c80.6,65.0,80.6,64.8,80.9,63.9c81.1,63.1,81.2,61.6,81.1,56.7l81.1,50.5l79.8,48.6c79.1,47.6,78.2,46.6,77.9,46.5c77.6,46.4,77.2,46.1,77.0,45.9c76.5,45.3,13.5,45.4,13.1,45.9c12.9,46.2,12.4,46.4,12.0,46.4c11.6,46.4,11.2,46.6,11.0,46.9c10.8,47.2,10.5,47.4,10.3,47.4c9.8,47.4,7.0,51.5,7.0,52.2c7.0,52.5,6.9,53.0,6.7,53.2c6.5,53.5,6.4,59.0,6.4,78.3l6.4,103.0l7.4,104.5l8.4,106.0l41.3,106.1c66.7,106.3,74.4,106.4,74.7,106.7c75.4,107.3,77.2,107.3,77.8,106.7|m268.9,106.8c269.4,106.4,276.6,106.3,301.1,106.1l332.6,106.0l333.6,104.5l334.6,103.0l334.6,76.2l334.6,49.4l333.3,47.6l332.0,45.8l321.9,45.5c307.4,45.1,266.9,45.5,266.6,46.0c266.5,46.2,266.0,46.4,265.7,46.4c265.2,46.4,264.6,46.9,263.5,48.5c262.7,49.7,262.0,50.9,262.0,51.2c262.0,51.5,261.8,52.0,261.6,52.2c261.4,52.5,261.3,52.9,261.3,53.2c261.3,53.5,261.2,54.0,261.0,54.2c260.6,54.9,260.6,100.8,261.0,101.4c261.2,101.6,261.3,102.3,261.3,102.9c261.3,104.2,262.5,106.1,263.4,106.1c263.8,106.1,264.3,106.4,264.7,106.7c265.5,107.3,268.0,107.3,268.9,106.8|m406.4,106.7c406.7,106.4,407.1,106.2,407.4,106.2c407.7,106.2,408.3,105.5,408.9,104.5l409.8,102.9l409.8,76.5c409.8,50.4,409.8,50.0,409.3,48.9c409.1,48.3,408.4,47.3,407.9,46.6l406.9,45.5l373.9,45.5c347.8,45.5,340.8,45.6,340.5,45.9c340.4,46.2,340.1,46.4,339.8,46.4c339.6,46.4,338.9,47.0,338.4,47.8c337.5,48.9,337.3,49.5,337.3,50.3c337.3,50.9,337.2,51.7,337.0,52.1c336.7,52.6,336.6,56.2,336.6,77.3l336.6,101.9l337.9,103.9l339.1,106.0l371.0,106.1c395.5,106.3,403.0,106.4,403.4,106.7c404.0,107.3,405.9,107.3,406.4,106.7|m657.4,106.7c657.7,106.4,658.1,106.2,658.3,106.2c658.5,106.2,659.1,105.5,659.6,104.6l660.5,103.0l660.7,96.8c660.8,93.3,660.8,81.3,660.8,70.2l660.7,49.9l660.0,48.7c659.7,48.0,659.0,47.0,658.5,46.5l657.7,45.5l625.0,45.5c599.2,45.5,592.2,45.6,592.0,45.9c591.9,46.2,591.6,46.4,591.4,46.4c590.9,46.4,589.7,47.8,589.2,49.0c588.8,50.0,588.8,51.0,588.8,76.5l588.8,103.0l589.7,104.3l590.6,105.7l593.9,105.9c595.8,106.0,609.9,106.2,625.3,106.2c648.1,106.2,653.4,106.3,654.0,106.7c655.1,107.3,656.9,107.3,657.4,106.7|m850.7,106.8c851.2,106.4,858.4,106.3,882.8,106.1l914.3,106.0l915.0,105.1c915.3,104.7,915.6,104.0,915.6,103.7c915.6,103.4,915.7,102.9,915.9,102.7c916.2,102.3,916.3,99.0,916.3,76.5l916.3,50.8l915.7,49.7c915.4,49.1,915.1,48.3,915.1,48.1c915.1,47.4,914.4,46.4,913.8,46.4c913.5,46.4,913.2,46.2,913.0,45.9c912.8,45.6,905.8,45.5,879.6,45.5c853.5,45.5,846.5,45.6,846.3,45.9c846.1,46.2,845.8,46.4,845.6,46.4c845.2,46.4,843.0,49.5,843.0,50.1c843.0,50.4,842.9,51.0,842.7,51.3c842.4,51.9,842.3,55.5,842.3,76.8l842.3,101.6l843.0,102.9c843.9,104.7,845.2,106.1,846.0,106.2c846.4,106.2,846.9,106.4,847.1,106.7c847.7,107.3,849.8,107.3,850.7,106.8|m154.7,105.3c156.2,103.7,156.1,104.3,156.2,77.1c156.3,52.5,156.3,52.3,155.8,50.7c155.5,49.8,154.7,48.3,154.1,47.4l152.9,45.8l142.7,45.5c127.9,45.1,87.3,45.5,87.0,46.0c86.8,46.2,86.4,46.4,86.0,46.4c85.1,46.4,83.8,47.9,83.6,49.1c83.5,49.7,83.4,50.2,83.3,50.3c83.1,50.5,83.0,61.2,83.0,76.9l83.0,103.3l84.0,104.6c85.0,105.8,85.0,105.8,87.3,105.9c88.6,106.0,104.2,106.0,121.9,106.0c154.0,106.0,154.0,106.0,154.7,105.3|m232.2,104.9c232.7,104.4,233.1,103.7,233.2,103.4c233.3,103.1,233.5,102.4,233.8,101.7c234.1,100.7,234.2,98.4,234.2,77.8c234.2,58.3,234.1,54.9,233.8,54.1c233.6,53.5,233.5,52.7,233.5,52.2c233.4,50.8,230.2,46.4,229.1,46.4c228.7,46.4,228.3,46.2,228.1,46.0c227.8,45.5,186.5,45.1,171.7,45.5l161.4,45.8l160.1,47.6c159.4,48.7,158.8,49.7,158.8,50.0c158.8,50.2,158.7,50.9,158.5,51.4c158.0,52.9,158.0,99.6,158.5,101.1c158.7,101.7,158.8,102.3,158.8,102.5c158.8,102.8,159.2,103.6,159.8,104.4l160.7,105.8l163.1,105.9c164.4,106.0,180.3,106.0,198.4,106.0l231.3,106.0l232.2,104.9|m486.1,105.3c486.5,105.0,487.0,104.2,487.3,103.6l487.8,102.5l487.8,78.3c487.8,59.3,487.8,53.9,487.5,53.5c487.4,53.3,487.3,52.8,487.3,52.4c487.3,51.9,487.1,51.4,486.9,51.2c486.7,50.9,486.5,50.6,486.5,50.3c486.5,49.4,485.5,48.1,484.3,47.2c483.5,46.7,482.7,46.1,482.4,45.9c481.5,45.3,416.7,45.4,416.3,45.9c416.2,46.2,415.9,46.4,415.7,46.4c415.5,46.4,414.7,47.2,414.0,48.2c413.0,49.6,412.7,50.3,412.6,51.4c412.4,53.1,412.4,100.4,412.6,102.2c412.6,103.0,413.0,103.9,413.5,104.6c414.3,105.8,414.3,105.8,416.8,105.9c418.2,106.0,434.2,106.0,452.4,106.0c484.4,106.0,485.5,106.0,486.1,105.3|m584.6,105.4c584.9,105.0,585.4,104.3,585.7,103.8c586.1,102.9,586.1,101.4,586.2,80.3c586.3,62.9,586.4,57.6,586.6,57.3c587.0,56.8,587.0,55.6,586.6,55.0c586.4,54.7,586.4,54.5,586.7,54.1c586.9,53.7,586.9,53.5,586.6,53.0c586.4,52.6,586.2,51.8,586.2,51.0c586.2,49.9,586.0,49.4,585.1,48.0c584.5,47.1,583.8,46.4,583.6,46.4c583.4,46.4,583.1,46.2,583.0,45.9c582.7,45.6,575.9,45.5,550.3,45.5c524.7,45.5,517.9,45.6,517.6,45.9c517.5,46.2,517.0,46.4,516.5,46.4c515.9,46.4,515.5,46.8,514.0,48.9c512.9,50.4,512.2,51.7,512.1,52.3c512.0,52.8,511.9,53.3,511.8,53.4c511.7,53.5,511.6,64.7,511.6,78.3l511.6,103.1l512.5,104.4l513.4,105.8l515.8,105.9c517.2,106.0,533.0,106.0,551.1,106.0c582.5,106.0,584.0,105.9,584.6,105.4|m733.1,105.9l736.6,105.7l737.6,104.4l738.6,103.1l738.6,78.4c738.6,59.0,738.5,53.5,738.3,53.2c738.1,53.0,738.0,52.3,738.0,51.7c738.0,50.2,735.4,46.4,734.3,46.4c734.0,46.4,733.5,46.2,733.4,45.9c733.0,45.4,667.1,45.3,666.6,45.9c666.5,46.1,666.1,46.4,665.7,46.5c665.4,46.6,664.7,47.3,664.2,48.1l663.3,49.5l663.3,76.3l663.3,103.0l664.0,104.1c664.3,104.6,664.9,105.1,665.1,105.1c665.4,105.1,665.7,105.3,665.9,105.4c666.0,105.6,667.1,105.8,668.4,105.9c673.1,106.1,729.6,106.1,733.1,105.9|m839.0,105.2c840.5,103.6,840.5,104.9,840.4,75.8l840.4,49.5l839.3,47.9c838.7,47.1,838.1,46.4,837.9,46.4c837.7,46.4,837.4,46.2,837.2,45.9c837.0,45.6,830.1,45.5,804.6,45.5c779.0,45.5,772.1,45.6,771.9,45.9c771.7,46.2,771.3,46.4,770.9,46.4c770.5,46.4,770.0,46.6,769.8,46.9c769.7,47.2,769.4,47.4,769.2,47.4c768.6,47.4,766.8,49.8,766.3,51.3c765.1,54.8,765.2,54.0,765.1,78.3c765.1,103.3,765.2,103.7,766.5,105.1c767.4,106.0,767.1,106.0,805.1,106.0l838.2,106.0l839.0,105.2|m991.9,104.5l992.9,103.0l992.9,77.8l992.9,52.6l992.2,51.6c991.9,51.1,991.6,50.4,991.6,50.2c991.6,49.5,990.2,47.4,989.7,47.4c989.5,47.4,989.2,47.2,989.0,46.9c988.8,46.6,988.5,46.4,988.3,46.4c988.1,46.4,987.8,46.2,987.7,46.0c987.3,45.5,946.1,45.1,931.6,45.5l921.6,45.8l920.2,47.7c919.5,48.7,918.8,49.8,918.8,50.1c918.8,50.4,918.7,50.9,918.5,51.1c918.3,51.5,918.2,57.1,918.2,76.8c918.2,96.5,918.3,102.1,918.5,102.4c918.7,102.7,918.8,103.1,918.8,103.4c918.8,103.7,919.1,104.4,919.5,104.9c920.1,105.7,920.3,105.8,922.6,105.9c923.9,106.0,939.8,106.0,957.9,106.0l990.9,106.0l991.9,104.5|m57.8,24.0l57.8,10.6l64.0,10.7c68.5,10.8,70.2,10.9,70.4,11.3c70.6,11.5,71.0,11.7,71.4,11.7c71.7,11.7,72.1,11.9,72.3,12.2c72.4,12.5,72.7,12.7,73.0,12.7c73.2,12.7,73.8,13.4,74.3,14.2l75.3,15.7l75.3,19.1l75.3,22.5l74.3,24.0c73.8,24.8,73.1,25.4,72.9,25.4c72.7,25.4,72.4,25.7,72.3,25.9c72.1,26.2,71.6,26.5,71.2,26.5c70.8,26.5,70.3,26.7,70.2,27.0c69.9,27.4,70.0,27.7,70.6,28.6c71.0,29.2,71.3,30.0,71.3,30.3c71.3,30.5,72.2,32.1,73.3,33.7c74.4,35.3,75.3,36.8,75.3,37.0c75.3,37.2,75.1,37.4,74.8,37.4c74.2,37.4,73.0,35.8,73.0,35.1c73.0,34.8,72.2,33.4,71.2,31.9c70.3,30.5,69.5,29.1,69.5,28.8c69.5,27.6,69.0,27.5,64.2,27.5c60.9,27.5,59.4,27.6,59.2,27.9c59.0,28.2,58.9,29.7,58.9,32.5c58.9,36.6,58.8,37.4,58.1,37.4c57.8,37.4,57.8,34.8,57.8,24.0|m109.9,36.9c109.9,36.7,110.0,36.4,110.2,36.2c110.3,36.1,110.4,35.8,110.4,35.4c110.4,35.1,110.7,34.4,111.1,33.8c111.5,33.3,111.8,32.6,111.8,32.3c111.8,31.9,112.0,31.5,112.2,31.3c112.4,31.0,112.5,30.6,112.5,30.3c112.5,29.9,112.8,29.2,113.2,28.7c113.6,28.1,113.9,27.4,113.9,27.1c113.9,26.8,114.1,26.3,114.3,26.1c114.5,25.9,114.6,25.5,114.6,25.3c114.6,25.2,114.9,24.4,115.3,23.7c115.7,23.0,116.0,22.2,116.0,21.9c116.0,21.6,116.2,21.2,116.4,21.0c116.6,20.7,116.7,20.3,116.7,20.1c116.7,19.9,117.0,19.3,117.4,18.7c117.8,18.2,118.1,17.5,118.1,17.2c118.1,16.9,118.4,16.2,118.7,15.8c119.0,15.4,119.3,14.7,119.3,14.4c119.3,14.1,119.5,13.6,119.6,13.4c119.8,13.2,120.0,12.7,120.0,12.4c120.0,11.0,121.6,10.1,122.3,11.1c122.4,11.3,122.6,11.8,122.6,12.2c122.6,12.6,122.9,13.4,123.3,13.9c123.7,14.5,124.0,15.1,124.0,15.3c124.0,15.5,124.1,15.9,124.3,16.1c124.5,16.4,124.7,16.8,124.7,17.2c124.7,17.5,125.0,18.2,125.4,18.7c125.8,19.3,126.1,20.0,126.1,20.3c126.1,20.6,126.2,21.0,126.3,21.1c126.4,21.2,126.5,21.6,126.5,21.9c126.5,22.3,126.9,23.0,127.3,23.5c127.6,24.1,128.0,24.8,128.0,25.1c128.0,25.4,128.1,25.9,128.3,26.1c128.5,26.3,128.7,26.8,128.7,27.1c128.7,27.4,129.0,28.1,129.4,28.7c129.7,29.2,130.1,29.9,130.1,30.1c130.1,30.3,130.2,30.7,130.4,30.9c130.6,31.2,130.8,31.7,130.8,32.1c130.8,32.5,131.1,33.3,131.5,33.8c131.8,34.4,132.2,35.1,132.2,35.4c132.2,35.7,132.3,36.2,132.5,36.4c133.0,37.0,132.9,37.4,132.3,37.4c131.9,37.4,131.7,37.2,131.7,37.0c131.7,36.7,131.5,36.3,131.3,36.1c131.2,35.8,131.0,35.4,131.0,35.1c131.0,34.7,130.7,34.0,130.3,33.5c129.9,33.0,129.6,32.3,129.6,31.9c129.6,31.6,129.3,31.0,128.9,30.5l128.3,29.5l121.3,29.5l114.2,29.5l113.6,30.5c113.3,31.0,113.0,31.7,113.0,32.0c113.0,32.3,112.7,33.0,112.3,33.5c111.9,34.0,111.6,34.7,111.6,35.1c111.6,35.4,111.4,35.8,111.2,36.1c111.0,36.3,110.9,36.7,110.9,37.0c110.9,37.2,110.7,37.4,110.4,37.4c110.2,37.4,109.9,37.2,109.9,36.9|m176.1,24.0c176.1,15.3,176.2,10.6,176.4,10.6c176.5,10.6,176.6,11.3,176.6,12.1c176.6,13.0,176.8,14.1,177.0,14.7c177.3,15.6,177.3,17.0,177.3,23.2c177.2,28.5,177.1,30.7,176.9,31.0c176.7,31.2,176.6,32.5,176.6,34.4c176.6,36.2,176.5,37.4,176.4,37.4c176.2,37.4,176.1,32.7,176.1,24.0|m311.3,24.0l311.3,10.6l317.3,10.7c322.0,10.7,323.3,10.8,323.8,11.2c324.2,11.4,324.7,11.7,325.0,11.7c325.3,11.7,325.7,11.9,325.8,12.2c326.0,12.5,326.3,12.7,326.5,12.7c327.0,12.7,328.4,14.7,328.4,15.3c328.4,15.6,328.6,16.2,328.8,16.7c329.4,18.4,329.2,20.5,328.2,23.3c328.1,23.6,327.9,24.0,327.6,24.1c327.4,24.3,327.1,24.5,326.8,24.7c326.6,24.9,326.2,25.2,325.9,25.4c325.7,25.6,325.4,25.9,325.3,26.1c325.2,26.3,324.9,26.5,324.7,26.5c324.5,26.5,324.1,26.7,323.9,27.1c323.5,27.7,323.5,27.8,323.9,28.2c324.0,28.4,324.2,28.9,324.2,29.2c324.2,29.5,325.0,30.9,326.0,32.3c326.9,33.7,327.7,35.1,327.7,35.4c327.7,35.6,327.9,36.2,328.2,36.6c328.7,37.4,328.7,37.4,328.3,37.4c327.7,37.4,325.8,34.8,325.8,34.0c325.8,33.7,324.9,32.1,323.7,30.4l321.6,27.5l317.0,27.5c313.7,27.5,312.3,27.6,312.1,27.9c311.9,28.2,311.8,29.8,311.8,32.9c311.8,35.7,311.7,37.4,311.6,37.4c311.4,37.4,311.3,32.7,311.3,24.0|m364.0,37.1c364.0,37.0,364.1,36.6,364.3,36.4c364.5,36.2,364.7,35.7,364.7,35.4c364.7,35.1,364.8,34.6,365.0,34.4c365.2,34.1,365.4,33.7,365.4,33.3c365.4,33.0,365.7,32.3,366.1,31.8c366.5,31.2,366.8,30.5,366.8,30.2c366.8,29.9,366.9,29.4,367.1,29.2c367.3,29.0,367.5,28.5,367.5,28.2c367.5,27.9,367.8,27.2,368.2,26.6c368.6,26.1,368.9,25.4,368.9,25.1c368.9,24.7,369.0,24.3,369.2,24.0c369.4,23.8,369.6,23.4,369.6,23.2c369.6,23.0,369.9,22.4,370.3,21.8c370.7,21.3,371.0,20.6,371.0,20.3c371.0,20.0,371.3,19.3,371.6,18.9c371.9,18.5,372.2,17.8,372.2,17.5c372.2,17.2,372.3,16.7,372.5,16.5c372.7,16.3,372.9,15.8,372.9,15.5c372.9,15.2,373.2,14.5,373.6,13.9c374.0,13.4,374.3,12.7,374.3,12.4c374.3,11.6,375.0,10.6,375.6,10.6c376.1,10.6,376.8,11.7,376.8,12.4c376.8,12.7,377.2,13.4,377.5,13.9c377.9,14.5,378.2,15.1,378.2,15.3c378.2,15.5,378.4,15.9,378.6,16.1c378.8,16.4,378.9,16.8,378.9,17.2c378.9,17.5,379.2,18.0,379.4,18.4c379.7,18.7,380.2,20.0,380.6,21.1c380.9,22.3,381.4,23.4,381.6,23.7c381.8,23.9,382.3,25.1,382.7,26.2c383.0,27.4,383.6,28.6,383.8,29.0c384.1,29.4,384.3,29.9,384.3,30.2c384.3,30.5,384.6,31.2,385.0,31.8c385.4,32.3,385.7,33.0,385.7,33.3c385.7,33.7,385.9,34.1,386.1,34.4c386.3,34.6,386.4,35.1,386.4,35.4c386.4,35.7,386.6,36.2,386.8,36.4c387.3,37.0,387.2,37.4,386.5,37.4c386.2,37.4,386.0,37.2,386.0,37.0c386.0,36.7,385.8,36.3,385.6,36.1c385.4,35.8,385.3,35.4,385.3,35.1c385.3,34.8,384.9,34.1,384.6,33.4c384.2,32.8,383.9,32.1,383.9,31.8c383.9,31.6,383.6,31.0,383.2,30.5l382.5,29.5l375.7,29.5l368.9,29.5l368.1,30.4c367.6,30.9,367.3,31.6,367.3,31.9c367.3,32.1,366.9,32.9,366.5,33.5c366.2,34.2,365.8,34.9,365.8,35.2c365.8,35.4,365.6,36.0,365.2,36.5c364.5,37.4,364.0,37.7,364.0,37.1|m430.4,24.0c430.4,15.3,430.5,10.6,430.6,10.6c430.8,10.6,430.9,15.3,430.9,24.0c430.9,32.7,430.8,37.4,430.6,37.4c430.5,37.4,430.4,32.7,430.4,24.0|m560.1,37.1c559.9,36.8,559.9,36.5,560.1,36.1c560.3,35.6,560.2,35.3,560.0,34.8c559.7,34.4,559.6,32.1,559.6,22.4l559.5,10.6l565.7,10.7c570.7,10.7,571.9,10.7,572.5,11.2c572.9,11.4,573.4,11.7,573.8,11.7c574.2,11.7,574.6,11.9,574.7,12.2c574.9,12.5,575.2,12.7,575.4,12.7c575.9,12.7,577.1,14.4,577.1,15.2c577.1,15.5,577.2,15.9,577.4,16.1c577.7,16.5,577.8,17.3,577.8,19.0c577.8,21.3,577.7,21.6,577.1,22.5c576.7,23.0,576.4,23.7,576.4,23.9c576.4,24.2,576.2,24.4,576.1,24.4c575.9,24.4,575.5,24.9,575.1,25.4c574.6,26.1,574.2,26.5,573.7,26.5c572.9,26.5,572.4,27.0,572.4,27.9c572.4,28.3,573.1,29.8,574.0,31.2c574.9,32.7,575.7,34.0,575.7,34.2c575.7,34.4,576.1,35.2,576.7,36.0c577.5,37.2,577.6,37.4,577.2,37.4c576.7,37.4,573.3,32.7,573.3,32.0c573.3,31.8,572.7,30.7,571.9,29.5l570.5,27.5l565.9,27.5c562.6,27.5,561.2,27.6,561.0,27.9c560.8,28.2,560.7,29.8,560.7,32.9c560.7,35.4,560.6,37.4,560.5,37.4c560.4,37.4,560.2,37.3,560.1,37.1|m614.4,36.7c614.6,36.2,614.8,35.6,615.0,35.2c615.1,34.8,615.3,34.3,615.4,34.2c615.6,34.1,615.7,33.7,615.7,33.3c615.7,33.0,615.8,32.5,616.0,32.3c616.2,32.1,616.4,31.6,616.4,31.3c616.4,30.9,616.6,30.4,616.8,30.1c617.1,29.7,617.6,28.5,618.0,27.3c618.4,26.2,618.9,25.0,619.2,24.6c619.4,24.2,619.6,23.7,619.6,23.3c619.6,23.0,619.8,22.6,620.0,22.3c620.2,22.1,620.4,21.7,620.4,21.4c620.4,21.2,620.7,20.5,621.1,19.8c621.4,19.2,621.8,18.4,621.8,18.1c621.8,17.8,621.9,17.4,622.1,17.2c622.3,16.9,622.5,16.5,622.5,16.2c622.5,15.8,622.8,15.1,623.2,14.6c623.5,14.1,623.9,13.4,623.9,13.1c623.9,12.8,624.1,12.1,624.5,11.6c625.2,10.5,626.4,10.3,626.4,11.3c626.4,11.6,626.7,12.3,627.1,12.9c627.5,13.4,627.8,14.1,627.8,14.5c627.8,14.8,627.9,15.2,628.1,15.3c628.2,15.4,628.3,15.8,628.3,16.1c628.3,16.4,628.6,17.1,629.0,17.7c629.4,18.2,629.7,18.9,629.7,19.3c629.7,19.6,629.9,20.0,630.1,20.3c630.3,20.5,630.4,21.0,630.4,21.3c630.4,21.6,630.7,22.3,631.1,22.8c631.5,23.4,631.8,24.0,631.8,24.2c631.8,24.5,632.0,24.8,632.2,25.1c632.4,25.3,632.5,25.7,632.5,26.0c632.5,26.3,632.8,27.1,633.2,27.8c633.6,28.5,633.9,29.3,633.9,29.5c633.9,29.7,634.1,30.0,634.3,30.2c634.5,30.5,634.6,30.9,634.6,31.2c634.6,31.6,634.9,32.3,635.3,32.8c635.7,33.3,636.0,34.0,636.0,34.4c636.0,34.7,636.3,35.3,636.6,35.7c637.4,36.8,637.4,37.5,636.6,37.4c636.0,37.3,635.8,36.9,635.2,35.1c634.8,34.0,634.3,32.7,634.0,32.2c633.7,31.8,633.5,31.2,633.5,30.9c633.5,29.6,633.1,29.5,625.4,29.5c617.6,29.5,617.3,29.6,617.3,31.0c617.3,31.7,617.0,32.7,616.1,34.4c615.7,35.1,615.4,35.8,615.4,36.0c615.4,36.4,614.6,37.4,614.3,37.4c614.1,37.4,614.1,37.2,614.4,36.7|m680.9,36.9c680.6,36.4,680.6,33.9,680.6,24.0c680.6,14.2,680.6,11.7,680.9,11.2c681.1,10.9,681.3,10.6,681.4,10.6c681.5,10.6,681.6,16.6,681.6,24.0c681.6,31.5,681.5,37.4,681.4,37.4c681.3,37.4,681.1,37.2,680.9,36.9|m815.5,37.0c815.4,36.8,815.3,30.7,815.3,23.6l815.2,10.6l821.3,10.7c826.3,10.7,827.6,10.7,828.2,11.2c828.5,11.4,829.1,11.7,829.4,11.7c829.9,11.7,830.4,12.2,831.4,13.7c832.1,14.8,832.7,15.9,832.7,16.2c832.7,16.5,832.9,16.9,833.1,17.2c833.3,17.4,833.5,18.2,833.5,19.1c833.5,19.9,833.3,20.7,833.1,21.0c832.9,21.2,832.7,21.7,832.7,22.0c832.7,22.3,832.6,22.8,832.4,23.0c832.2,23.3,832.0,23.7,832.0,23.9c832.0,24.2,831.9,24.4,831.7,24.4c831.5,24.4,831.3,24.6,831.1,24.9c831.0,25.2,830.6,25.4,830.4,25.4c830.2,25.4,829.9,25.7,829.7,25.9c829.5,26.2,829.2,26.5,829.0,26.5c828.6,26.5,827.8,27.5,827.8,28.1c827.8,28.4,828.4,29.4,829.1,30.4c829.8,31.4,830.5,32.7,830.7,33.1c830.9,33.6,831.5,34.8,832.0,35.7c832.6,36.7,832.9,37.4,832.7,37.4c832.3,37.4,828.8,32.4,828.8,31.7c828.8,31.4,828.2,30.4,827.5,29.3l826.2,27.5l821.6,27.5c818.3,27.5,816.9,27.6,816.7,27.9c816.5,28.2,816.4,29.8,816.4,32.9c816.4,36.6,816.3,37.4,816.0,37.4c815.9,37.4,815.6,37.3,815.5,37.0|m869.7,36.7c869.9,36.2,870.1,35.7,870.2,35.4c870.3,35.1,870.5,34.6,870.6,34.4c870.7,34.1,871.0,33.3,871.4,32.6c871.7,31.9,872.0,31.1,872.0,30.8c872.0,30.5,872.2,30.1,872.4,29.9c872.6,29.7,872.7,29.3,872.7,29.0c872.7,28.8,873.0,28.3,873.3,27.8c873.7,27.4,873.9,26.8,873.9,26.4c873.9,26.1,874.1,25.7,874.3,25.4c874.5,25.2,874.6,24.7,874.6,24.4c874.6,24.1,874.9,23.4,875.3,22.8c875.7,22.3,876.0,21.6,876.0,21.3c876.0,21.0,876.3,20.3,876.7,19.8c877.1,19.2,877.4,18.5,877.4,18.2c877.4,17.9,877.6,17.4,877.8,17.2c878.0,16.9,878.1,16.5,878.1,16.2c878.1,15.8,878.4,15.1,878.8,14.6c879.2,14.1,879.5,13.4,879.5,13.0c879.5,12.7,879.7,12.3,879.9,12.0c880.1,11.8,880.2,11.4,880.2,11.1c880.2,10.8,880.5,10.6,881.1,10.6c881.6,10.6,881.9,10.8,881.9,11.1c881.9,11.4,882.0,11.8,882.2,12.0c882.4,12.3,882.6,12.7,882.6,13.0c882.6,13.4,882.9,14.1,883.3,14.6c883.7,15.1,884.0,15.8,884.0,16.1c884.0,16.5,884.3,17.1,884.7,17.7c885.1,18.2,885.4,18.9,885.4,19.3c885.4,19.6,885.5,20.0,885.7,20.3c885.9,20.5,886.1,21.0,886.1,21.3c886.1,21.6,886.4,22.3,886.8,22.8c887.2,23.4,887.5,24.1,887.5,24.4c887.5,24.7,887.6,25.2,887.8,25.4c888.0,25.7,888.2,26.1,888.2,26.4c888.2,26.8,888.5,27.4,888.8,27.8c889.4,28.7,890.1,30.4,890.1,31.1c890.1,31.3,890.4,31.9,890.8,32.5c891.1,33.0,891.5,33.7,891.5,34.0c891.5,34.4,891.6,34.8,891.8,35.0c892.0,35.3,892.2,35.7,892.2,36.0c892.2,36.4,892.3,36.8,892.4,37.0c892.7,37.4,892.6,37.4,892.2,37.4c891.7,37.4,891.0,36.4,891.0,35.7c891.0,35.4,890.7,34.8,890.4,34.4c890.1,33.9,889.8,33.4,889.8,33.1c889.8,32.9,889.7,32.5,889.5,32.3c889.3,32.1,889.1,31.5,889.1,31.1c889.1,29.6,889.0,29.5,881.1,29.5c873.2,29.5,873.0,29.6,873.0,31.1c873.0,31.5,872.7,32.2,872.4,32.6c872.1,33.1,871.8,33.6,871.8,33.9c871.8,34.1,871.7,34.5,871.5,34.7c871.3,34.9,871.1,35.4,871.1,35.7c871.1,36.4,870.4,37.4,869.9,37.4c869.5,37.4,869.5,37.3,869.7,36.7|m936.8,24.0c936.8,15.3,936.9,10.6,937.1,10.6c937.2,10.6,937.3,12.2,937.3,14.5c937.3,17.4,937.4,18.6,937.7,19.1c938.1,20.0,938.1,25.5,937.7,26.1c937.4,26.5,937.3,27.6,937.3,32.0c937.3,35.4,937.2,37.4,937.1,37.4c936.9,37.4,936.8,32.7,936.8,24.0|m117.6,27.8c118.1,27.8,118.7,28.1,118.9,28.4c119.6,29.0,121.9,29.0,122.3,28.3c122.5,28.0,123.0,27.8,123.7,27.8c124.4,27.8,125.0,28.0,125.1,28.3c125.5,29.0,126.8,29.0,127.2,28.4c127.5,27.9,127.6,26.2,127.3,25.9c127.1,25.8,127.0,25.5,127.0,25.1c127.0,24.8,126.7,24.1,126.3,23.5c125.9,23.0,125.6,22.3,125.6,22.0c125.6,21.6,125.5,21.2,125.3,21.0c125.1,20.7,124.9,20.3,124.9,19.9c124.9,19.6,124.6,18.9,124.2,18.4c123.8,17.8,123.5,17.2,123.5,17.0c123.5,16.8,123.4,16.4,123.2,16.1c123.0,15.9,122.8,15.5,122.8,15.2c122.8,14.9,122.5,14.1,122.1,13.4c121.5,12.2,121.4,12.2,121.0,12.9c120.7,13.2,120.5,13.8,120.5,14.1c120.5,14.4,120.2,15.1,119.8,15.6c119.4,16.2,119.1,16.9,119.1,17.2c119.1,17.5,118.9,18.0,118.7,18.2c118.5,18.4,118.4,18.9,118.4,19.2c118.4,19.5,118.1,20.2,117.8,20.6c117.5,21.1,117.2,21.6,117.2,21.8c117.2,22.0,116.9,22.6,116.5,23.2c116.1,23.7,115.8,24.4,115.8,24.8c115.8,25.1,115.6,25.5,115.4,25.8c115.0,26.3,115.0,27.4,115.5,28.2c115.8,28.8,115.9,28.8,116.3,28.3c116.5,28.1,117.1,27.8,117.6,27.8|m381.5,28.4c381.9,27.9,381.8,26.3,381.4,25.8c381.2,25.5,381.1,25.1,381.1,24.8c381.1,24.4,380.8,23.8,380.5,23.4c380.1,22.9,379.9,22.3,379.9,22.0c379.9,21.7,379.6,21.0,379.2,20.4c378.8,19.9,378.5,19.2,378.5,18.9c378.5,18.6,378.3,18.1,378.1,17.9c377.9,17.6,377.8,17.2,377.8,16.9c377.8,16.5,377.5,15.8,377.1,15.3c376.7,14.7,376.4,14.1,376.4,13.9c376.4,13.7,376.2,13.2,375.9,12.9c375.5,12.4,375.5,12.4,374.9,13.3c374.6,13.8,374.0,15.1,373.7,16.2c373.4,17.2,372.8,18.4,372.5,18.9c372.2,19.3,371.9,19.9,371.9,20.2c371.9,20.5,371.5,21.6,371.0,22.8c370.5,23.9,370.1,24.9,370.1,25.0c370.1,25.1,369.9,25.5,369.7,25.8c369.3,26.4,369.3,26.5,369.7,27.1c370.0,27.6,370.4,27.8,371.1,27.8c371.7,27.8,372.4,28.1,372.8,28.3c373.7,29.0,381.0,29.1,381.5,28.4|m631.8,28.4c632.3,27.7,632.1,26.3,631.3,25.2c631.0,24.7,630.6,24.1,630.6,23.9c630.6,23.7,630.3,23.0,629.9,22.5c629.6,22.0,629.2,21.3,629.2,20.9c629.2,20.6,629.0,20.1,628.8,19.8c628.5,19.4,627.8,17.7,627.3,16.0c626.7,14.2,626.1,12.7,625.9,12.5c625.6,12.2,624.3,14.0,624.3,14.8c624.3,15.1,624.0,15.8,623.6,16.3c623.2,16.9,622.9,17.6,622.9,17.9c622.9,18.2,622.8,18.7,622.6,18.9c622.4,19.1,622.2,19.6,622.2,19.9c622.2,20.2,621.9,20.9,621.5,21.5c621.1,22.0,620.8,22.7,620.8,22.9c620.8,23.2,620.5,24.0,620.1,24.6c619.3,25.9,619.2,27.3,619.8,28.2c620.2,28.8,620.7,28.9,625.8,28.9c629.9,28.9,631.6,28.7,631.8,28.4|m882.9,28.3c883.8,27.7,885.5,27.7,885.9,28.3c886.1,28.8,886.2,28.8,886.6,28.3c887.2,27.4,887.1,25.9,886.3,24.4c885.9,23.7,885.6,22.9,885.6,22.8c885.6,22.6,885.5,22.2,885.3,22.0c885.1,21.8,884.9,21.3,884.9,21.0c884.9,20.7,884.6,20.0,884.2,19.4c883.8,18.9,883.5,18.2,883.5,17.8c883.5,17.5,883.4,17.1,883.2,16.8c883.0,16.6,882.8,16.2,882.8,15.9c882.8,15.1,881.6,13.4,881.1,13.4c880.5,13.4,879.3,15.1,879.3,15.9c879.3,16.2,879.1,16.6,878.9,16.8c878.8,17.1,878.6,17.5,878.6,17.8c878.6,18.2,878.3,18.9,877.9,19.4c877.5,20.0,877.2,20.6,877.2,21.0c877.2,21.3,876.9,22.0,876.5,22.5c876.1,23.0,875.8,23.7,875.8,24.1c875.8,24.4,875.6,24.8,875.4,25.1c875.0,25.6,875.0,27.9,875.4,28.4c875.8,29.1,882.0,29.0,882.9,28.3|m71.0,25.3c71.3,25.0,71.6,24.8,71.8,24.7c72.3,24.7,74.2,21.9,74.2,21.1c74.2,20.7,74.3,20.1,74.5,19.6c74.9,18.9,74.9,18.7,74.5,17.6c74.2,16.9,73.5,15.4,72.8,14.3c71.8,12.8,71.3,12.4,70.8,12.4c70.4,12.3,69.9,12.1,69.6,11.8c69.0,11.2,59.7,11.1,59.2,11.7c58.8,12.3,58.8,24.8,59.2,25.4c59.7,26.0,70.4,25.9,71.0,25.3|m324.6,25.3c324.8,25.0,325.2,24.8,325.4,24.7c325.6,24.7,326.2,24.0,326.8,23.2l327.8,21.6l327.8,19.1l327.8,16.5l326.4,14.4c325.1,12.5,325.0,12.4,324.0,12.4c323.4,12.3,322.7,12.1,322.5,11.8c322.1,11.4,321.2,11.3,317.8,11.3l313.6,11.4l312.8,12.3l312.0,13.3l311.9,19.0c311.8,23.3,311.8,24.8,312.0,25.2c312.5,26.0,323.9,26.0,324.6,25.3|m573.5,25.3c573.7,25.0,574.1,24.8,574.3,24.7c574.8,24.7,575.9,23.0,575.9,22.3c575.9,22.0,576.1,21.5,576.3,21.3c576.5,21.0,576.6,20.2,576.6,18.6l576.6,16.3l575.3,14.4c574.0,12.5,573.8,12.4,572.9,12.4c572.3,12.3,571.6,12.1,571.4,11.8c570.8,11.2,561.4,11.1,561.0,11.7c560.8,12.0,560.7,14.0,560.7,18.6c560.7,23.1,560.8,25.1,561.0,25.4c561.4,26.0,572.9,25.9,573.5,25.3|m830.5,23.3l832.3,20.9l832.3,19.1c832.3,17.9,832.2,17.1,831.9,16.8c831.7,16.6,831.6,16.2,831.6,15.9c831.6,15.1,830.4,13.4,829.9,13.4c829.7,13.4,829.4,13.2,829.2,12.9c829.1,12.6,828.6,12.4,828.2,12.4c827.8,12.3,827.3,12.1,827.0,11.8c826.4,11.2,817.1,11.1,816.7,11.7c816.5,12.0,816.4,14.0,816.4,18.6c816.4,23.1,816.5,25.1,816.7,25.4c816.9,25.7,818.6,25.8,822.8,25.8l828.7,25.8l830.5,23.3"


if __name__ == "__main__":
    pdf = generer_pdf(nb_cartes=16, couleur=False)
    with open("test_rai.pdf", "wb") as f:
        f.write(pdf.read())
    print("RAI genere")
# ═════════════════════════════════════════════════════════════════════
# 🌈 28/09 — RAI sur sa nouvelle planche (sceau Maeva)
#   ⚠️ CE N'EST PAS UN JEU NEUF : meme identifiant, memes familles de dix
#   (30-39 x3 · 40-49 x2 · 50-59 x3), memes HUIT boules, case du milieu
#   toujours vide. Le crieur ne change pas (30 a 59).
#   ⚠️⚠️ CE QUI CHANGE : 16 cartons par feuille A4 PAYSAGE au lieu de 12
#   en portrait. Sans cette reinscription la boutique ferait sortir 12
#   cartons par feuille alors que la planche en porte 16 : une commande
#   de 500 feuilles n'en donnerait que 375.
#   ⚠️⚠️ LES NUAGES DISPARAISSENT : sa nouvelle planche est au trait pur,
#   sans aucune image. RAI sort donc de JEUX_AVEC_IMAGE, sinon le menu
#   annonce « AVEC IMAGE » et le quota des jeux a image continue de se
#   declencher sur un carton qui n'a plus de dessin.
#   ⚠️⚠️ CE QUE JE NE TOUCHE PAS : RAI reste dans JEUX_HABILLES, la liste
#   des jeux RESERVES aux partenaires. C'est un choix commercial, pas
#   technique : a toi de dire si RAI doit y rester maintenant qu'il n'a
#   plus de nuages.
# ═════════════════════════════════════════════════════════════════════
GRIS_PARTICULIERS.update({"rai": 0.40})
_GRIS_POSES = _imposer_gris_maison()
JEUX_AVEC_IMAGE.discard("rai")
_enregistrer_paire("rai", "RAI", "\U0001f308", 16, rai.generer_pdf)
# 🌈 la regle du 28/09 : on rememorise la table de fabrication APRES
#    tout bloc qui touche au catalogue (le plafond des 375 feuilles).
CARTES_PAR_FEUILLE.update({_j: _v["cartes_par_feuille"] for _j, _v in REGISTRE_JEUX.items()})
print("[RAI] nouvelle planche — 16 cartons par feuille, %d jeux au catalogue" % len(REGISTRE_JEUX))
# ═════════════════════════════════════════════════════════════════════
# 🧙 28/09 — WIZ 4 BOULES sur sa nouvelle planche (sceau Maeva)
#   ⚠️ CE N'EST PAS UN JEU NEUF : meme identifiant, memes plages
#   (haut et bas 16-30 · gauche 1-15 · droite 31-45), memes QUATRE
#   numeros en losange. Le crieur ne change pas (1 a 45).
#   ⚠️⚠️ CE QUI CHANGE : 16 cartons par feuille A4 PAYSAGE au lieu de 12
#   en portrait. Sans cette reinscription, une commande de 500 feuilles
#   n'en sortirait que 375.
#   ⚠️⚠️ LE DESSIN DU SORCIER DISPARAIT : sa nouvelle planche est au
#   trait pur, sans aucune image. WIZ sort donc de JEUX_AVEC_IMAGE.
#   ⚠️⚠️ CE QUE JE NE TOUCHE PAS : WIZ reste dans JEUX_HABILLES, la liste
#   des jeux RESERVES aux partenaires — comme RAI. C'est un choix
#   commercial, a elle de le dire.
# ═════════════════════════════════════════════════════════════════════
GRIS_PARTICULIERS.update({"wiz": 0.40})
_GRIS_POSES = _imposer_gris_maison()
JEUX_AVEC_IMAGE.discard("wiz")
_enregistrer_paire("wiz", "WIZ 4 boules", "\U0001f9d9", 16, wiz.generer_pdf)
# ⭐ la regle du 28/09 : on rememorise la table de fabrication APRES
#    tout bloc qui touche au catalogue (le plafond des 375 feuilles).
CARTES_PAR_FEUILLE.update({_j: _v["cartes_par_feuille"] for _j, _v in REGISTRE_JEUX.items()})
print("[WIZ] nouvelle planche — 16 cartons par feuille, %d jeux au catalogue" % len(REGISTRE_JEUX))
# ═════════════════════════════════════════════════════════════════════
# 🎏 28/09 — LES DEUX INO sur sa nouvelle planche (sceau Maeva)
#   ⚠️ CE NE SONT PAS DES JEUX NEUFS : memes identifiants, memes plages
#   (I 16-30 · N 31-45 · O 61-75), memes numeros aux memes places.
#     INO 5 boules : 5 numeros, QUATRE cases vides, le QR au milieu-gauche
#     INO 8 boules : 8 numeros tries, la case du CENTRE vide, le QR dedans
#   Le crieur ne change pas : 16-45 puis 61-75, le 46-60 n'existe pas.
#   ⚠️⚠️ CE QUI CHANGE : 16 cartons par feuille A4 PAYSAGE au lieu de 12
#   en portrait, pour les DEUX. Sans cette reinscription, une commande de
#   500 feuilles n'en sortirait que 375.
#   ⭐ RIEN A CHANGER D'AUTRE : ni l'un ni l'autre n'est dans
#   JEUX_AVEC_IMAGE ou JEUX_HABILLES, et tous deux RESTENT dans
#   JEUX_MOTIF — les clientes gardent le filigrane en fond.
# ═════════════════════════════════════════════════════════════════════
GRIS_PARTICULIERS.update({"ino": 0.40, "ino8": 0.40})
_GRIS_POSES = _imposer_gris_maison()
_enregistrer_paire("ino",  "INO 5 boules", "\U0001f38f", 16, ino.generer_pdf)
_enregistrer_paire("ino8", "INO 8 boules", "\U0001f390", 16, ino8.generer_pdf)
# ⭐ la regle du 28/09 : on rememorise la table de fabrication APRES
#    tout bloc qui touche au catalogue (le plafond des 375 feuilles).
CARTES_PAR_FEUILLE.update({_j: _v["cartes_par_feuille"] for _j, _v in REGISTRE_JEUX.items()})
print("[INO] les deux INO sur la nouvelle planche — 16 cartons par feuille, %d jeux au catalogue"
      % len(REGISTRE_JEUX))
# ═════════════════════════════════════════════════════════════════════
# 💫 28/09 — POW 6 BOULES : nouvelle planche ET nouvelle regle
#   (sceau Maeva : « changeant la maquette du jeu POW 6 boules »,
#    puis « met 6 boules stp »)
#   ⚠️⚠️ LA REGLE DU JEU CHANGE, ce n'est pas qu'un habillage :
#     AVANT : 5 numeros, la case du bas-milieu vide pour le QR
#     APRES : 6 numeros, DEUX par famille de neuf, la grille est pleine
#             1-9 (x2) · 10-18 (x2) · 19-27 (x2), ordre libre
#   ⚠️ LE CRIEUR NE CHANGE PAS : toujours 1 a 27, memes familles.
#     Mais un carton se remplit plus vite : 6 numeros au lieu de 5.
#   ⚠️ IL N'Y A PLUS DE QR : sa case porte maintenant une boule.
#     Le microtexte et le numero de serie unique restent.
#   ⭐ CE QUE CA REPARE : 46 656 -> 373 248 cartons differents.
#     L'ancien sortait 659 doublons par rame de 500 feuilles.
#   ⚠️⚠️ LE NOM CHANGE AU MENU : « POW 5 boules » devient « POW 6
#     boules ». L'IDENTIFIANT reste pow6 : les anciennes commandes se
#     retrouvent, mais elles se regenereront avec SIX numeros.
#   ⚠️⚠️ 16 cartons par feuille A4 PAYSAGE au lieu de 12 en portrait.
#   ⭐ POW 8, POW 9 et POW CASINO ne bougent pas. POW 6 reste dans
#     JEUX_MOTIF : les clientes gardent le filigrane.
# ═════════════════════════════════════════════════════════════════════
GRIS_PARTICULIERS.update({"pow6": 0.40})
_GRIS_POSES = _imposer_gris_maison()
_enregistrer_paire("pow6", "POW 6 boules", "\U0001f4ab", 16, pow6.generer_pdf)
# ⭐ la regle du 28/09 : on rememorise la table de fabrication APRES
#    tout bloc qui touche au catalogue (le plafond des 375 feuilles).
CARTES_PAR_FEUILLE.update({_j: _v["cartes_par_feuille"] for _j, _v in REGISTRE_JEUX.items()})
print("[POW 6] nouvelle planche et 6 boules — 16 cartons par feuille, %d jeux au catalogue"
      % len(REGISTRE_JEUX))
# ═════════════════════════════════════════════════════════════════════
# ⭕ 29/09 — OAOA : nouvelle planche ET nouvelles plages
#   (sceau Maeva : « changeant la maquette du jeu OAOA », puis elle a
#    confirme les plages ecrites sur sa planche)
#   ⚠️⚠️ LA REGLE DU JEU CHANGE :
#     AVANT : O = 16 a 30 · A = 61 a 75  ->  30 boules
#     APRES : O = 1 a 30  · A = 31 a 75  ->  LES 75 BOULES
#     Trois numeros par colonne, tries : ca ne change pas.
#   ⚠️⚠️ LE CRIEUR CHANGE DONC AUSSI — c'est fait plus bas : il passe de
#     « 16 a 75 avec un trou de 31 a 60 » a « 1 a 75, toutes les boules ».
#   ⚠️ LA PARTIE DURE BEAUCOUP PLUS LONGTEMPS : six numeros a sortir
#     parmi 75 au lieu de 30. A tester une fois en salle.
#   ⚠️⚠️ 16 cartons par feuille A4 PORTRAIT au lieu de 12. Sans cette
#     reinscription, 500 feuilles commandees n'en donneraient que 375.
#   ⚠️ IL N'Y A PLUS DE QR : sa planche n'a pas de bande pour lui.
#     Microtexte et numero de serie unique conserves.
#   ⭐ CE QUE CA REPARE : 207 025 -> 57 611 400 cartons differents.
# ═════════════════════════════════════════════════════════════════════
GRIS_PARTICULIERS.update({"oaoa": 0.40})
_GRIS_POSES = _imposer_gris_maison()
_enregistrer_paire("oaoa", "OAOA", "\u2b55", 16, oaoa.generer_pdf)
_PLAGES_CALLER["oaoa"] = (1, 75)
_BOULES_CALLER["oaoa"] = [n for n in range(1, 76)]
# ⭐ la regle du 28/09 : on rememorise la table de fabrication APRES
#    tout bloc qui touche au catalogue (le plafond des 375 feuilles).
CARTES_PAR_FEUILLE.update({_j: _v["cartes_par_feuille"] for _j, _v in REGISTRE_JEUX.items()})
print("[OAOA] nouvelle planche · O 1-30 et A 31-75 · crieur %s · 16 cartons/feuille · %d jeux"
      % (_PLAGES_CALLER["oaoa"], len(REGISTRE_JEUX)))
# ═════════════════════════════════════════════════════════════════════
# 🍽️ 29/09 — KAI 7 BOULES : nouvelle planche
#   (sceau Maeva : « maintenant le jeu KAI »)
#   ⭐ LA REGLE NE CHANGE PAS : col 1-10 -> 2 numeros, col 11-20 -> 3,
#     col 21-30 -> 2. Sept numeros, deux cases barrees d'une croix.
#   ⚠️⚠️ 16 cartons par feuille A4 PAYSAGE au lieu de 12 en portrait.
#     Sans cette reinscription, 500 feuilles commandees n'en donneraient
#     que 375.
#   ⚠️⚠️ LE CRIEUR ETAIT FAUX : il etait regle sur 1 a 29, alors que la
#     troisieme colonne monte jusqu'a 30. Le 30 ne sortait JAMAIS : un
#     carton qui l'avait ne pouvait pas gagner. Corrige plus bas.
#   ⚠️ IL N'Y A PLUS LE PUZZLE AUX DES : sa planche est au trait, donc le
#     jeu sort de la liste « carton avec dessin » (menu + quota d'images).
#     Il reste dans les jeux reserves : c'est son choix commercial, a elle
#     de dire si elle veut l'en sortir.
#   ⭐ CE QUE CA REPARE : 120 doublons par rame de 500 feuilles.
# ═════════════════════════════════════════════════════════════════════
GRIS_PARTICULIERS.update({"kai": 0.40})
_GRIS_POSES = _imposer_gris_maison()
_enregistrer_paire("kai", "KAI 7 boules", "\U0001f37d️", 16, kai.generer_pdf)
try:
    JEUX_AVEC_IMAGE.discard("kai")
except Exception:
    pass
_PLAGES_CALLER["kai"] = (1, 30)
_BOULES_CALLER["kai"] = [n for n in range(1, 31)]
# ⭐ la regle du 28/09 : on rememorise la table de fabrication APRES
#    tout bloc qui touche au catalogue (le plafond des 375 feuilles).
CARTES_PAR_FEUILLE.update({_j: _v["cartes_par_feuille"] for _j, _v in REGISTRE_JEUX.items()})
print("[KAI] nouvelle planche · crieur %s · 16 cartons/feuille · %d jeux"
      % (_PLAGES_CALLER["kai"], len(REGISTRE_JEUX)))
# ═════════════════════════════════════════════════════════════════════
# 🌱 29/09 — BIO 8 BOULES : nouvelle planche
#   (sceau Maeva : « changeant la maquette du jeu BIO 8 boules »)
#   ⭐ LA REGLE NE CHANGE PAS : B 1-15 -> 3 numeros, I 16-30 -> 2 (la case
#     du milieu reste vide), O 61-75 -> 3. Huit numeros, tries.
#     Le crieur ne bouge pas non plus : il saute toujours le 31-60.
#   ⚠️⚠️ 16 cartons par feuille A4 PAYSAGE au lieu de 12 en portrait.
#     Sans cette reinscription, 500 feuilles commandees n'en donneraient
#     que 375.
#   ⚠️ IL N'Y A PLUS DE QR : l'ancienne planche logeait le QR dans la case
#     vide du centre. Sa nouvelle planche y dessine une case ordinaire, la
#     case reste donc vide. Microtexte et numero de serie conserves.
#   ⚠️ Le BIO 5 boules n'est PAS touche : il garde son ancienne planche.
# ═════════════════════════════════════════════════════════════════════
GRIS_PARTICULIERS.update({"bio": 0.40})
_GRIS_POSES = _imposer_gris_maison()
_enregistrer_paire("bio", "BIO 8 boules", "\U0001f331", 16, bio.generer_pdf)
try:
    JEUX_AVEC_IMAGE.discard("bio")
except Exception:
    pass
# ⭐ la regle du 28/09 : on rememorise la table de fabrication APRES
#    tout bloc qui touche au catalogue (le plafond des 375 feuilles).
CARTES_PAR_FEUILLE.update({_j: _v["cartes_par_feuille"] for _j, _v in REGISTRE_JEUX.items()})
print("[BIO] nouvelle planche · crieur %s · 16 cartons/feuille · %d jeux"
      % (_PLAGES_CALLER["bio"], len(REGISTRE_JEUX)))
# ═════════════════════════════════════════════════════════════════════
# 🍵 29/09 — TEA : nouvelle planche
#   (sceau Maeva : « on va changer la maquette du jeu TEA »)
#   ⭐ LA REGLE NE CHANGE PAS : T 35-45, E 46-56, A 57-67, deux numeros
#     par colonne, tries. Six numeros. Le crieur reste sur 35-67.
#   ⚠️⚠️ 16 cartons par feuille A4 PAYSAGE au lieu de 12 en portrait.
#     Sans cette reinscription, 500 feuilles commandees n'en donneraient
#     que 375.
#   ⭐ Les faux numeros 580001 a 580016 de sa planche sont effaces : le
#     vrai numero de serie se pose exactement a leur place.
#   ⚠️ LE TRAIT N'EST PAS AFFINE : sa planche est deja a 0,379 mm et un
#     cran cassait son gobelet en miettes. On la garde telle quelle.
#   ⭐ CE QUE CA REPARE : environ 180 doublons par rame de 500 feuilles.
# ═════════════════════════════════════════════════════════════════════
GRIS_PARTICULIERS.update({"tea": 0.40})
_GRIS_POSES = _imposer_gris_maison()
_enregistrer_paire("tea", "TEA", "\U0001f375", 16, tea.generer_pdf)
try:
    JEUX_AVEC_IMAGE.discard("tea")
except Exception:
    pass
# ⭐ la regle du 28/09 : on rememorise la table de fabrication APRES
#    tout bloc qui touche au catalogue (le plafond des 375 feuilles).
CARTES_PAR_FEUILLE.update({_j: _v["cartes_par_feuille"] for _j, _v in REGISTRE_JEUX.items()})
print("[TEA] nouvelle planche · crieur %s · 16 cartons/feuille · %d jeux"
      % (_PLAGES_CALLER["tea"], len(REGISTRE_JEUX)))
# ═════════════════════════════════════════════════════════════════════
# 🏆 29/09 — WIN 9 BOULES : nouvelle planche
#   (sceau Maeva : « on change la maquette du jeu WIN »)
#   ⭐ LA REGLE NE CHANGE PAS : col 1-15, col 16-30, col 31-45, trois
#     numeros par colonne, tries. Neuf numeros, grille pleine.
#     Le crieur reste sur 1-45.
#   ⚠️⚠️ 16 cartons par feuille A4 PAYSAGE au lieu de 12 en portrait.
#     Sans cette reinscription, 500 feuilles commandees n'en donneraient
#     que 375.
#   ⚠️ IL N'Y A PLUS LE PUZZLE : sa planche est au trait, donc le jeu sort
#     de la liste « carton avec dessin » (menu + quota d'images). Il reste
#     dans les jeux reserves : c'est son choix commercial.
#   ⭐ L'arc-en-ciel est carton par carton, comme avant.
#   ⚠️ LE WIN CASINO (les des) partage la planche du WIN : il change donc
#     aussi de maquette, et passe lui aussi a 16 cartons par feuille.
# ═════════════════════════════════════════════════════════════════════
GRIS_PARTICULIERS.update({"win": 0.40})
_GRIS_POSES = _imposer_gris_maison()
_enregistrer_paire("win", "WIN 9 boules", "\U0001f3c6", 16, win.generer_pdf)
# ⚠️⚠️ LE JUMEAU « WIN CASINO » TOURNE SUR LA MEME PLANCHE : lui aussi passe
#    a 16 cartons par feuille, sinon il tombait a 375 feuilles pour 500.
GRIS_PARTICULIERS.update({"win_casino": 0.40})
_enregistrer_paire("win_casino", "WIN CASINO", "\U0001f3b2", 16, win.generer_pdf_casino)
try:
    JEUX_AVEC_IMAGE.discard("win_casino")
except Exception:
    pass
try:
    JEUX_AVEC_IMAGE.discard("win")
except Exception:
    pass
# ⭐ la regle du 28/09 : on rememorise la table de fabrication APRES
#    tout bloc qui touche au catalogue (le plafond des 375 feuilles).
CARTES_PAR_FEUILLE.update({_j: _v["cartes_par_feuille"] for _j, _v in REGISTRE_JEUX.items()})
print("[WIN] nouvelle planche · crieur %s · 16 cartons/feuille · %d jeux"
      % (_PLAGES_CALLER["win"], len(REGISTRE_JEUX)))
# ═════════════════════════════════════════════════════════════════════
# 🎲 29/09 — POL 6 BOULES : nouvelle planche
#   (sceau Maeva : « travaillant sur la maquette du jeu POL »)
#   ⭐ LES PLAGES NE CHANGENT PAS : col 30-40, col 41-50, col 51-60, deux
#     numeros par colonne, tries. Six numeros. Le crieur reste sur 30-60.
#   ⚠️ LE DESSIN DU JEU CHANGE, c'est sa planche qui le dit : six cases au
#     lieu d'une grille 3x3, plus de cases barrees d'un X, et le numero de
#     serie descend dans le pied au lieu d'occuper la case du milieu.
#     Pour la joueuse et la crieuse, la partie se joue pareil.
#   ⚠️⚠️ 16 cartons par feuille A4 PAYSAGE au lieu de 8. Sans cette
#     reinscription, 500 feuilles commandees n'en donneraient que 250.
#   ⚠️ Sa planche est au trait, donc le jeu sort de la liste « carton avec
#     dessin » (menu + quota d'images). Il reste dans les jeux reserves :
#     c'est son choix commercial.
#   ⚠️ Le POL CLASSIC n'est PAS touche : il garde son ancienne planche.
#   ⭐ CE QUE CA REPARE : pres de 300 doublons par rame de 500 feuilles.
# ═════════════════════════════════════════════════════════════════════
GRIS_PARTICULIERS.update({"pol": 0.40})
_GRIS_POSES = _imposer_gris_maison()
_enregistrer_paire("pol", "POL 6 boules", "\U0001f3b2", 16, pol.generer_pdf)
try:
    JEUX_AVEC_IMAGE.discard("pol")
except Exception:
    pass
# ⭐ la regle du 28/09 : on rememorise la table de fabrication APRES
#    tout bloc qui touche au catalogue (le plafond des 375 feuilles).
CARTES_PAR_FEUILLE.update({_j: _v["cartes_par_feuille"] for _j, _v in REGISTRE_JEUX.items()})
print("[POL] nouvelle planche · crieur %s · 16 cartons/feuille · %d jeux"
      % (_PLAGES_CALLER["pol"], len(REGISTRE_JEUX)))
# ═════════════════════════════════════════════════════════════════════
# 🌊 29/09 — ANI (TEAHUPOO au catalogue) : nouvelle planche
#   (sceau Maeva : « on change la maquette du jeu ANI l'original »)
#   ⭐ LA REGLE NE CHANGE PAS : A 61-70, N 71-80, I 81-90, trois numeros
#     par colonne, tries. Neuf numeros, grille pleine. Crieur : 61-90.
#   ⚠️⚠️ 16 cartons par feuille A4 PAYSAGE au lieu de 8. Sans cette
#     reinscription, 500 feuilles commandees n'en donneraient que 250.
#   ⚠️⚠️ LE NOM : au catalogue ce jeu s'appelle TEAHUPOO depuis le 14/08
#     (c'est elle qui l'avait rebaptise), mais sa nouvelle planche porte
#     « ANI ». ON NE TOUCHE PAS AU NOM DU MENU : c'est son choix
#     commercial. Pour le renommer ANI un jour, il suffira de remplacer
#     "TEAHUPOO" par "ANI" dans la ligne _enregistrer_paire ci-dessous.
#   ⚠️ Le TEAHUPOO CLASSIC n'est PAS touche : il garde son ancienne planche.
# ═════════════════════════════════════════════════════════════════════
GRIS_PARTICULIERS.update({"ani": 0.40})
_GRIS_POSES = _imposer_gris_maison()
# ⚠️⚠️ L'ORDRE COMPTE : le menu ecrit « AVEC IMAGE » ou « SANS IMAGE » au
#    MOMENT de l'inscription. On sort donc le jeu de la liste AVANT de
#    l'inscrire, sinon l'etiquette reste fausse.
try:
    JEUX_AVEC_IMAGE.discard("ani")
except Exception:
    pass
_enregistrer_paire("ani", "TEAHUPOO", "\U0001f30a", 16, ani.generer_pdf)
_PLAGES_CALLER["ani"] = (61, 90)

# ═════════════════════════════════════════════════════════════════════
# 🏷️ REPARATION D'ETIQUETTES — quatre jeux annoncaient « AVEC IMAGE »
#    dans le menu alors que leur carton n'a plus aucun dessin en image.
#    C'est ma faute : dans les blocs precedents j'avais sorti le jeu de la
#    liste APRES l'avoir inscrit, et l'etiquette etait deja ecrite.
#    Verifie en fabriquant une carte de chacun : zero image dans le PDF.
#    Rien d'autre ne change : memes planches, memes regles, memes
#    cartons par feuille, memes fonctions.
# ═════════════════════════════════════════════════════════════════════
for _b, _nom, _emo, _cpf, _fn in (
        ("kai",        "KAI 7 boules", "\U0001f37d️", 16, kai.generer_pdf),
        ("win",        "WIN 9 boules", "\U0001f3c6",       16, win.generer_pdf),
        ("win_casino", "WIN CASINO",   "\U0001f3b2",       16, win.generer_pdf_casino),
        ("pol",        "POL 6 boules", "\U0001f3b2",       16, pol.generer_pdf),
        ("trio75",     "TRIO 75",      "\U0001f3ab",        2, trio75.generer_pdf)):
    try:
        JEUX_AVEC_IMAGE.discard(_b)
        _enregistrer_paire(_b, _nom, _emo, _cpf, _fn)
    except Exception as _e:
        print("[ETIQUETTE] %s : %s" % (_b, _e))

# ⭐ la regle du 28/09 : on rememorise la table de fabrication APRES
#    tout bloc qui touche au catalogue (le plafond des 375 feuilles).
CARTES_PAR_FEUILLE.update({_j: _v["cartes_par_feuille"] for _j, _v in REGISTRE_JEUX.items()})
print("[ANI] nouvelle planche · crieur %s · 16 cartons/feuille · %d jeux"
      % (_PLAGES_CALLER["ani"], len(REGISTRE_JEUX)))
# ═════════════════════════════════════════════════════════════════════
# 💧 29/09 — VAI : nouvelle planche ET nouvelle regle
#   (sceau Maeva : « on mettra que 7 boules, 3 a droite, 1 au milieu et
#    3 a gauche », et elle a confirme les plages du VAI)
#   ⚠️⚠️ LA REGLE DU JEU CHANGE :
#     AVANT : NEUF numeros, un par goutte.
#     APRES : SEPT numeros —
#        gauche 61-70 : 3 numeros · milieu 71-80 : 1 · droite 81-90 : 3
#     Le numero du milieu se pose EN HAUT : sa goutte occupe la case du
#     centre ET celle du bas de cette colonne (mesure sur sa planche).
#   ⚠️ LE CRIEUR NE CHANGE PAS : toujours les 30 boules de 61 a 90.
#   ⚠️ LA PARTIE EST PLUS LONGUE : sept numeros a sortir au lieu de neuf.
#     A tester une fois en salle avant une grosse rame.
#   ⚠️⚠️ 16 cartons par feuille A4 PAYSAGE au lieu de 8. Sans cette
#     reinscription, 500 feuilles commandees n'en donneraient que 250.
#   ⭐ Le nom passe de « VAI 9 boules » a « VAI 7 boules » : c'est ce que
#     le carton fait maintenant.
#   ⭐ CE QUE CA REPARE : plus de 200 doublons par rame de 500 feuilles.
#   ⚠️⚠️ COMBIEN DE CARTONS DIFFERENTS : 120 x 10 x 120 = 144 000. Au-dela
#     de 9 000 feuilles le jeu est epuise. A savoir avant une tres grosse
#     commande.
# ═════════════════════════════════════════════════════════════════════
GRIS_PARTICULIERS.update({"vai": 0.40})
_GRIS_POSES = _imposer_gris_maison()
# ⚠️ L'ORDRE COMPTE : le menu ecrit « AVEC IMAGE » ou « SANS IMAGE » au
#    MOMENT de l'inscription. On sort donc le jeu de la liste AVANT.
try:
    JEUX_AVEC_IMAGE.discard("vai")
except Exception:
    pass
_enregistrer_paire("vai", "VAI 7 boules", "\U0001f4a7", 16, vai.generer_pdf)
_PLAGES_CALLER["vai"] = (61, 90)
# ⭐ la regle du 28/09 : on rememorise la table de fabrication APRES
#    tout bloc qui touche au catalogue (le plafond des 375 feuilles).
CARTES_PAR_FEUILLE.update({_j: _v["cartes_par_feuille"] for _j, _v in REGISTRE_JEUX.items()})
print("[VAI] nouvelle planche · 7 boules · crieur %s · 16 cartons/feuille · %d jeux"
      % (_PLAGES_CALLER["vai"], len(REGISTRE_JEUX)))
# ═════════════════════════════════════════════════════════════════════
# 😄 29/09 — LETTRE L : nouvelle planche
#   (sceau Maeva : « changeant la maquette du jeu LETTRE L »)
#   ⭐ LA REGLE NE CHANGE PAS :
#     bras vertical (les 5 cases de gauche, de haut en bas) : 5 numeros
#       de 1 a 15, tries. La 5e case, tout en bas, est le COIN.
#     pied (les 4 cases qui partent du coin vers la droite) : un 16-30,
#       un 31-45, un 46-60, un 61-75.
#     NEUF numeros. Le crieur reste sur 1-75.
#   ⚠️⚠️ 16 cartons par feuille A4 PAYSAGE au lieu de 6. Sans cette
#     reinscription, 500 feuilles commandees n'en donneraient que 187.
#   ⚠️ IL N'Y A PLUS DE QR : l'ancienne planche le logeait au centre, sa
#     nouvelle planche y met le personnage. Le numero de serie se pose en
#     haut a gauche, a un endroit verifie vide sur les SEIZE cartons.
#   ⭐ SEIZE PERSONNAGES DIFFERENTS sur la feuille — raye, a pois, en
#     puzzle, en ecailles, en mosaique... c'est sa planche, on n'y touche pas.
#   ⚠️ Sa planche est au trait, donc le jeu sort de la liste « carton avec
#     dessin » (menu + quota d'images).
#   ⚠️ La LETTRE U n'est PAS touchee : elle garde son ancienne planche.
# ═════════════════════════════════════════════════════════════════════
GRIS_PARTICULIERS.update({"lettre_l": 0.40})
_GRIS_POSES = _imposer_gris_maison()
# ⚠️ L'ORDRE COMPTE : le menu ecrit « AVEC IMAGE » ou « SANS IMAGE » au
#    MOMENT de l'inscription. On sort donc le jeu de la liste AVANT.
try:
    JEUX_AVEC_IMAGE.discard("lettre_l")
except Exception:
    pass
_enregistrer_paire("lettre_l", "LETTRE L", "\U0001f604", 16, lettre_l.generer_pdf)
_PLAGES_CALLER["lettre_l"] = (1, 75)
# ⭐ la regle du 28/09 : on rememorise la table de fabrication APRES
#    tout bloc qui touche au catalogue (le plafond des 375 feuilles).
CARTES_PAR_FEUILLE.update({_j: _v["cartes_par_feuille"] for _j, _v in REGISTRE_JEUX.items()})
print("[LETTRE L] nouvelle planche · crieur %s · 16 cartons/feuille · %d jeux"
      % (_PLAGES_CALLER["lettre_l"], len(REGISTRE_JEUX)))
# ═════════════════════════════════════════════════════════════════════
# 🌊 30/09 — ON SEPARE TEAHUPOO ET ANI : DEUX JEUX DISTINCTS
#   (sceau Maeva : « je veux que l'on differencie TEAHUPOO et ANI »)
#
#   CE QUI S'ETAIT PASSE : le 14/08 elle avait rebaptise le ANI en
#   TEAHUPOO et l'avait habille de la surfeuse dans la vague. Le 29/09
#   elle a pose une planche toute neuve, au trait, portant « ANI » — qui
#   a donc REMPLACE la surfeuse dans le meme fichier. Depuis, le
#   TEAHUPOO a la surfeuse n'etait plus fabricable.
#
#   CE QUE FAIT CE BLOC :
#     · ANI      = sa planche du 29/09, au trait, 16 cartons/feuille.
#                  Le menu disait encore TEAHUPOO : il dira ANI.
#     · TEAHUPOO = la surfeuse, remise en jeu A PART, 8 cartons/feuille,
#                  reprise A L'IDENTIQUE de la version du 25/08.
#
#   ⚠️ LES DEUX JEUX ONT LES MEMES NUMEROS : 61-70 / 71-80 / 81-90, neuf
#     par carton. Le crieur sort les memes 30 boules pour les deux. Ce
#     sont deux habillages du meme jeu, pas deux regles differentes.
#     A NE PAS MELANGER DANS UNE MEME PARTIE : un carton ANI et un carton
#     TEAHUPOO se valent, ils peuvent gagner ensemble.
#
#   ⚠️ TEAHUPOO CLASSIC (le carton sobre, sans dessin) ne bouge pas : il
#     reste le jumeau sans image, avec les memes numeros.
#   ⚠️ La surfeuse est une IMAGE, pas un trace : elle ne se laisse ni
#     affiner ni recolorier comme les planches au trait. Elle entre donc
#     dans la liste « carton avec dessin » (menu + quota d'images).
# ═════════════════════════════════════════════════════════════════════
from generators import teahupoo

# ── 1. ANI reprend son nom ───────────────────────────────────────────
# ⚠️ L'ORDRE COMPTE : le menu ecrit « AVEC IMAGE » ou « SANS IMAGE » au
#    MOMENT de l'inscription. On regle la liste AVANT d'inscrire.
try:
    JEUX_AVEC_IMAGE.discard("ani")
except Exception:
    pass
_enregistrer_paire("ani", "ANI", "\U0001f30a", 16, ani.generer_pdf)
_PLAGES_CALLER["ani"] = (61, 90)

# ── 2. TEAHUPOO revient, avec sa surfeuse ────────────────────────────
GRIS_PARTICULIERS.update({"teahupoo": 0.40})
_GRIS_POSES = _imposer_gris_maison()
try:
    JEUX_AVEC_IMAGE.add("teahupoo")
except Exception:
    pass
_enregistrer_paire("teahupoo", "TEAHUPOO", "\U0001f3c4", 8, teahupoo.generer_pdf)
_PLAGES_CALLER["teahupoo"] = (61, 90)
_BOULES_CALLER["teahupoo"] = [n for n in range(61, 91)]

# ⭐ la regle du 28/09 : on rememorise la table de fabrication APRES
#    tout bloc qui touche au catalogue (le plafond des 375 feuilles).
CARTES_PAR_FEUILLE.update({_j: _v["cartes_par_feuille"] for _j, _v in REGISTRE_JEUX.items()})
print("[ANI/TEAHUPOO] deux jeux separes · ANI 16 cartons/feuille · TEAHUPOO 8 · %d jeux"
      % len(REGISTRE_JEUX))
# ═════════════════════════════════════════════════════════════════════
# ☀️ 30/09 — SUN 8 BOULES : nouvelle planche
#   (sceau Maeva : « on va changer la maquette du jeu SUN »)
#   ⭐ LA REGLE NE CHANGE PAS : col 1 = 1-8 (trois numeros), col 2 = 9-16
#     (deux numeros), col 3 = 17-24 (trois numeros). Huit numeros par
#     carton, tries du plus petit en haut au plus grand en bas. La case
#     VIDE est toujours celle du bas-milieu. Crieur : 1-24.
#   ⭐ SA PLANCHE ET LA REGLE DISENT LA MEME CHOSE : son soleil est dessine
#     exactement dans la case du bas-milieu, celle qui doit rester vide.
#   ⚠️ LE DESSIN DU JEU CHANGE : avant, les huit numeros se lisaient EN
#     COURONNE autour d'une plaque au soleil ; ils se lisent maintenant
#     dans une GRILLE 3x3, comme sa planche le demande. Les huit numeros
#     et leurs plages sont identiques : la partie se joue pareil.
#   ⚠️⚠️ 16 cartons par feuille A4 PAYSAGE au lieu de 12 en portrait. Sans
#     cette reinscription, 500 feuilles commandees n'en donneraient que
#     375.
#   ⚠️ Sa planche est au trait : le jeu n'embarque plus d'image. Il sort
#     donc de la liste « carton avec dessin » (etiquette du menu ET
#     supplement image). Il RESTE dans les jeux reserves : JEUX_HABILLES
#     n'est pas touche, c'est son choix commercial.
#   ⭐ CE QUE CA REPARE : le garde-fou anti-doublon. 56 x 28 x 56 = 87 808
#     cartons differents ; une rame de 500 feuilles en contient 8 000, et
#     sans garde-fou le calcul donne plus de 350 doublons par rame.
# ═════════════════════════════════════════════════════════════════════
GRIS_PARTICULIERS.update({"sun": 0.40})
_GRIS_POSES = _imposer_gris_maison()
try:
    JEUX_AVEC_IMAGE.discard("sun")
except Exception:
    pass
_enregistrer_paire("sun", "SUN 8 boules", "☀️", 16, sun.generer_pdf)
# ⭐ la regle du 28/09 : on rememorise la table de fabrication APRES
#    tout bloc qui touche au catalogue (le plafond des 375 feuilles).
CARTES_PAR_FEUILLE.update({_j: _v["cartes_par_feuille"] for _j, _v in REGISTRE_JEUX.items()})
print("[SUN] nouvelle planche · crieur %s · 16 cartons/feuille · %d jeux"
      % (_PLAGES_CALLER["sun"], len(REGISTRE_JEUX)))
# ═════════════════════════════════════════════════════════════════════
# 🥂 30/09 — CHAMPAGNE : nouvelle planche, celle aux grosses bulles
#   (sceau Maeva : « voici la nouvelle maquette du jeu CHAMPAGNE »)
#   ⭐ LES PLAGES NE CHANGENT PAS : B 1-15 (1 numero), I 16-30 (3),
#     N 31-45 (4), G 46-60 (3), O 61-75 (1). Douze numeros par carton,
#     tries de gauche a droite. Le crieur reste sur 1-75.
#   ⚠️ LE DESSIN DU JEU CHANGE : les quinzaines se lisaient en COLONNES
#     (losange de bulles), elles se lisent maintenant en RANGEES, chacune
#     marquee par sa lettre B, I, N, G, O. Pour la joueuse et la crieuse,
#     la partie se joue exactement pareil.
#   ⭐ ELLE A SES 25 PT. Cette maquette met NEUF cartons par feuille au
#     lieu de seize : le trou des bulles passe de 6,28 a 10,69 mm et le
#     carton de 68x44 a 94x66 mm. Mesure sur les 108 bulles d'une
#     feuille : 0,21 mm de blanc avant son trait. A 27 pt ca toucherait.
#   ⚠️⚠️ 9 cartons par feuille A4 PAYSAGE au lieu de 6 en portrait. Sans
#     cette reinscription, 500 feuilles commandees n'en donneraient que
#     333.
#   ⚠️ Le jeu RESTE dans la liste « carton avec dessin » et RESTE au
#     tarif ordinaire (IMAGE_TARIF_NB_ORDINAIRE) : rien n'est touche de
#     ce cote, c'est son choix commercial.
#   ⭐ 63 582 553 125 cartons differents : le jeu ne s'epuise pas.
# ═════════════════════════════════════════════════════════════════════
GRIS_PARTICULIERS.update({"champagne": 0.40})
_GRIS_POSES = _imposer_gris_maison()
_enregistrer_paire("champagne", "CHAMPAGNE", "\U0001f942", 9, champagne.generer_pdf)
# ⭐ la regle du 28/09 : on rememorise la table de fabrication APRES
#    tout bloc qui touche au catalogue (le plafond des 375 feuilles).
CARTES_PAR_FEUILLE.update({_j: _v["cartes_par_feuille"] for _j, _v in REGISTRE_JEUX.items()})
print("[CHAMPAGNE] nouvelle planche · crieur %s · 9 cartons/feuille · %d jeux"
      % (_PLAGES_CALLER["champagne"], len(REGISTRE_JEUX)))
# ═════════════════════════════════════════════════════════════════════
# 🟤 30/09 — BROWN 8 BOULES : nouvelle planche
#   (sceau Maeva : « travaillant sur le changement de la maquette du
#    BROWN 8 boules »)
#   ⭐ LA REGLE NE CHANGE PAS : B 1-15 (deux numeros), I 16-30 (un),
#     N 31-45 (deux), G 46-60 (un), O 61-75 (deux). Huit numeros par
#     carton, tries du plus petit en haut. Crieur : 1-75.
#   ⭐ SA PLANCHE ET LA REGLE DISENT LA MEME CHOSE : elle a dessine deux
#     cases sous B, N et O, et une seule sous I et G. Huit cases, huit
#     numeros.
#   ⚠️ LE DESSIN DU JEU CHANGE : avant, les huit numeros se lisaient dans
#     un BOUQUET DE HUIT FLEURS, chacune portant sa lettre sur un fanion.
#     Ils se lisent maintenant dans les cases de sa planche. Les huit
#     numeros et leurs plages sont identiques : la partie se joue pareil.
#   ⚠️⚠️ 16 cartons par feuille A4 PAYSAGE au lieu de 8. Sans cette
#     reinscription, 500 feuilles commandees n'en donneraient que 250.
#   ⚠️ Sa planche est au trait : le jeu n'embarque plus d'image. Il sort
#     donc de la liste « carton avec dessin » (etiquette du menu ET
#     supplement image). Il RESTE dans les jeux reserves : JEUX_HABILLES
#     n'est pas touche, c'est son choix commercial.
#   ⚠️ Le BROWN 8 CLASSIC n'est PAS touche : il garde son ancienne planche
#     et ses 8 cartons par feuille.
#   ⭐ 260 465 625 cartons differents : le jeu ne s'epuise pas.
# ═════════════════════════════════════════════════════════════════════
GRIS_PARTICULIERS.update({"brown8": 0.40})
_GRIS_POSES = _imposer_gris_maison()
try:
    JEUX_AVEC_IMAGE.discard("brown8")
except Exception:
    pass
_enregistrer_paire("brown8", "BROWN 8 boules", "\U0001f7e4", 16, brown8.generer_pdf)
# ⭐ la regle du 28/09 : on rememorise la table de fabrication APRES
#    tout bloc qui touche au catalogue (le plafond des 375 feuilles).
CARTES_PAR_FEUILLE.update({_j: _v["cartes_par_feuille"] for _j, _v in REGISTRE_JEUX.items()})
print("[BROWN 8] nouvelle planche · crieur %s · 16 cartons/feuille · %d jeux"
      % (_PLAGES_CALLER["brown8"], len(REGISTRE_JEUX)))
# ═════════════════════════════════════════════════════════════════════
# 💎 30/09 — 5000 FRANCS : DEUX BILLETS DE PLUS PAR FEUILLE
#   (sceau Maeva : « je veux que l'on rajoute encore 2 grille sur le jeu
#    5000 francs »)
#   ⭐ 10 billets par feuille A4 au lieu de 8, en 2 colonnes x 5 rangees.
#   ⭐ LA REGLE NE CHANGE PAS : quatre numeros aux coins, le montant au
#     centre, les quatre fleches. Le crieur reste sur 1-65.
#   ⚠️ CE QUE CA COUTE : le billet garde ses proportions, il n'est PAS
#     deforme, mais il descend de 93,5 x 54,3 mm a 88,3 x 51,3 mm,
#     soit 5,6 % de moins. A 8 billets la case etait haute et il restait
#     12,7 mm de vide en haut et en bas ; a 10 billets c'est la hauteur
#     qui commande.
#   ⚠️ Les marges de la feuille ne bougent pas : 8 mm sur les cotes,
#     9 mm en haut, 8 mm en bas, 4 mm entre les billets.
#   ⚠️⚠️ Sans cette reinscription, 500 feuilles commandees n'en
#     donneraient que 400.
#   ⭐ CE QUE CA RAPPORTE : 25 % de billets en plus par feuille, donc
#     20 % de papier en moins pour la meme commande.
# ═════════════════════════════════════════════════════════════════════
_enregistrer_paire("francs5000", "5000 FRANCS", "\U0001f48e", 10, francs5000.generer_pdf)
# ═════════════════════════════════════════════════════════════════════
# 💵 ET LA MEME REPARATION POUR LE 500 FRANCS — un defaut trouve ce soir
#   Le fichier francs500.py est passe a 10 billets par feuille le 29/09
#   et il est bien en ligne, MAIS app.py en comptait toujours 8. Resultat
#   mesure : une commande de 500 feuilles ne sortait que 400 feuilles.
#   Elle en perdait 100 par rame. On le reinscrit a 10, comme le fichier.
#   La regle du 500 F ne change pas, son billet ne change pas non plus.
# ═════════════════════════════════════════════════════════════════════
_enregistrer_paire("francs500", "500 FRANCS", "\U0001f4b5", 10, francs500.generer_pdf)
# ⭐ la regle du 28/09 : on rememorise la table de fabrication APRES
#    tout bloc qui touche au catalogue (le plafond des 375 feuilles).
CARTES_PAR_FEUILLE.update({_j: _v["cartes_par_feuille"] for _j, _v in REGISTRE_JEUX.items()})
print("[BILLETS] 5000 F et 500 F a 10 billets/feuille · %d jeux"
      % len(REGISTRE_JEUX))
# ═════════════════════════════════════════════════════════════════════
# 🌿 30/09 — BIO 6 BOULES : nouvelle planche (ex BIO 5, passe a 6 boules)
#   (sceau Maeva : « on va changer la maquette du jeu BIO 5 boules » puis
#    « 6 boules »)
#   ⭐ LA REGLE : B 1-15 (deux numeros), I 16-30 (deux), O 61-75 (deux).
#     SIX numeros par carton — les six cases de la grille 3x2 sont
#     occupees. Tries du plus petit en haut. Crieur : 1-30 et 61-75 (il
#     saute le 31-60, comme avant).
#   ⚠️ CE QUI CHANGE : avant une grille 3x3 avec le QR au coeur et CINQ
#     numeros ; maintenant une grille 3x2 toute simple et SIX numeros (le
#     I passe de un a deux). C'est son choix du 30/09.
#   ⚠️ PLUS DE QR : sa planche n'a plus de case centrale pour le loger.
#   ⚠️⚠️ 16 cartons par feuille A4 PAYSAGE au lieu de 12. Sans cette
#     reinscription, 500 feuilles commandees n'en donneraient que 375.
#   ⚠️ Sa planche est au trait : si le jeu portait une image, il en sort
#     (etiquette du menu + supplement). JEUX_HABILLES et JEUX_MOTIF ne
#     sont PAS touches, c'est son choix commercial.
#   ⭐ 105 x 105 x 105 = plus d'un million de cartons differents : le jeu
#     ne s'epuise pas. Le garde-fou evite les doublons dans une meme rame.
# ═════════════════════════════════════════════════════════════════════
GRIS_PARTICULIERS.update({"bio5": 0.40})
_GRIS_POSES = _imposer_gris_maison()
try:
    JEUX_AVEC_IMAGE.discard("bio5")
except Exception:
    pass
_enregistrer_paire("bio5", "BIO 6 boules", "\U0001f33f", 16, bio5.generer_pdf)
# ⭐ la regle du 28/09 : on rememorise la table de fabrication APRES
#    tout bloc qui touche au catalogue (le plafond des 375 feuilles).
CARTES_PAR_FEUILLE.update({_j: _v["cartes_par_feuille"] for _j, _v in REGISTRE_JEUX.items()})
print("[BIO 6] nouvelle planche · crieur %s · 16 cartons/feuille · %d jeux"
      % (_PLAGES_CALLER["bio5"], len(REGISTRE_JEUX)))
# ═════════════════════════════════════════════════════════════════════
# 💎 30/09 — DIAMANT : nouvelle planche
#   (sceau Maeva : « changeant la maquette du jeu DIAMANT »)
#   ⭐ LA REGLE NE CHANGE PAS : B 1-15, I 16-30, N 31-45, G 46-60,
#     O 61-75. Dix numeros par carton, deux par lettre, le petit en haut
#     le grand en bas, chacun dans la table de son diamant. Crieur 1-75.
#   ⚠️ LE DESSIN DU JEU CHANGE : avant les dix diamants etaient une image,
#     maintenant ils sont dessines au trait avec les lettres B·I·N·G·O en
#     hexagones. Les dix numeros et leurs plages sont identiques : la
#     partie se joue pareil.
#   ⚠️⚠️ 16 cartons par feuille A4 PAYSAGE au lieu de 8. Sans cette
#     reinscription, 500 feuilles commandees n'en donneraient que 250.
#   ⚠️ Sa planche est au trait : le jeu n'embarque plus d'image. Il sort
#     de la liste « carton avec dessin » (etiquette du menu + supplement).
#     Il RESTE dans les jeux reserves : JEUX_HABILLES n'est pas touche.
#   ⭐ 105^5 = plus de 12 milliards de cartons differents : le jeu ne
#     s'epuise pas. Le garde-fou evite les doublons dans une meme rame.
# ═════════════════════════════════════════════════════════════════════
GRIS_PARTICULIERS.update({"diamant": 0.40})
_GRIS_POSES = _imposer_gris_maison()
try:
    JEUX_AVEC_IMAGE.discard("diamant")
except Exception:
    pass
_enregistrer_paire("diamant", "DIAMANT", "\U0001f48e", 16, diamant.generer_pdf)
# ⭐ la regle du 28/09 : on rememorise la table de fabrication APRES
#    tout bloc qui touche au catalogue (le plafond des 375 feuilles).
CARTES_PAR_FEUILLE.update({_j: _v["cartes_par_feuille"] for _j, _v in REGISTRE_JEUX.items()})
print("[DIAMANT] nouvelle planche · crieur %s · 16 cartons/feuille · %d jeux"
      % (_PLAGES_CALLER["diamant"], len(REGISTRE_JEUX)))
# ═════════════════════════════════════════════════════════════════════
# 🌙 30/09 — MOON : nouvelle planche
#   (sceau Maeva : « on change la maquette du jeu MOON »)
#   ⭐ LA REGLE NE CHANGE PAS : M 1-15, O 16-30, O 46-60, N 61-75. Huit
#     numeros par carton, deux par lettre, le petit en haut le grand en
#     bas. LE 31-45 N'EXISTE PAS : le crieur sort 1-30 et 46-75, comme
#     avant.
#   ⚠️ LE DESSIN DU JEU CHANGE : avant les huit numeros etaient une image,
#     maintenant la planche porte le titre MOON, son croissant de lune,
#     ses etoiles et HUIT cases carrees. Les huit numeros et leurs plages
#     sont identiques : la partie se joue pareil.
#   ⚠️⚠️ 16 cartons par feuille A4 PAYSAGE au lieu de 8. Sans cette
#     reinscription, 500 feuilles commandees n'en donneraient que 250.
#   ⚠️ Sa planche est au trait : le jeu n'embarque plus d'image. Il sort
#     de la liste « carton avec dessin » (etiquette du menu + supplement).
#     Il RESTE dans les jeux reserves : JEUX_HABILLES n'est pas touche.
#   ⚠️ Le MOON CLASSIC n'est PAS touche : il garde son ancienne planche.
#   ⭐ 105^4 = plus de 121 millions de cartons differents.
# ═════════════════════════════════════════════════════════════════════
GRIS_PARTICULIERS.update({"moon": 0.40})
_GRIS_POSES = _imposer_gris_maison()
try:
    JEUX_AVEC_IMAGE.discard("moon")
except Exception:
    pass
_enregistrer_paire("moon", "MOON", "\U0001f319", 16, moon.generer_pdf)
# ⭐ la regle du 28/09 : on rememorise la table de fabrication APRES
#    tout bloc qui touche au catalogue (le plafond des 375 feuilles).
CARTES_PAR_FEUILLE.update({_j: _v["cartes_par_feuille"] for _j, _v in REGISTRE_JEUX.items()})
print("[MOON] nouvelle planche · crieur %s · 16 cartons/feuille · %d jeux"
      % (_PLAGES_CALLER["moon"], len(REGISTRE_JEUX)))
# ═════════════════════════════════════════════════════════════════════
# 🏝️ 01/10 — LAGOON 5 BOULES : nouvelle planche
#   (sceau Maeva : « on change la maquette du jeu LAGOON »)
#   ⭐ LA REGLE NE CHANGE PAS : cinq numeros en croix dans le cercle.
#     En haut 1-10, au milieu 11-20 · 21-30 · 31-40 (gauche a droite),
#     en bas 41-50. Un numero par plage. Crieur 1-50.
#   ⚠️ LE DESSIN DU JEU CHANGE : avant le cercle et ses cases etaient une
#     image, maintenant ils sont dessines au trait, avec le cocotier,
#     l'ilot et les oiseaux. Les cinq numeros et leurs plages sont
#     identiques : la partie se joue pareil.
#   ⚠️⚠️ 16 cartons par feuille A4 PAYSAGE au lieu de 12. Sans cette
#     reinscription, 500 feuilles commandees n'en donneraient que 375.
#   ⚠️ Sa planche est au trait : le jeu n'embarque plus d'image. Il sort
#     de la liste « carton avec dessin » (etiquette du menu + supplement).
#     Il RESTE dans les jeux reserves : JEUX_HABILLES n'est pas touche.
#   ⚠️ Le LAGOON CLASSIC n'est PAS touche : il garde son ancienne planche.
#   ⭐ 10^5 = 100 000 cartons differents. Le garde-fou evite les doublons
#     dans une meme rame.
# ═════════════════════════════════════════════════════════════════════
GRIS_PARTICULIERS.update({"lagoon": 0.40})
_GRIS_POSES = _imposer_gris_maison()
try:
    JEUX_AVEC_IMAGE.discard("lagoon")
except Exception:
    pass
_enregistrer_paire("lagoon", "LAGOON 5 boules", "\U0001f3dd️", 16, lagoon.generer_pdf)
# ⭐ la regle du 28/09 : on rememorise la table de fabrication APRES
#    tout bloc qui touche au catalogue (le plafond des 375 feuilles).
CARTES_PAR_FEUILLE.update({_j: _v["cartes_par_feuille"] for _j, _v in REGISTRE_JEUX.items()})
print("[LAGOON] nouvelle planche · crieur %s · 16 cartons/feuille · %d jeux"
      % (_PLAGES_CALLER["lagoon"], len(REGISTRE_JEUX)))
# ═════════════════════════════════════════════════════════════════════
# 🎱 01/10 — IGO : nouvelle planche
#   (sceau Maeva : « changeant la maquette du jeu IGO »)
#   ⭐ LA REGLE NE CHANGE PAS : cinq numeros. Rangee du haut I 16-30,
#     G 46-60, O 61-75 ; dessous deux bulles G 46-60. Les trois G sont
#     distincts. Crieur : 16-30 et 46-75 (il saute 1-15 et 31-45).
#   ⚠️ LE DESSIN DU JEU CHANGE : sa nouvelle planche dessine les cinq
#     bulles au trait avec les lettres I · G · O. Les cinq numeros et
#     leurs plages sont identiques : la partie se joue pareil.
#   ⚠️⚠️ 16 cartons par feuille A4 PAYSAGE au lieu de 12. Sans cette
#     reinscription, 500 feuilles commandees n'en donneraient que 375.
#   ⚠️ Sa planche est au trait : le jeu n'embarque plus d'image. Il sort
#     de la liste « carton avec dessin » (etiquette du menu + supplement).
#     Son tarif special (TARIF_NB_150) et le reste ne sont PAS touches.
#   ⭐ 15 x 15 x (15x14x13) = 614 250 cartons differents. Le garde-fou
#     evite les doublons dans une meme rame.
# ═════════════════════════════════════════════════════════════════════
GRIS_PARTICULIERS.update({"igo": 0.40})
_GRIS_POSES = _imposer_gris_maison()
try:
    JEUX_AVEC_IMAGE.discard("igo")
except Exception:
    pass
_enregistrer_paire("igo", "IGO", "\U0001f3b1", 16, igo.generer_pdf)
# ⭐ la regle du 28/09 : on rememorise la table de fabrication APRES
#    tout bloc qui touche au catalogue (le plafond des 375 feuilles).
CARTES_PAR_FEUILLE.update({_j: _v["cartes_par_feuille"] for _j, _v in REGISTRE_JEUX.items()})
print("[IGO] nouvelle planche · crieur %s · 16 cartons/feuille · %d jeux"
      % (_PLAGES_CALLER["igo"], len(REGISTRE_JEUX)))
# ═════════════════════════════════════════════════════════════════════
# 🦪 01/10 — POE : nouvelle planche, celle aux six cases carrees
#   (sceau Maeva : « on change la maquette du jeu POE »)
#   ⚠️ POE et POE PARAU restent DEUX JEUX DIFFERENTS. Ce bloc ne touche
#     QUE le POE. Le POE PARAU garde sa planche et ses medaillons.
#   ⭐ LA REGLE NE CHANGE PAS : six numeros, DEUX par plage — 45-60,
#     61-75, 76-90, tries. Dans ses six cases (2 rangees x 3 colonnes),
#     une colonne par plage, le petit en haut et le grand en bas. Le
#     crieur reste sur 45-90.
#   ⚠️ LE DESSIN DU JEU CHANGE : avant, chaque numero vivait dans SON
#     medaillon ovale avec sa perle (six medaillons). Il se lit
#     maintenant dans les cases carrees de sa planche. Les six numeros
#     et leurs plages sont identiques : pour la joueuse et la crieuse,
#     la partie se joue exactement pareil.
#   ⚠️⚠️ 16 cartons par feuille A4 PAYSAGE au lieu de 12. Sans cette
#     reinscription, 500 feuilles commandees n'en donneraient que 375.
#   ⚠️ Sa planche est au trait : le jeu reste « SANS IMAGE » (il l'etait
#     deja), rien n'est touche cote tarif ni cote jeux reserves.
#   ⭐ 120 x 105 x 105 = 1 323 000 cartons differents : le jeu ne
#     s'epuise pas (une rame de 500 feuilles en fait 8 000).
# ═════════════════════════════════════════════════════════════════════
_enregistrer_paire("poe", "POE 6 boules", "⚪", 16, poegen.generer_pdf)
# ⭐ la regle du 28/09 : on rememorise la table de fabrication APRES
#    tout bloc qui touche au catalogue (le plafond des 375 feuilles).
CARTES_PAR_FEUILLE.update({_j: _v["cartes_par_feuille"] for _j, _v in REGISTRE_JEUX.items()})
print("[POE] nouvelle planche · crieur %s · 16 cartons/feuille · %d jeux"
      % (_PLAGES_CALLER["poe"], len(REGISTRE_JEUX)))
# ═════════════════════════════════════════════════════════════════════
# 🎯 01/10 — BIN 6 boules : nouvelle planche, celle au tableau de 6 cases
#   (sceau Maeva : « on change la maquette du jeu BIN 6 boules »)
#   ⭐ LA REGLE NE CHANGE PAS : six numeros, DEUX par colonne — B 1-12,
#     I 13-24, N 25-36, en ordre vertical LIBRE (non trie). Le crieur
#     reste sur 1-36.
#   ⚠️ LE DESSIN DU JEU CHANGE : avant, chaque numero se logeait dans une
#     NOIX DE COCO. Il se lit maintenant dans les cases de son tableau.
#     Les six numeros et leurs plages sont identiques : pour la joueuse
#     et la crieuse, la partie se joue exactement pareil.
#   ⚠️⚠️ 16 cartons par feuille A4 PAYSAGE au lieu de 12. Sans cette
#     reinscription, 500 feuilles commandees n'en donneraient que 375.
#   ⚠️ Sa planche est au trait : le carton ne porte plus d'image (le coco).
#     Le jeu sort de la liste « AVEC IMAGE » (etiquette du menu). Son tarif
#     et ses jeux reserves ne sont pas touches.
#   ⚠️ Le BIN 8 boules n'est PAS touche : il garde sa planche et ses 12
#     cartons par feuille.
#   ⭐ 132^3 = 2 299 968 cartons differents : le jeu ne s'epuise pas (une
#     rame de 500 feuilles en fait 8 000).
# ═════════════════════════════════════════════════════════════════════
try:
    JEUX_AVEC_IMAGE.discard("bin6")
except Exception:
    pass
_enregistrer_paire("bin6", "BIN 6 boules", "\U0001f3af", 16, bin6.generer_pdf)
# ⭐ la regle du 28/09 : on rememorise la table de fabrication APRES
#    tout bloc qui touche au catalogue (le plafond des 375 feuilles).
CARTES_PAR_FEUILLE.update({_j: _v["cartes_par_feuille"] for _j, _v in REGISTRE_JEUX.items()})
print("[BIN 6] nouvelle planche · crieur %s · 16 cartons/feuille · %d jeux"
      % (_PLAGES_CALLER["bin6"], len(REGISTRE_JEUX)))
# ═════════════════════════════════════════════════════════════════════
# 🫒 02/10 — OLIVE : NOUVEAU JEU (maquette de Maeva)
#   (sceau Maeva : « créant un nouveau jeu OLIVE, voici les plages du
#    BINGO »)
#   ⭐ LA REGLE : CINQ numeros, UN par colonne — les plages du BINGO :
#        O 1-15 · L 16-30 · I 31-45 · V 46-60 · E 61-75. Crieur 1-75.
#   ⭐ Dans chaque colonne, une case porte une croix (×, decor fixe de sa
#     planche) et l'autre est vide : le numero se pose dans la case VIDE.
#   ⭐ 16 cartons par feuille A4 PAYSAGE. Sa planche est au trait (pas
#     d'image a facturer) : le jeu est « SANS IMAGE », tarif ordinaire.
#   ⭐ 15^5 = 759 375 cartons differents : une rame de 500 feuilles en
#     fait 8 000, tous differents (garde-fou dans olive.py).
# ═════════════════════════════════════════════════════════════════════
from generators import olive as olivegen
_PLAGES_CALLER["olive"] = (1, 75)
_enregistrer_paire("olive", "OLIVE 5 boules", "\U0001fad2", 16, olivegen.generer_pdf)
# ⭐ la regle du 28/09 : on rememorise la table de fabrication APRES
#    tout bloc qui touche au catalogue (le plafond des 375 feuilles).
CARTES_PAR_FEUILLE.update({_j: _v["cartes_par_feuille"] for _j, _v in REGISTRE_JEUX.items()})
print("[OLIVE] nouveau jeu · crieur %s · 16 cartons/feuille · %d jeux"
      % (_PLAGES_CALLER["olive"], len(REGISTRE_JEUX)))
# ═════════════════════════════════════════════════════════════════════
# 👑 02/10 — KING 40 : NOUVEAU JEU (maquette de Maeva)
#   (sceau Maeva : « nouveau jeu KING 40, voici les plages 1-10, 11-20,
#    21-30, 31-40 »)
#   ⭐ LA REGLE : DOUZE numeros, TROIS par colonne — une colonne par plage :
#        colonne 1 : 1-10  ·  colonne 2 : 11-20
#        colonne 3 : 21-30 ·  colonne 4 : 31-40
#     Dans chaque colonne, tries du plus petit en haut. Crieur 1-40.
#   ⭐ 12 cartons par feuille A4 PORTRAIT (3 colonnes × 4 rangees), comme
#     sa planche. Jeu au trait, « SANS IMAGE », tarif ordinaire.
#   ⭐ C(10,3)^4 = 120^4 = 207 360 000 cartons differents : le jeu ne
#     s'epuise pas (garde-fou dans king.py).
# ═════════════════════════════════════════════════════════════════════
from generators import king as kinggen
_PLAGES_CALLER["king"] = (1, 40)
_enregistrer_paire("king", "KING 40", "\U0001f451", 12, kinggen.generer_pdf)
# ⭐ la regle du 28/09 : on rememorise la table de fabrication APRES
#    tout bloc qui touche au catalogue (le plafond des 375 feuilles).
CARTES_PAR_FEUILLE.update({_j: _v["cartes_par_feuille"] for _j, _v in REGISTRE_JEUX.items()})
print("[KING 40] nouveau jeu · crieur %s · 12 cartons/feuille · %d jeux"
      % (_PLAGES_CALLER["king"], len(REGISTRE_JEUX)))
# ═════════════════════════════════════════════════════════════════════
# ⭐ 02/10 — STAR : NOUVEAU JEU (maquette de Maeva)
#   (sceau Maeva : « jeu STAR, voici les plages 30-49, 50-60, 61-79,
#    80-90 »)
#   ⭐ LA REGLE : HUIT numeros. Les quatre coins portent une croix (×,
#     decor fixe) ; le numero se pose dans les cases VIDES. Une plage par
#     colonne :
#        colonne 1 : 30-49 -> 1 numero (au milieu)
#        colonne 2 : 50-60 -> 3 numeros (tries)
#        colonne 3 : 61-79 -> 3 numeros (tries)
#        colonne 4 : 80-90 -> 1 numero (au milieu)
#     Crieur 30-90.
#   ⭐ 12 cartons par feuille A4 PORTRAIT (3 colonnes × 4 rangees), comme
#     sa planche. Jeu au trait, « SANS IMAGE », tarif ordinaire.
#   ⭐ 20 × C(11,3) × C(19,3) × 11 = 35 174 700 cartons differents
#     (garde-fou dans star.py).
# ═════════════════════════════════════════════════════════════════════
from generators import star as stargen
_PLAGES_CALLER["star"] = (30, 90)
_enregistrer_paire("star", "STAR", "\U00002b50", 12, stargen.generer_pdf)
# ⭐ la regle du 28/09 : on rememorise la table de fabrication APRES
#    tout bloc qui touche au catalogue (le plafond des 375 feuilles).
CARTES_PAR_FEUILLE.update({_j: _v["cartes_par_feuille"] for _j, _v in REGISTRE_JEUX.items()})
print("[STAR] nouveau jeu · crieur %s · 12 cartons/feuille · %d jeux"
      % (_PLAGES_CALLER["star"], len(REGISTRE_JEUX)))
# ═════════════════════════════════════════════════════════════════════
# 💛 02/10 — LOVE : NOUVEAU JEU (maquette de Maeva)
#   (sceau Maeva : « jeu LOVE, voici les plages 1-15, 16-30, 31-45,
#    46-60 »)
#   ⭐ LA REGLE : DOUZE numeros, TROIS par colonne — une colonne par plage :
#        colonne 1 : 1-15  ·  colonne 2 : 16-30
#        colonne 3 : 31-45 ·  colonne 4 : 46-60
#     Dans chaque colonne, tries du plus petit en haut. Crieur 1-60.
#   ⭐ 12 cartons par feuille A4 PORTRAIT (3 colonnes × 4 rangees), comme
#     sa planche. Jeu au trait, « SANS IMAGE », tarif ordinaire.
#   ⭐ C(15,3)^4 = 455^4 = 42 859 950 625 cartons differents (garde-fou
#     dans love.py).
# ═════════════════════════════════════════════════════════════════════
from generators import love as lovegen
_PLAGES_CALLER["love"] = (1, 60)
_enregistrer_paire("love", "LOVE", "\U0001f49b", 12, lovegen.generer_pdf)
# ⭐ la regle du 28/09 : on rememorise la table de fabrication APRES
#    tout bloc qui touche au catalogue (le plafond des 375 feuilles).
CARTES_PAR_FEUILLE.update({_j: _v["cartes_par_feuille"] for _j, _v in REGISTRE_JEUX.items()})
print("[LOVE] nouveau jeu · crieur %s · 12 cartons/feuille · %d jeux"
      % (_PLAGES_CALLER["love"], len(REGISTRE_JEUX)))
# ═════════════════════════════════════════════════════════════════════
# 🌺 02/10 — TIARE : nouvelle planche, celle a la fleur de tiare
#   (sceau Maeva : « changeant la maquette du jeu TIARE »)
#   ⭐ LA REGLE NE CHANGE PAS : cinq numeros tires de 50 a 90, tries du
#     plus petit au plus grand. Le crieur reste sur 50-90.
#   ⚠️ LE DESSIN DU JEU CHANGE : avant, le carton portait une IMAGE de
#     tiare. La fleur est maintenant au trait sur sa planche, avec cinq
#     cases (deux a gauche, deux a droite, une large en bas). Les cinq
#     numeros et leur plage sont identiques : la partie se joue pareil.
#   ⚠️⚠️ 16 cartons par feuille A4 PAYSAGE au lieu de 12. Sans cette
#     reinscription, 500 feuilles commandees n'en donneraient que 375.
#   ⚠️ Sa planche est au trait : le carton ne porte plus d'image. Le jeu
#     sort de la liste « AVEC IMAGE » (etiquette du menu). Son tarif et ses
#     jeux reserves ne sont pas touches.
#   ⭐ C(41,5) = 749 398 cartons differents : le jeu ne s'epuise pas (une
#     rame de 500 feuilles en fait 8 000).
# ═════════════════════════════════════════════════════════════════════
try:
    JEUX_AVEC_IMAGE.discard("tiare")
except Exception:
    pass
_enregistrer_paire("tiare", "TIARE 50-90", "\U0001f33c", 16, tiaregen.generer_pdf)
# ⭐ la regle du 28/09 : on rememorise la table de fabrication APRES
#    tout bloc qui touche au catalogue (le plafond des 375 feuilles).
CARTES_PAR_FEUILLE.update({_j: _v["cartes_par_feuille"] for _j, _v in REGISTRE_JEUX.items()})
print("[TIARE] nouvelle planche · crieur %s · 16 cartons/feuille · %d jeux"
      % (_PLAGES_CALLER["tiare"], len(REGISTRE_JEUX)))
# ═════════════════════════════════════════════════════════════════════
# 4️⃣ 02/10 — « 4 » : NOUVEAU JEU (maquette de Maeva, planche agrandie)
#   (sceau Maeva : « nouveau jeu 4, les plages sont celle du bingo B I G O »
#    puis « je veux 30 pt » -> planche 3 cases plus larges, 20 cartons)
#   ⭐ LA REGLE : QUATRE numeros, UN par colonne, aux plages du bingo
#     B·I·G·O :
#        case 1 : B 1-15  ·  case 2 : I 16-30
#        case 3 : G 46-60 ·  case 4 : O 61-75
#     On saute le N (31-45) : le crieur sort 1-30 et 46-75 (comme le
#     FAFAPITI).
#   ⭐ 20 cartons par feuille A4 PAYSAGE (4 colonnes × 5 rangees), comme sa
#     nouvelle planche. Chiffres a 30 pt. Jeu au trait, « SANS IMAGE ».
#   ⭐ 15^4 = 50 625 cartons differents (garde-fou dans jeu4.py).
# ═════════════════════════════════════════════════════════════════════
from generators import jeu4 as jeu4gen
_PLAGES_CALLER["jeu4"] = (1, 75)
_BOULES_CALLER["jeu4"] = [n for n in range(1, 31)] + [n for n in range(46, 76)]
_enregistrer_paire("jeu4", "4", "\U00000034\U0000fe0f\U000020e3", 20, jeu4gen.generer_pdf)
# ⭐ la regle du 28/09 : on rememorise la table de fabrication APRES
#    tout bloc qui touche au catalogue (le plafond des 375 feuilles).
CARTES_PAR_FEUILLE.update({_j: _v["cartes_par_feuille"] for _j, _v in REGISTRE_JEUX.items()})
print("[4] nouveau jeu · crieur %s (B.I.G.O, sans N) · 20 cartons/feuille · %d jeux"
      % (_PLAGES_CALLER["jeu4"], len(REGISTRE_JEUX)))
# ═════════════════════════════════════════════════════════════════════
# 5️⃣ 02/10 — « 5 » : NOUVEAU JEU (maquette de Maeva)
#   (sceau Maeva : « nouveau jeu 5, les plages sont ceux du BINGO »)
#   ⭐ LA REGLE : CINQ numeros, UN par colonne, aux plages du BINGO complet :
#        case 1 : B 1-15  ·  case 2 : I 16-30  ·  case 3 : N 31-45
#        case 4 : G 46-60 ·  case 5 : O 61-75
#     Le crieur sort 1-75 (toutes les boules, le N est inclus).
#   ⭐ 20 cartons par feuille A4 PAYSAGE (4 colonnes × 5 rangees), comme sa
#     planche. Chiffres a 32 pt. Jeu au trait, « SANS IMAGE ».
#   ⭐ 15^5 = 759 375 cartons differents (garde-fou dans jeu5.py).
# ═════════════════════════════════════════════════════════════════════
from generators import jeu5 as jeu5gen
_PLAGES_CALLER["jeu5"] = (1, 75)
_BOULES_CALLER["jeu5"] = [n for n in range(1, 76)]
_enregistrer_paire("jeu5", "5", "\U00000035\U0000fe0f\U000020e3", 20, jeu5gen.generer_pdf)
# ⭐ la regle du 28/09 : on rememorise la table de fabrication APRES
#    tout bloc qui touche au catalogue (le plafond des 375 feuilles).
CARTES_PAR_FEUILLE.update({_j: _v["cartes_par_feuille"] for _j, _v in REGISTRE_JEUX.items()})
print("[5] nouveau jeu · crieur %s (B.I.N.G.O complet) · 20 cartons/feuille · %d jeux"
      % (_PLAGES_CALLER["jeu5"], len(REGISTRE_JEUX)))
# ═════════════════════════════════════════════════════════════════════
# 6️⃣ 02/10 — « 6 » : NOUVEAU JEU (maquette de Maeva)
#   (sceau Maeva : « nouveau jeu 6, ces plages sont celle du BINGO et 90
#    soit 76-90 »)
#   ⭐ LA REGLE : SIX numeros, UN par colonne, aux plages du BINGO + une
#     6e colonne :
#        case 1 : B 1-15  ·  case 2 : I 16-30 ·  case 3 : N 31-45
#        case 4 : G 46-60 ·  case 5 : O 61-75 ·  case 6 : 76-90
#     Le crieur sort 1-90 (toutes les boules).
#   ⭐ 15 cartons par feuille A4 PAYSAGE (3 colonnes × 5 rangees), comme sa
#     planche. Chiffres a 32 pt. Jeu au trait, « SANS IMAGE ».
#   ⭐ 15^6 = 11 390 625 cartons differents (garde-fou dans jeu6.py).
# ═════════════════════════════════════════════════════════════════════
from generators import jeu6 as jeu6gen
_PLAGES_CALLER["jeu6"] = (1, 90)
_BOULES_CALLER["jeu6"] = [n for n in range(1, 91)]
_enregistrer_paire("jeu6", "6", "\U00000036\U0000fe0f\U000020e3", 15, jeu6gen.generer_pdf)
# ⭐ la regle du 28/09 : on rememorise la table de fabrication APRES
#    tout bloc qui touche au catalogue (le plafond des 375 feuilles).
CARTES_PAR_FEUILLE.update({_j: _v["cartes_par_feuille"] for _j, _v in REGISTRE_JEUX.items()})
print("[6] nouveau jeu · crieur %s (B.I.N.G.O + 76-90) · 15 cartons/feuille · %d jeux"
      % (_PLAGES_CALLER["jeu6"], len(REGISTRE_JEUX)))
