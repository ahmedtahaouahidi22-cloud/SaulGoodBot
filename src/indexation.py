import shutil

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

import config
from ingestion import charger_et_decouper_pdf


def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name=config.EMBEDDING_MODEL,
        encode_kwargs={"normalize_embeddings": True},
    )


def creer_base_vectorielle():
    print("Récupération des segments de texte...")
    segments = charger_et_decouper_pdf(config.DATA_DIR)
    if not segments:
        raise SystemExit("Aucun segment à indexer.")

    if config.DB_DIR.exists():
        print(f"Suppression de l'ancienne base {config.DB_DIR.name}/ ...")
        shutil.rmtree(config.DB_DIR)

    print(f"Chargement du modèle d'embedding {config.EMBEDDING_MODEL} (1re fois : téléchargement)...")
    embeddings = get_embeddings()

    print("Création de la base vectorielle...")
    db = Chroma(
        collection_name=config.COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(config.DB_DIR),
    )
    # Ajout par lots pour ne pas saturer la mémoire avec de gros codes
    lot = 200
    for i in range(0, len(segments), lot):
        db.add_documents(segments[i : i + lot])
        print(f"   {min(i + lot, len(segments))}/{len(segments)} segments indexés")

    print(f"\nSuccès ! Base prête dans {config.DB_DIR} (collection « {config.COLLECTION_NAME} »).")
    return db


if __name__ == "__main__":
    creer_base_vectorielle()
