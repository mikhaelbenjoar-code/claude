# -*- coding: utf-8 -*-
"""Etape 1 : constitution et deduplication de la base RPPS par specialite.

Entree  : extraction publique "Annuaire Sante / PS_LibreAcces" de l'ANS
          (fichier PS_LibreAcces_Personne_activite_*.txt, seul ou dans le ZIP).
Sortie  : un classeur Excel consolide et dedoublonne par campagne.

Le script ne connait PAS a l'avance l'orthographe exacte des en-tetes : il les
detecte, et s'arrete en affichant la liste reelle des colonnes si un champ
obligatoire manque. Aucune donnee n'est inventee : ce qui est absent de la
source reste vide.

Usage :
    python3 outils/01_extraction_rpps.py --source donnees_source/<fichier>
    python3 outils/01_extraction_rpps.py --source <fichier> --campagne 03_RHUMATOLOGUES
    python3 outils/01_extraction_rpps.py --source <fichier> --audit-libelles
"""

from __future__ import annotations

import argparse
import csv
import io
import os
import re
import sys
import zipfile
from collections import Counter, OrderedDict
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C  # noqa: E402

csv.field_size_limit(10 ** 7)

# --- Detection des colonnes ------------------------------------------------
# Pour chaque champ logique : motifs recherches dans l'en-tete normalise,
# par ordre de preference. `None` en 2e position = champ facultatif.
CHAMPS = OrderedDict([
    ("rpps",          ([r"identification nationale pp", r"identifiant pp"], True)),
    ("nom",           ([r"nom d'exercice", r"^nom$"], True)),
    ("prenom",        ([r"prenom d'exercice", r"^prenom$"], True)),
    ("civilite",      ([r"libelle civilite d'exercice", r"libelle civilite"], False)),
    ("profession",    ([r"libelle profession"], False)),
    ("specialite",    ([r"libelle savoir.?faire"], True)),
    ("mode_exercice", ([r"libelle mode exercice"], False)),
    ("raison_sociale",([r"raison sociale site", r"enseigne commerciale site"], False)),
    ("num_voie",      ([r"numero voie"], False)),
    ("indice_voie",   ([r"indice repetition voie"], False)),
    ("type_voie",     ([r"libelle type de voie"], False)),
    ("libelle_voie",  ([r"libelle voie"], False)),
    ("complement",    ([r"complement destinataire"], False)),
    ("code_postal",   ([r"code postal"], True)),
    ("commune",       ([r"libelle commune"], False)),
    ("telephone",     ([r"^telephone \(coord", r"^telephone"], False)),
    ("email",         ([r"adresse e.?mail"], False)),
    ("departement",   ([r"code departement"], False)),
    ("dep_libelle",   ([r"libelle departement"], False)),
    ("finess",        ([r"numero finess site"], False)),
])


def detecter_colonnes(entetes: list[str]) -> dict[str, int]:
    norm = [C.normaliser(e) for e in entetes]
    trouve: dict[str, int] = {}
    manquants: list[str] = []
    for champ, (motifs, obligatoire) in CHAMPS.items():
        idx = None
        for motif in motifs:
            for i, h in enumerate(norm):
                if i in trouve.values():
                    continue
                if re.search(motif, h):
                    idx = i
                    break
            if idx is not None:
                break
        if idx is not None:
            trouve[champ] = idx
        elif obligatoire:
            manquants.append(champ)
    if manquants:
        print("ERREUR : champs obligatoires introuvables dans la source : "
              + ", ".join(manquants), file=sys.stderr)
        print("\nEn-tetes reellement presents dans le fichier :", file=sys.stderr)
        for i, e in enumerate(entetes):
            print("  [%3d] %s" % (i, e), file=sys.stderr)
        print("\nAdaptez le dictionnaire CHAMPS dans outils/01_extraction_rpps.py.",
              file=sys.stderr)
        sys.exit(2)
    return trouve


