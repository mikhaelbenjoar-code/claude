# -*- coding: utf-8 -*-
"""Journalisation immuable et garde-fou anti-doublon.

Deux journaux separes, en append-only, au format JSONL :
  <campagne>/journaux/journal_recherches.jsonl  -> toute recherche Connect
  <campagne>/journaux/journal_envois.jsonl      -> les envois REELLEMENT effectues

Le journal d'envois est chaine par empreinte : chaque entree porte le SHA-256
de l'entree precedente. Toute reecriture a posteriori (y compris un changement
de modele de message) casse la chaine et devient detectable par
`verifier_integrite()`. Le texte exact envoye est fige par son empreinte :
modifier un modele plus tard ne reecrit jamais l'historique.

Garde-fou : `peut_envoyer()` refuse un envoi si le professionnel est exclu,
deja contacte (dans N'IMPORTE quelle campagne, y compris via un autre compte
Connect ou un autre lieu d'exercice), ou si son statut n'est pas EXACT.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C  # noqa: E402

FICHIER_EXCLUSION = os.path.join(C.DOSSIER_COMMUN, "liste_exclusion.csv")
GENESE = "0" * 64


def _registre_modeles() -> list[dict]:
    """Modeles valides, lus directement (voir outils/03_valider_modele.py)."""
    chemin = os.path.join(C.DOSSIER_COMMUN, "modeles", "registre_modeles.jsonl")
    if not os.path.exists(chemin):
        return []
    with open(chemin, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def modele_valide(campagne: str, version: str) -> dict | None:
    for e in _registre_modeles():
        if e.get("campagne") == campagne and e.get("version") == version:
            return e
    return None


# --- Utilitaires ----------------------------------------------------------
def _horodatage() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def empreinte_texte(texte: str) -> str:
    """Empreinte stable d'un texte de message (sert de preuve de version)."""
    return hashlib.sha256(texte.encode("utf-8")).hexdigest()


def _empreinte_entree(entree: dict, precedent: str) -> str:
    charge = json.dumps(entree, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256((precedent + charge).encode("utf-8")).hexdigest()


def chemin_journal(campagne: str, genre: str) -> str:
    d = os.path.join(C.RACINE, campagne, "journaux")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "journal_%s.jsonl" % genre)


def lire_journal(campagne: str, genre: str) -> list[dict]:
    chemin = chemin_journal(campagne, genre)
    if not os.path.exists(chemin):
        return []
    entrees = []
    with open(chemin, encoding="utf-8") as f:
        for ligne in f:
            ligne = ligne.strip()
            if ligne:
                entrees.append(json.loads(ligne))
    return entrees


def _ajouter(campagne: str, genre: str, entree: dict) -> dict:
    """Ajout strictement en fin de fichier. Jamais de reecriture."""
    existantes = lire_journal(campagne, genre)
    precedent = existantes[-1]["empreinte"] if existantes else GENESE
    entree = dict(entree)
    entree["horodatage"] = entree.get("horodatage") or _horodatage()
    entree["rang"] = len(existantes) + 1
    entree["empreinte_precedente"] = precedent
    entree["empreinte"] = _empreinte_entree(entree, precedent)
    with open(chemin_journal(campagne, genre), "a", encoding="utf-8") as f:
        f.write(json.dumps(entree, ensure_ascii=False, sort_keys=True) + "\n")
    return entree


# --- Journal des recherches ----------------------------------------------
def consigner_recherche(campagne: str, rpps: str, nom: str, prenom: str,
                        requete: str, nb_resultats: int, candidats: list,
                        statut: str, profil: str = "", motif: str = "",
                        operateur: str = "assistant") -> dict:
    if statut not in C.STATUTS:
        raise ValueError("Statut inconnu : %r (voir config.STATUTS)" % statut)
    return _ajouter(campagne, "recherches", {
        "rpps": rpps, "nom": nom, "prenom": prenom,
        "requete_effectuee": requete, "nb_resultats": nb_resultats,
        "candidats": candidats, "statut_retenu": statut,
        "profil_retenu": profil, "motif": motif, "operateur": operateur,
    })


# --- Liste d'exclusion durable -------------------------------------------
def charger_exclusions() -> dict[str, str]:
    """Retourne {cle: motif}. Cles : RPPS et/ou 'nom prenom' normalise."""
    import csv
    exclusions: dict[str, str] = {}
    if not os.path.exists(FICHIER_EXCLUSION):
        return exclusions
    with open(FICHIER_EXCLUSION, encoding="utf-8") as f:
        for l in csv.DictReader(f):
            motif = (l.get("motif") or "").strip()
            if (l.get("rpps") or "").strip():
                exclusions[l["rpps"].strip()] = motif
            cle_nom = C.normaliser((l.get("nom") or "") + " " + (l.get("prenom") or ""))
            if cle_nom.strip():
                exclusions[cle_nom] = motif
    return exclusions


