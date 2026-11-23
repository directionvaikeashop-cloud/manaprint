# -*- coding: utf-8 -*-
"""MANAPRINT — LIVRAISON NUMÉRIQUE (22/11/2026, idée de Maeva).

Le suivi des commandes de 2KEA & Associé / Chez TUKEA, de la préparation au
bateau, en s'inspirant du catalogue numérique :

  ÉQUIPE  — manaprint.app/livraison
     · code d'accès commun + prénom (on sait qui a validé quoi)
     · créer une commande (à la main, ou en COLLANT la commande de la boutique)
     · préparer : chaque article « ✓ Je valide » / « ✗ Je ne valide pas »
     · « Commande préparée » -> notification à l'équipe (écran + son) et au
       client (message WhatsApp tout prêt, avec son lien de suivi)
     · au bateau : photos du bac / du conteneur prises au téléphone
       -> le client les reçoit par son lien

  CLIENT  — manaprint.app/suivi/<code>
     · page à son nom : étapes, articles, photos du bateau, contact
     · elle se met à jour toute seule

Tout est rangé dans la même base que MANAPRINT (tables livraison_*) et les
photos sur le volume persistant, à côté de la base (/data/livraisons_photos).
"""
import io
import os
import re
import json
import secrets
import sqlite3
from datetime import datetime, timedelta
from contextlib import contextmanager
from functools import wraps

from flask import (Blueprint, jsonify, request, session, render_template,
                   send_file, abort, redirect)

bp = Blueprint("livraison", __name__)

DB_PATH = os.environ.get("MANAPRINT_DB", os.path.join(os.path.dirname(os.path.abspath(__file__)), "manaprint.db"))
PHOTOS_DIR = os.path.join(os.path.dirname(os.path.abspath(DB_PATH)), "livraisons_photos")
# 🔑 code d'accès de l'équipe — à changer dans Railway (variable MANAPRINT_LIVRAISON_CODE)
CODE_EQUIPE = os.environ.get("MANAPRINT_LIVRAISON_CODE", "TUKEA-PREPA")
TEL_BOUTIQUE = os.environ.get("MANAPRINT_TEL_BOUTIQUE", "89 22 23 05")
NOM_BOUTIQUE = "2KEA & Associé · Chez TUKEA"

# ✉️ 22/11 (Maeva : « l'option mail du client ») — même boîte d'envoi que MANAPRINT
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")

STATUTS = ["recue", "preparation", "preparee", "bateau", "livree"]
LIBELLES = {
    "recue": "Commande reçue",
    "preparation": "En préparation",
    "preparee": "Commande préparée",
    "bateau": "Déposée au bateau",
    "livree": "Livrée",
}


def _maintenant():
    """Heure de Tahiti (UTC-10), au format ISO court."""
    return (datetime.utcnow() - timedelta(hours=10)).strftime("%d/%m/%Y à %Hh%M")


