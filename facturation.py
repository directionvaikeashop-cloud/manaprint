# -*- coding: utf-8 -*-
"""MANA DEVIS — DEVIS & FACTURATION (22/11/2026, idée de Maeva : « et si on
créait nous-mêmes notre outil de devis et facturation »).

Remplace Zervant, et se branche sur la LIVRAISON NUMÉRIQUE :

  ÉQUIPE  — manaprint.app/facturation   (même code d'accès que /livraison)
     · 2 entreprises : EI TUKEA IMPORT et 2KEA & Associé (réglages modifiables)
     · devis -> « Transformer en facture » en un clic
     · TVA Polynésie : 16 % produits, 13 % services, 5 % taux réduit, 0 %
     · numéros qui se suivent sans trou, par entreprise et par année
       (FA-2K-2026-0001…), attribués au moment où on ÉMET — un brouillon
       n'a pas de numéro, une facture émise ne se modifie plus (on fait un avoir)
     · PDF propre avec toutes les mentions, envoi par email (PDF joint) ou WhatsApp
     · « Payée » à la main (espèces, virement, chèque) OU paiement par carte
       depuis le lien du client (Stripe, le même compte que MANAPRINT)

  CLIENT  — manaprint.app/f/<code>
     · voit son devis / sa facture, télécharge le PDF
     · devis : bouton « J'accepte ce devis »
     · facture : bouton « Payer par carte »

  ⭐ Une facture PAYÉE (carte ou à la main) part TOUTE SEULE dans
     « À préparer » de la Livraison numérique, avec ses articles.
"""
import io
import os
import re
import csv
import json
import secrets
import sqlite3
from datetime import datetime, timedelta
from contextlib import contextmanager

from flask import (Blueprint, jsonify, request, session, render_template,
                   send_file, abort, redirect, Response)

import livraison as _liv

bp = Blueprint("facturation", __name__)

DB_PATH = _liv.DB_PATH
DOSSIER = os.path.join(os.path.dirname(os.path.abspath(DB_PATH)), "facturation")

TAUX_TVA = [16, 13, 5, 0]          # Polynésie française (DICP)
LIB_TAUX = {16: "16 % — produits", 13: "13 % — services", 5: "5 % — taux réduit", 0: "0 % — exonéré"}

ENTITES_DEFAUT = {
    "2K": {"nom": "2KEA & Associé", "adresse": "Papeete, Tahiti — Polynésie française",
           "tahiti": "", "rcs": "", "tel": "89 22 23 05", "email": "", "banque": "",
           "pied": "Merci de votre confiance — Māuruuru !", "couleur": "#0f6b66"},
    "TI": {"nom": "EI TUKEA IMPORT", "adresse": "Papeete, Tahiti — Polynésie française",
           "tahiti": "", "rcs": "", "tel": "89 22 23 05", "email": "", "banque": "",
           "pied": "Merci de votre confiance — Māuruuru !", "couleur": "#0a4a47"},
}
PREFIXE = {"devis": "DE", "facture": "FA", "avoir": "AV"}
LIB_TYPE = {"devis": "Devis", "facture": "Facture", "avoir": "Avoir"}
LIB_STATUT = {
    "brouillon": "Brouillon", "envoye": "Envoyé", "accepte": "Accepté", "refuse": "Refusé",
    "facture": "Facturé", "emise": "À encaisser", "emis": "Émis", "payee": "Payée", "annulee": "Annulée",
}
MODES = {"carte": "Carte bancaire (en ligne)", "especes": "Espèces", "virement": "Virement",
         "cheque": "Chèque", "tpe": "Carte au comptoir", "autre": "Autre"}


def _tahiti():
    return datetime.utcnow() - timedelta(hours=10)


def _aujourdhui():
    return _tahiti().strftime("%Y-%m-%d")


