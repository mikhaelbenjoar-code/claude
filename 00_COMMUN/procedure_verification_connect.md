# Procédure de vérification sur Doctolib Connect

À appliquer professionnel par professionnel, dans l'ordre du classeur Excel.

## Cadre strict

- Utiliser **uniquement** la messagerie professionnelle et la recherche de
  professionnels du compte Connect.
- **Ne créer aucun « cas patient »**, aucune demande d'avis, aucun dossier.
- Doctolib Connect uniquement. **Aucune campagne LinkedIn.**

## Étapes pour chaque ligne

1. **Recherche** : rechercher « Nom Prénom », puis si besoin « Nom » + ville.
   Noter la requête exacte effectuée.
2. **Comparaison** : confronter nom, prénom, spécialité, ville et lieux
   d'exercice du profil Connect avec la ligne RPPS.
3. **Classement** : appliquer `00_COMMUN/referentiel_statuts.md`. En cas de
   doute, `A_CONFIRMER` ou `AMBIGU` — jamais `EXACT`.
4. **Consignation immédiate**, même en cas de résultat négatif :

   ```python
   import sys; sys.path.insert(0, "outils")
   import journal as J
   J.consigner_recherche(
       campagne="03_RHUMATOLOGUES", rpps="...", nom="...", prenom="...",
       requete="Nom Prénom", nb_resultats=2,
       candidats=["profil A — rhumatologue, Créteil", "profil B — MPR, Paris 12e"],
       statut="AMBIGU", motif="Deux profils homonymes, spécialités proches.")
   ```
5. **Ambiguïté** : reporter la ligne dans `ambiguites_a_verifier.csv` en
   décrivant les candidats trouvés et la raison précise du doute, pour qu'une
   vérification humaine soit possible.
6. Mettre à jour `Statut_Connect` dans le classeur Excel.

## Avant tout envoi (après validation du texte par le Dr Benjoar)

1. Contrôle programmatique obligatoire :

   ```python
   autorise, motif = J.peut_envoyer(campagne, rpps, nom, prenom, statut, profil_connect)
   ```

   Il refuse : statut ≠ `EXACT`, exclusion nominative, et tout professionnel
   déjà contacté — y compris dans une autre campagne, via un autre compte
   Connect ou un autre lieu d'exercice.
2. **Ouvrir la conversation du destinataire et lire son historique.** Le
   contrôle programmatique ne remplace pas cette vérification visuelle : un
   échange antérieur hors journal doit être détecté.
3. **Saisie du message** : coller le texte **en bloc, en texte brut**, en une
   seule opération. Ne jamais saisir caractère par caractère : les retours à
   la ligne partiraient comme autant de messages séparés.
4. Après envoi, vérifier ce que l'interface affiche réellement, puis consigner
   avec `J.consigner_envoi(...)` en décrivant cette confirmation.

## Après toute erreur de saisie, de navigation ou de destinataire

Ne pas recommencer immédiatement. Vérifier d'abord, dans cet ordre :
la **conversation** (un message parti ?), le **brouillon** (résidu à effacer ?),
l'**historique** du destinataire. Consigner l'incident dans le journal des
recherches avant toute reprise.