def ajouter_exclusion(rpps: str, nom: str, prenom: str, motif: str,
                      demande_par: str = "Dr Benjoar") -> None:
    import csv
    nouveau = not os.path.exists(FICHIER_EXCLUSION)
    with open(FICHIER_EXCLUSION, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if nouveau:
            w.writerow(["date", "rpps", "nom", "prenom", "motif", "demande_par"])
        w.writerow([_horodatage()[:10], rpps, nom, prenom, motif, demande_par])


# --- Garde-fou anti-doublon ----------------------------------------------
def historique_envois_global() -> list[dict]:
    """Tous les envois, toutes campagnes confondues."""
    tout = []
    for campagne in C.CAMPAGNES:
        for e in lire_journal(campagne, "envois"):
            e = dict(e)
            e["campagne"] = campagne
            tout.append(e)
    return tout


def deja_contacte(rpps: str, nom: str = "", prenom: str = "",
                  profil_connect: str = "") -> list[dict]:
    """Envois anterieurs correspondant a ce professionnel.

    Le rapprochement est volontairement large : meme RPPS, OU meme identite
    normalisee, OU meme profil Connect. Un professionnel disposant de
    plusieurs comptes ou lieux d'exercice reste ainsi detecte une seule fois.
    """
    cle_nom = C.normaliser(nom + " " + prenom).strip()
    trouves = []
    for e in historique_envois_global():
        if rpps and e.get("rpps") == rpps:
            trouves.append(e)
        elif cle_nom and C.normaliser(e.get("nom", "") + " " + e.get("prenom", "")) == cle_nom:
            trouves.append(e)
        elif profil_connect and e.get("profil_connect") == profil_connect:
            trouves.append(e)
    return trouves


def peut_envoyer(campagne: str, rpps: str, nom: str, prenom: str,
                 statut: str, profil_connect: str = "") -> tuple[bool, str]:
    """Verifie TOUTES les conditions avant un envoi. (autorise, motif)."""
    exclusions = charger_exclusions()
    cle_nom = C.normaliser(nom + " " + prenom)
    if rpps in exclusions:
        return False, "Exclusion nominative (RPPS %s) : %s" % (rpps, exclusions[rpps])
    if cle_nom in exclusions:
        return False, "Exclusion nominative (%s %s) : %s" % (nom, prenom, exclusions[cle_nom])
    if statut not in C.STATUTS:
        return False, "Statut inconnu : %r" % statut
    if statut not in C.STATUTS_ENVOI_AUTORISE:
        return False, ("Statut %s : envoi interdit (seul EXACT est autorise). %s"
                       % (statut, C.DESCRIPTION_STATUTS[statut]))
    anterieurs = deja_contacte(rpps, nom, prenom, profil_connect)
    if anterieurs:
        p = anterieurs[0]
        return False, ("Deja contacte le %s dans la campagne %s (version %s). "
                       "Ne pas solliciter a nouveau."
                       % (p.get("horodatage", "?")[:10], p.get("campagne", "?"),
                          p.get("version_message", "?")))
    return True, "Conditions reunies. L'envoi reste subordonne a la validation ecrite du texte."


# --- Journal des envois ---------------------------------------------------
def consigner_envoi(campagne: str, rpps: str, nom: str, prenom: str,
                    profil_connect: str, version_message: str, texte_envoye: str,
                    confirmation_interface: str, operateur: str = "assistant") -> dict:
    """A n'appeler qu'APRES un envoi reellement constate dans l'interface.

    `confirmation_interface` doit decrire ce que l'interface a reellement
    affiche. Une chaine vide est refusee : on ne consigne jamais un envoi
    non confirme.
    """
    if not confirmation_interface.strip():
        raise ValueError(
            "confirmation_interface est vide : un envoi non confirme par "
            "l'interface ne doit jamais etre consigne comme effectue.")
    modele = modele_valide(campagne, version_message)
    if modele is None:
        raise ValueError(
            "Version de message %r non enregistree comme validee pour %s. "
            "Aucun envoi ne peut etre consigne avant validation explicite du "
            "texte par le Dr Benjoar (voir outils/03_valider_modele.py)."
            % (version_message, campagne))
    if empreinte_texte(texte_envoye) != modele["empreinte_texte"]:
        raise ValueError(
            "Le texte envoye ne correspond pas mot pour mot a la version "
            "validee %s. Toute modification substantielle impose une nouvelle "
            "validation et une nouvelle version." % version_message)
    autorise, motif = peut_envoyer(campagne, rpps, nom, prenom, "EXACT", profil_connect)
    if not autorise:
        raise ValueError("Envoi non consignable : %s" % motif)
    return _ajouter(campagne, "envois", {
        "rpps": rpps, "nom": nom, "prenom": prenom,
        "profil_connect": profil_connect,
        "version_message": version_message,
        "empreinte_texte": empreinte_texte(texte_envoye),
        "longueur_texte": len(texte_envoye),
        "confirmation_interface": confirmation_interface,
        "operateur": operateur,
    })


# --- Controle d'integrite -------------------------------------------------
def verifier_integrite(campagne: str, genre: str) -> tuple[bool, str]:
    entrees = lire_journal(campagne, genre)
    precedent = GENESE
    for e in entrees:
        attendu = dict(e)
        empreinte = attendu.pop("empreinte", None)
        if attendu.get("empreinte_precedente") != precedent:
            return False, ("Rupture de chaine au rang %s : empreinte precedente "
                           "inattendue." % e.get("rang"))
        if _empreinte_entree(attendu, precedent) != empreinte:
            return False, ("Entree modifiee au rang %s : l'empreinte ne "
                           "correspond plus au contenu." % e.get("rang"))
        precedent = empreinte
    return True, "%d entree(s) verifiee(s), chaine intacte." % len(entrees)


if __name__ == "__main__":
    for campagne in C.CAMPAGNES:
        for genre in ("recherches", "envois"):
            ok, msg = verifier_integrite(campagne, genre)
            print("[%s] %-11s %s %s" % (campagne, genre, "OK " if ok else "ALERTE", msg))
