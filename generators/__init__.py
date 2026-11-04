# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════════════════════
# FILET DE SÉCURITÉ (03/11/2026) — un générateur manquant ou cassé ne doit
# JAMAIS faire tomber tout le site.
#
# app.py importe des dizaines de générateurs (« from generators import X »).
# Si UN seul fichier .py manque sur le dépôt (ou contient une erreur), l'import
# plante au démarrage sous gunicorn → « Application failed to respond », et
# Railway continue de servir l'ancienne version.
#
# Grâce au __getattr__ ci-dessous : si « generators.X » existe, on renvoie le
# VRAI module (comportement normal, aucun changement) ; s'il manque ou plante,
# on renvoie un remplaçant qui fabrique une page blanche, on note le problème
# dans le log ([GEN MANQUANT] X …), et le reste du site démarre normalement.
# ═══════════════════════════════════════════════════════════════════════════
import importlib as _il


def _page_blanche_pdf(*_a, **_k):
    """Feuille A4 blanche de secours quand un générateur manque."""
    import io
    from reportlab.pdfgen import canvas as _canvas
    from reportlab.lib.pagesizes import A4 as _A4
    buf = io.BytesIO()
    c = _canvas.Canvas(buf, pagesize=_A4)
    c.showPage()
    c.save()
    buf.seek(0)
    return buf


class _GenerateurManquant(object):
    """Remplace un module générateur absent/illisible, sans casser l'inscription
    du jeu : generer_pdf renvoie une page blanche ; tout autre attribut renvoie
    une valeur inoffensive."""

    def __init__(self, nom):
        self._nom = nom

    def generer_pdf(self, *a, **k):
        return _page_blanche_pdf(*a, **k)

    def __getattr__(self, cle):
        if cle.startswith("__"):
            raise AttributeError(cle)
        return None


def __getattr__(name):
    # Appelé seulement quand « from generators import <name> » ne trouve pas
    # l'attribut directement : on tente le VRAI sous-module d'abord.
    try:
        return _il.import_module("." + name, __name__)
    except Exception as _e:
        print("[GEN MANQUANT] generators.%s introuvable/illisible — "
              "page blanche de secours (%r)" % (name, _e))
        return _GenerateurManquant(name)