@contextmanager
def _db():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=30000")
    except Exception:
        pass
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_tables():
    with _db() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS livraisons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE, ref TEXT, client TEXT, telephone TEXT, ile TEXT,
            bateau TEXT, depart TEXT, notes TEXT, origine TEXT,
            statut TEXT DEFAULT 'recue', cree_le TEXT, cree_par TEXT,
            prepare_le TEXT, prepare_par TEXT, bateau_le TEXT, bateau_par TEXT,
            livre_le TEXT, maj_le TEXT, archive INTEGER DEFAULT 0)""")
        _cols = [r[1] for r in c.execute("PRAGMA table_info(livraisons)")]
        if "email" not in _cols:
            c.execute("ALTER TABLE livraisons ADD COLUMN email TEXT")
        c.execute("""CREATE TABLE IF NOT EXISTS livraison_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            livraison_id INTEGER, ordre INTEGER, qte TEXT, designation TEXT,
            etat TEXT DEFAULT '', motif TEXT, par TEXT, le TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS livraison_photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            livraison_id INTEGER, fichier TEXT, legende TEXT, par TEXT, le TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS livraison_journal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            livraison_id INTEGER, le TEXT, qui TEXT, quoi TEXT, type TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS livraison_reglages (
            cle TEXT PRIMARY KEY, valeur TEXT)""")
    os.makedirs(PHOTOS_DIR, exist_ok=True)


try:
    init_tables()
except Exception as _e:
    print("[LIVRAISON] tables :", repr(_e))


# ── outils ────────────────────────────────────────────────────────────────
def _equipe_requise(f):
    @wraps(f)
    def w(*a, **k):
        if not session.get("livraison_equipe"):
            return jsonify({"ok": False, "message": "Connexion de l'équipe nécessaire"}), 403
        return f(*a, **k)
    return w


def _qui():
    return session.get("livraison_prenom") or "Équipe"


def _numero_whatsapp(tel):
    """89 22 23 05 -> 68989222305 (Polynésie) ; garde un numéro déjà international."""
    d = re.sub(r"\D", "", tel or "")
    if not d:
        return ""
    if d.startswith("00"):
        d = d[2:]
    if len(d) == 8:
        d = "689" + d
    return d


def _email_valide(e):
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", e or ""))


def _corps_email(d, type_):
    """Un email clair et joli : titre, message, gros bouton vers la page de suivi."""
    import html as _h
    prenom = _h.escape((d.get("client") or "").split(" ")[0])
    if type_ == "bateau":
        titre = "Votre commande est au bateau 🚢"
        texte = ("Vos colis sont déposés au bateau%s%s. Retrouvez les photos du chargement "
                 "sur votre page de suivi.") % (
            (" " + _h.escape(d["bateau"])) if d.get("bateau") else "",
            (" (départ " + _h.escape(d["depart"]) + ")") if d.get("depart") else "")
        bouton = "Voir les photos du bateau"
    else:
        titre = "Votre commande est prête ✅"
        non = [a for a in d["articles"] if a["etat"] == "non"]
        texte = "Notre équipe a préparé %d article(s)%s." % (
            d["nb_ok"], (" — %d indisponible(s)" % len(non)) if non else "")
        bouton = "Suivre ma commande"
    lignes = "".join(
        '<tr><td style="padding:6px 10px;border-top:1px solid #e3e7e5;font-weight:700;color:#0a4a47">%s</td>'
        '<td style="padding:6px 10px;border-top:1px solid #e3e7e5;%s">%s%s</td></tr>' % (
            _h.escape(a["qte"]), "color:#8a9592;text-decoration:line-through" if a["etat"] == "non" else "",
            _h.escape(a["designation"]), " — indisponible" if a["etat"] == "non" else "")
        for a in d["articles"])
    html = """<!doctype html><html><body style="margin:0;background:#f6f3ec;font-family:Arial,Helvetica,sans-serif;color:#14211f">
