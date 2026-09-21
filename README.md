# SmartDoc DSI

**Assistant IA de recherche dans la documentation interne de la Direction des Systèmes d'Information (DSI).**

SmartDoc DSI est un chatbot documentaire basé sur la technique **RAG** (*Retrieval-Augmented Generation*). Il permet aux équipes DSI de poser des questions en langage naturel et d'obtenir des réponses fondées sur les procédures et politiques internes, avec citation des sources.

---

## Fonctionnalités

- **Recherche sémantique** dans une base documentaire interne (Markdown)
- **Réponses en français**, structurées et concises
- **Citation des documents sources** utilisés pour générer la réponse
- **API REST** simple via FastAPI (`POST /ask`)
- **Mode démo** sans clé OpenAI (embeddings locaux + extraits bruts)
- **Support multi-fournisseur** : OpenAI ou Ollama (100 % local)
- **Conteneurisation Docker** pour un déploiement rapide

---

## Architecture

```
Utilisateur
    │
    ▼
FastAPI (main.py)          ← POST /ask
    │
    ▼
RAG Engine (rag_engine.py)
    │
    ├── Chargement docs/ (.md, .txt)
    ├── Découpage en chunks (500 tokens, overlap 80)
    ├── Embeddings → ChromaDB (chroma_db/)
    ├── Retrieval (top 4 chunks pertinents)
    └── LLM (OpenAI / Ollama) → réponse contextualisée
```

### Pipeline RAG

1. **Indexation** — Les fichiers du dossier `docs/` sont chargés, découpés en segments, puis vectorisés et stockés dans ChromaDB.
2. **Requête** — La question de l'utilisateur est convertie en vecteur et comparée aux chunks indexés.
3. **Génération** — Les passages les plus pertinents sont injectés dans le prompt système, puis le LLM produit une réponse en s'appuyant uniquement sur ce contexte.

---

## Stack technique

| Composant        | Technologie                                      |
|------------------|--------------------------------------------------|
| API              | FastAPI + Uvicorn                                |
| Orchestration IA | LangChain                                        |
| Base vectorielle | ChromaDB                                         |
| Embeddings       | OpenAI / Ollama / HuggingFace (mode démo)        |
| LLM              | GPT-4o-mini (OpenAI) ou Llama 3.2 (Ollama)       |
| Conteneur        | Docker (Python 3.10)                             |

---

## Structure du projet

```
smartdoc-dsi/
├── docs/                      # Documentation DSI indexée par le RAG
│   ├── procedure_db.md        # Redémarrage PostgreSQL
│   ├── regles_securite.md     # Politique mots de passe & clés API
│   ├── acces_reseau.md        # Déblocage accès VPN
│   └── sauvegarde_restore.md  # Sauvegarde et restauration des données
├── rag_engine.py              # Moteur RAG (indexation, retrieval, génération)
├── main.py                    # Point d'entrée FastAPI
├── requirements.txt           # Dépendances Python
├── Dockerfile                 # Image Docker
├── .env.example               # Variables d'environnement (modèle)
└── .gitignore
```

---

## Documentation indexée

| Fichier                  | Contenu                                              |
|--------------------------|------------------------------------------------------|
| `procedure_db.md`        | Procédure de redémarrage PostgreSQL (prod/pré-prod) |
| `regles_securite.md`     | Exigences mots de passe, MFA, gestion des clés API   |
| `acces_reseau.md`        | Diagnostic et déblocage VPN FortiClient              |
| `sauvegarde_restore.md`  | Politique de sauvegarde et restauration PostgreSQL   |

> Ces documents sont **fictifs** et servent de jeu de données de démonstration pour le projet.

---

## Prérequis

- Python 3.10+
- [Docker](https://www.docker.com/) (optionnel)
- Clé API OpenAI **ou** instance [Ollama](https://ollama.com/) locale

---

## Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/FATYLS/smartdoc-dsi.git
cd smartdoc-dsi
```

### 2. Environnement virtuel

```bash
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
pip install -r requirements.txt
```

### 3. Configuration

```bash
cp .env.example .env
```

Éditez `.env` selon le fournisseur choisi :

**OpenAI (recommandé en production) :**
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-votre-cle-ici
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBED_MODEL=text-embedding-3-small
```

**Ollama (100 % local) :**
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
OLLAMA_EMBED_MODEL=nomic-embed-text
```

**Mode démo (sans clé API) :** laissez `OPENAI_API_KEY=sk-your-key-here` — le système utilise des embeddings HuggingFace locaux et retourne les extraits pertinents sans génération LLM.

### 4. Lancer l'API

```bash
uvicorn main:app --reload --port 8000
```

L'API est disponible sur **http://localhost:8000**  
Documentation interactive : **http://localhost:8000/docs**

---

## Docker

```bash
docker build -t smartdoc-dsi .
docker run -p 8000:8000 --env-file .env smartdoc-dsi
```

---

## Utilisation de l'API

### Vérifier l'état du service

```bash
curl http://localhost:8000/health
```

Réponse :
```json
{"status": "ok"}
```

### Poser une question

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Comment redémarrer PostgreSQL ?"}'
```

Réponse :
```json
{
  "question": "Comment redémarrer PostgreSQL ?",
  "answer": "..."
}
```

### Exemples de questions

- *« Quelle est la politique de mots de passe pour les comptes privilégiés ? »*
- *« Comment débloquer un accès VPN ? »*
- *« Quelle est la rétention des sauvegardes PostgreSQL ? »*
- *« Où stocker une clé API ? »*

---

## Ajouter de la documentation

1. Placez vos fichiers `.md` ou `.txt` dans le dossier `docs/`
2. Supprimez le cache vectoriel pour forcer la réindexation :
   ```bash
   rm -rf chroma_db/
   ```
3. Relancez l'API — l'index sera reconstruit automatiquement au premier appel

---

## Variables d'environnement

| Variable              | Défaut                        | Description                              |
|-----------------------|-------------------------------|------------------------------------------|
| `LLM_PROVIDER`        | `openai`                      | Fournisseur LLM : `openai` ou `ollama`   |
| `OPENAI_API_KEY`      | —                             | Clé API OpenAI                           |
| `OPENAI_MODEL`        | `gpt-4o-mini`                 | Modèle de chat OpenAI                    |
| `OPENAI_EMBED_MODEL`  | `text-embedding-3-small`      | Modèle d'embeddings OpenAI               |
| `OLLAMA_BASE_URL`     | `http://localhost:11434`      | URL du serveur Ollama                    |
| `OLLAMA_MODEL`        | `llama3.2`                    | Modèle de chat Ollama                    |
| `OLLAMA_EMBED_MODEL`  | `nomic-embed-text`            | Modèle d'embeddings Ollama               |

---

## Contexte projet

Ce projet a été réalisé dans le cadre d'une **initiation à l'IA appliquée à la DSI** : mise en place d'un assistant documentaire capable de répondre aux questions opérationnelles des équipes infrastructure, sécurité et support, à partir d'une base de connaissances interne.

---

## Auteur

**FATYLS** — [github.com/FATYLS](https://github.com/FATYLS)

---

## Licence

Projet éducatif — usage libre à des fins d'apprentissage.