def _fr(d):
    """2026-11-22 -> 22/11/2026"""
    try:
        return datetime.strptime(d, "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        return d or ""


def xpf(n):
    """12345 -> « 12 345 F »"""
    try:
        n = int(round(float(n)))
    except Exception:
        n = 0
    s = "{:,}".format(abs(n)).replace(",", " ")
    return ("-" if n < 0 else "") + s + " F"


@contextmanager
def _db():
    conn = sqlite3.connect(DB_PATH, timeout=30, isolation_level=None)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA busy_timeout=30000")
    except Exception:
        pass
    try:
        conn.execute("BEGIN IMMEDIATE")
        yield conn
        conn.execute("COMMIT")
    except Exception:
        try:
            conn.execute("ROLLBACK")
        except Exception:
            pass
        raise
    finally:
        conn.close()


def init_tables():
    with _db() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS fac_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE, type TEXT, entite TEXT, numero TEXT, statut TEXT,
            date TEXT, echeance TEXT, objet TEXT,
            client TEXT, adresse TEXT, tahiti_client TEXT, telephone TEXT, email TEXT, ile TEXT,
            saisie TEXT DEFAULT 'ttc', notes TEXT, conditions TEXT,
            total_ht INTEGER DEFAULT 0, total_tva INTEGER DEFAULT 0, total_ttc INTEGER DEFAULT 0,
            a_livrer INTEGER DEFAULT 1, livraison_id INTEGER,
            origine_id INTEGER, lie_id INTEGER,
            paye_le TEXT, mode_paiement TEXT, stripe_session TEXT,
            cree_le TEXT, cree_par TEXT, emis_le TEXT, emis_par TEXT, maj_le TEXT,
            vu_le TEXT, accepte_le TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS fac_lignes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER, ordre INTEGER, designation TEXT,
            qte REAL, prix INTEGER, taux INTEGER)""")
        c.execute("""CREATE TABLE IF NOT EXISTS fac_compteurs (
            entite TEXT, type TEXT, annee TEXT, dernier INTEGER,
            PRIMARY KEY (entite, type, annee))""")
        c.execute("""CREATE TABLE IF NOT EXISTS fac_entites (
            code TEXT PRIMARY KEY, donnees TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS fac_journal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER, le TEXT, qui TEXT, quoi TEXT)""")
        for k, v in ENTITES_DEFAUT.items():
            c.execute("INSERT OR IGNORE INTO fac_entites (code, donnees) VALUES (?,?)",
                      (k, json.dumps(v, ensure_ascii=False)))
    os.makedirs(DOSSIER, exist_ok=True)


try:
    init_tables()
except Exception as _e:
    print("[FACTURATION] tables :", repr(_e))


# ── outils ────────────────────────────────────────────────────────────────
_equipe_requise = _liv._equipe_requise
_qui = _liv._qui


def _entites(c):
    out = {}
    for r in c.execute("SELECT code, donnees FROM fac_entites"):
        d = dict(ENTITES_DEFAUT.get(r["code"], {}))
        try:
            d.update(json.loads(r["donnees"] or "{}"))
        except Exception:
            pass
        d["code"] = r["code"]
        d["logo"] = os.path.exists(os.path.join(DOSSIER, "logo_%s.png" % r["code"]))
        out[r["code"]] = d
    return out


def _journal(c, did, quoi):
    try:
        qui = _qui()
    except Exception:
        qui = "Client"
    c.execute("INSERT INTO fac_journal (document_id, le, qui, quoi) VALUES (?,?,?,?)",
              (did, _liv._maintenant(), qui, quoi))
    c.execute("UPDATE fac_documents SET maj_le=? WHERE id=?", (_liv._maintenant(), did))


def _calcul(lignes, saisie):
    """Totaux par taux. XPF = sans centimes.
    saisie 'ht'  : prix saisis HT  -> TVA = HT x taux, arrondie par taux
    saisie 'ttc' : prix saisis TTC -> HT = TTC / (1 + taux), TVA = TTC - HT"""
    par_taux = {}
    for l in lignes:
        t = int(l.get("taux") or 0)
        mt = int(round(float(l.get("qte") or 0) * int(l.get("prix") or 0)))
        par_taux[t] = par_taux.get(t, 0) + mt
    ventil = []
    for t in sorted(par_taux, reverse=True):
        base = par_taux[t]
        if saisie == "ht":
            ht, tva = base, int(round(base * t / 100.0))
        else:
            ht = int(round(base / (1 + t / 100.0)))
            tva = base - ht
        ventil.append({"taux": t, "ht": ht, "tva": tva, "ttc": ht + tva})
    return {"ventilation": ventil,
            "ht": sum(v["ht"] for v in ventil),
            "tva": sum(v["tva"] for v in ventil),
            "ttc": sum(v["ttc"] for v in ventil)}


def _lien(code, hote=None):
    try:
        h = hote or request.host
    except Exception:
        h = "manaprint.app"
    sch = "http" if h.startswith(("localhost", "127.")) else "https"
    return "%s://%s/f/%s" % (sch, h, code)


def _doc(c, did, pour_client=False, hote=None):
    r = c.execute("SELECT * FROM fac_documents WHERE id=?", (did,)).fetchone()
    if not r:
        return None
    d = dict(r)
    d["lignes"] = [dict(l) for l in c.execute(
        "SELECT * FROM fac_lignes WHERE document_id=? ORDER BY ordre, id", (did,))]
    for l in d["lignes"]:
        if l["qte"] is not None and float(l["qte"]).is_integer():
            l["qte"] = int(l["qte"])
        l["montant"] = int(round(float(l["qte"] or 0) * int(l["prix"] or 0)))
    d["calcul"] = _calcul(d["lignes"], d.get("saisie") or "ttc")
    ent = _entites(c).get(d["entite"]) or dict(ENTITES_DEFAUT["2K"], code="2K", logo=False)
    d["vendeur"] = ent
    d["libelle_type"] = LIB_TYPE.get(d["type"], d["type"])
    d["libelle_statut"] = LIB_STATUT.get(d["statut"], d["statut"])
    d["libelle_mode"] = MODES.get(d.get("mode_paiement") or "", d.get("mode_paiement") or "")
    d["lien"] = _lien(d["code"], hote)
    d["date_fr"] = _fr(d.get("date"))
    d["echeance_fr"] = _fr(d.get("echeance"))
    if d.get("lie_id"):
        l2 = c.execute("SELECT id, type, numero, statut FROM fac_documents WHERE id=?",
                       (d["lie_id"],)).fetchone()
        d["lie"] = dict(l2) if l2 else None
    if d.get("origine_id"):
        o = c.execute("SELECT id, type, numero FROM fac_documents WHERE id=?",
                      (d["origine_id"],)).fetchone()
        d["origine"] = dict(o) if o else None
    if d.get("livraison_id"):
        lv = c.execute("SELECT id, statut, code FROM livraisons WHERE id=?", (d["livraison_id"],)).fetchone()
        d["livraison"] = ({"id": lv["id"], "statut": lv["statut"],
                           "libelle": _liv.LIBELLES.get(lv["statut"], lv["statut"]),
                           "code": lv["code"]} if lv else None)
    if pour_client:
        for k in ("notes", "cree_par", "emis_par", "stripe_session", "origine_id", "lie_id",
                  "livraison_id", "a_livrer"):
            d.pop(k, None)
        d["peut_payer"] = (d["type"] == "facture" and d["statut"] == "emise"
                           and bool(_cle_stripe()) and d["calcul"]["ttc"] > 0)
        d["peut_accepter"] = d["type"] == "devis" and d["statut"] == "envoye"
    else:
        d["journal"] = [dict(j) for j in c.execute(
            "SELECT le, qui, quoi FROM fac_journal WHERE document_id=? ORDER BY id DESC LIMIT 60", (did,))]
    return d


def _resume(r):
    d = dict(r)
    d["libelle_statut"] = LIB_STATUT.get(d["statut"], d["statut"])
    d["libelle_type"] = LIB_TYPE.get(d["type"], d["type"])
    d["date_fr"] = _fr(d.get("date"))
    d["echeance_fr"] = _fr(d.get("echeance"))
    d["en_retard"] = bool(d["statut"] == "emise" and d.get("echeance") and d["echeance"] < _aujourdhui())
    return d


def _numero_suivant(c, entite, type_, annee):
    r = c.execute("SELECT dernier FROM fac_compteurs WHERE entite=? AND type=? AND annee=?",
                  (entite, type_, annee)).fetchone()
    n = (r["dernier"] if r else 0) + 1
    c.execute("INSERT OR REPLACE INTO fac_compteurs (entite, type, annee, dernier) VALUES (?,?,?,?)",
              (entite, type_, annee, n))
    return "%s-%s-%s-%04d" % (PREFIXE[type_], entite, annee, n)


def _enregistrer_lignes(c, did, lignes):
    c.execute("DELETE FROM fac_lignes WHERE document_id=?", (did,))
    n = 0
    for i, l in enumerate(lignes[:200]):
        des = (str(l.get("designation") or "")).strip()[:300]
        if not des:
            continue
        try:
            qte = float(str(l.get("qte") or "1").replace(",", "."))
        except Exception:
            qte = 1
        try:
            prix = int(round(float(str(l.get("prix") or "0").replace(" ", "").replace(",", "."))))
        except Exception:
            prix = 0
        try:
            taux = int(l.get("taux"))
        except Exception:
            taux = 16
        if taux not in TAUX_TVA:
            taux = 16
        c.execute("INSERT INTO fac_lignes (document_id, ordre, designation, qte, prix, taux) VALUES (?,?,?,?,?,?)",
                  (did, i, des, qte, prix, taux))
        n += 1
    return n


def _maj_totaux(c, did):
    r = c.execute("SELECT saisie FROM fac_documents WHERE id=?", (did,)).fetchone()
    lignes = [dict(l) for l in c.execute("SELECT qte, prix, taux FROM fac_lignes WHERE document_id=?", (did,))]
    k = _calcul(lignes, (r["saisie"] if r else "ttc") or "ttc")
    c.execute("UPDATE fac_documents SET total_ht=?, total_tva=?, total_ttc=? WHERE id=?",
              (k["ht"], k["tva"], k["ttc"], did))


def _champs_client(d):
    return {
        "client": (d.get("client") or "").strip()[:120],
        "adresse": (d.get("adresse") or "").strip()[:300],
        "tahiti_client": (d.get("tahiti_client") or "").strip()[:30],
        "telephone": (d.get("telephone") or "").strip()[:30],
        "email": (d.get("email") or "").strip()[:120],
        "ile": (d.get("ile") or "").strip()[:60],
    }


# ── la passerelle vers la LIVRAISON NUMÉRIQUE ─────────────────────────────
def _vers_livraison(c, did, qui):
    """Facture payée -> commande « reçue » dans la Livraison numérique (une seule fois)."""
    d = c.execute("SELECT * FROM fac_documents WHERE id=?", (did,)).fetchone()
    if not d or d["type"] != "facture" or not d["a_livrer"] or d["livraison_id"]:
        return None
    lignes = c.execute("SELECT designation, qte FROM fac_lignes WHERE document_id=? ORDER BY ordre, id",
                       (did,)).fetchall()
    lignes = [l for l in lignes if (l["designation"] or "").strip() and float(l["qte"] or 0) > 0]
    if not lignes:
        return None
    code = secrets.token_urlsafe(6).replace("-", "x").replace("_", "y")
    now = _liv._maintenant()
    cur = c.execute(
        "INSERT INTO livraisons (code, ref, client, telephone, email, ile, notes, origine,"
        " statut, cree_le, cree_par, maj_le) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (code, d["numero"] or "", d["client"] or "", d["telephone"] or "", d["email"] or "",
         d["ile"] or "", ("Payée — %s" % MODES.get(d["mode_paiement"] or "", "")).strip(" —"),
         "facture", "recue", now, qui, now))
    lid = cur.lastrowid
    for i, l in enumerate(lignes):
        q = float(l["qte"])
        c.execute("INSERT INTO livraison_articles (livraison_id, ordre, qte, designation) VALUES (?,?,?,?)",
                  (lid, i, str(int(q)) if q.is_integer() else str(q), l["designation"][:160]))
    c.execute("INSERT INTO livraison_journal (livraison_id, le, qui, quoi, type) VALUES (?,?,?,?,?)",
              (lid, now, qui, "💶 Facture %s payée — commande arrivée toute seule (%d articles)"
               % (d["numero"], len(lignes)), "creation"))
    c.execute("UPDATE fac_documents SET livraison_id=? WHERE id=?", (lid, did))
    _journal(c, did, "🚚 Envoyée dans « À préparer » de la Livraison numérique")
    return lid


def _marquer_payee(c, did, mode, qui, le=None):
    d = c.execute("SELECT type, statut FROM fac_documents WHERE id=?", (did,)).fetchone()
    if not d or d["type"] != "facture" or d["statut"] != "emise":
        return False
    c.execute("UPDATE fac_documents SET statut='payee', paye_le=?, mode_paiement=? WHERE id=?",
              (le or _aujourdhui(), mode, did))
    c.execute("INSERT INTO fac_journal (document_id, le, qui, quoi) VALUES (?,?,?,?)",
              (did, _liv._maintenant(), qui, "💶 Payée — %s" % MODES.get(mode, mode)))
    _vers_livraison(c, did, qui)
    return True


# ── 💳 Stripe (même compte que MANAPRINT) ──────────────────────────────────
def _cle_stripe():
    k = os.environ.get("STRIPE_SECRET_KEY", "").strip()
    if not k:
        for _k, _v in os.environ.items():
            if _k.strip() == "STRIPE_SECRET_KEY" and _v.strip():
                return _v.strip()
    return k


def paiement_stripe_confirme(code, session_id=""):
    """Appelé par le webhook Stripe de MANAPRINT ou au retour du client. Idempotent."""
    with _db() as c:
        r = c.execute("SELECT id FROM fac_documents WHERE code=?", (code,)).fetchone()
        if not r:
            return False
        if session_id:
            c.execute("UPDATE fac_documents SET stripe_session=? WHERE id=? AND (stripe_session IS NULL OR stripe_session='')",
                      (session_id, r["id"]))
        ok = _marquer_payee(c, r["id"], "carte", "Paiement en ligne")
    if ok:
        _notifier_equipe(r["id"], "payee")
    return ok


def _verifier_session(code, sid):
    """Demande à Stripe si la session est bien payée (on ne croit jamais l'URL seule)."""
    if not sid or not _cle_stripe():
        return False
    try:
        import stripe
        stripe.api_key = _cle_stripe()
        s = stripe.checkout.Session.retrieve(sid)
        if s["payment_status"] == "paid" and s["metadata"]["facture_code"] == code:
            return paiement_stripe_confirme(code, sid)
    except Exception as e:
        print("[FACTURATION] vérif Stripe :", repr(e))
    return False


def _verifier_en_attente():
    """Rattrape les paiements carte dont le webhook aurait été raté (7 derniers jours)."""
    if not _cle_stripe():
        return
    with _db() as c:
        rows = c.execute("SELECT code, stripe_session FROM fac_documents WHERE type='facture' "
                         "AND statut='emise' AND stripe_session IS NOT NULL AND stripe_session<>'' "
                         "ORDER BY id DESC LIMIT 8").fetchall()
    for r in rows:
        _verifier_session(r["code"], r["stripe_session"])


# ── 📄 le PDF ──────────────────────────────────────────────────────────────
def _couleur(hexa):
    from reportlab.lib.colors import HexColor
    try:
        return HexColor(hexa)
    except Exception:
        return HexColor("#0f6b66")


def _pdf_txt(t):
    import unicodedata
    t = str(t or "")
    for a, b in (("ʻ", "'"), ("’", "'"), ("‘", "'"), ("ʼ", "'")):
        t = t.replace(a, b)
    out = []
    for ch in t:
        try:
            ch.encode("cp1252")
            out.append(ch)
        except UnicodeEncodeError:
            base = unicodedata.normalize("NFD", ch)[0]
            try:
                base.encode("cp1252")
                out.append(base)
            except UnicodeEncodeError:
                out.append("")
    return "".join(out)


def pdf_document(d):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import HexColor, white, black
    from reportlab.pdfbase.pdfmetrics import stringWidth

    W, H = A4
    M = 40
    buf = io.BytesIO()

    class _Toile(canvas.Canvas):
        """Helvetica ne connaît pas les macrons tahitiens (ā, ē…) : on les adoucit."""
        def drawString(self, x, y, t, *a, **k):
            return super().drawString(x, y, _pdf_txt(t), *a, **k)

        def drawRightString(self, x, y, t, *a, **k):
            return super().drawRightString(x, y, _pdf_txt(t), *a, **k)

        def drawCentredString(self, x, y, t, *a, **k):
            return super().drawCentredString(x, y, _pdf_txt(t), *a, **k)

    cv = _Toile(buf, pagesize=A4)
    v = d["vendeur"]
    coul = _couleur(v.get("couleur") or "#0f6b66")
    gris = HexColor("#5b6b68")
    ligne = HexColor("#d5dcda")
    num = d.get("numero") or "BROUILLON"
    titre = d["libelle_type"].upper()
    page = [1]

    def wrap(txt, font, size, larg):
        mots, out, cur = (txt or "").replace("\r", "").split(" "), [], ""
        for para in (txt or "").replace("\r", "").split("\n"):
            cur = ""
            for m in para.split(" "):
                t = (cur + " " + m).strip()
                if stringWidth(t, font, size) <= larg:
                    cur = t
                else:
                    if cur:
                        out.append(cur)
                    cur = m
            out.append(cur)
        return out

    def entete():
        y = H - M
        logo = os.path.join(DOSSIER, "logo_%s.png" % v.get("code"))
        x_txt = M
        if v.get("logo") and os.path.exists(logo):
            try:
                cv.drawImage(logo, M, y - 58, width=110, height=58, preserveAspectRatio=True,
                             anchor="sw", mask="auto")
                x_txt = M
                y_v = y - 70
            except Exception:
                y_v = y
        else:
            y_v = y
        cv.setFillColor(coul)
        cv.setFont("Helvetica-Bold", 16)
        cv.drawString(M, y_v - 4, v.get("nom") or "")
        cv.setFillColor(gris)
        cv.setFont("Helvetica", 9)
        yy = y_v - 18
        infos = [v.get("adresse")]
        if v.get("tahiti"):
            infos.append("N° TAHITI : " + v["tahiti"])
        if v.get("rcs"):
            infos.append("RCS : " + v["rcs"])
        contact = " · ".join([x for x in ("Tél. " + v["tel"] if v.get("tel") else "", v.get("email") or "") if x])
        if contact:
            infos.append(contact)
        for t in infos:
            for l in wrap(t or "", "Helvetica", 9, 260):
                cv.drawString(M, yy, l)
                yy -= 12
        # bloc titre à droite
        cv.setFillColor(coul)
        cv.setFont("Helvetica-Bold", 26)
        cv.drawRightString(W - M, y - 18, titre)
        cv.setFillColor(black)
        cv.setFont("Helvetica-Bold", 11)
        cv.drawRightString(W - M, y - 36, "N° " + num)
        cv.setFont("Helvetica", 10)
        cv.setFillColor(gris)
        yy2 = y - 52
        cv.drawRightString(W - M, yy2, "Date : " + d["date_fr"])
        if d.get("echeance"):
            yy2 -= 14
            cv.drawRightString(W - M, yy2, ("Valable jusqu'au : " if d["type"] == "devis" else "Échéance : ")
                               + d["echeance_fr"])
        if d.get("origine") and d["origine"].get("numero"):
            yy2 -= 14
            cv.drawRightString(W - M, yy2, ("Selon devis " if d["origine"]["type"] == "devis" else "Annule la facture ")
                               + d["origine"]["numero"])
        return min(yy, yy2) - 14

    def pied():
        cv.setStrokeColor(ligne)
        cv.line(M, 52, W - M, 52)
        cv.setFillColor(gris)
        cv.setFont("Helvetica", 8)
        bas = " · ".join(x for x in (v.get("nom"), v.get("adresse"),
                                      ("N° TAHITI " + v["tahiti"]) if v.get("tahiti") else "") if x)
        cv.drawCentredString(W / 2, 40, bas[:150])
        cv.drawRightString(W - M, 28, "%s %s — page %d" % (d["libelle_type"], num, page[0]))

    y = entete()
    # client
    bx, bw = W / 2 + 10, W / 2 - M - 10
    lignes_cli = [d.get("client") or ""]
    for t in (d.get("adresse") or "").split("\n"):
        if t.strip():
            lignes_cli.append(t.strip())
    if d.get("ile"):
        lignes_cli.append(d["ile"])
    if d.get("tahiti_client"):
        lignes_cli.append("N° TAHITI : " + d["tahiti_client"])
    if d.get("telephone"):
        lignes_cli.append("Tél. " + d["telephone"])
    if d.get("email"):
        lignes_cli.append(d["email"])
    hb = 26 + 13 * len(lignes_cli)
    cv.setFillColor(HexColor("#f4f7f6"))
    cv.setStrokeColor(ligne)
    cv.roundRect(bx, y - hb, bw, hb, 8, fill=1, stroke=1)
    cv.setFillColor(gris)
    cv.setFont("Helvetica-Bold", 8)
    cv.drawString(bx + 12, y - 14, "CLIENT")
    cv.setFillColor(black)
    yc = y - 28
    for i, t in enumerate(lignes_cli):
        cv.setFont("Helvetica-Bold" if i == 0 else "Helvetica", 11 if i == 0 else 9.5)
        cv.drawString(bx + 12, yc, t[:60])
        yc -= 13
    y = y - hb - 18
    if d.get("objet"):
        cv.setFont("Helvetica-Bold", 11)
        cv.setFillColor(black)
        for l in wrap("Objet : " + d["objet"], "Helvetica-Bold", 11, W - 2 * M):
            cv.drawString(M, y, l)
            y -= 15
        y -= 4

    # tableau
    cols = [M, M + 270, M + 320, M + 400, M + 440]   # désignation, qté, P.U., TVA, montant
    lib_pu = "P.U. HT" if d.get("saisie") == "ht" else "P.U. TTC"
    lib_mt = "Montant HT" if d.get("saisie") == "ht" else "Montant TTC"

    def entete_tableau(y):
        cv.setFillColor(coul)
        cv.rect(M, y - 18, W - 2 * M, 20, fill=1, stroke=0)
        cv.setFillColor(white)
        cv.setFont("Helvetica-Bold", 9)
        cv.drawString(cols[0] + 6, y - 12, "Désignation")
        cv.drawRightString(cols[2] - 6, y - 12, "Qté")
        cv.drawRightString(cols[3] - 6, y - 12, lib_pu)
        cv.drawRightString(cols[4] - 4, y - 12, "TVA")
        cv.drawRightString(W - M - 6, y - 12, lib_mt)
        return y - 30

    y = entete_tableau(y)
    for l in d["lignes"]:
        des = wrap(l["designation"], "Helvetica", 9.5, cols[1] - cols[0] + 30)
        h = 13 * len(des) + 6
        if y - h < 200:
            pied()
            cv.showPage()
            page[0] += 1
            y = entete_tableau(H - M - 10)
        cv.setFillColor(black)
        cv.setFont("Helvetica", 9.5)
        yl = y
        for t in des:
            cv.drawString(cols[0] + 6, yl, t)
            yl -= 13
        q = l["qte"]
        cv.drawRightString(cols[2] - 6, y, ("%g" % q).replace(".", ","))
        cv.drawRightString(cols[3] - 6, y, xpf(l["prix"]))
        cv.drawRightString(cols[4] - 4, y, "%d %%" % l["taux"])
        cv.setFont("Helvetica-Bold", 9.5)
        cv.drawRightString(W - M - 6, y, xpf(l["montant"]))
        y -= h
        cv.setStrokeColor(ligne)
        cv.line(M, y + 8, W - M, y + 8)

    # totaux
    k = d["calcul"]
    if y < 230:
        pied()
        cv.showPage()
        page[0] += 1
        y = H - M - 20
    y -= 6
    tx = W - M - 230
    cv.setFont("Helvetica", 9)
    cv.setFillColor(gris)
    cv.drawString(M, y, "Détail de la TVA")
    yt = y - 14
    cv.setFont("Helvetica", 8.5)
    cv.drawString(M, yt, "Taux")
    cv.drawRightString(M + 120, yt, "Base HT")
    cv.drawRightString(M + 190, yt, "TVA")
    for vt in k["ventilation"]:
        yt -= 12
        cv.setFillColor(black)
        cv.drawString(M, yt, "%d %%" % vt["taux"])
        cv.drawRightString(M + 120, yt, xpf(vt["ht"]))
        cv.drawRightString(M + 190, yt, xpf(vt["tva"]))

    def ligne_tot(lbl, val, yy, gras=False, grand=False):
        cv.setFillColor(black)
        cv.setFont("Helvetica-Bold" if gras else "Helvetica", 13 if grand else 10)
        cv.drawString(tx, yy, lbl)
        cv.drawRightString(W - M - 6, yy, val)

    ligne_tot("Total HT", xpf(k["ht"]), y)
    ligne_tot("Total TVA", xpf(k["tva"]), y - 16)
    cv.setFillColor(coul)
    cv.roundRect(tx - 8, y - 46, W - M - tx + 8, 24, 6, fill=1, stroke=0)
    cv.setFillColor(white)
    cv.setFont("Helvetica-Bold", 13)
    cv.drawString(tx, y - 38, "Total TTC")
    cv.drawRightString(W - M - 6, y - 38, xpf(k["ttc"]))
    y = min(y - 62, yt - 20)

    # payé / conditions
    if d["statut"] == "payee":
        cv.saveState()
        cv.setFillColor(HexColor("#2e7d32"))
        cv.setStrokeColor(HexColor("#2e7d32"))
        cv.setLineWidth(2)
        cv.roundRect(M, y - 44, 250, 44, 6, fill=0, stroke=1)
        cv.setFont("Helvetica-Bold", 15)
        cv.drawString(M + 12, y - 20, "PAYÉE le %s" % _fr(d.get("paye_le")))
        cv.setFont("Helvetica", 9.5)
        cv.drawString(M + 12, y - 35, d.get("libelle_mode") or "")
        cv.restoreState()
        y -= 58
    if d["statut"] == "annulee":
        cv.setFillColor(HexColor("#c62828"))
        cv.setFont("Helvetica-Bold", 14)
        cv.drawString(M, y - 16, "FACTURE ANNULÉE PAR AVOIR" + ((" " + d["lie"]["numero"]) if d.get("lie") else ""))
        y -= 30
    cv.setFillColor(black)
    blocs = []
    if d.get("conditions"):
        blocs.append(("Conditions", d["conditions"]))
    if d["type"] == "facture" and v.get("banque") and d["statut"] != "payee":
        blocs.append(("Règlement par virement", v["banque"]))
    if d["type"] == "facture" and d["statut"] == "emise":
        blocs.append(("Paiement par carte", "En ligne, en toute sécurité : " + d["lien"]))
    if d["type"] == "devis":
        blocs.append(("Bon pour accord", "Acceptez ce devis en un clic : " + d["lien"]))
    for t, txt in blocs:
        if y < 90:
            pied()
            cv.showPage()
            page[0] += 1
            y = H - M - 20
        cv.setFont("Helvetica-Bold", 9)
        cv.setFillColor(coul)
        cv.drawString(M, y, t)
        y -= 12
        cv.setFillColor(gris)
        cv.setFont("Helvetica", 9)
        for l in wrap(txt, "Helvetica", 9, W - 2 * M):
            cv.drawString(M, y, l)
            y -= 11
        y -= 8
    if v.get("pied"):
        cv.setFillColor(coul)
        cv.setFont("Helvetica-Oblique", 10)
        cv.drawCentredString(W / 2, max(y - 6, 66), v["pied"][:120])
    pied()
    cv.save()
    return buf.getvalue()


# ── ✉️ email avec le PDF joint ─────────────────────────────────────────────
def _envoyer_email(did, qui, hote):
    import threading

    def tache():
        with _db() as c:
            d = _doc(c, did, hote=hote)
        if not d or not _liv._email_valide(d.get("email")):
            return
        if not _liv.SMTP_USER or not _liv.SMTP_PASS:
            ok, msg = False, "boîte d'envoi non configurée (SMTP_USER / SMTP_PASS sur Railway)"
        else:
            try:
                import smtplib
                import html as _h
                from email.message import EmailMessage
                v = d["vendeur"]
                prenom = (d.get("client") or "").strip()
                if d["type"] == "devis":
                    phrase, bouton = "Voici votre devis. Vous pouvez l'accepter en un clic.", "Voir et accepter le devis"
                elif d["statut"] == "payee":
                    phrase, bouton = "Merci pour votre règlement. Voici votre facture acquittée.", "Voir ma facture"
                else:
                    phrase, bouton = "Voici votre facture. Vous pouvez la régler par carte en ligne.", "Voir et payer ma facture"
                sujet = "%s %s — %s (%s)" % (d["libelle_type"], d["numero"] or "", v["nom"], xpf(d["calcul"]["ttc"]))
                html = """<!doctype html><html><body style="margin:0;background:#f6f3ec;font-family:Arial,Helvetica,sans-serif;color:#14211f">
<table width="100%%" cellpadding="0" cellspacing="0" style="background:#f6f3ec"><tr><td align="center" style="padding:24px 12px">
<table width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%%;background:#fff;border-radius:16px;overflow:hidden">
<tr><td style="background:%s;color:#fff;padding:26px 24px">
<div style="font-size:12px;letter-spacing:2px;text-transform:uppercase;opacity:.85">%s</div>
<div style="font-size:26px;font-weight:bold;margin-top:8px">Ia ora na %s 🌺</div>
<div style="opacity:.9;margin-top:4px">%s %s</div></td></tr>
<tr><td style="padding:24px">
<p style="font-size:15px;line-height:1.5">%s</p>
<div style="font-size:30px;font-weight:bold;color:#0a4a47;text-align:center;margin:10px 0">%s</div>
<p style="text-align:center;margin:22px 0"><a href="%s" style="background:%s;color:#fff;text-decoration:none;font-weight:bold;padding:14px 26px;border-radius:12px;display:inline-block">%s</a></p>
<p style="font-size:13px;color:#5b6b68">Le PDF est joint à cet email. Une question ? Répondez simplement, ou appelez-nous au %s.</p>
<p style="font-size:11px;color:#9aa6a3;text-align:center;margin-top:18px">Envoyé avec MANA DEVIS</p>
</td></tr></table></td></tr></table></body></html>""" % (
                    _h.escape(v.get("couleur") or "#0f6b66"), _h.escape(v["nom"]), _h.escape(prenom),
                    _h.escape(d["libelle_type"]), _h.escape(d["numero"] or ""), phrase,
                    xpf(d["calcul"]["ttc"]), d["lien"], _h.escape(v.get("couleur") or "#0f6b66"),
                    bouton, _h.escape(v.get("tel") or _liv.TEL_BOUTIQUE))
                m = EmailMessage()
                m["Subject"] = sujet
                m["From"] = "%s <%s>" % (v["nom"], _liv.SMTP_USER)
                m["To"] = d["email"]
                m["Reply-To"] = v.get("email") or _liv.SMTP_USER
                m.set_content("Ia ora na %s,\n\n%s\n%s : %s\n\n%s" % (
                    prenom, phrase, d["libelle_type"], d["lien"], v["nom"]))
                m.add_alternative(html, subtype="html")
                m.add_attachment(pdf_document(d), maintype="application", subtype="pdf",
                                 filename="%s.pdf" % (d["numero"] or "document"))
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as s_:
                    s_.login(_liv.SMTP_USER, _liv.SMTP_PASS)
                    s_.send_message(m)
                ok, msg = True, ""
            except Exception as e:
                ok, msg = False, str(e)[:160]
        with _db() as c:
            c.execute("INSERT INTO fac_journal (document_id, le, qui, quoi) VALUES (?,?,?,?)",
                      (did, _liv._maintenant(), qui,
                       ("✉️ Envoyé par email à %s (PDF joint)" % d["email"]) if ok else ("⚠️ Email non parti : " + msg)))
        if not ok:
            _notifier_equipe(did, "email_rate", msg)
    threading.Thread(target=tache, daemon=True).start()


# ═══ 🔔 26/11 — L'ÉQUIPE PRÉVENUE PAR EMAIL (demande de Maeva) ═══
#   Un email part tout seul vers Maeva et ses deux vendeuses quand :
#     · un client ACCEPTE un devis en ligne ;
#     · un client PAIE une facture par carte ;
#     · un email à un client n'a PAS pu partir.
#   Adresses changeables sur Railway : variable MANADEVIS_ALERTES
#   (adresses séparées par des virgules). Sans variable : les 3 ci-dessous.
ALERTES_DEFAUT = ["directionvaikeashop@gmail.com",
                  "inanakiparaurahi13@gmail.com",
                  "tuhoe.tumata21@gmail.com"]


def _destinataires_alertes():
    brut = os.environ.get("MANADEVIS_ALERTES", "").strip()
    liste = [a.strip() for a in brut.split(",") if a.strip()] if brut else list(ALERTES_DEFAUT)
    return [a for a in liste if _liv._email_valide(a)]


def _notifier_equipe(did, evenement, detail=""):
    """🔔 Prévient l'équipe par email, sans jamais bloquer ni casser l'action du client."""
    import threading

    def tache():
        try:
            dest = _destinataires_alertes()
            if not dest:
                return
            with _db() as c:
                d = _doc(c, did)
            if not d:
                return
            client = (d.get("client") or "Client").strip()
            ref = "%s %s" % (d["libelle_type"], d.get("numero") or "")
            montant = xpf(d["calcul"]["ttc"])
            if evenement == "accepte":
                sujet = "✅ Devis accepté — %s — %s (%s)" % (d.get("numero") or "", client, montant)
                texte = "%s a accepté le devis %s en ligne (%s).\nPensez à le transformer en facture." % (
                    client, d.get("numero") or "", montant)
            elif evenement == "payee":
                sujet = "💳 Facture payée par carte — %s — %s (%s)" % (d.get("numero") or "", client, montant)
                texte = "%s a réglé la facture %s par carte en ligne (%s)." % (
                    client, d.get("numero") or "", montant)
            else:
                sujet = "⚠️ Email non parti — %s — %s" % (ref.strip(), client)
                texte = ("L'email du %s pour %s n'a pas pu partir.\nRaison : %s\n"
                         "Envoyez-le par WhatsApp ou vérifiez l'adresse du client.") % (
                    ref.strip(), client, detail or "inconnue")
            if not _liv.SMTP_USER or not _liv.SMTP_PASS:
                raise RuntimeError("boîte d'envoi non configurée (SMTP_USER / SMTP_PASS sur Railway)")
            import smtplib
            from email.message import EmailMessage
            m = EmailMessage()
            m["Subject"] = sujet
            m["From"] = "MANA DEVIS <%s>" % _liv.SMTP_USER
            m["To"] = ", ".join(dest)
            m.set_content("Ia ora na l'équipe 🌺\n\n%s\n\nClient : %s\nTéléphone : %s\n"
                          "Montant : %s\n\nOuvrir MANA DEVIS : https://manaprint.app/facturation\n"
                          "Lien client : %s\n\n— MANA DEVIS" % (
                              texte, client, d.get("telephone") or "—", montant, d.get("lien") or ""))
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as s_:
                s_.login(_liv.SMTP_USER, _liv.SMTP_PASS)
                s_.send_message(m)
            quoi = "🔔 Équipe prévenue par email (%d adresses)" % len(dest)
        except Exception as e:
            quoi = "🔔 Alerte équipe non partie : " + str(e)[:140]
        try:
            with _db() as c:
                c.execute("INSERT INTO fac_journal (document_id, le, qui, quoi) VALUES (?,?,?,?)",
                          (did, _liv._maintenant(), "MANA DEVIS", quoi))
        except Exception as e:
            print("[FACTURATION] alerte équipe :", repr(e))
    threading.Thread(target=tache, daemon=True).start()


def _message_wa(d):
    prenom = (d.get("client") or "").strip() or "Bonjour"
    if d["type"] == "devis":
        return "Ia ora na %s 🌺\nVoici votre devis %s (%s) :\n%s\nVous pouvez l'accepter en un clic.\n— %s" % (
            prenom, d["numero"] or "", xpf(d["calcul"]["ttc"]), d["lien"], d["vendeur"]["nom"])
    if d["statut"] == "payee":
        return "Ia ora na %s 🌺\nMerci pour votre règlement ! Votre facture %s acquittée :\n%s\n— %s" % (
            prenom, d["numero"] or "", d["lien"], d["vendeur"]["nom"])
    return "Ia ora na %s 🌺\nVoici votre facture %s (%s).\nPaiement par carte ici : %s\n— %s" % (
        prenom, d["numero"] or "", xpf(d["calcul"]["ttc"]), d["lien"], d["vendeur"]["nom"])


def _pour_equipe(c, did):
    d = _doc(c, did)
    if d:
        d["message_wa"] = _message_wa(d)
        d["wa_client"] = _liv._numero_whatsapp(d.get("telephone"))
    return d


# ── pages ─────────────────────────────────────────────────────────────────
@bp.route("/facturation")
def page_equipe():
    return render_template("facturation.html")


@bp.route("/f/<code>")
def page_client(code):
    sid = request.args.get("session_id")
    if sid:
        _verifier_session(code, sid)
        return redirect("/f/%s?merci=1" % code)
    with _db() as c:
        r = c.execute("SELECT id, statut FROM fac_documents WHERE code=?", (code,)).fetchone()
        if not r or r["statut"] == "brouillon":
            return render_template("facture_client.html", code="", introuvable=True), 404
        c.execute("UPDATE fac_documents SET vu_le=? WHERE id=? AND vu_le IS NULL", (_liv._maintenant(), r["id"]))
    return render_template("facture_client.html", code=code, introuvable=False)


@bp.route("/f/<code>/donnees")
def api_client(code):
    with _db() as c:
        r = c.execute("SELECT id, statut FROM fac_documents WHERE code=?", (code,)).fetchone()
        if not r or r["statut"] == "brouillon":
            return jsonify({"ok": False}), 404
        d = _doc(c, r["id"], pour_client=True)
    d["wa_boutique"] = _liv._numero_whatsapp(d["vendeur"].get("tel") or _liv.TEL_BOUTIQUE)
    resp = jsonify({"ok": True, "document": d})
    resp.headers["Cache-Control"] = "no-store"
    return resp


@bp.route("/f/<code>/pdf")
def pdf_client(code):
    with _db() as c:
        r = c.execute("SELECT id, statut FROM fac_documents WHERE code=?", (code,)).fetchone()
        if not r or r["statut"] == "brouillon":
            abort(404)
        d = _doc(c, r["id"])
    return send_file(io.BytesIO(pdf_document(d)), mimetype="application/pdf",
                     download_name="%s.pdf" % (d["numero"] or "document"),
                     as_attachment=request.args.get("dl") == "1")


@bp.route("/f/<code>/accepter", methods=["POST"])
def accepter(code):
    with _db() as c:
        r = c.execute("SELECT id, type, statut FROM fac_documents WHERE code=?", (code,)).fetchone()
        if not r or r["type"] != "devis" or r["statut"] != "envoye":
            return jsonify({"ok": False, "message": "Ce devis ne peut plus être accepté"}), 400
        c.execute("UPDATE fac_documents SET statut='accepte', accepte_le=? WHERE id=?",
                  (_liv._maintenant(), r["id"]))
        c.execute("INSERT INTO fac_journal (document_id, le, qui, quoi) VALUES (?,?,?,?)",
                  (r["id"], _liv._maintenant(), "Client", "✅ Le client a accepté le devis en ligne"))
    _notifier_equipe(r["id"], "accepte")
    return jsonify({"ok": True})


@bp.route("/f/<code>/payer", methods=["POST"])
def payer(code):
    if not _cle_stripe():
        return jsonify({"ok": False, "message": "Paiement par carte indisponible"}), 400
    with _db() as c:
        r = c.execute("SELECT id FROM fac_documents WHERE code=? AND type='facture' AND statut='emise'",
                      (code,)).fetchone()
        if not r:
            return jsonify({"ok": False, "message": "Cette facture n'est plus à régler"}), 400
        d = _doc(c, r["id"])
    try:
        import stripe
        stripe.api_key = _cle_stripe()
        base = os.environ.get("MANAPRINT_BASE_URL", request.host_url.rstrip("/"))
        kw = dict(
            mode="payment",
            line_items=[{"price_data": {"currency": "xpf", "unit_amount": int(d["calcul"]["ttc"]),
                                        "product_data": {"name": "%s %s — %s" % (
                                            d["libelle_type"], d["numero"], d["vendeur"]["nom"])}},
                         "quantity": 1}],
            success_url=base + "/f/" + code + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=base + "/f/" + code,
            metadata={"facture_code": code, "facture_numero": d["numero"] or ""},
        )
        if _liv._email_valide(d.get("email")):
            kw["customer_email"] = d["email"]
        s = stripe.checkout.Session.create(**kw)
    except Exception as e:
        print("[FACTURATION] Stripe :", repr(e))
        return jsonify({"ok": False, "message": "Le paiement n'a pas pu démarrer, réessayez"}), 500
    with _db() as c:
        c.execute("UPDATE fac_documents SET stripe_session=? WHERE id=?", (s.id, r["id"]))
        c.execute("INSERT INTO fac_journal (document_id, le, qui, quoi) VALUES (?,?,?,?)",
                  (r["id"], _liv._maintenant(), "Client", "💳 Le client a ouvert le paiement par carte"))
    return jsonify({"ok": True, "url": s.url})


# ── API équipe ────────────────────────────────────────────────────────────
@bp.route("/facturation/api/tout")
@_equipe_requise
def api_tout():
    try:
        _verifier_en_attente()
    except Exception as e:
        print("[FACTURATION] rattrapage :", repr(e))
    with _db() as c:
        docs = [_resume(r) for r in c.execute(
            "SELECT id, code, type, entite, numero, statut, date, echeance, client, ile, telephone, "
            "total_ttc, total_ht, paye_le, mode_paiement, livraison_id, vu_le, accepte_le, maj_le "
            "FROM fac_documents ORDER BY id DESC LIMIT 1500")]
        ent = _entites(c)
        mois = _aujourdhui()[:7]
        stats = {}
        for code in ent:
            r1 = c.execute("SELECT COALESCE(SUM(total_ttc),0) FROM fac_documents WHERE entite=? AND type='facture' "
                           "AND statut='payee' AND substr(paye_le,1,7)=?", (code, mois)).fetchone()[0]
            r2 = c.execute("SELECT COALESCE(SUM(total_ttc),0), COUNT(*) FROM fac_documents WHERE entite=? "
                           "AND type='facture' AND statut='emise'", (code,)).fetchone()
            stats[code] = {"encaisse_mois": r1, "a_encaisser": r2[0], "nb_a_encaisser": r2[1]}
        favoris = [dict(r) for r in c.execute(
            "SELECT l.designation, l.prix, l.taux, COUNT(*) n FROM fac_lignes l JOIN fac_documents d ON d.id=l.document_id "
            "WHERE d.type<>'avoir' AND l.prix>0 GROUP BY l.designation, l.prix, l.taux "
            "ORDER BY n DESC, MAX(l.id) DESC LIMIT 300")]
        clients = [dict(r) for r in c.execute(
            "SELECT client, adresse, tahiti_client, telephone, email, ile, MAX(id) dernier FROM fac_documents "
            "WHERE client<>'' GROUP BY lower(client) ORDER BY dernier DESC LIMIT 800")]
    return jsonify({"ok": True, "documents": docs, "entites": ent, "stats": stats, "favoris": favoris,
                    "clients": clients, "taux": [{"taux": t, "libelle": LIB_TAUX[t]} for t in TAUX_TVA],
                    "modes": MODES, "stripe": bool(_cle_stripe()), "prenom": _qui(), "aujourdhui": _aujourdhui()})


# ── 🛒 catalogue de la boutique (jeux, tampons, prix membre / non-membre / pro) ──
_CATALOGUE = {"le": None, "data": None}


@bp.route("/facturation/api/catalogue")
@_equipe_requise
def api_catalogue():
    """Articles et prix de cheztukea.app (caisse), lus avec la clé partagée MANAPRINT_IMPORT_CLE.
    Gardés 5 minutes en mémoire."""
    import time
    import urllib.request
    if _CATALOGUE["data"] and time.time() - _CATALOGUE["le"] < 300 and not request.args.get("frais"):
        return jsonify(_CATALOGUE["data"])
    cle = os.environ.get("MANAPRINT_IMPORT_CLE", "").strip()
    url = os.environ.get("CHEZTUKEA_CATALOGUE_URL", "").strip() or "https://cheztukea.app/api/catalogue-prive"
    if not cle:
        return jsonify({"ok": False, "message": "Clé MANAPRINT_IMPORT_CLE absente sur Railway"}), 400
    try:
        req = urllib.request.Request(url, headers={"X-Cle-Boutique": cle, "User-Agent": "MANADEVIS/1.0"})
        with urllib.request.urlopen(req, timeout=20) as rep:
            data = json.loads(rep.read().decode("utf-8"))
    except Exception as e:
        if _CATALOGUE["data"]:
            return jsonify(_CATALOGUE["data"])
        return jsonify({"ok": False, "message": "Catalogue de la boutique injoignable : %s" % str(e)[:120]}), 502
    if not data.get("ok"):
        return jsonify({"ok": False, "message": data.get("erreur") or "refusé"}), 502
    _CATALOGUE.update(le=time.time(), data=data)
    return jsonify(data)


@bp.route("/facturation/api/documents", methods=["POST"])
@_equipe_requise
def api_creer():
    d = request.get_json(force=True, silent=True) or {}
    type_ = d.get("type") if d.get("type") in ("devis", "facture") else "facture"
    entite = d.get("entite") if d.get("entite") in ENTITES_DEFAUT else "2K"
    with _db() as c:
        code = secrets.token_urlsafe(9).replace("-", "x").replace("_", "y")
        jours = 30 if type_ == "devis" else 15
        cur = c.execute(
            "INSERT INTO fac_documents (code, type, entite, statut, date, echeance, saisie, a_livrer, cree_le, cree_par, maj_le)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (code, type_, entite, "brouillon", _aujourdhui(),
             (_tahiti() + timedelta(days=jours)).strftime("%Y-%m-%d"),
             "ht" if d.get("saisie") == "ht" else "ttc", 1, _liv._maintenant(), _qui(), _liv._maintenant()))
        did = cur.lastrowid
        _journal(c, did, "%s créé (brouillon)" % LIB_TYPE[type_])
        out = _pour_equipe(c, did)
    return jsonify({"ok": True, "document": out})