<table width="100%%" cellpadding="0" cellspacing="0" style="background:#f6f3ec"><tr><td align="center" style="padding:24px 12px">
<table width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%%;background:#ffffff;border-radius:16px;overflow:hidden">
<tr><td style="background:#0f6b66;color:#fff;padding:26px 24px">
<div style="font-size:12px;letter-spacing:2px;text-transform:uppercase;opacity:.85">Chez TUKEA · 2KEA &amp; Associé</div>
<div style="font-size:26px;font-weight:bold;margin-top:8px">Ia ora na %s 🌺</div>
<div style="opacity:.9;margin-top:4px">Commande %s%s</div></td></tr>
<tr><td style="padding:24px">
<div style="font-size:21px;font-weight:bold;color:#0a4a47">%s</div>
<p style="font-size:15px;line-height:1.5">%s</p>
<p style="text-align:center;margin:22px 0"><a href="%s" style="background:#0f6b66;color:#fff;text-decoration:none;font-weight:bold;padding:14px 26px;border-radius:12px;display:inline-block">%s</a></p>
<table width="100%%" cellpadding="0" cellspacing="0" style="font-size:14px">%s</table>
<p style="font-size:13px;color:#5b6b68;margin-top:22px">Une question ? Répondez à cet email ou appelez-nous au %s.</p>
</td></tr></table></td></tr></table></body></html>""" % (
        prenom, _h.escape(d.get("ref") or ""), (" · " + _h.escape(d["ile"])) if d.get("ile") else "",
        titre, texte, d["lien"], bouton, lignes, TEL_BOUTIQUE)
    brut = "Ia ora na %s,\n\n%s\n%s\n\nVotre page de suivi : %s\n\n%s · %s" % (
        d.get("client") or "", titre, re.sub("<[^>]+>", "", texte), d["lien"], NOM_BOUTIQUE, TEL_BOUTIQUE)
    sujet = "%s — commande %s" % (titre, d.get("ref") or "")
    return sujet, brut, html


def _envoyer_email_client(lid, type_, qui):
    """Envoie l'email au client en tâche de fond et note le résultat dans l'historique."""
    import threading
    hote = request.host

    def tache():
        with _db() as c:
            d = _dossier(c, lid, hote=hote)
        if not d or not _email_valide(d.get("email")):
            return
        if not SMTP_USER or not SMTP_PASS:
            ok, msg = False, "boîte d'envoi non configurée (SMTP_USER / SMTP_PASS sur Railway)"
        else:
            try:
                import smtplib
                from email.message import EmailMessage
                sujet, brut, html = _corps_email(d, type_)
                m = EmailMessage()
                m["Subject"] = sujet
                m["From"] = "Chez TUKEA <%s>" % SMTP_USER
                m["To"] = d["email"]
                m["Reply-To"] = SMTP_USER
                m.set_content(brut)
                m.add_alternative(html, subtype="html")
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as s_:
                    s_.login(SMTP_USER, SMTP_PASS)
                    s_.send_message(m)
                ok, msg = True, ""
            except Exception as e:
                ok, msg = False, str(e)[:160]
        with _db() as c:
            c.execute("INSERT INTO livraison_journal (livraison_id, le, qui, quoi, type) VALUES (?,?,?,?,?)",
                      (lid, _maintenant(), qui,
                       ("✉️ Email « %s » envoyé à %s" % (LIBELLES.get(type_, type_), d["email"])) if ok
                       else ("⚠️ Email non parti : " + msg), "email_ok" if ok else "email_err"))
    try:
        threading.Thread(target=tache, daemon=True).start()
    except Exception as e:
        print("[LIVRAISON] email :", repr(e))


def _journal(c, lid, quoi, type_="info"):
    c.execute("INSERT INTO livraison_journal (livraison_id, le, qui, quoi, type) VALUES (?,?,?,?,?)",
              (lid, _maintenant(), _qui(), quoi, type_))
    c.execute("UPDATE livraisons SET maj_le=? WHERE id=?", (_maintenant(), lid))


def _reglage(c, cle, defaut=""):
    r = c.execute("SELECT valeur FROM livraison_reglages WHERE cle=?", (cle,)).fetchone()
    return r["valeur"] if r else defaut


def _analyser_articles(texte):
    """Une ligne = un article. « 3 x OHANA 75 » / « 3 OHANA 75 » / « OHANA 75 x3 »."""
    out = []
    for ligne in (texte or "").splitlines():
        l = ligne.strip(" \t-•*·")
        if not l:
            continue
        qte, nom = "1", l
        m = re.match(r"^(\d+)\s*(?:x|×|X|\*)?\s+(.+)$", l)
        if m:
            qte, nom = m.group(1), m.group(2)
        else:
            m = re.match(r"^(.+?)\s*(?:x|×|X|\*)\s*(\d+)$", l)
            if m:
                nom, qte = m.group(1), m.group(2)
        out.append((qte, nom.strip()[:160]))
    return out[:200]


def _dossier(c, lid, pour_client=False, hote=None):
    l = c.execute("SELECT * FROM livraisons WHERE id=?", (lid,)).fetchone()
    if not l:
        return None
    d = dict(l)
    d["articles"] = [dict(a) for a in c.execute(
        "SELECT * FROM livraison_articles WHERE livraison_id=? ORDER BY ordre, id", (lid,))]
    d["photos"] = [dict(p) for p in c.execute(
        "SELECT id, legende, par, le FROM livraison_photos WHERE livraison_id=? ORDER BY id", (lid,))]
    d["journal"] = [dict(j) for j in c.execute(
        "SELECT le, qui, quoi, type FROM livraison_journal WHERE livraison_id=? ORDER BY id DESC LIMIT 60", (lid,))]
    n = len(d["articles"])
    d["nb_ok"] = sum(1 for a in d["articles"] if a["etat"] == "ok")
    d["nb_non"] = sum(1 for a in d["articles"] if a["etat"] == "non")
    d["nb_total"] = n
    d["libelle"] = LIBELLES.get(d["statut"], d["statut"])
    _hote = hote or (request.host if request else "") or "manaprint.app"
    _sch = "http" if _hote.startswith(("localhost", "127.")) else "https"
    d["lien"] = "%s://%s/suivi/%s" % (_sch, _hote, d["code"])
    if pour_client:
        for k in ("cree_par", "prepare_par", "bateau_par", "notes", "journal", "email"):
            d.pop(k, None)
        for a in d["articles"]:
            a.pop("par", None)
    return d


def _messages(d):
    """Les messages WhatsApp tout prêts (client et équipe)."""
    prenom = (d.get("client") or "").split(" ")[0] or "Bonjour"
    lien = d["lien"]
    non = [a for a in d["articles"] if a["etat"] == "non"]
    m_prep = ("Ia ora na %s 🌺\nVotre commande %s est PRÊTE ✅\n"
              "%d article(s) préparé(s)%s.\nSuivez-la ici : %s\n— %s · %s") % (
        prenom, d.get("ref") or "", d["nb_ok"],
        (" · %d indisponible(s)" % len(non)) if non else "", lien, NOM_BOUTIQUE, TEL_BOUTIQUE)
    m_bat = ("Ia ora na %s 🚢\nVotre commande %s est déposée au bateau%s%s.\n"
             "Les photos du chargement sont ici : %s\nMāuruuru ! — %s") % (
        prenom, d.get("ref") or "",
        (" " + d["bateau"]) if d.get("bateau") else "",
        (" (départ " + d["depart"] + ")") if d.get("depart") else "", lien, NOM_BOUTIQUE)
    m_equipe = "✅ Commande %s (%s · %s) préparée par %s." % (
        d.get("ref") or "#%d" % d["id"], d.get("client") or "", d.get("ile") or "", d.get("prepare_par") or "")
    return {"preparee": m_prep, "bateau": m_bat, "equipe": m_equipe}


# ── pages ─────────────────────────────────────────────────────────────────
@bp.route("/livraison")
def page_equipe():
    return render_template("livraison_equipe.html")


@bp.route("/suivi/<code>")
def page_suivi(code):
    with _db() as c:
        l = c.execute("SELECT id FROM livraisons WHERE code=?", (code,)).fetchone()
    if not l:
        return render_template("livraison_suivi.html", code="", introuvable=True), 404
    return render_template("livraison_suivi.html", code=code, introuvable=False)


# ── API équipe ────────────────────────────────────────────────────────────
@bp.route("/livraison/api/connexion", methods=["POST"])
def api_connexion():
    d = request.get_json(force=True, silent=True) or {}
    if (d.get("code") or "").strip().upper() != CODE_EQUIPE.upper():
        return jsonify({"ok": False, "message": "Code incorrect"}), 401
    session.permanent = True
    session["livraison_equipe"] = True
    session["livraison_prenom"] = (d.get("prenom") or "").strip()[:30] or "Équipe"
    return jsonify({"ok": True, "prenom": session["livraison_prenom"]})


@bp.route("/livraison/api/moi")
def api_moi():
    return jsonify({"ok": bool(session.get("livraison_equipe")), "prenom": session.get("livraison_prenom", "")})


@bp.route("/livraison/api/deconnexion", methods=["POST"])
def api_deconnexion():
    session.pop("livraison_equipe", None)
    return jsonify({"ok": True})


@bp.route("/livraison/api/commandes")
@_equipe_requise
def api_commandes():
    archives = request.args.get("archives") == "1"
    with _db() as c:
        rows = c.execute(
            "SELECT * FROM livraisons WHERE archive=? ORDER BY id DESC LIMIT 400",
            (1 if archives else 0,)).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            st = c.execute("SELECT COUNT(*) n, SUM(etat='ok') ok, SUM(etat='non') non "
                           "FROM livraison_articles WHERE livraison_id=?", (r["id"],)).fetchone()
            d["nb_total"], d["nb_ok"], d["nb_non"] = st["n"] or 0, st["ok"] or 0, st["non"] or 0
            d["nb_photos"] = c.execute("SELECT COUNT(*) FROM livraison_photos WHERE livraison_id=?",
                                       (r["id"],)).fetchone()[0]
            d["libelle"] = LIBELLES.get(d["statut"], d["statut"])
            out.append(d)
        eq = _reglage(c, "tel_equipe")
    return jsonify({"ok": True, "commandes": out, "tel_equipe": eq, "prenom": _qui()})


@bp.route("/livraison/api/commandes", methods=["POST"])
@_equipe_requise
def api_creer():
    d = request.get_json(force=True, silent=True) or {}
    client = (d.get("client") or "").strip()[:80]
    if not client:
        return jsonify({"ok": False, "message": "Le nom du client est obligatoire"}), 400
    articles = _analyser_articles(d.get("articles") or "")
    if not articles:
        return jsonify({"ok": False, "message": "Ajoute au moins un article (une ligne par article)"}), 400
    with _db() as c:
        code = secrets.token_urlsafe(6).replace("-", "x").replace("_", "y")
        cur = c.execute(
            "INSERT INTO livraisons (code, ref, client, telephone, email, ile, bateau, depart, notes, origine,"
            " statut, cree_le, cree_par, maj_le) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (code, (d.get("ref") or "").strip()[:40], client, (d.get("telephone") or "").strip()[:30],
             (d.get("email") or "").strip()[:120],
             (d.get("ile") or "").strip()[:60], (d.get("bateau") or "").strip()[:60],
             (d.get("depart") or "").strip()[:30], (d.get("notes") or "").strip()[:600],
             (d.get("origine") or "main")[:20], "recue", _maintenant(), _qui(), _maintenant()))
        lid = cur.lastrowid
        if not (d.get("ref") or "").strip():
            c.execute("UPDATE livraisons SET ref=? WHERE id=?", ("LV-%04d" % lid, lid))
        for i, (q, n) in enumerate(articles):
            c.execute("INSERT INTO livraison_articles (livraison_id, ordre, qte, designation) VALUES (?,?,?,?)",
                      (lid, i, q, n))
        _journal(c, lid, "Commande créée (%d articles)" % len(articles), "creation")
        dos = _dossier(c, lid)
    return jsonify({"ok": True, "commande": dos})


@bp.route("/livraison/api/commandes/<int:lid>")
@_equipe_requise
def api_detail(lid):
    with _db() as c:
        d = _dossier(c, lid)
    if not d:
        return jsonify({"ok": False, "message": "Commande introuvable"}), 404
    d["messages"] = _messages(d)
    d["wa_client"] = _numero_whatsapp(d.get("telephone"))
    return jsonify({"ok": True, "commande": d})


@bp.route("/livraison/api/commandes/<int:lid>", methods=["PATCH"])
@_equipe_requise
def api_modifier(lid):
    d = request.get_json(force=True, silent=True) or {}
    champs = {k: (str(d[k]).strip()[:600]) for k in
              ("client", "telephone", "email", "ile", "bateau", "depart", "notes", "ref") if k in d}
    with _db() as c:
        if champs:
            c.execute("UPDATE livraisons SET %s WHERE id=?" % ", ".join("%s=?" % k for k in champs),
                      list(champs.values()) + [lid])
            _journal(c, lid, "Infos modifiées : " + ", ".join(champs.keys()))
        if "ajouter" in d:
            arts = _analyser_articles(d.get("ajouter"))
            base = c.execute("SELECT COALESCE(MAX(ordre),0) FROM livraison_articles WHERE livraison_id=?",
                             (lid,)).fetchone()[0]
            for i, (q, n) in enumerate(arts):
                c.execute("INSERT INTO livraison_articles (livraison_id, ordre, qte, designation) VALUES (?,?,?,?)",
                          (lid, base + 1 + i, q, n))
            if arts:
                _journal(c, lid, "%d article(s) ajouté(s)" % len(arts))
        if "archive" in d:
            c.execute("UPDATE livraisons SET archive=? WHERE id=?", (1 if d["archive"] else 0, lid))
            _journal(c, lid, "Commande archivée" if d["archive"] else "Commande ressortie des archives")
        dos = _dossier(c, lid)
    return jsonify({"ok": True, "commande": dos})


@bp.route("/livraison/api/articles/<int:aid>", methods=["POST"])
@_equipe_requise
def api_article(aid):
    d = request.get_json(force=True, silent=True) or {}
    etat = d.get("etat", "")
    if etat not in ("ok", "non", ""):
        return jsonify({"ok": False}), 400
    with _db() as c:
        a = c.execute("SELECT * FROM livraison_articles WHERE id=?", (aid,)).fetchone()
        if not a:
            return jsonify({"ok": False}), 404
        c.execute("UPDATE livraison_articles SET etat=?, motif=?, par=?, le=? WHERE id=?",
                  (etat, (d.get("motif") or "").strip()[:120] if etat == "non" else "",
                   _qui() if etat else "", _maintenant() if etat else "", aid))
        lid = a["livraison_id"]
        l = c.execute("SELECT statut FROM livraisons WHERE id=?", (lid,)).fetchone()
        if l and l["statut"] == "recue" and etat:
            c.execute("UPDATE livraisons SET statut='preparation' WHERE id=?", (lid,))
            _journal(c, lid, "Préparation commencée", "preparation")
        quoi = {"ok": "✓ validé", "non": "✗ non validé", "": "remis en attente"}[etat]
        _journal(c, lid, "%s %s — %s%s" % (a["qte"], a["designation"], quoi,
                                          (" (" + d.get("motif") + ")") if etat == "non" and d.get("motif") else ""),
                 "article")
        dos = _dossier(c, lid)
    return jsonify({"ok": True, "commande": dos})


@bp.route("/livraison/api/commandes/<int:lid>/statut", methods=["POST"])
@_equipe_requise
def api_statut(lid):
    d = request.get_json(force=True, silent=True) or {}
    st = d.get("statut")
    if st not in STATUTS:
        return jsonify({"ok": False}), 400
    with _db() as c:
        dos = _dossier(c, lid)
        if not dos:
            return jsonify({"ok": False}), 404
        if st == "preparee":
            reste = dos["nb_total"] - dos["nb_ok"] - dos["nb_non"]
            if reste > 0:
                return jsonify({"ok": False, "message": "Il reste %d article(s) à valider ou refuser" % reste}), 400
            c.execute("UPDATE livraisons SET statut=?, prepare_le=?, prepare_par=? WHERE id=?",
                      (st, _maintenant(), _qui(), lid))
        elif st == "bateau":
            c.execute("UPDATE livraisons SET statut=?, bateau_le=?, bateau_par=? WHERE id=?",
                      (st, _maintenant(), _qui(), lid))
        elif st == "livree":
            c.execute("UPDATE livraisons SET statut=?, livre_le=? WHERE id=?", (st, _maintenant(), lid))
        else:
            c.execute("UPDATE livraisons SET statut=? WHERE id=?", (st, lid))
        _journal(c, lid, LIBELLES[st], st)
        dos = _dossier(c, lid)
    if st in ("preparee", "bateau") and _email_valide(dos.get("email")):
        _envoyer_email_client(lid, st, _qui())      # ✉️ automatique
        dos["email_part"] = True
    dos["messages"] = _messages(dos)
    dos["wa_client"] = _numero_whatsapp(dos.get("telephone"))
    return jsonify({"ok": True, "commande": dos})


@bp.route("/livraison/api/commandes/<int:lid>/email", methods=["POST"])
@_equipe_requise
def api_email(lid):
    d = request.get_json(force=True, silent=True) or {}
    type_ = d.get("type") if d.get("type") in ("preparee", "bateau") else "preparee"
    with _db() as c:
        l = c.execute("SELECT email FROM livraisons WHERE id=?", (lid,)).fetchone()
    if not l or not _email_valide(l["email"]):
        return jsonify({"ok": False, "message": "Pas d'email valide pour ce client"}), 400
    _envoyer_email_client(lid, type_, _qui())
    return jsonify({"ok": True})


@bp.route("/livraison/api/commandes/<int:lid>/photos", methods=["POST"])
@_equipe_requise
def api_photos(lid):
    fichiers = request.files.getlist("photos")
    if not fichiers:
        return jsonify({"ok": False, "message": "Aucune photo reçue"}), 400
    from PIL import Image, ImageOps
    os.makedirs(os.path.join(PHOTOS_DIR, str(lid)), exist_ok=True)
    n = 0
    with _db() as c:
        if not c.execute("SELECT 1 FROM livraisons WHERE id=?", (lid,)).fetchone():
            return jsonify({"ok": False}), 404
        for f in fichiers[:20]:
            try:
                im = Image.open(f.stream)
                im = ImageOps.exif_transpose(im).convert("RGB")
                im.thumbnail((1800, 1800))
                nom = "%s.jpg" % secrets.token_hex(8)
                im.save(os.path.join(PHOTOS_DIR, str(lid), nom), "JPEG", quality=82, optimize=True)
                c.execute("INSERT INTO livraison_photos (livraison_id, fichier, legende, par, le) VALUES (?,?,?,?,?)",
                          (lid, nom, (request.form.get("legende") or "").strip()[:120], _qui(), _maintenant()))
                n += 1
            except Exception as e:
                print("[LIVRAISON] photo refusée :", repr(e))
        if n:
            _journal(c, lid, "%d photo(s) du chargement ajoutée(s)" % n, "photo")
        dos = _dossier(c, lid)
    dos["messages"] = _messages(dos)
    dos["wa_client"] = _numero_whatsapp(dos.get("telephone"))
    return jsonify({"ok": True, "ajoutees": n, "commande": dos})


@bp.route("/livraison/api/photos/<int:pid>", methods=["DELETE"])
@_equipe_requise
def api_photo_suppr(pid):
    with _db() as c:
        p = c.execute("SELECT * FROM livraison_photos WHERE id=?", (pid,)).fetchone()
        if not p:
            return jsonify({"ok": False}), 404
        try:
            os.remove(os.path.join(PHOTOS_DIR, str(p["livraison_id"]), p["fichier"]))
        except Exception:
            pass
        c.execute("DELETE FROM livraison_photos WHERE id=?", (pid,))
        _journal(c, p["livraison_id"], "Une photo retirée", "photo")
        dos = _dossier(c, p["livraison_id"])
    return jsonify({"ok": True, "commande": dos})


@bp.route("/livraison/api/reglages", methods=["POST"])
@_equipe_requise
def api_reglages():
    d = request.get_json(force=True, silent=True) or {}
    with _db() as c:
        if "tel_equipe" in d:
            c.execute("INSERT OR REPLACE INTO livraison_reglages (cle, valeur) VALUES ('tel_equipe', ?)",
                      ((d.get("tel_equipe") or "").strip()[:30],))
    return jsonify({"ok": True})


@bp.route("/livraison/api/flux")
@_equipe_requise
def api_flux():
    """Les derniers événements (pour les notifications sur les écrans de l'équipe)."""
    depuis = int(request.args.get("depuis") or 0)
    with _db() as c:
        rows = c.execute(
            "SELECT j.id, j.le, j.qui, j.quoi, j.type, l.id lid, l.ref, l.client, l.ile "
            "FROM livraison_journal j JOIN livraisons l ON l.id=j.livraison_id "
            "WHERE j.id>? ORDER BY j.id DESC LIMIT 40", (depuis,)).fetchall()
        dernier = c.execute("SELECT COALESCE(MAX(id),0) FROM livraison_journal").fetchone()[0]
    return jsonify({"ok": True, "evenements": [dict(r) for r in rows], "dernier": dernier})


@bp.route("/livraison/photo/<int:pid>")
@_equipe_requise
def photo_equipe(pid):
    return _servir_photo(pid, None)


# ── 🛒 22/11 : les commandes PAYÉES de cheztukea.app arrivent toutes seules ──
# La boutique appelle cette adresse avec la clé secrète partagée
# (variable MANAPRINT_IMPORT_CLE, la même sur les 2 projets Railway).
CLE_IMPORT = os.environ.get("MANAPRINT_IMPORT_CLE", "").strip()
MODES_RETRAIT = {"retrait": "Retrait en boutique", "coursier": "Coursier du client"}
PAIEMENTS = {"carte": "💳 Carte (en ligne)", "especes": "💵 Espèces", "virement": "🏦 Virement"}


@bp.route("/livraison/api/import", methods=["POST"])
def api_import():
    cle = (request.headers.get("X-Cle-Boutique") or "").strip()
    if not CLE_IMPORT or not secrets.compare_digest(cle, CLE_IMPORT):
        return jsonify({"ok": False, "message": "clé refusée"}), 403
    d = request.get_json(force=True, silent=True) or {}
    ref = (str(d.get("ref") or "")).strip()[:40]
    client = (str(d.get("client") or "")).strip()[:80]
    arts = []
    for a in (d.get("articles") or [])[:200]:
        try:
            q = str(int(a.get("qte") or 1))
        except Exception:
            q = "1"
        nom = (str(a.get("designation") or "")).strip()[:160]
        if nom:
            arts.append((q, nom))
    if not ref or not client or not arts:
        return jsonify({"ok": False, "message": "commande incomplète"}), 400
    with _db() as c:
        deja = c.execute("SELECT id, code FROM livraisons WHERE ref=? AND origine='boutique'", (ref,)).fetchone()
        if deja:
            lien = _dossier(c, deja["id"])["lien"]
            return jsonify({"ok": True, "deja": True, "lien": lien})
        notes = []
        if d.get("mode"):
            notes.append(MODES_RETRAIT.get(d["mode"], str(d["mode"])))
        if d.get("adresse"):
            notes.append("Adresse : " + str(d["adresse"])[:200])
        pai = PAIEMENTS.get(d.get("paiement") or "carte", str(d.get("paiement") or ""))
        try:
            reste = int(d.get("reste") or 0)
        except Exception:
            reste = 0
        notes.append("%s — payée%s" % (pai, (" (acompte) · reste %s F au retrait" % "{:,}".format(reste).replace(",", " ")) if reste > 0 else ""))
        if d.get("note"):
            notes.append("Note du client : " + str(d["note"])[:300])
        code = secrets.token_urlsafe(6).replace("-", "x").replace("_", "y")
        now = _maintenant()
        cur = c.execute(
            "INSERT INTO livraisons (code, ref, client, telephone, email, ile, notes, origine,"
            " statut, cree_le, cree_par, maj_le) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (code, ref, client, (str(d.get("telephone") or "")).strip()[:30],
             (str(d.get("email") or "")).strip()[:120], (str(d.get("ile") or "")).strip()[:60],
             " · ".join(notes)[:600], "boutique", "recue", now, "cheztukea.app", now))
        lid = cur.lastrowid
        for i, (q, n) in enumerate(arts):
            c.execute("INSERT INTO livraison_articles (livraison_id, ordre, qte, designation) VALUES (?,?,?,?)",
                      (lid, i, q, n))
        c.execute("INSERT INTO livraison_journal (livraison_id, le, qui, quoi, type) VALUES (?,?,?,?,?)",
                  (lid, now, "cheztukea.app", "🛒 Commande %s payée sur la boutique — arrivée toute seule (%d articles)"
                   % (ref, len(arts)), "creation"))
        c.execute("UPDATE livraisons SET maj_le=? WHERE id=?", (now, lid))
        lien = _dossier(c, lid, hote="manaprint.app")["lien"]
    return jsonify({"ok": True, "lien": lien})


