import hashlib
from dataclasses import dataclass, field

from langchain_chroma import Chroma
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq

import config
from knowledge import trouver_faits

#Modifier ce prompt en fonction des besoins

SYSTEM_PROMPT = """Tu es Saul, un assistant juridique expert en droit marocain et, quand c'est pertinent, en droit européen (RGPD).

Règles de réponse :
- Réponds directement, en 3 à 6 lignes, avec l'essentiel et une courte explication. Pas d'introduction ni de formule de politesse.
- Donne les chiffres, durées et délais EXACTS. Cite l'article de loi seulement si tu en es sûr.
- Si des « FAITS VÉRIFIÉS » sont fournis, ils priment sur tout le reste : ne change jamais leurs chiffres.
- Utilise ensuite les extraits de textes de loi, puis les résultats web, pour compléter.
- Si la loi marocaine et la loi française diffèrent, donne la règle MAROCAINE (précise la française seulement si utile).
- Ne parle jamais de « PDF », d'« extraits », de « contexte » ou de « documents fournis » : réponds comme un avocat qui connaît la loi.
- Si l'information n'est pas certaine, dis-le en une phrase et indique quoi vérifier (texte, administration compétente).
- Utilise des listes à puces courtes quand il y a plusieurs conditions ou étapes."""


@dataclass
class Reponse:
    texte: str
    sources: list = field(default_factory=list)   # [{"fichier": ..., "page": ...}]
    fait_verifie: bool = False


class AssistantJuridique:
    def __init__(self):
        if not config.GROQ_API_KEY:
            raise RuntimeError(
                "GROQ_API_KEY manquante."
            )
        if not config.DB_DIR.exists():
            raise RuntimeError(
                f"Base vectorielle introuvable ({config.DB_DIR})"
            )

        print("Chargement de la base vectorielle...")
        from indexation import get_embeddings  

        self.db = Chroma(
            collection_name=config.COLLECTION_NAME,
            embedding_function=get_embeddings(),
            persist_directory=str(config.DB_DIR),
        )
        nb = self.db._collection.count()
        if nb == 0:
            raise RuntimeError(
                f"La collection « {config.COLLECTION_NAME} » est vide. Relance python src/indexation.py"
            )
        print(f"Base chargée ✓ ({nb} segments)")

        self.retriever = self.db.as_retriever(
            search_type="mmr",
            search_kwargs={"k": config.RETRIEVER_K, "fetch_k": config.RETRIEVER_FETCH_K},
        )
        self.llm = ChatGroq(
            model=config.GROQ_MODEL,
            api_key=config.GROQ_API_KEY,
            temperature=config.TEMPERATURE,
        )
        self._cache_web: dict[str, str] = {}

    # ── Sources d'information ─────────────────────────────────
    def rechercher_pdf(self, question: str):
        try:
            return self.retriever.invoke(question)
        except Exception as e:
            print(f"[retriever] erreur : {e}")
            return []

    def rechercher_web(self, question: str) -> str:
        if not config.WEB_SEARCH_ENABLED:
            return ""
        cle = hashlib.md5(question.lower().strip().encode()).hexdigest()
        if cle in self._cache_web:
            return self._cache_web[cle]
        try:
            from ddgs import DDGS

            resultats = DDGS().text(
                f"{question} droit marocain loi Maroc",
                region="fr-fr",
                max_results=config.WEB_MAX_RESULTS,
            )
            texte = "\n".join(f"- {r.get('title', '')} : {r.get('body', '')}" for r in resultats or [])
        except Exception as e:  
            print(f"[web] recherche indisponible : {e}")
            texte = ""
        self._cache_web[cle] = texte
        return texte

    # ── Génération ────────────────────────────────────────────
    def repondre(self, question: str, historique: list | None = None) -> Reponse:
        question = question.strip()
        faits = trouver_faits(question)
        docs = self.rechercher_pdf(question)
        web = self.rechercher_web(question)

        blocs = []
        if faits:
            blocs.append("FAITS VÉRIFIÉS (prioritaires) :\n" + "\n".join(f"- {f}" for f in faits))
        if docs:
            extraits = "\n\n".join(
                f"[{d.metadata.get('source_file', '?')} p.{d.metadata.get('page', '?')}]\n{d.page_content}"
                for d in docs
            )
            blocs.append("EXTRAITS DE TEXTES DE LOI :\n" + extraits)
        if web:
            blocs.append("RÉSULTATS WEB (à recouper, moins fiables) :\n" + web)
        contexte = "\n\n".join(blocs) or "(aucune information complémentaire)"

        messages = [SystemMessage(content=SYSTEM_PROMPT)]
        for m in (historique or [])[-2 * config.HISTORY_TURNS :]:
            cls = HumanMessage if m.get("role") == "user" else AIMessage
            messages.append(cls(content=str(m.get("content", ""))[:2000]))
        messages.append(HumanMessage(content=f"{contexte}\n\nQUESTION : {question}"))

        texte = self.llm.invoke(messages).content.strip()

        sources, vues = [], set()
        for d in docs:
            cle = (d.metadata.get("source_file", "?"), d.metadata.get("page", "?"))
            if cle not in vues:
                vues.add(cle)
                sources.append({"fichier": cle[0], "page": cle[1]})
        return Reponse(texte=texte, sources=sources, fait_verifie=bool(faits))
