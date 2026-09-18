# -*- coding: utf-8 -*-
"""Etape 5 : reversement des envois reellement effectues dans le journal immuable.

Ne consigne QUE les lignes portant une confirmation d interface non vide. Une
ligne sans confirmation n est jamais consignee comme envoyee : on ne declare
jamais un envoi que l interface n a pas confirme.

    python3 outils/05_consigner_envois.py --campagne 03_RHUMATOLOGUES \
        --version RHUM-v1 --feuille <chemin>/_feuille_de_confirmation.csv
"""
from __future__ import annotations

import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C
import journal as J


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--campagne", required=True, choices=list(C.CAMPAGNES))
    p.add_argument("--version", required=True)
    p.add_argument("--feuille", required=True)
    p.add_argument("--operateur", default="saisie humaine")
    a = p.parse_args()

    modele = J.modele_valide(a.campagne, a.version)
    if modele is None:
        print("REFUS : version %r non validee." % a.version, file=sys.stderr)
        return 1
    chemin_texte = os.path.join(C.RACINE, modele["fichier"])
    with open(chemin_texte, encoding="utf-8") as f:
        texte = f.read()
    if J.empreinte_texte(texte) != modele["empreinte_texte"]:
        print("REFUS : le fichier du modele a change depuis sa validation.", file=sys.stderr)
        return 1

    consignes, ignores, refuses = 0, 0, 0
    with open(a.feuille, encoding="utf-8") as f:
        for l in csv.DictReader(f):
            confirmation = (l.get("confirmation_interface") or "").strip()
            nom, prenom = l.get("nom", ""), l.get("prenom", "")
            if not confirmation:
                ignores += 1
                continue
            if (l.get("historique_verifie_OUI") or "").strip().lower() not in ("oui", "o", "yes"):
                print("  REFUS %s %s : historique non verifie." % (nom, prenom))
                refuses += 1
                continue
            try:
                J.consigner_envoi(
                    campagne=a.campagne, rpps=(l.get("rpps") or "").strip(),
                    nom=nom, prenom=prenom,
                    profil_connect=(l.get("profil_connect") or "").strip(),
                    version_message=a.version, texte_envoye=texte,
                    confirmation_interface=confirmation, operateur=a.operateur)
                consignes += 1
            except ValueError as exc:
                print("  REFUS %s %s : %s" % (nom, prenom, exc))
                refuses += 1

    print("\nConsignes comme envoyes : %d" % consignes)
    print("Ignores (aucune confirmation d interface) : %d" % ignores)
    print("Refuses par les garde-fous : %d" % refuses)
    ok, msg = J.verifier_integrite(a.campagne, "envois")
    print("Journal des envois : %s %s" % ("INTACT" if ok else "ALERTE", msg))
    print("\nPensez a recalculer : python3 outils/02_bilan.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