# ── API client (lien public par code) ─────────────────────────────────────
@bp.route("/suivi/<code>/donnees")
def api_suivi(code):
    with _db() as c:
        l = c.execute("SELECT id FROM livraisons WHERE code=?", (code,)).fetchone()
        if not l:
            return jsonify({"ok": False}), 404
        d = _dossier(c, l["id"], pour_client=True)
    d["tel_boutique"] = TEL_BOUTIQUE
    d["wa_boutique"] = _numero_whatsapp(TEL_BOUTIQUE)
    d["statuts"] = [{"cle": s, "libelle": LIBELLES[s]} for s in STATUTS]
    r = jsonify({"ok": True, "commande": d})
    r.headers["Cache-Control"] = "no-store"
    return r


@bp.route("/suivi/<code>/photo/<int:pid>")
def photo_client(code, pid):
    return _servir_photo(pid, code)


def _servir_photo(pid, code):
    with _db() as c:
        p = c.execute("SELECT p.*, l.code FROM livraison_photos p JOIN livraisons l ON l.id=p.livraison_id "
                      "WHERE p.id=?", (pid,)).fetchone()
    if not p or (code is not None and p["code"] != code):
        abort(404)
    chemin = os.path.join(PHOTOS_DIR, str(p["livraison_id"]), p["fichier"])
    if not os.path.exists(chemin):
        abort(404)
    return send_file(chemin, mimetype="image/jpeg", max_age=86400)
