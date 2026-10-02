---
name: devops-education
description: À utiliser à CHAQUE étape du projet jlm-vs-mlp qui touche au code, à la CI/CD, aux données, aux secrets, à l'infra ou au déploiement. Fait respecter les principes DevOps et oblige à mettre à jour dev-ops-education-followup.html pour expliquer visuellement à l'utilisateur (data scientist qui apprend le DevOps) chaque concept introduit.
---

# Éducation DevOps — jlm-vs-mlp

L'utilisateur est data scientist et apprend le DevOps via ce projet. Livrer du code ne suffit pas :
chaque étape doit **respecter** les principes ci-dessous ET les **enseigner**.

## 1. Avant de coder : vérifier les principes

| # | Principe | Question à se poser |
|---|---|---|
| P1 | Tout est code et versionné | La config, la CI, le schéma de données sont-ils dans git ? |
| P2 | Automatiser | Une étape manuelle répétée peut-elle devenir un job CI/cron ? |
| P3 | Petits changements, main toujours vert | Une branche + une PR par sujet, CI verte avant merge ? |
| P4 | Sécurité dès le départ | Secrets hors du code, moindre privilège, dépendances épinglées, entrées non fiables traitées comme telles (tweets → injection de prompt) ? |
| P5 | Reproductibilité | Lockfile à jour, version du prompt/modèle enregistrée avec chaque résultat ? |
| P6 | Idempotence | Relancer le job deux fois donne-t-il le même état (pas de doublons, pas de double facture) ? |
| P7 | Observabilité | Si ça casse à 3h du matin, comment le sait-on ? Logs, alerte, fraîcheur, coût ? |
| P8 | Feedback rapide | L'erreur est-elle attrapée au plus tôt (pre-commit > CI > prod) ? |
| P9 | Simplicité | Est-ce la solution la plus simple qui marche (pas de serveur/BDD sans besoin démontré) ? |
| P10 | Coûts maîtrisés (FinOps) | Plafond de dépense, cache, coût estimé par run ? |

Un principe volontairement ignoré se dit à l'utilisateur, avec la raison et le moment où on y reviendra.

## 2. Après chaque étape : mettre à jour `dev-ops-education-followup.html`

Fichier unique, autonome (aucune dépendance externe), à la racine du repo. **Le lire d'abord** :
il sert de gabarit — réutiliser ses classes CSS et sa structure, ne jamais le réécrire de zéro.

1. **Timeline** (`#timeline`) : passer l'étape terminée à `done`, la suivante à `doing`.
2. **Nouvelle section d'étape** (`<section class="step" id="etape-N">`) insérée avant `#glossaire`,
   avec une **carte par concept** (un concept = une carte, jamais deux concepts mélangés) :
   - **C'est quoi** — une phrase, sans jargon non défini.
   - **Pourquoi** — le problème concret que ça évite.
   - **Chez nous** — fichier(s) ou commande(s) exacts du repo.
   - **Schéma** — un `.flow` (boîtes + flèches) ou `.layers` (couches) ; visuel obligatoire.
   - **Analogie data science** — relier à ce que l'utilisateur connaît (seed, train/test, pipeline sklearn…).
   - **Piège courant** — l'erreur classique.
   - Badges des principes concernés (`P1`…`P10`).
3. **Lien du nav** vers la nouvelle section.
4. **Glossaire** : ajouter chaque nouveau terme (ordre alphabétique).
5. Concept déjà expliqué à une étape précédente → ne pas le redétailler, lier vers sa carte.

## 3. Dans le chat

Terminer l'étape par 3 lignes max : concepts ajoutés au fichier + principe(s) clé(s) de l'étape.
Tout en français.
