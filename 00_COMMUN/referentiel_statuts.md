# Référentiel des statuts Doctolib Connect

Vocabulaire fermé. Les scripts refusent toute autre valeur, et la colonne
`Statut_Connect` des classeurs Excel n'accepte que cette liste.

| Statut | Définition | Envoi autorisé |
|---|---|---|
| `NON_VERIFIE` | Pas encore recherché dans l'annuaire Connect. État initial de toute ligne issue du RPPS. | Non |
| `EXACT` | Nom, prénom, spécialité et au moins un lieu d'exercice concordent. Correspondance certaine. | **Oui**, et seulement après validation écrite du texte |
| `A_CONFIRMER` | Un profil est trouvé, mais la spécialité ou l'identité n'est pas suffisamment certaine. | Non |
| `AMBIGU` | Plusieurs candidats, homonyme non départageable, ou données contradictoires. | Non — vérification humaine |
| `ABSENT` | Aucun profil dans l'annuaire Connect, ou professionnel n'utilisant pas Connect. | Non |
| `DEJA_CONTACTE` | A déjà reçu une présentation du centre. | Non — ne pas solliciter à nouveau |
| `EXCLU` | Exclusion nominative demandée par le Dr Benjoar. | Non — jamais |

## Règle de décision

Une correspondance n'est classée `EXACT` que si **tous** ces points sont vérifiés
dans l'annuaire Connect :

1. Nom **et** prénom concordent (y compris nom d'usage / nom de jeune fille) ;
2. la spécialité affichée sur Connect correspond à la spécialité RPPS ciblée ;
3. au moins un lieu d'exercice concorde avec la base RPPS (ville ou adresse) ;
4. aucun autre professionnel de la même spécialité ne porte le même nom dans le
   périmètre, ou bien les homonymes sont départagés sans ambiguïté par le lieu.

Si l'un de ces points échoue : `A_CONFIRMER` ou `AMBIGU`, jamais `EXACT`.
**En cas de doute, on ne classe pas `EXACT` et on n'envoie rien.**

## Règle de non-affirmation

Un envoi n'est consigné dans le journal que si l'interface Doctolib affiche
explicitement sa confirmation, et le champ `confirmation_interface` décrit ce
qui a été réellement affiché. Aucune lecture, acceptation ou mise en relation
n'est jamais déclarée sans confirmation explicite de l'interface.
