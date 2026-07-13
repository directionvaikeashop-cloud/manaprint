# -*- coding: utf-8 -*-
"""
MANAPRINT — Générateur de FACTURES PARTENAIRES (format A4)
Facture mensuelle du dû à 2KEA & Associé : les redevances PDF (1,5 F / feuille)
des commandes réglées « en boutique » chez un partenaire imprimeur
(FUN AND CO, COCOTIE MER, RANIHEI).

Usage :
    from generators import facture
    pdf = facture.generer_facture(numero, mois_label, partenaire, lignes, total)
    # lignes = [{"date": "2026-07-12", "commande": 12, "jeu": "BIN 6 boules",
    #            "feuilles": 250, "pu": 1.5, "montant": 375}, ...]
"""
import io
from datetime import date
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm

TEAL = colors.HexColor("#2D6E63")
TEAL_D = colors.HexColor("#1A4A42")
GRIS = colors.Color(0.42, 0.42, 0.42)
GRIS_CLAIR = colors.Color(0.92, 0.94, 0.93)
LIGNE = colors.Color(0.85, 0.87, 0.86)

EMETTEUR = {
    "nom": "2KEA & ASSOCIÉ",
    "detail": "Réseau MANAPRINT — manaprint.app",
    "adresse": "Papeete · Tahiti · Polynésie française",
    "tel": "Tél : 89 52 98 83",
    "email": "directionvaikeashop@gmail.com",
}

PAGE_W, PAGE_H = A4
MARGE = 18 * mm
LIGNES_PAR_PAGE = 24


def _entete(c, numero, mois_label, partenaire, page, pages):
    """Bandeau émetteur + destinataire + cartouche facture."""
    # Bandeau émetteur
    c.setFillColor(TEAL_D)
    c.setFont("Helvetica-Bold", 17)
    c.drawString(MARGE, PAGE_H - 22 * mm, EMETTEUR["nom"])
    c.setFillColor(GRIS); c.setFont("Helvetica", 8.5)
    c.drawString(MARGE, PAGE_H - 27 * mm, EMETTEUR["detail"])
    c.drawString(MARGE, PAGE_H - 31 * mm, EMETTEUR["adresse"])
    c.drawString(MARGE, PAGE_H - 35 * mm, EMETTEUR["tel"] + "  ·  " + EMETTEUR["email"])
    c.setStrokeColor(TEAL); c.setLineWidth(1.2)
    c.line(MARGE, PAGE_H - 38 * mm, PAGE_W - MARGE, PAGE_H - 38 * mm)

    # Cartouche FACTURE (droite)
    c.setFillColor(TEAL)
    c.roundRect(PAGE_W - MARGE - 62 * mm, PAGE_H - 33 * mm, 62 * mm, 13 * mm, 2 * mm, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(PAGE_W - MARGE - 31 * mm, PAGE_H - 25.5 * mm, "FACTURE")
    c.setFont("Helvetica", 8)
    c.drawCentredString(PAGE_W - MARGE - 31 * mm, PAGE_H - 30.5 * mm, "N° " + numero)

    # Destinataire + période
    y = PAGE_H - 48 * mm
    c.setFillColor(GRIS); c.setFont("Helvetica", 8)
    c.drawString(MARGE, y, "FACTURÉ À")
    c.setFillColor(colors.black); c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGE, y - 5.5 * mm, partenaire.get("nom", ""))
    c.setFillColor(GRIS); c.setFont("Helvetica", 8.5)
    lz = partenaire.get("zone", "")
    if partenaire.get("tel"):
        lz += ("  ·  " if lz else "") + partenaire["tel"]
    c.drawString(MARGE, y - 10 * mm, lz)
    if partenaire.get("email"):
        c.drawString(MARGE, y - 14 * mm, partenaire["email"])

    c.setFillColor(GRIS); c.setFont("Helvetica", 8)
    c.drawRightString(PAGE_W - MARGE, y, "PÉRIODE")
    c.setFillColor(colors.black); c.setFont("Helvetica-Bold", 10)
    c.drawRightString(PAGE_W - MARGE, y - 5.5 * mm, mois_label)
    c.setFillColor(GRIS); c.setFont("Helvetica", 8)
    c.drawRightString(PAGE_W - MARGE, y - 10 * mm, "Émise le " + date.today().strftime("%d/%m/%Y"))
    c.drawRightString(PAGE_W - MARGE, y - 14 * mm, "Page %d / %d" % (page, pages))

    # Objet
    c.setFillColor(TEAL_D); c.setFont("Helvetica-Bold", 9.5)
    c.drawString(MARGE, y - 22 * mm, "Objet : redevances PDF MANAPRINT — commandes réglées en boutique chez le partenaire (1,5 F / feuille)")
    return y - 28 * mm


