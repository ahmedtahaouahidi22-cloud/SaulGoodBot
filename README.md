# ⚖️ SaulGoodBot : assistant juridique marocain (RAG)

Projet académique réalisé dans le cadre du cours d'Agent IA,Ensam Rabat, 2025-2026.

SaulGoodBot répond en français à des questions de droit marocain (travail, données personnelles, consommation, commerce). Il repose sur une architecture **RAG** (*Retrieval-Augmented Generation*) : le modèle de langage ne répond pas de mémoire, il rédige à partir de sources que le système lui fournit.

> ⚠️ **Avertissement** : ce projet est un prototype pédagogique. Il ne fournit pas de conseil juridique et ne remplace ni un avocat, ni les textes officiels.

---

## 1. Objectifs du projet

- Concevoir un pipeline RAG complet : ingestion de documents, vectorisation, recherche sémantique, génération.
- Limiter les erreurs factuelles d'un LLM sur des données chiffrées (congés, SMIG, délais) en les isolant dans une base de faits vérifiés qui prime sur les autres sources.
- Comparer et combiner plusieurs sources : faits vérifiés, textes de loi indexés, recherche web.

## 2. Fonctionnement

À chaque question, le système interroge trois sources, puis assemble un prompt pour le LLM :

```
Question ─┬─> knowledge.trouver_faits()  ── faits vérifiés (prioritaires)
          ├─> ChromaDB (MMR, k=5)         ── extraits des lois + numéro de page
          └─> ddgs (recherche web)        ── résultats complémentaires (optionnel)
                     │
                     ▼
         Prompt système + historique (3 derniers échanges)
                     │
                     ▼
         LLM hébergé sur Groq  ──>  réponse courte + sources
```

| Composant | Rôle |
|---|---|
| `knowledge.py` | Faits juridiques vérifiés à la main. Ils priment sur les extraits et le web, et le LLM ne doit pas modifier leurs chiffres. La correspondance se fait par groupes de mots-clés, sans tenir compte des accents. |
| ChromaDB | Base vectorielle contenant les textes de loi découpés en segments. Recherche sémantique avec MMR (*Maximal Marginal Relevance*) pour limiter les doublons. |
| Embeddings | `paraphrase-multilingual-MiniLM-L12-v2` (multilingue, adapté au français). |
| Recherche web | DuckDuckGo via `ddgs`. Ses résultats sont considérés comme moins fiables que les deux autres sources. |
| LLM | Modèle hébergé sur Groq (voir `.env`), appelé via `langchain-groq`. |
| Mémoire | Les 3 derniers échanges sont renvoyés au modèle. |

## 3. Technologies

Python 3.10 à 3.12 · LangChain (`langchain-core`, `langchain-chroma`, `langchain-huggingface`, `langchain-groq`) · ChromaDB · Sentence-Transformers · Groq API · ddgs

## 4. Structure du dépôt

```
SaulGoodBot/
├── data/                  ← PDF juridiques (non fournis, voir §5)
├── db_juridique/          ← base ChromaDB (générée, non versionnée)
├── src/
│   ├── config.py          ← lecture du .env (clé, modèle, chemins, réglages)
│   ├── ingestion.py       ← lecture des PDF et découpage en segments
│   ├── indexation.py      ← vectorisation et stockage dans ChromaDB
│   ├── knowledge.py       ← faits vérifiés
│   ├── rag.py             ← moteur (faits + PDF + web + LLM)
│   └── cli.py             ← interface en ligne de commande
├── tests/
│   └── test_questions.py  ← banc de test, écrit tests/resultats.md
├── .env.example           ← modèle du fichier de configuration
├── requirements.txt
└── README.md
```

## 5. Installation

**Prérequis** : Python 3.10 à 3.12 et une clé API Groq (gratuite sur [console.groq.com](https://console.groq.com)).

```bash
git clone https://github.com/ahmedtahaouahidi22-cloud/SaulGoodBot.git
cd SaulGoodBot
python -m venv venv
```

Activation de l'environnement :

```bash
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate
```

Puis :

```bash
pip install -r requirements.txt
```

Copie `.env.example` vers `.env` (`copy` sous Windows, `cp` sous Linux/macOS) et renseigne ta clé :

```
GROQ_API_KEY=gsk_...
```


**Documents juridiques.** Place les PDFs dans `data/` (ils doivent contenir du texte, pas des scans). Sources publiques possibles :

- Secrétariat général du gouvernement : [sgg.gov.ma](https://www.sgg.gov.ma)
- Adala (ministère de la Justice) : [adala.justice.gov.ma](https://adala.justice.gov.ma)
- CNDP : [cndp.ma](https://www.cndp.ma)

Textes visés : Code du travail (loi 65-99), loi 09-08 (données personnelles), loi 31-08 (protection du consommateur), Code de commerce, DOC.

## 6. Utilisation

**1. Indexer les documents** :

```bash
python src/indexation.py
```

Au premier lancement, le modèle d'embedding (environ 470 Mo) est téléchargé une seule fois.

**2. Lancer l'assistant en terminal :**

```bash
python src/cli.py
```


## 3. Configuration

Les réglages se trouvent dans `.env` (voir `.env.example`) :

| Variable | Rôle |
|---|---|
| `GROQ_API_KEY` | Clé API Groq (obligatoire) |
| `GROQ_MODEL` | Modèle utilisé. Groq retire régulièrement d'anciens modèles : consulte la [liste des dépréciations](https://console.groq.com/docs/deprecations) si tu obtiens une erreur 404 |
| `EMBEDDING_MODEL` | Modèle d'embedding. Après un changement, relance `indexation.py` |
| `RETRIEVER_K`, `CHUNK_SIZE` | Nombre d'extraits récupérés et taille des segments |
| `WEB_SEARCH_ENABLED` | `false` pour répondre uniquement avec les faits et les PDF |

Pour modifier le ton ou la longueur des réponses, voir `SYSTEM_PROMPT` dans `src/rag.py`.

## 4. Dépannage

| Message | Solution |
|---|---|
| `GROQ_API_KEY manquante` | `.env` absent ou clé vide |
| `Base vectorielle introuvable` / collection vide | Lancer `python src/indexation.py` |
| `no such column: collections.topic` | Base créée avec une autre version de ChromaDB : relancer `indexation.py` |
| `ImportError … langchain…` | Créer un venv neuf puis réinstaller `requirements.txt` |
| `model_not_found` (404) | Le modèle Groq configuré n'existe plus : en choisir un autre dans `.env` |
| `429 rate limit` | Limite du plan gratuit Groq : attendre quelques secondes |
| `Web search error` / `ratelimit` | DuckDuckGo limite les requêtes. L'assistant répond sans le web |
| `Aucun texte extrait (PDF scanné ?)` | Passer le PDF dans un OCR (par exemple `ocrmypdf`) |

## 5. Limites

- La qualité des réponses dépend de la qualité des PDF indexés et de la mise à jour des faits vérifiés (le SMIG, par exemple, change régulièrement).
- Les faits de `knowledge.py` ont été saisis manuellement. Ils doivent être relus sur les textes officiels avant toute utilisation sérieuse.
- La recherche web peut remonter des sources peu fiables.
- Un LLM peut produire des réponses inexactes malgré le RAG. Les sources affichées doivent être vérifiées.
- Le projet ne couvre que quelques domaines du droit marocain.

## 6. Pistes d'amélioration

- Évaluation quantitative plus poussée (jeu de questions annotées, métriques de fidélité et de pertinence).
- Interface web.
- Extension du corpus juridique.

