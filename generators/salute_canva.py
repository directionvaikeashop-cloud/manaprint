# -*- coding: utf-8 -*-
"""MANAPRINT — SALUTE 6 boules — la Corse au coeur (une création TUKEA, maquette CANVA de Maeva).
NOUVELLE MAQUETTE de Maeva (24/11/2026, « salute_canva_12_A4 ») reprise TELLE QUELLE :
12 billets / feuille A4 PAYSAGE (3 colonnes x 4 rangées), traits de coupe en pointillés.
Chaque billet : cadre arrondi, le grand X en diagonales grises, la CORSE au centre
(montagnes et arbres), titre SALUTE, 6 grands chiffres sur leur réserve blanche,
« Création TUKEA » et « 89 22 23 05 - Carte N° ».
(Fichier à part : l'ancien salute.py reste pour le SALUTE SMORFIA.)
RÈGLE (inchangée), la lettre B I G O posée contre chaque chiffre (24/11) :
   gauche                       : B  1-15
   haut-gauche / bas-gauche     : I 16-30 (le plus petit en haut)
   haut-droite / bas-droite     : G 46-60 (le plus petit en haut)
   droite                       : O 61-75
   -> crieur 1-30 et 46-75 (le N n'existe pas).
Chiffres comme la maquette : Helvetica 28 pt.
Le tout est réduit pour garder 6 mm de marge d'impression (Konica / Sharp)."""
import io, os as _os, random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors

PAGE_W, PAGE_H = landscape(A4)
COLS, RANGS = 3, 4
CARTES_PAGE = COLS * RANGS                # 12
CELL_W, CELL_H = 280.6299, 148.8189
NOIR = colors.black
RAINBOW = ["#E53935", "#FB8C00", "#F9A825", "#43A047", "#00ACC1",
           "#1E88E5", "#3949AB", "#8E24AA", "#D81B60", "#6D4C41"]
POLICE_NUM, T_NUM = "Helvetica", 28       # comme la maquette (Liberation Sans 28 pt)

_ICI = _os.path.dirname(_os.path.abspath(__file__))
_IMG_CORSE = _os.path.join(_ICI, "salute_v2_corse.png")

# (centre x du chiffre, ligne de base, lettre)
CASES = [
    (24.37682, 58.0075, "B"),     # gauche          1-15
    (73.69852, 92.02324, "I"),    # haut-gauche    16-30 (petit)
    (73.69852, 18.32246, "I"),    # bas-gauche     16-30 (grand)
    (198.4229, 93.44057, "G"),    # haut-droite    46-60 (petit)
    (198.4229, 19.73978, "G"),    # bas-droite     46-60 (grand)
    (256.2497, 58.0075, "O"),     # droite         61-75
]

MARGE_SURE = 6 * 72 / 25.4
ECHELLE = min((PAGE_W - 2 * MARGE_SURE) / PAGE_W, (PAGE_H - 2 * MARGE_SURE) / PAGE_H)
DECAL_X = (PAGE_W - PAGE_W * ECHELLE) / 2.0
DECAL_Y = (PAGE_H - PAGE_H * ECHELLE) / 2.0


def _numeros(rng):
    b = rng.randint(1, 15)
    i1, i2 = sorted(rng.sample(range(16, 31), 2))
    g1, g2 = sorted(rng.sample(range(46, 61), 2))
    o = rng.randint(61, 75)
    return [b, i1, i2, g1, g2, o]