@bp.route("/facturation/api/documents/<int:did>")
@_equipe_requise
def api_detail(did):
    with _db() as c:
        d = _pour_equipe(c, did)
    if not d:
        return jsonify({"ok": False, "message": "Introuvable"}), 404
    return jsonify({"ok": True, "document": d})


@bp.route("/facturation/api/documents/<int:did>", methods=["PATCH"])
@_equipe_requise
def api_modifier(did):
    d = request.get_json(force=True, silent=True) or {}
    with _db() as c:
        r = c.execute("SELECT * FROM fac_documents WHERE id=?", (did,)).fetchone()
        if not r:
            return jsonify({"ok": False}), 404
        brouillon = r["statut"] == "brouillon"
        champs = {}
        if brouillon:
            champs.update({k: v for k, v in _champs_client(d).items() if k in d})
            for k in ("objet", "conditions"):
                if k in d:
                    champs[k] = (d.get(k) or "").strip()[:1500]
            for k in ("date", "echeance"):
                if k in d and (d[k] == "" or re.match(r"^\d{4}-\d{2}-\d{2}$", d[k] or "")):
                    champs[k] = d[k]
            if d.get("entite") in ENTITES_DEFAUT:
                champs["entite"] = d["entite"]
            if d.get("saisie") in ("ht", "ttc"):
                champs["saisie"] = d["saisie"]
        # toujours modifiables (n'apparaissent pas sur la facture)
        if "notes" in d:
            champs["notes"] = (d.get("notes") or "").strip()[:1500]
        if "a_livrer" in d:
            champs["a_livrer"] = 1 if d["a_livrer"] else 0
        if not brouillon and set(d) - {"notes", "a_livrer", "lignes"}:
            pass  # on ignore en silence : un document émis ne change plus
        if champs:
            c.execute("UPDATE fac_documents SET %s WHERE id=?" % ", ".join("%s=?" % k for k in champs),
                      list(champs.values()) + [did])
        if brouillon and isinstance(d.get("lignes"), list):
            _enregistrer_lignes(c, did, d["lignes"])
        _maj_totaux(c, did)
        c.execute("UPDATE fac_documents SET maj_le=? WHERE id=?", (_liv._maintenant(), did))
        out = _pour_equipe(c, did)
    return jsonify({"ok": True, "document": out})


