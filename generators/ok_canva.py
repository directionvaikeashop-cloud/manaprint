# -*- coding: utf-8 -*-
"""MANAPRINT — OK · 6 boules · maquette Canva de Maeva (27/11/2026, « ok_canva_16_A4 »).
Reprise TELLE QUELLE : 16 cartons / feuille A4 PORTRAIT (4 x 4), traits de coupe en pointillés.
Chaque carton : le titre OK avec rayons et étoiles, la main qui fait OK (dessins Canva posés en
pochoir : en couleur, MANAPRINT les repeint avec les cases, les chiffres restent noirs),
les 6 cases B · G · O · G · O · I, le N°.
RÈGLE (celle d'OK, inchangée) : B 1-15 en haut · G 46-60 ×2 à gauche · O 61-75 ×2 à droite
   (dans l'ordre) · I 16-30 en bas.   Crieur : 1-30 et 46-75 (le 31-45 n'existe pas).
Chiffres Times 30 pt noirs, comme sur la maquette.
Le tout est réduit pour garder 6 mm de marge d'impression (Konica / Sharp)."""

import io, random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

try:
    from generators import canva_masque as _masque
except Exception:
    import canva_masque as _masque

PAGE_W, PAGE_H = A4
COLS, RANGS = 4, 4
CARTES_PAGE = COLS * RANGS                # 16
CELL_W, CELL_H = 148.8189, 210.4724
NOIR = colors.black
POLICE_NUM = "Times-Roman"
# (centre x, ligne de base, taille) : B 1-15 · G 46-60 · O 61-75 · G 46-60 · O 61-75 · I 16-30
CASES = [(74.409, 132.541, 30), (31.181, 106.462, 30), (117.638, 106.462, 30),
         (31.181, 60.541, 30), (117.638, 60.541, 30), (74.409, 19.155, 30)]
ORIGINE_Y = 631.4173        # le dessin de la maquette est relevé dans sa case du haut à gauche
_IMGS = [(23.38583, 784.1586, 102.0472, 52.6288), (50.88189, 698.2402, 45.92126, 52.02363)]

MARGE_SURE = 6 * 72 / 25.4
ECHELLE = min((PAGE_W - 2 * MARGE_SURE) / PAGE_W, (PAGE_H - 2 * MARGE_SURE) / PAGE_H)
DECAL_X = (PAGE_W - PAGE_W * ECHELLE) / 2.0
DECAL_Y = (PAGE_H - PAGE_H * ECHELLE) / 2.0
_DEJA = set()


def _numeros(rng):
    t = None
    for _ in range(500):
        g = sorted(rng.sample(range(46, 61), 2)); o = sorted(rng.sample(range(61, 76), 2))
        t = (rng.randint(1, 15), g[0], o[0], g[1], o[1], rng.randint(16, 30))
        if t not in _DEJA:
            break
    _DEJA.add(t)
    return t


def _txt(c, s, x, y, police, taille, col, centre=False):
    w = c.stringWidth(s, police, taille)
    t = c.beginText(x - w / 2.0 if centre else x, y); t.setFont(police, taille)
    t.setFillColor(col); t.textOut(s)
    c.drawText(t)


def _en_teinte():
    import sys
    for nom in ("app", "__main__"):
        m = sys.modules.get(nom)
        e = getattr(m, "_TEINTE_ETAT", None) if m else None
        if e is not None and getattr(e, "canva", False):
            return True
    return False


def _modele(c):
    if getattr(c, "_ok_modele", False):
        return
    import base64
    d = _DESSIN
    if _en_teinte():          # version couleur : les bulles grises prennent aussi la couleur du billet
        d = d.replace(".15 G", "0 G")
    for k, v in (("{HB}", "Helvetica-Bold"), ("{H}", "Helvetica")):
        d = d.replace(k, c._doc.getInternalFontName(v))
    c.beginForm("OK_CANVA", 0, 0, CELL_W, CELL_H)
    c._code.append("q\n0 g\n0 G\n1 0 0 1 0 %.4f cm" % -ORIGINE_Y)
    morceaux = d
    for i in range(len(_IMGS)):
        morceaux = morceaux.replace("@IMG%d@" % i, "\x00%d\x00" % i)
    for j, part in enumerate(morceaux.split("\x00")):
        if j % 2 == 1:
            i = int(part); x, y, w, h = _IMGS[i]
            _masque.poser(c, "OK_IMG_%d" % i, base64.b64decode(_PNG[i]), x, y, w, h)
        elif part:
            c._code.append(part)
    c._code.append("Q")
    c.endForm()
    c._ok_modele = True