def _billet(c, ox, oy, serie, nums, col):
    c.saveState()
    c.translate(ox, oy)
    c.setStrokeColor(NOIR); c.setLineWidth(0.6)
    c.roundRect(2.267717, 2.267717, 276.0945, 144.2835, 3.134, stroke=1, fill=0)
    c.setStrokeColor(colors.Color(.45, .45, .45)); c.setLineWidth(0.35)
    for x0, y0 in ((4.535433, 144.2835), (276.0945, 144.2835), (4.535433, 4.535433), (276.0945, 4.535433)):
        c.line(x0, y0, 140.315, 66.33071)
    try:
        c.drawImage(_IMG_CORSE, 113.5737, 10.77165, 53.48245, 107.7165, preserveAspectRatio=False, mask="auto")
    except Exception:
        pass
    t = c.beginText(101.2488, 126.4252); t.setFont("Helvetica", 17); t.setCharSpace(2.4)
    t.setFillColor(NOIR); t.textOut("SALUTE"); t.setCharSpace(0); c.drawText(t)
    for (cx, by, let), n in zip(CASES, nums):
        s = str(n); w = c.stringWidth(s, POLICE_NUM, T_NUM)
        c.setFillColor(colors.white)
        c.rect(cx - w / 2.0 - 2.83, by - 4.716, w + 5.66, 29.48031, stroke=0, fill=1)
        tt = c.beginText(cx - w / 2.0, by); tt.setFont(POLICE_NUM, T_NUM); tt.setFillColor(col)
        tt.textOut(s); c.drawText(tt)
        # lettre : pastille blanche contre le coin haut-gauche du chiffre
        lx, ly = cx - w / 2.0 - 4.2, by + 21.5
        if let == "B":                   # le B est tout contre le bord : sa pastille va au-dessus du chiffre
            lx, ly = cx, by + 29.5
        c.setFillColor(colors.white); c.setStrokeColor(NOIR); c.setLineWidth(0.6)
        c.circle(lx, ly, 4.6, stroke=1, fill=1)
        c.setFillColor(col); c.setFont("Helvetica-Bold", 7.0); c.drawCentredString(lx, ly - 2.5, let)
    c.setFillColor(colors.white)
    c.rect(8.503937, 5.669291, 70.86614, 8.503937, stroke=0, fill=1)
    c.rect(175.748, 5.669291, 96.37795, 8.503937, stroke=0, fill=1)
    gris = colors.Color(.35, .35, .35)
    for x, s in ((11.90551, "Cr\u00e9ation TUKEA"),
                 (205.8117, "89 22 23 05  -  Carte N\u00b0 %06d" % serie)):
        tt = c.beginText(x, 7.937008); tt.setFont("Helvetica-Bold", 4.4); tt.setFillColor(gris)
        tt.textOut(s); c.drawText(tt)
    c.restoreState()


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    rng = random.Random(int(serie_start) * 100003 + 6060)
    serie = int(serie_start)
    faits = 0
    try:
        no_page = max(1, int(page_start))
    except Exception:
        no_page = 1
    col_imposee = None
    if couleur and couleur_perso:
        try:
            col_imposee = colors.HexColor(couleur_perso)
        except Exception:
            col_imposee = None

    while faits < n_:
        entete = "  ·  ".join(t for t in ((nom_evenement or "").strip(), (date_lieu or "").strip()) if t)
        if entete:
            c.setFillColor(NOIR); c.setFont("Helvetica-Bold", 7)
            c.drawCentredString(PAGE_W / 2.0, PAGE_H - DECAL_Y / 2.0 - 2.5, entete)
        c.setFillColor(colors.Color(0.5, 0.5, 0.5)); c.setFont("Helvetica", 6)
        c.drawRightString(PAGE_W - DECAL_X, DECAL_Y / 2.0 - 2, "page %d" % no_page)

        c.saveState()
        c.translate(DECAL_X, DECAL_Y); c.scale(ECHELLE, ECHELLE)
        for idx in range(CARTES_PAGE):
            if faits >= n_:
                break
            ox = (idx % COLS) * CELL_W
            oy = (RANGS - 1 - idx // COLS) * CELL_H
            col = (col_imposee or colors.HexColor(RAINBOW[serie % len(RAINBOW)])) if couleur else NOIR
            _billet(c, ox, oy, serie, _numeros(rng), col)
            serie += 1
            faits += 1
        c.setStrokeColor(colors.Color(0.5, 0.5, 0.5)); c.setLineWidth(0.3); c.setDash(2, 2)
        for i in (1, 2):
            c.line(i * CELL_W, 0, i * CELL_W, RANGS * CELL_H)
        for j in (1, 2, 3):
            c.line(0, j * CELL_H, COLS * CELL_W, j * CELL_H)
        c.restoreState()
        c.showPage()
        no_page += 1
    c.save()
    buf.seek(0)
    return buf


if __name__ == "__main__":
    open("test_salute.pdf", "wb").write(generer_pdf(nb_cartes=12, couleur=False).read())
    print("SALUTE genere")