@bp.route("/facturation/api/documents/<int:did>", methods=["DELETE"])
@_equipe_requise
def api_supprimer(did):
    with _db() as c:
        r = c.execute("SELECT statut FROM fac_documents WHERE id=?", (did,)).fetchone()
        if not r or r["statut"] != "brouillon":
            return jsonify({"ok": False, "message": "Seul un brouillon se supprime. Une facture émise s'annule par un avoir."}), 400
        c.execute("DELETE FROM fac_lignes WHERE document_id=?", (did,))
        c.execute("DELETE FROM fac_journal WHERE document_id=?", (did,))
        c.execute("DELETE FROM fac_documents WHERE id=?", (did,))
    return jsonify({"ok": True})


@bp.route("/facturation/api/documents/<int:did>/action", methods=["POST"])
@_equipe_requise
def api_action(did):
    d = request.get_json(force=True, silent=True) or {}
    act = d.get("action")
    hote = request.host
    envoyer_mail = False
    nouveau = None
    with _db() as c:
        r = c.execute("SELECT * FROM fac_documents WHERE id=?", (did,)).fetchone()
        if not r:
            return jsonify({"ok": False}), 404
        if act == "emettre":
            if r["statut"] != "brouillon":
                return jsonify({"ok": False, "message": "Déjà émis"}), 400
            if not (r["client"] or "").strip():
                return jsonify({"ok": False, "message": "Il manque le nom du client"}), 400
            n = c.execute("SELECT COUNT(*) FROM fac_lignes WHERE document_id=?", (did,)).fetchone()[0]
            if not n:
                return jsonify({"ok": False, "message": "Ajoute au moins une ligne"}), 400
            date = r["date"] or _aujourdhui()
            num = _numero_suivant(c, r["entite"], r["type"], date[:4])
            st = "envoye" if r["type"] == "devis" else "emise"
            c.execute("UPDATE fac_documents SET numero=?, statut=?, date=?, emis_le=?, emis_par=? WHERE id=?",
                      (num, st, date, _liv._maintenant(), _qui(), did))
            _maj_totaux(c, did)
            _journal(c, did, "📄 Émis sous le n° %s" % num)
            envoyer_mail = bool(d.get("email")) and _liv._email_valide(r["email"])
        elif act == "payee":
            mode = d.get("mode") if d.get("mode") in MODES else "especes"
            le = d.get("le") if re.match(r"^\d{4}-\d{2}-\d{2}$", d.get("le") or "") else None
            if not _marquer_payee(c, did, mode, _qui(), le):
                return jsonify({"ok": False, "message": "Seule une facture émise peut passer payée"}), 400
        elif act == "non_payee":
            if r["statut"] != "payee":
                return jsonify({"ok": False}), 400
            c.execute("UPDATE fac_documents SET statut='emise', paye_le=NULL, mode_paiement=NULL WHERE id=?", (did,))
            _journal(c, did, "↩️ Paiement annulé (remise « à encaisser »)")
        elif act in ("accepte", "refuse"):
            if r["type"] != "devis" or r["statut"] not in ("envoye", "accepte", "refuse"):
                return jsonify({"ok": False}), 400
            c.execute("UPDATE fac_documents SET statut=? WHERE id=?", (act, did))
            _journal(c, did, "Devis marqué « %s »" % LIB_STATUT[act])
        elif act == "transformer":
            if r["type"] != "devis" or r["statut"] == "brouillon":
                return jsonify({"ok": False, "message": "Émets d'abord le devis"}), 400
            nouveau = _copier(c, r, "facture")
            c.execute("UPDATE fac_documents SET statut='facture', lie_id=? WHERE id=?", (nouveau, did))
            _journal(c, did, "➡️ Transformé en facture")
        elif act == "dupliquer":
            nouveau = _copier(c, r, r["type"] if r["type"] != "avoir" else "facture", lier=False)
        elif act == "avoir":
            if r["type"] != "facture" or r["statut"] not in ("emise", "payee"):
                return jsonify({"ok": False, "message": "Seule une facture émise s'annule par un avoir"}), 400
            nouveau = _copier(c, r, "avoir")
            num = _numero_suivant(c, r["entite"], "avoir", _aujourdhui()[:4])
            c.execute("UPDATE fac_documents SET numero=?, statut='emis', date=?, echeance='', emis_le=?, emis_par=? WHERE id=?",
                      (num, _aujourdhui(), _liv._maintenant(), _qui(), nouveau))
            c.execute("UPDATE fac_lignes SET prix=-prix WHERE document_id=?", (nouveau,))
            _maj_totaux(c, nouveau)
            _journal(c, nouveau, "📄 Avoir émis sous le n° %s" % num)
            c.execute("UPDATE fac_documents SET statut='annulee', lie_id=? WHERE id=?", (nouveau, did))
            _journal(c, did, "❌ Annulée par l'avoir %s" % num)
        elif act == "livraison":
            if r["statut"] != "payee":
                return jsonify({"ok": False, "message": "La facture doit être payée"}), 400
            c.execute("UPDATE fac_documents SET a_livrer=1 WHERE id=?", (did,))
            if not _vers_livraison(c, did, _qui()):
                return jsonify({"ok": False, "message": "Déjà dans la Livraison numérique"}), 400
        elif act == "email":
            if not _liv._email_valide(r["email"]):
                return jsonify({"ok": False, "message": "Pas d'email valide pour ce client"}), 400
            if r["statut"] == "brouillon":
                return jsonify({"ok": False, "message": "Émets d'abord le document"}), 400
            envoyer_mail = True
        else:
            return jsonify({"ok": False}), 400
        out = _pour_equipe(c, nouveau or did)
    if envoyer_mail:
        _envoyer_email(did, _qui(), hote)
        out["email_part"] = True
    return jsonify({"ok": True, "document": out})


