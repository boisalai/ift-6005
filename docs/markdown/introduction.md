# Introduction


[!CAUTION]
> Document de travail en cours de rédaction.

Les principales différences entre RAG et agents :

RAG (Retrieval-Augmented Generation)[^1] :
- Se concentre sur l'enrichissement du contexte en récupérant des informations pertinentes depuis des sources externes
- Processus en 2 étapes : récupération puis génération
- Utilise principalement la recherche documentaire comme outil

Agents[^1] :
- Peuvent utiliser de nombreux outils différents, dont RAG n'est qu'un exemple
- Capables de planifier et d'exécuter des séquences d'actions complexes
- Peuvent interagir directement avec leur environnement via des actions de lecture/écriture
- Nécessitent des capacités de planification et de réflexion
- Peuvent combiner plusieurs outils pour accomplir des tâches complexes

En résumé, RAG est un cas particulier d'agent où l'outil principal est la recherche documentaire. Les agents sont plus polyvalents car ils peuvent utiliser divers outils et planifier des séquences d'actions pour atteindre leurs objectifs.

[^1]: Huyen, C. (2025). *AI Engineering: Building Applications with Foundation Models*. O'Reilly Media.