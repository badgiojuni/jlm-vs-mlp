---
name: daily-report
description: À utiliser sur le projet jlm-vs-mlp à la fin de chaque journée de travail, quand l'utilisateur demande un récap / rapport / point d'avancement, ou en début de session si la dernière journée travaillée n'a pas de rapport. Génère followup/AAAA-MM-JJ.html, rapport visuel de ce qui a été fait ce jour-là.
---

# Rapport quotidien — jlm-vs-mlp

Un fichier par jour travaillé : `followup/AAAA-MM-JJ.html`. Autonome (aucune dépendance externe), en français.

## Quand

- Fin de journée ou demande de récap → créer (ou compléter) le rapport du jour.
- Début de session : si des commits existent pour une journée sans rapport → le générer d'abord.
- Le rapport du jour existe déjà → le **compléter**, ne pas en créer un second.

## Sources (ne rien inventer)

- `git log --since=<jour> --until=<jour+1>` et les PR du jour (`gh pr list --state all`).
- La conversation : décisions, incidents, actions demandées à l'utilisateur.
- Coûts : uniquement ceux réellement loggés (ex. ligne `coût estimé` de `pipeline.ingest`). Inconnu → écrire « non mesuré ».
- Pas d'heure inventée : ordre chronologique sans horodatage si l'heure n'est pas connue.

## Gabarit

**Lire le rapport précédent le plus récent** et réutiliser sa structure et son CSS. Sections, dans l'ordre :

1. **En-tête** : date, une phrase de résumé, lien vers le rapport précédent.
2. **Chiffres du jour** (tuiles) : étapes terminées / total, PR fusionnées, tweets ingérés, coût API du jour.
3. **Avancement** : timeline des étapes (même liste que `#timeline` du carnet DevOps).
4. **Ce qui a été fait** : chronologique, une ligne par action, lien vers le commit ou la PR.
5. **Décisions** : tableau décision / alternative écartée / pourquoi.
6. **Incidents et blocages** : symptôme → cause → résolution (ou « ouvert »).
7. **Concepts DevOps vus** : liens vers les cartes de `../dev-ops-education-followup.html#c-…`, sans réexpliquer.
8. **Prochaines étapes** et **actions attendues de l'utilisateur**.

## Après

Ajouter une ligne en tête de la liste de `followup/README.md` (le plus récent en haut).
Livrer via une branche + PR, comme tout le reste. Dans le chat : lien vers le fichier et 2 lignes de résumé.