def _copier(c, r, type_, lier=True):
    code = secrets.token_urlsafe(9).replace("-", "x").replace("_", "y")
    jours = 30 if type_ == "devis" else 15
    cur = c.execute(
        "INSERT INTO fac_documents (code, type, entite, statut, date, echeance, objet, client, adresse, "
        "tahiti_client, telephone, email, ile, saisie, conditions, a_livrer, origine_id, cree_le, cree_par, maj_le)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (code, type_, r["entite"], "brouillon", _aujourdhui(),
         (_tahiti() + timedelta(days=jours)).strftime("%Y-%m-%d"), r["objet"], r["client"], r["adresse"],
         r["tahiti_client"], r["telephone"], r["email"], r["ile"], r["saisie"], r["conditions"],
         r["a_livrer"] if type_ == "facture" else 0, r["id"] if lier else None,
         _liv._maintenant(), _qui(), _liv._maintenant()))
    nid = cur.lastrowid
    for l in c.execute("SELECT * FROM fac_lignes WHERE document_id=? ORDER BY ordre, id", (r["id"],)).fetchall():
        c.execute("INSERT INTO fac_lignes (document_id, ordre, designation, qte, prix, taux) VALUES (?,?,?,?,?,?)",
                  (nid, l["ordre"], l["designation"], l["qte"], l["prix"], l["taux"]))
    _maj_totaux(c, nid)
    _journal(c, nid, ("Créé depuis %s %s" % (LIB_TYPE.get(r["type"], ""), r["numero"] or "")) if lier
             else "Copie de %s" % (r["numero"] or "brouillon"))
    return nid