def _tete_tableau(c, y):
    c.setFillColor(TEAL)
    c.rect(MARGE, y - 7 * mm, PAGE_W - 2 * MARGE, 7 * mm, stroke=0, fill=1)
    c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 8)
    xs = _colonnes()
    for (x, _w, _a), titre in zip(xs, ["Date", "Commande", "Jeu", "Feuilles", "P.U.", "Montant"]):
        c.drawString(x + 1.5 * mm, y - 4.8 * mm, titre)
    return y - 7 * mm


def _colonnes():
    """(x, largeur, alignement) de chaque colonne."""
    zone = PAGE_W - 2 * MARGE
    parts = [0.11, 0.13, 0.34, 0.13, 0.12, 0.17]
    xs, cur = [], MARGE
    for p in parts:
        xs.append((cur, zone * p, "g"))
        cur += zone * p
    return xs


def _fmt(n):
    """1234 -> '1 234'"""
    return "{:,}".format(int(round(n))).replace(",", " ")


def generer_facture(numero, mois_label, partenaire, lignes, total):
    """Construit la facture PDF et retourne un BytesIO."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, pageCompression=1)
    pages = max(1, (len(lignes) + LIGNES_PAR_PAGE - 1) // LIGNES_PAR_PAGE)
    total_feuilles = sum(int(l.get("feuilles", 0)) for l in lignes)

    idx = 0
    for page in range(1, pages + 1):
        y = _entete(c, numero, mois_label, partenaire, page, pages)
        y = _tete_tableau(c, y)
        xs = _colonnes()
        bloc = lignes[idx:idx + LIGNES_PAR_PAGE]
        idx += LIGNES_PAR_PAGE
        for i, l in enumerate(bloc):
            h = 6.5 * mm
            if i % 2 == 1:
                c.setFillColor(GRIS_CLAIR)
                c.rect(MARGE, y - h, PAGE_W - 2 * MARGE, h, stroke=0, fill=1)
            c.setFillColor(colors.black); c.setFont("Helvetica", 8.5)
            valeurs = [
                str(l.get("date", ""))[:10],
                "#%s" % l.get("commande", ""),
                str(l.get("jeu", ""))[:40],
                _fmt(l.get("feuilles", 0)),
                "1,5 F",
                _fmt(l.get("montant", 0)) + " F",
            ]
            for (x, w, _a), v in zip(xs, valeurs):
                c.drawString(x + 1.5 * mm, y - 4.6 * mm, v)
            c.setStrokeColor(LIGNE); c.setLineWidth(0.3)
            c.line(MARGE, y - h, PAGE_W - MARGE, y - h)
            y -= h

        if page == pages:
            # Bloc TOTAL
            y -= 4 * mm
            c.setFillColor(TEAL_D)
            c.roundRect(PAGE_W - MARGE - 78 * mm, y - 12 * mm, 78 * mm, 12 * mm, 2 * mm, stroke=0, fill=1)
            c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 10)
            c.drawString(PAGE_W - MARGE - 74 * mm, y - 7.5 * mm, "TOTAL DÛ")
            c.setFont("Helvetica-Bold", 13)
            c.drawRightString(PAGE_W - MARGE - 4 * mm, y - 8 * mm, _fmt(total) + " XPF")
            c.setFillColor(GRIS); c.setFont("Helvetica", 8.5)
            c.drawString(MARGE, y - 7.5 * mm,
                         "%d commande(s) · %s feuille(s) PDF au tarif partenaire de 1,5 F / feuille" % (len(lignes), _fmt(total_feuilles)))

            # Mentions de règlement
            y -= 22 * mm
            c.setFillColor(colors.black); c.setFont("Helvetica-Bold", 9)
            c.drawString(MARGE, y, "Règlement")
            c.setFillColor(GRIS); c.setFont("Helvetica", 8.5)
            c.drawString(MARGE, y - 5 * mm, "À réception de la présente facture — en boutique 2KEA Papeete, ou par virement (coordonnées sur demande).")
            c.drawString(MARGE, y - 9.5 * mm, "Référence à rappeler : FACTURE N° " + numero)

        # Pied de page
        c.setFillColor(GRIS); c.setFont("Helvetica", 7)
        c.drawCentredString(PAGE_W / 2, 12 * mm,
                            "2KEA & Associé · MANAPRINT — manaprint.app · Papeete, Tahiti, Polynésie française")
        c.showPage()

    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    lignes = [{"date": "2026-07-12", "commande": i, "jeu": "BIN 6 boules · ÉCO (N&B)",
               "feuilles": 250, "pu": 1.5, "montant": 375} for i in range(1, 5)]
    pdf = generer_facture("F-202607-FUNANDCO", "Juillet 2026",
                          {"nom": "FUN AND CO", "zone": "Presqu'île (Tahiti Iti)",
                           "tel": "87 26 73 24", "email": "funandco24@gmail.com"},
                          lignes, sum(l["montant"] for l in lignes))
    with open("test_facture.pdf", "wb") as f:
        f.write(pdf.read())
    print("Facture générée")
