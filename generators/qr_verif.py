# -*- coding: utf-8 -*-
"""
MANAPRINT — Module QR DE VÉRIFICATION (anti-duplication, authenticité, traçabilité)
====================================================================================
Chaque carton reçoit un QR code unique lié à un événement + son N° de série, plus
un CODE COURT à 6 caractères (lisible à l'œil, pour vérification manuelle).

Le code est un hash SHA-256 tronqué d'un secret + événement + série : un fraudeur
ne peut PAS le deviner ni le recalculer sans le secret. Une photocopie duplique
l'image du QR, mais au scan la plateforme répond DÉJÀ RÉCLAMÉ / INCONNU.

Anti-panne : si ce module est absent, les cartons sortent normalement sans QR.
Le secret DOIT venir d'une variable d'environnement en production (MANAPRINT_QR_SECRET).
"""
import os
import hashlib

from reportlab.lib.units import mm
from reportlab.lib import colors

try:
    from reportlab.graphics.barcode import qr
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics import renderPDF
    _QR_OK = True
except Exception:
    _QR_OK = False

# Secret de signature — À DÉFINIR en production via variable d'environnement.
_SECRET = os.environ.get("MANAPRINT_QR_SECRET", "TUKEA-2KEA-MANAPRINT-DEFAUT")

# Base publique des liens de vérification (ajustable via env).
_BASE_URL = os.environ.get("MANAPRINT_BASE_URL", "https://manaprint.up.railway.app")

# Alphabet lisible : sans 0/O ni 1/I pour éviter les confusions à l'œil.
_TABLE = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def code_verif(evenement_id, serie):
    """Code court unique et infalsifiable (6 caractères) pour un carton."""
    base = "%s|%s|%s" % (_SECRET, evenement_id or "GEN", serie)
    h = hashlib.sha256(base.encode("utf-8")).hexdigest().upper()
    n = int(h[:12], 16)
    code = ""
    for _ in range(6):
        code += _TABLE[n % len(_TABLE)]
        n //= len(_TABLE)
    return code


def url_verif(evenement_id, serie):
    """URL complète encodée dans le QR."""
    return "%s/v/%s/%06d/%s" % (_BASE_URL, evenement_id or "GEN", int(serie), code_verif(evenement_id, serie))


def verifier(evenement_id, serie, code):
    """Contrôle qu'un code correspond bien à l'événement + série (côté serveur)."""
    return str(code).upper() == code_verif(evenement_id, serie)


def dessiner_qr(c, x, y, taille, evenement_id, serie, avec_code=True,
                couleur_texte=colors.Color(0.42, 0.42, 0.42)):
    """Dessine le QR (taille x taille, coin bas-gauche en x,y) + le code court dessous.
    Renvoie True si dessiné, False si le QR n'est pas disponible (anti-panne)."""
    if not _QR_OK:
        return False
    data = url_verif(evenement_id, serie)
    widget = qr.QrCodeWidget(data)
    widget.barLevel = "M"  # ~15% de correction d'erreur : robuste à l'impression laser
    b = widget.getBounds()
    w = b[2] - b[0]
    h = b[3] - b[1]
    d = Drawing(taille, taille, transform=[taille / w, 0, 0, taille / h, 0, 0])
    d.add(widget)
    renderPDF.draw(d, c, x, y)
    if avec_code:
        code = code_verif(evenement_id, serie)
        c.setFillColor(couleur_texte)
        c.setFont("Helvetica", max(4.5, taille * 0.09))
        c.drawCentredString(x + taille / 2, y - taille * 0.14, code)
    return True
