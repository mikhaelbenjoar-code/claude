# État d'avancement

Dernière mise à jour : 2026-09-18.
Ce fichier est la mémoire du projet : il permet de reprendre le travail sans
rien perdre et sans dépendre de l'historique de la conversation.

---

## Tableau d'avancement

| Étape | État | Détail |
|---|---|---|
| 0. Lecture des `AGENTS.md` | Fait | **Aucun `AGENTS.md` n'existe** dans le dossier de travail (dépôt vide, un README d'une ligne). Aucune consigne locale à appliquer. |
| 1. Création des 4 projets | **Fait** | 4 dossiers, référentiels, procédures, outillage. |
| 2. Constitution des bases RPPS | **Bloqué** | Accès réseau refusé. Voir `BLOCAGES.md`. Chaîne de traitement écrite et testée. |
| 3. Déduplication RPPS + regroupement des lieux | **Prêt, non exécuté** | Implémenté et validé sur jeu d'essai. Attend les données. |
| 4. Vérification Doctolib Connect | **Bloqué** | Aucun accès au compte. Aucune recherche effectuée, aucun « cas patient » créé. |
| 5. Classement par statut | Prêt | Référentiel fermé, liste déroulante dans Excel. |
| 6. Projets de message | **Fait — en attente de validation** | 4 projets rédigés, mentions RGPD obligatoires intégrées, à corriger et valider. |
| 6 bis. Conformité | **Fait — 4 vérifications ouvertes** | Voir ci-dessous et `CONFORMITE.md`. |
| 7. Envois | **Aucun** | 0 message envoyé. Verrouillé tant que les textes ne sont pas validés. |

---

## Chiffres au 2026-09-18

| Campagne | Recensés | Vérifiés | Exacts | Ambigus | Envoyés |
|---|---:|---:|---:|---:|---:|
| Endocrinologues | 0 | 0 | 0 | 0 | 0 |
| ORL / chirurgie cervico-faciale | 0 | 0 | 0 | 0 | 0 |
| Rhumatologues | 0 | 0 | 0 | 0 | 0 |
| Orthopédistes / traumatologues | 0 | 0 | 0 | 0 | 0 |

Tous les zéros s'expliquent par les blocages d'accès, **pas** par une absence de
professionnels. Chiffres recalculés par `python3 outils/02_bilan.py`.

---

## Vérifications de conformité — préalables à tout envoi

Issues de la recherche du 2026-09-18 (`00_COMMUN/CONFORMITE.md`). Les deux
premières peuvent remettre en cause la campagne entière.

| # | À vérifier | Auprès de qui | État |
|---|---|---|---|
| C1 | Le centre est-il un « centre de santé » au sens de L.6323-1 CSP ? Si oui, L.6323-1-9 interdit toute publicité. | vous / votre conseil | **ouvert** |
| C2 | La Charte de réutilisation RPPS admet-elle la prospection confraternelle ? | support ANS | **ouvert** |
| C3 | Les CGU Doctolib Connect autorisent-elles une prise de contact non sollicitée via l'annuaire, même manuelle ? | Doctolib | **ouvert** |
| C4 | Position ordinale sur un courrier de présentation de plateau technique. | conseil départemental de l'Ordre | **ouvert** |

À noter : l'extraction RPPS en libre accès **ne contient aucune coordonnée de
contact personnelle** — seulement l'identité, les qualifications et les
coordonnées de structure. Elle permet d'identifier les correspondants, pas de les
joindre. C'est pourquoi C3 est structurant.

## Décisions attendues du Dr Benjoar

1. **Contenu des messages** — corriger les quatre `projet_message.md`. Chaque
   affirmation clinique non vérifiée y est isolée dans un tableau à cocher.
   Aucun texte ne partira tant que des crochets subsistent.
2. **Données RPPS** — autoriser les hôtes, ou déposer le fichier dans
   `donnees_source/` (voir `BLOCAGES.md`).
3. **Vérification Connect** — vérification manuelle par le centre, ou
   vérification assistée avec accès explicitement autorisé au compte.
4. **Périmètre des spécialités** — deux choix par défaut à confirmer :
   - l'endocrinologie **pédiatrique** est exclue ;
   - la chirurgie orthopédique **pédiatrique** est exclue.
   Modifiables dans `outils/config.py` (`motifs_exclusion`).

---

## Reprise du travail

```bash
python3 outils/test_journal.py     # vérifier les garde-fous
python3 outils/journal.py          # vérifier l'intégrité des journaux
python3 outils/02_bilan.py         # recalculer tous les chiffres
```

Aucune étape ne dépend de la mémoire de la conversation : tout l'état est sur le
disque.