def ouvrir_source(chemin: str):
    """Retourne (flux texte, nom du fichier reel). Gere ZIP et fichier nu."""
    if chemin.lower().endswith(".zip"):
        zf = zipfile.ZipFile(chemin)
        noms = [n for n in zf.namelist()
                if "personne_activite" in C.normaliser(n).replace(" ", "_")]
        if not noms:
            noms = [n for n in zf.namelist() if n.lower().endswith((".txt", ".csv"))]
        if not noms:
            print("ERREUR : aucun fichier exploitable dans %s" % chemin, file=sys.stderr)
            sys.exit(2)
        nom = noms[0]
        brut = zf.read(nom)
    else:
        nom = os.path.basename(chemin)
        with open(chemin, "rb") as f:
            brut = f.read()
    for enc in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return io.StringIO(brut.decode(enc)), nom
        except UnicodeDecodeError:
            continue
    return io.StringIO(brut.decode("latin-1", "replace")), nom


def sniffer_delimiteur(premiere_ligne: str) -> str:
    comptes = {d: premiere_ligne.count(d) for d in [";", "\t", "|", ","]}
    return max(comptes, key=comptes.get)


def composer_adresse(l: dict) -> str:
    morceaux = [l.get("complement", ""), l.get("num_voie", ""), l.get("indice_voie", ""),
                l.get("type_voie", ""), l.get("libelle_voie", "")]
    return " ".join(m.strip() for m in morceaux if m and m.strip()).strip()


def departement_depuis_cp(cp: str) -> str:
    cp = (cp or "").strip()
    if len(cp) >= 2 and cp[:2].isdigit():
        return cp[:2]
    return ""


def correspond(specialite_norm: str, camp: dict) -> bool:
    if any(re.search(m, specialite_norm) for m in camp["motifs_exclusion"]):
        return False
    return any(re.search(m, specialite_norm) for m in camp["motifs"])


def lire_et_filtrer(chemin: str, campagnes: dict, audit_seulement: bool):
    flux, nom_fichier = ouvrir_source(chemin)
    premiere = flux.readline()
    delim = sniffer_delimiteur(premiere)
    flux.seek(0)
    lecteur = csv.reader(flux, delimiter=delim, quotechar='"')
    entetes = next(lecteur)
    cols = detecter_colonnes(entetes)
    print("Source     : %s" % nom_fichier)
    print("Delimiteur : %r  |  %d colonnes detectees" % (delim, len(entetes)))

    libelles_vus = Counter()          # audit global
    libelles_retenus = {k: Counter() for k in campagnes}
    # resultats[campagne][rpps] = enregistrement agrege
    resultats = {k: OrderedDict() for k in campagnes}
    lignes = 0

    for ligne in lecteur:
        lignes += 1
        if len(ligne) <= max(cols.values()):
            continue
        val = {champ: (ligne[i] or "").strip() for champ, i in cols.items()}

        spec_norm = C.normaliser(val["specialite"])
        if not spec_norm:
            continue

        dep = val.get("departement", "").strip() or departement_depuis_cp(val.get("code_postal", ""))
        dep = dep[:2] if len(dep) > 2 else dep
        if dep not in C.DEPARTEMENTS_IDF:
            continue
        libelles_vus[val["specialite"]] += 1
        if audit_seulement:
            continue

        for cle, camp in campagnes.items():
            if not correspond(spec_norm, camp):
                continue
            libelles_retenus[cle][val["specialite"]] += 1
            rpps = val["rpps"].strip()
            if not rpps:
                continue  # pas de cle de deduplication fiable : ligne ecartee

            adresse = composer_adresse(val)
            lieu = " / ".join(x for x in [
                val.get("raison_sociale", ""), adresse,
                (val.get("code_postal", "") + " " + val.get("commune", "")).strip(),
            ] if x)

            rec = resultats[cle].get(rpps)
            if rec is None:
                rec = {
                    "RPPS": rpps,
                    "Nom": val["nom"], "Prenom": val["prenom"],
                    "_noms": {C.normaliser(val["nom"] + " " + val["prenom"])},
                    "Civilite": val.get("civilite", ""),
                    "Profession": val.get("profession", ""),
                    "_specialites": OrderedDict(),
                    "Specialite_exacte": val["specialite"],
                    "Mode_exercice": val.get("mode_exercice", ""),
                    "Departement": dep,
                    "Departement_libelle": C.DEPARTEMENTS_IDF[dep],
                    "Ville": val.get("commune", ""),
                    "Code_postal": val.get("code_postal", ""),
                    "Adresse": adresse,
                    "Etablissement_cabinet": val.get("raison_sociale", ""),
                    "Telephone_structure": val.get("telephone", ""),
                    "Email_professionnel": val.get("email", ""),
                    "_lieux": OrderedDict(),
                }
                resultats[cle][rpps] = rec
            rec["_specialites"][val["specialite"]] = True
            rec["_noms"].add(C.normaliser(val["nom"] + " " + val["prenom"]))
            if lieu:
                rec["_lieux"][lieu] = True
            # premier telephone / email non vide rencontre
            if not rec["Telephone_structure"]:
                rec["Telephone_structure"] = val.get("telephone", "")
            if not rec["Email_professionnel"]:
                rec["Email_professionnel"] = val.get("email", "")

    return resultats, libelles_vus, libelles_retenus, nom_fichier, lignes


