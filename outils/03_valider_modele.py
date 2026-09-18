# -*- coding: utf-8 -*-
"""Registre immuable des modeles de message validés par le Dr Benjoar.

Un texte ne peut etre envoye que s'il a ete enregistre ici, et il est envoye
mot pour mot. Le registre est append-only : une version validee n'est jamais
modifiee, une correction cree une NOUVELLE version. L'historique des textes
deja envoyes reste donc intact quoi qu'il advienne des modeles.

Enregistrer une version validee :
    python3 outils/03_valider_modele.py --enregistrer \
        --campagne 03_RHUMATOLOGUES --version RHUM-v1 \
        --fichier 00_COMMUN/modeles/RHUM-v1.txt \
        --valide-par "Dr Benjoar" --preuve "validation ecrite du 2026-09-20"

Lister :
    python3 outils/03_valider_modele.py --lister
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C
import journal as J

DOSSIER_MODELES = os.path.join(C.DOSSIER_COMMUN, "modeles")
REGISTRE = os.path.join(DOSSIER_MODELES, "registre_modeles.jsonl")

# Un texte pret a l'envoi ne contient plus aucun marqueur a completer.
MARQUEURS = [
    (r"\[[^\]\n]{3,}\]", "un crochet a completer subsiste"),
    (r"_{4,}", "un champ a remplir (____) subsiste"),
    (r"(?i)\ba confirmer\b", "la mention « a confirmer » subsiste"),
    (r"(?i)\bnon verifie\b", "la mention « non verifie » subsiste"),
    (r"(?i)\ba valider\b", "la mention « a valider » subsiste"),
    (r"(?i)\bprojet\b", "la mention « projet » subsiste"),
]


def lire_registre() -> list[dict]:
    if not os.path.exists(REGISTRE):
        return []
    with open(REGISTRE, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def controler_texte(texte: str) -> list[str]:
    problemes = []
    if not texte.strip():
        problemes.append("le texte est vide")
    for motif, libelle in MARQUEURS:
        for trouve in re.findall(motif, C.normaliser(texte) if "(?i)" in motif else texte):
            problemes.append("%s : %r" % (libelle, trouve if isinstance(trouve, str) else trouve))
            break
    return problemes


def enregistrer(campagne: str, version: str, fichier: str, valide_par: str,
                preuve: str, forcer: bool) -> int:
    if campagne not in C.CAMPAGNES:
        print("ERREUR : campagne inconnue.", file=sys.stderr)
        return 2
    if not os.path.exists(fichier):
        print("ERREUR : fichier introuvable : %s" % fichier, file=sys.stderr)
        return 2
    with open(fichier, encoding="utf-8") as f:
        texte = f.read()

    problemes = controler_texte(texte)
    if problemes and not forcer:
        print("REFUS : le texte n'est pas pret a l'envoi.", file=sys.stderr)
        for p in problemes:
            print("  - %s" % p, file=sys.stderr)
        print("\nCompletez le texte, ou --forcer si ces marqueurs sont "
              "volontaires et valides tels quels.", file=sys.stderr)
        return 1

    registre = lire_registre()
    empreinte = J.empreinte_texte(texte)
    for e in registre:
        if e["version"] == version:
            print("REFUS : la version %s existe deja (enregistree le %s). "
                  "Une correction doit creer une NOUVELLE version."
                  % (version, e["horodatage"][:10]), file=sys.stderr)
            return 1
        if e["empreinte_texte"] == empreinte and e["campagne"] == campagne:
            print("REFUS : ce texte exact est deja enregistre sous %s."
                  % e["version"], file=sys.stderr)
            return 1

    if not preuve.strip():
        print("ERREUR : --preuve est obligatoire (trace de la validation).",
              file=sys.stderr)
        return 2

    os.makedirs(DOSSIER_MODELES, exist_ok=True)
    entree = {
        "horodatage": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "campagne": campagne,
        "version": version,
        "fichier": os.path.relpath(fichier, C.RACINE),
        "empreinte_texte": empreinte,
        "longueur": len(texte),
        "nb_lignes": texte.count("\n") + 1,
        "valide_par": valide_par,
        "preuve_validation": preuve,
    }
    with open(REGISTRE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entree, ensure_ascii=False, sort_keys=True) + "\n")
    print("Version %s enregistree pour %s." % (version, campagne))
    print("  empreinte : %s" % empreinte)
    print("  %d caracteres, %d lignes" % (entree["longueur"], entree["nb_lignes"]))
    print("\nSeul ce texte exact peut desormais etre envoye sous cette version.")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--enregistrer", action="store_true")
    p.add_argument("--lister", action="store_true")
    p.add_argument("--campagne")
    p.add_argument("--version")
    p.add_argument("--fichier")
    p.add_argument("--valide-par", default="Dr Benjoar")
    p.add_argument("--preuve", default="")
    p.add_argument("--forcer", action="store_true")
    a = p.parse_args()

    if a.lister or not a.enregistrer:
        registre = lire_registre()
        if not registre:
            print("Aucun modele valide. Aucun envoi n'est possible.")
            return 0
        print("%-28s %-14s %-12s %s" % ("CAMPAGNE", "VERSION", "DATE", "EMPREINTE"))
        for e in registre:
            print("%-28s %-14s %-12s %s" % (e["campagne"], e["version"],
                                            e["horodatage"][:10], e["empreinte_texte"][:16]))
        return 0

    for champ in ("campagne", "version", "fichier"):
        if not getattr(a, champ):
            print("ERREUR : --%s est obligatoire." % champ, file=sys.stderr)
            return 2
    return enregistrer(a.campagne, a.version, a.fichier, a.valide_par, a.preuve, a.forcer)


if __name__ == "__main__":
    sys.exit(main())