@bp.route("/facturation/api/documents/<int:did>/pdf")
@_equipe_requise
def api_pdf(did):
    with _db() as c:
        d = _doc(c, did)
    if not d:
        abort(404)
    return send_file(io.BytesIO(pdf_document(d)), mimetype="application/pdf",
                     download_name="%s.pdf" % (d["numero"] or "brouillon"))


@bp.route("/facturation/api/entites", methods=["POST"])
@_equipe_requise
def api_entites():
    d = request.get_json(force=True, silent=True) or {}
    code = d.get("code")
    if code not in ENTITES_DEFAUT:
        return jsonify({"ok": False}), 400
    with _db() as c:
        ent = _entites(c)[code]
        for k in ("nom", "adresse", "tahiti", "rcs", "tel", "email", "banque", "pied", "couleur"):
            if k in d:
                ent[k] = (str(d[k]) or "").strip()[:600]
        ent.pop("logo", None)
        ent.pop("code", None)
        c.execute("UPDATE fac_entites SET donnees=? WHERE code=?", (json.dumps(ent, ensure_ascii=False), code))
        out = _entites(c)
    return jsonify({"ok": True, "entites": out})


@bp.route("/facturation/api/entites/<code>/logo", methods=["POST", "DELETE"])
@_equipe_requise
def api_logo(code):
    if code not in ENTITES_DEFAUT:
        abort(404)
    chemin = os.path.join(DOSSIER, "logo_%s.png" % code)
    if request.method == "DELETE":
        try:
            os.remove(chemin)
        except Exception:
            pass
    else:
        f = request.files.get("logo")
        if not f:
            return jsonify({"ok": False, "message": "Aucune image"}), 400
        from PIL import Image
        im = Image.open(f.stream).convert("RGBA")
        im.thumbnail((800, 400))
        os.makedirs(DOSSIER, exist_ok=True)
        im.save(chemin, "PNG")
    with _db() as c:
        out = _entites(c)
    return jsonify({"ok": True, "entites": out})


