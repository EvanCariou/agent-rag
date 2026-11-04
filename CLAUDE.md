# CLAUDE.md — RAG-Nevezia

Instructions spécifiques au projet d'apprentissage Python RAG.
Ces règles s'appliquent en priorité sur le CLAUDE.md parent pour ce dossier.

---

## Règle d'apprentissage — NON NÉGOCIABLE

Claude Code NE fournit PAS de code complet pour ce projet.
Il guide, explique les concepts, répond aux blocages spécifiques.
Evan apprend de façon autonome via le cours Docstring (YouTube, 7h, français).
On revient à Claude Code uniquement quand bloqué sur un concept précis.
Jamais pour obtenir la solution directement.

Si Evan demande "écris-moi le code pour...", répondre :
"Je t'explique le concept, tu l'écris. Montre-moi ce que tu as tenté."

---

## Objectif du projet

Construire un chatbot capable de répondre à des questions sur Nevezia
en s'appuyant sur les fichiers Markdown du projet.
Ce projet a vocation à devenir l'agent Nevezia construit en Python.

---

## Architecture cible

```
RAG-Nevezia/
├── documents/     ← fichiers Markdown base de connaissance + ScriptRAG.py
├── db/            ← base ChromaDB locale (Module 4)
├── api_rag.env    ← clés API (ne jamais commiter)
├── loader.py      ← lecture fichiers (Module 1)
├── chunker.py     ← découpage en chunks (Module 2)
├── embedder.py    ← appels API embeddings (Module 3)
├── retriever.py   ← recherche ChromaDB (Module 4)
└── chatbot.py     ← chatbot final (Module 5)
```

---

## État d'avancement

**Module 1 — Lecture de fichiers : TERMINÉ**
Acquis : `open()`, `with`, `os.path`, `__file__`, boucle sur fichiers, `list.append()`

**Module 2 — Découpage en chunks : TERMINÉ**
Acquis : `split()`, `join()`, `range(start, stop, step)`, slicing, double boucle, dictionnaires, tuples
Résultat : 22 chunks de 200 mots avec 50 mots de chevauchement

**Module 3 — Embeddings : TERMINÉ**
Acquis : `python-dotenv`, client OpenAI, `client.embeddings.create()`, `reponse.data[0].embedding`
Résultat : 22 vecteurs de 1536 dimensions stockés dans chaque chunk

**Module 4 — ChromaDB : TERMINÉ**
Acquis : `chromadb.PersistentClient(path=)`, `get_or_create_collection()`, `collection.upsert()`, `collection.query()`, `enumerate()`, `str()`
Résultat : 22 chunks insérés dans `db/`, recherche par similarité fonctionnelle

**Module 5 — Chatbot LLM : TERMINÉ**
Acquis : `client.chat.completions.create()`, structure `messages` avec rôles `system`/`user`/`assistant`, injection du contexte RAG, `.choices[0].message.content`
Résultat : RAG complet fonctionnel — question → ChromaDB → contexte → LLM → réponse en français

**Roadmap NEVEN Python (mise à jour 4 mai 2026) :**

Niveau 1 — TERMINÉ :
- Mémoire de conversation (historique messages[] dans la boucle while)
- Logs des chunks utilisés à chaque réponse
- Indexation automatique si nouveaux fichiers détectés

Niveau 2 — TERMINÉ :
- Claude API en remplacement d'OpenAI (embeddings restent OpenAI)
- Streaming des réponses (client.messages.stream())
- Interface Gradio avec thème sombre charte Nevezia
- Lanceur NEVEN.bat pour démarrage en un clic depuis le bureau

Niveau 2.5 — Enrichissement de l'agent :

- ✅ Recherche web en temps réel (API Tavily) — TERMINÉ (1er mai 2026)
- ✅ Upload de fichiers dans l'interface (PDF + texte) — TERMINÉ (4 mai 2026)
- Transcription audio / vocaux entrants (Whisper OpenAI)
- Réflexion profonde (prompt système étendu)

Niveau 3 — App bureautique + mémoire persistante + architecture hybride :
- Encapsulation PyWebView : Gradio → vraie fenêtre native sans navigateur
  (transition fluide, zéro réécriture du code Python existant)
