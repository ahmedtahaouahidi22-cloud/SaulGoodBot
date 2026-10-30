import re
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

import config


def charger_et_decouper_pdf(directory: Path = config.DATA_DIR):
    directory = Path(directory)
    pdfs = sorted(p for p in directory.iterdir() if p.suffix.lower() == ".pdf")
    if not pdfs:
        raise FileNotFoundError(f"Aucun PDF trouvé dans {directory}. Ajoute tes textes de loi.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\nArticle ", "\nArt. ", "\n\n", "\n", ". ", " ", ""],
    )

    all_chunks = []
    for pdf in pdfs:
        print(f"--- Traitement de : {pdf.name} ---")
        try:
            docs = PyPDFLoader(str(pdf)).load()
        except Exception as e: 
            print(f"   ⚠️  Ignoré ({e})")
            continue

        # Nettoyage léger :
        docs = [d for d in docs if d.page_content and d.page_content.strip()]
        for d in docs:
            d.page_content = re.sub(r"[ \t]+", " ", d.page_content)
            d.page_content = re.sub(r"\n{3,}", "\n\n", d.page_content)
        if not docs:
            print("   ⚠️  Aucun texte extrait (PDF scanné ? il faut un OCR).")
            continue

        chunks = splitter.split_documents(docs)
        for c in chunks:
            c.metadata["source_file"] = pdf.name
            c.metadata["page"] = int(c.metadata.get("page", 0)) + 1  # pages humaines (1, 2, …)
        all_chunks.extend(chunks)
        print(f"   {len(chunks)} segments")

    print(f"\nTerminé ! {len(all_chunks)} segments créés à partir de {len(pdfs)} PDF.")
    return all_chunks


if __name__ == "__main__":
    segments = charger_et_decouper_pdf()
    if segments:
        print("\nExemple de segment :")
        print(segments[0].page_content[:300] + "...")