@bp.route("/facturation/logo/<code>")
def logo(code):
    chemin = os.path.join(DOSSIER, "logo_%s.png" % code)
    if code not in ENTITES_DEFAUT or not os.path.exists(chemin):
        abort(404)
    return send_file(chemin, mimetype="image/png", max_age=300)


@bp.route("/facturation/api/export.csv")
@_equipe_requise
def api_export():
    """Journal des ventes pour la comptable (Excel l'ouvre directement)."""
    ent = request.args.get("entite") or ""
    de = request.args.get("de") or "0000-00-00"
    a = request.args.get("a") or "9999-99-99"
    out = io.StringIO()
    w = csv.writer(out, delimiter=";")
    w.writerow(["Entreprise", "Type", "Numéro", "Date", "Client", "N° TAHITI client",
                "HT 16%", "TVA 16%", "HT 13%", "TVA 13%", "HT 5%", "TVA 5%", "HT 0%",
                "Total HT", "Total TVA", "Total TTC", "Statut", "Payée le", "Mode"])
    with _db() as c:
        noms = {k: v["nom"] for k, v in _entites(c).items()}
        rows = c.execute("SELECT id FROM fac_documents WHERE type IN ('facture','avoir') AND statut<>'brouillon' "
                         "AND date BETWEEN ? AND ? %s ORDER BY entite, date, numero"
                         % ("AND entite=?" if ent else ""), [de, a] + ([ent] if ent else [])).fetchall()
        for r in rows:
            d = _doc(c, r["id"])
            vt = {x["taux"]: x for x in d["calcul"]["ventilation"]}
            g = lambda t, k: vt.get(t, {}).get(k, 0)
            w.writerow([noms.get(d["entite"], d["entite"]), d["libelle_type"], d["numero"], d["date_fr"],
                        d["client"], d.get("tahiti_client") or "",
                        g(16, "ht"), g(16, "tva"), g(13, "ht"), g(13, "tva"), g(5, "ht"), g(5, "tva"), g(0, "ht"),
                        d["calcul"]["ht"], d["calcul"]["tva"], d["calcul"]["ttc"], d["libelle_statut"],
                        _fr(d.get("paye_le")), d["libelle_mode"]])
    nom = "journal-ventes-%s%s.csv" % (ent + "-" if ent else "", _aujourdhui())
    return Response("\ufeff" + out.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=%s" % nom})