- Mémoire persistante multi-sessions (SQLite)
- Briefing matinal automatique (cron Python)
- Accès Gmail + Google Agenda (API Google)
- Architecture hybride RAG + Second Brain :
  Remplacer les documents bruts par une wiki Markdown structurée (style Karpathy)
  ChromaDB indexe les articles de la wiki (pas des chunks de docs bruts)
  Claude charge les 2-3 articles pertinents via RAG → répond depuis du contenu structuré
  Résultat : accumulation de connaissance + retrieval rapide + coût tokens maîtrisé

Niveau 4 — Long terme :
- Consommer les outputs Veilleur / Analyste / Rédacteur
- NEVEN proactif (décisions autonomes)
- Auto-apprentissage et auto-amélioration
- Interface WhatsApp

Session complète sauvegardée : _bmad-output/brainstorming/brainstorming-session-2026-04-28-001.md

---

## Documentation Notion associée

Page principale : RAG Nevezia — Apprentissage Python & Projet Fil Rouge
Référence concepts pratiques : Référence Python — Concepts Pratiques
Sous-pages par thème : Fichiers et chemins, Chaînes de caractères, Modules standards, Types et variables

Quand un nouveau concept Python est maîtrisé, le documenter dans Notion via MCP.

---

## Comportement dans les sessions

- Lire `chatbot.py` et `indexer.py` directement plutôt que demander à Evan de montrer le code.
  Chemins : `RAG-Nevezia/Script_python/chatbot.py` et `RAG-Nevezia/Script_python/indexer.py`
- `ScriptRAG.py` est l'ancien fichier monolithique, remplacé par `indexer.py` + `chatbot.py`
- Lire les fichiers autonomement sans demander à Evan de les montrer.
- Commiter et pousser sur GitHub après chaque fonctionnalité terminée, sans attendre qu'Evan le demande.

## État Niveau 1 — TERMINÉ (29 avril 2026)

- Mémoire de conversation : `messages[]` initialisé avant la boucle, alimenté à chaque tour
- Logs des chunks : affichage numéroté après chaque réponse (commenté par défaut)
- Indexation automatique : comparaison fichiers `.md` vs métadonnées ChromaDB, relance `indexer.py` si nouveau fichier

## Niveau 2 — TERMINÉ (1er mai 2026)

- Migration Claude API : `client_embedding` (OpenAI) pour les embeddings, `client` (Anthropic) pour le LLM
  - Modèle : `claude-sonnet-4-6`
  - Syntaxe réponse Anthropic : `reponses.content[0].text` (pas `.choices[0].message.content`)
  - `max_tokens` obligatoire dans `client.messages.create()`
  - Prompt système : paramètre `system=` séparé (pas dans `messages[]`)
- Streaming : `client.messages.stream()`, `stream.text_stream`, `stream.get_final_message()`
- Interface Gradio : `gr.Blocks(css=css)` + `gr.ChatInterface(fn=...)`, thème sombre charte Nevezia
- Lanceur NEVEN.bat : `start "" "python.exe" "script.py"`, `timeout /t 3`, `start http://...`

## Niveau 2.5 — En cours

- ✅ Recherche web Tavily (1er mai 2026) :
  - `TavilyClient(api_key=...)`, appel `.search(query=question, max_results=3)`
  - Résultat : dict avec clé `"results"` → liste de dicts avec `"content"`, `"url"`, `"title"`
  - Extraction : `[r["content"] for r in resultat_web["results"]]`
  - Injection : deux contextes séparés (`contexte_interne` ChromaDB + `contexte_web` Tavily)

- ✅ Upload de fichiers (4 mai 2026) :
  - `from pypdf import PdfReader` pour lire les PDF
  - `reader = PdfReader(fichier)`, `reader.pages` → liste de pages, `.extract_text()` par page
  - Détection du type : `fichier.endswith(".pdf")` → pypdf, sinon `open()` classique
  - `gr.ChatInterface(fn=..., additional_inputs=gr.File())` pour exposer l'upload dans Gradio
  - Fonction `telecharger_fichier()` retourne une string vide si aucun fichier uploadé

- Transcription audio Whisper : à faire
- Réflexion profonde : à faire