def finaliser(rec: dict, source: str, date_source: str) -> dict:
    specs = list(rec["_specialites"].keys())
    lieux = list(rec["_lieux"].keys())
    variantes = sorted(n for n in rec["_noms"]
                       if n != C.normaliser(rec["Nom"] + " " + rec["Prenom"]))
    sortie = {
        "Nom_usage_variantes": " | ".join(variantes),
        "Specialite_exacte": specs[0] if specs else "",
        "Surspecialite": " | ".join(specs[1:]),
        "Nb_lieux_exercice": len(lieux),
        "Liste_lieux_exercice": " | ".join(lieux),
        "Source": source,
        "Date_source": date_source,
        "Statut_Connect": "NON_VERIFIE",
    }
    for k, v in rec.items():
        if not k.startswith("_") and k not in sortie:
            sortie[k] = v
    return sortie


def ecrire_excel(cle: str, lignes: list[dict], chemin: str, camp: dict) -> None:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation

    wb = Workbook()
    ws = wb.active
    ws.title = "Base RPPS"

    entetes = [c[0] for c in C.COLONNES_BASE]
    ws.append(entetes)
    for i, (nom, largeur, commentaire) in enumerate(C.COLONNES_BASE, start=1):
        cell = ws.cell(row=1, column=i)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", start_color="1F4E79")
        cell.alignment = Alignment(vertical="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(i)].width = largeur
    ws.freeze_panes = "C2"
    ws.auto_filter.ref = "A1:%s%d" % (get_column_letter(len(entetes)), max(len(lignes) + 1, 1))

    for l in lignes:
        ws.append([l.get(e, "") for e in entetes])

    # Colonne RPPS en texte : preserve les zeros non significatifs
    idx_rpps = entetes.index("RPPS") + 1
    for r in range(2, ws.max_row + 1):
        ws.cell(row=r, column=idx_rpps).number_format = "@"

    # Liste deroulante fermee sur le statut Connect
    idx_statut = entetes.index("Statut_Connect") + 1
    col = get_column_letter(idx_statut)
    dv = DataValidation(type="list", formula1='"%s"' % ",".join(C.STATUTS),
                        allow_blank=False, showErrorMessage=True)
    dv.error = "Valeur hors du referentiel (voir 00_COMMUN/referentiel_statuts.md)."
    ws.add_data_validation(dv)
    dv.add("%s2:%s5000" % (col, col))

    # Onglet dictionnaire des colonnes
    ws2 = wb.create_sheet("Dictionnaire")
    ws2.append(["Colonne", "Description"])
    for c in ws2[1]:
        c.font = Font(bold=True)
    for nom, _, commentaire in C.COLONNES_BASE:
        ws2.append([nom, commentaire])
    ws2.column_dimensions["A"].width = 30
    ws2.column_dimensions["B"].width = 90

    # Onglet statuts
    ws3 = wb.create_sheet("Statuts")
    ws3.append(["Statut", "Definition", "Envoi autorise"])
    for c in ws3[1]:
        c.font = Font(bold=True)
    for s in C.STATUTS:
        ws3.append([s, C.DESCRIPTION_STATUTS[s],
                    "OUI" if s in C.STATUTS_ENVOI_AUTORISE else "NON"])
    ws3.column_dimensions["A"].width = 18
    ws3.column_dimensions["B"].width = 95
    ws3.column_dimensions["C"].width = 16

    wb.save(chemin)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--source", required=True,
                   help="ZIP ou fichier PS_LibreAcces_Personne_activite")
    p.add_argument("--campagne", action="append",
                   help="limiter a une campagne (repetable)")
    p.add_argument("--date-source", default=date.today().isoformat(),
                   help="date de l'extraction ANS (AAAA-MM-JJ)")
    p.add_argument("--audit-libelles", action="store_true",
                   help="lister les libelles de specialite rencontres en IdF, sans produire de fichier")
    args = p.parse_args()

    if not os.path.exists(args.source):
        print("ERREUR : source introuvable : %s" % args.source, file=sys.stderr)
        return 2

    campagnes = {k: v for k, v in C.CAMPAGNES.items()
                 if not args.campagne or k in args.campagne}
    if not campagnes:
        print("ERREUR : campagne inconnue. Choix : %s" % ", ".join(C.CAMPAGNES),
              file=sys.stderr)
        return 2

    res, vus, retenus, nom_fichier, lignes = lire_et_filtrer(
        args.source, campagnes, args.audit_libelles)
    print("Lignes lues : %d" % lignes)

    if args.audit_libelles:
        print("\n=== Libelles de savoir-faire rencontres en Ile-de-France ===")
        for lib, n in vus.most_common():
            marque = ""
            for cle, camp in C.CAMPAGNES.items():
                if correspond(C.normaliser(lib), camp):
                    marque = "  <-- capte par %s" % cle
            print("%7d  %s%s" % (n, lib, marque))
        return 0

    for cle, enregs in res.items():
        dossier = os.path.join(C.RACINE, cle)
        os.makedirs(dossier, exist_ok=True)
        chemin = os.path.join(dossier, "base_rpps_%s.xlsx" % cle.split("_", 1)[1].lower())
        lignes_f = [finaliser(r, nom_fichier, args.date_source) for r in enregs.values()]
        lignes_f.sort(key=lambda l: (l["Departement"], C.normaliser(l["Nom"]),
                                     C.normaliser(l["Prenom"])))
        ecrire_excel(cle, lignes_f, chemin, C.CAMPAGNES[cle])
        par_dep = Counter(l["Departement"] for l in lignes_f)
        print("\n[%s] %d professionnels uniques (deduplication par RPPS) -> %s"
              % (cle, len(lignes_f), os.path.relpath(chemin, C.RACINE)))
        print("   repartition : " + ", ".join("%s=%d" % (d, par_dep[d])
                                              for d in sorted(par_dep)))
        print("   libelles RPPS captes :")
        for lib, n in retenus[cle].most_common():
            print("      %6d  %s" % (n, lib))
        print("   >>> A VALIDER PAR UN HUMAIN : ces libelles correspondent-ils bien a la cible ?")
    return 0


if __name__ == "__main__":
    sys.exit(main())