def _billet(c, ox, oy, serie, nums, col):
    _modele(c)
    c.saveState()
    c.translate(ox, oy)
    c.doForm("OK_CANVA")
    _txt(c, "N\u00b0 %06d" % serie, 8.503937, 200.5512, "Helvetica", 4.8, colors.Color(.25, .25, .25))
    for (x, y, t), n in zip(CASES, nums):
        _txt(c, str(n), x, y, POLICE_NUM, t, col, centre=True)
    c.restoreState()


def generer_pdf(nb_cartes=None, nb_tickets=None, serie_start=1, theme="", couleur=True,
                nom_evenement="", titre_jeu="", couleur_perso="", date_lieu="",
                telephone="", page_start=1, evenement_id="", style="", motif="", **_ig):
    n_ = nb_cartes if nb_cartes is not None else nb_tickets
    n_ = max(1, int(n_ if n_ else CARTES_PAGE))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    c.setTitle("OK · 6 boules")
    rng = random.Random(int(serie_start) * 100003 + 2716)
    _DEJA.clear()
    serie = int(serie_start)
    faits = 0
    try:
        no_page = max(1, int(page_start))
    except Exception:
        no_page = 1
    while faits < n_:
        c.setFillColor(colors.Color(0.5, 0.5, 0.5)); c.setFont("Helvetica", 7)
        c.drawRightString(PAGE_W - DECAL_X, PAGE_H - DECAL_Y / 2.0 - 2.5, "page %d" % no_page)
        entete = "  ·  ".join(t for t in ((nom_evenement or "").strip(), (date_lieu or "").strip()) if t)
        if entete:
            c.setFillColor(NOIR); c.setFont("Helvetica-Bold", 7)
            c.drawCentredString(PAGE_W / 2.0, PAGE_H - DECAL_Y / 2.0 - 2.5, entete)
        c.saveState()
        c.translate(DECAL_X, DECAL_Y); c.scale(ECHELLE, ECHELLE)
        for idx in range(CARTES_PAGE):
            if faits >= n_:
                break
            ox = (idx % COLS) * CELL_W
            oy = (RANGS - 1 - idx // COLS) * CELL_H
            _billet(c, ox, oy, serie, _numeros(rng), NOIR)
            serie += 1
            faits += 1
        c.setStrokeColor(colors.Color(0.5, 0.5, 0.5)); c.setLineWidth(0.3); c.setDash(2, 2)
        for i in range(1, COLS):
            c.line(i * CELL_W, 0, i * CELL_W, RANGS * CELL_H)
        for j in range(1, RANGS):
            c.line(0, j * CELL_H, COLS * CELL_W, j * CELL_H)
        c.restoreState()
        c.showPage()
        no_page += 1
    c.save()
    buf.seek(0)
    return buf


_DESSIN = '.25 G\n.9 w\nn\n7.937008 633.685 m\n140.8819 633.685 l\n144.0159 633.685 146.5512 636.2203 146.5512 639.3543 c\n146.5512 833.9528 l\n146.5512 837.0867 144.0159 839.622 140.8819 839.622 c\n7.937008 839.622 l\n4.803024 839.622 2.267717 837.0867 2.267717 833.9528 c\n2.267717 639.3543 l\n2.267717 636.2203 4.803024 633.685 7.937008 633.685 c\nh\nS\n@IMG0@\n@IMG1@\n.25 g\n.15 G\n1 w\n1 g\nn\n59.38583 755.1496 m\n89.43307 755.1496 l\n92.88045 755.1496 95.66929 757.9384 95.66929 761.3858 c\n95.66929 786.3307 l\n95.66929 789.7781 92.88045 792.5669 89.43307 792.5669 c\n59.38583 792.5669 l\n55.93844 792.5669 53.14961 789.7781 53.14961 786.3307 c\n53.14961 761.3858 l\n53.14961 757.9384 55.93844 755.1496 59.38583 755.1496 c\nh\nB*\n0 g\n.2 g\nBT 1 0 0 1 55.98425 785.7638 Tm /{HB} 4.6 Tf 5.52 TL (B) Tj T* ET\n.15 G\n1 w\n1 g\nn\n15.30709 727.937 m\n47.05512 727.937 l\n50.5025 727.937 53.29134 730.7258 53.29134 734.1732 c\n53.29134 761.3858 l\n53.29134 764.8332 50.5025 767.622 47.05512 767.622 c\n15.30709 767.622 l\n11.8597 767.622 9.070866 764.8332 9.070866 761.3858 c\n9.070866 734.1732 l\n9.070866 730.7258 11.8597 727.937 15.30709 727.937 c\nh\nB*\n0 g\n.2 g\nBT 1 0 0 1 11.90551 760.8189 Tm /{HB} 4.6 Tf 5.52 TL (G) Tj T* ET\n.15 G\n1 w\n1 g\nn\n101.7638 727.937 m\n133.5118 727.937 l\n136.9592 727.937 139.748 730.7258 139.748 734.1732 c\n139.748 761.3858 l\n139.748 764.8332 136.9592 767.622 133.5118 767.622 c\n101.7638 767.622 l\n98.3164 767.622 95.52756 764.8332 95.52756 761.3858 c\n95.52756 734.1732 l\n95.52756 730.7258 98.3164 727.937 101.7638 727.937 c\nh\nB*\n0 g\n.2 g\nBT 1 0 0 1 98.3622 760.8189 Tm /{HB} 4.6 Tf 5.52 TL (O) Tj T* ET\n.15 G\n1 w\n1 g\nn\n15.30709 682.0157 m\n47.05512 682.0157 l\n50.5025 682.0157 53.29134 684.8046 53.29134 688.252 c\n53.29134 715.4646 l\n53.29134 718.9119 50.5025 721.7008 47.05512 721.7008 c\n15.30709 721.7008 l\n11.8597 721.7008 9.070866 718.9119 9.070866 715.4646 c\n9.070866 688.252 l\n9.070866 684.8046 11.8597 682.0157 15.30709 682.0157 c\nh\nB*\n0 g\n.2 g\nBT 1 0 0 1 11.90551 714.8976 Tm /{HB} 4.6 Tf 5.52 TL (G) Tj T* ET\n.15 G\n1 w\n1 g\nn\n101.7638 682.0157 m\n133.5118 682.0157 l\n136.9592 682.0157 139.748 684.8046 139.748 688.252 c\n139.748 715.4646 l\n139.748 718.9119 136.9592 721.7008 133.5118 721.7008 c\n101.7638 721.7008 l\n98.3164 721.7008 95.52756 718.9119 95.52756 715.4646 c\n95.52756 688.252 l\n95.52756 684.8046 98.3164 682.0157 101.7638 682.0157 c\nh\nB*\n0 g\n.2 g\nBT 1 0 0 1 98.3622 714.8976 Tm /{HB} 4.6 Tf 5.52 TL (O) Tj T* ET\n.15 G\n1 w\n1 g\nn\n40.96063 641.7638 m\n107.8583 641.7638 l\n111.3057 641.7638 114.0945 644.5526 114.0945 648 c\n114.0945 672.9449 l\n114.0945 676.3923 111.3057 679.1811 107.8583 679.1811 c\n40.96063 679.1811 l\n37.51325 679.1811 34.72441 676.3923 34.72441 672.9449 c\n34.72441 648 l\n34.72441 644.5526 37.51325 641.7638 40.96063 641.7638 c\nh\nB*\n0 g\n.2 g\nBT 1 0 0 1 37.55906 672.378 Tm /{HB} 4.6 Tf 5.52 TL (I) Tj T* ET'
_PNG = ['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']
