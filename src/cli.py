
from rag import AssistantJuridique
from indexation import creer_base_vectorielle


def main():
    creer_base_vectorielle()
    assistant = AssistantJuridique()
    historique = []

    print("\n" + "=" * 55)
    print("  ⚖️  Saul Goodbot — Assistant juridique marocain")
    print("=" * 55)
    print("  Tapez 'quitter' pour terminer, 'nouveau' pour effacer la conversation.\n")

    while True:
        try:
            question = input("Votre question : ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAu revoir !")
            break
        if not question:
            continue
        if question.lower() in ("quitter", "exit", "quit"):
            print("Au revoir !")
            break
        if question.lower() in ("nouveau", "new"):
            historique.clear()
            print("Historique effacé.\n")
            continue

        print("\n⏳ Recherche en cours...\n")
        try:
            rep = assistant.repondre(question, historique)
        except Exception as e:
            print(f"❌ Erreur : {e}\n")
            continue

        print("─" * 55)
        print(rep.texte)
        if rep.sources:
            print("\n📂 " + ", ".join(f"{s['fichier']} p.{s['page']}" for s in rep.sources[:4]))
        print("─" * 55 + "\n")

        historique += [{"role": "user", "content": question},
                       {"role": "assistant", "content": rep.texte}]


if __name__ == "__main__":
    main()
