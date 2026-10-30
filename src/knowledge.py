"""
Faits juridiques vérifiés (« réponses fixes »).

Pourquoi ? Dans une version précedente, le LLM reprenait parfois un mauvais
chiffre lu dans un extrait de PDF (ex. « 12 jours » de congés au lieu de 18).
Quand une question correspond à un fait ci-dessous, ce fait est injecté dans le
prompt comme référence PRIORITAIRE : le LLM rédige une réponse naturelle sans
pouvoir changer les chiffres.

À ADAPTER!
"""
import unicodedata

FAITS = [
    {
        "id": "conges_payes",
        "mots_cles": [["conge", "conges"], ["paye", "payes", "annuel", "par an", "combien"]],
        "fait": "Au Maroc, le salarié a droit à un congé annuel payé de 1,5 jour ouvrable par mois "
                "de service effectif, soit 18 jours ouvrables par an (Code du travail, art. 231). "
                "Pour les salariés de moins de 18 ans : 2 jours par mois (24 jours/an). La durée "
                "augmente d'1,5 jour par période de 5 ans d'ancienneté, dans la limite de 30 jours.",
        "verifie_le": "2026-10",
    },
    {
        "id": "duree_travail",
        "mots_cles": [["duree", "heures", "horaire", "temps de travail"], ["travail", "legale", "semaine"]],
        "fait": "La durée légale du travail est de 2 288 heures par an ou 44 heures par semaine dans "
                "les activités non agricoles, et de 2 496 heures par an dans le secteur agricole "
                "(Code du travail, art. 184). La durée journalière ne peut dépasser 10 heures.",
        "verifie_le": "2026-10",
    },
    {
        "id": "smig",
        "mots_cles": [["smig", "smag", "salaire minimum", "salaire minimal"]],
        "fait": "Depuis le 1er janvier 2026, le SMIG (secteurs non agricoles) est de 17,92 DH brut "
                "par heure, soit environ 3 423 DH brut par mois pour 191 heures. Le SMAG (secteur "
                "agricole) est de 97,44 DH par jour depuis le 1er avril 2026.",
        "verifie_le": "2026-10",
    },
    {
        "id": "periode_essai",
        "mots_cles": [["periode d'essai", "periode d essai", "en essai", "l'essai"]],
        "fait": "Pour un CDI, la période d'essai est de 3 mois pour les cadres, 1,5 mois pour les "
                "employés et 15 jours pour les ouvriers ; elle peut être renouvelée une seule fois "
                "(Code du travail, art. 14). Pendant l'essai, le contrat peut être rompu sans "
                "indemnité, sous réserve d'un préavis (2 jours pour les salariés payés à la journée/"
                "semaine, 8 jours pour les salariés payés au mois) après au moins une semaine de travail (art. 13).",
        "verifie_le": "2026-10",
    },
    {
        "id": "delais_paiement",
        "mots_cles": [["delai de paiement", "delais de paiement", "payer une facture",
                       "paiement d'une facture", "facture"]],
        "fait": "Selon la loi 69-21 (modifiant le Code de commerce), le délai de paiement entre "
                "professionnels est de 60 jours à compter de la date de facturation à défaut "
                "d'accord ; il peut être convenu par écrit jusqu'à 120 jours maximum. Le retard "
                "entraîne des pénalités et une amende au profit de l'État.",
        "verifie_le": "2026-10",
    },
    {
        "id": "conservation_cv",
        "mots_cles": [["cv", "candidat", "candidature"], ["conserver", "conservation", "garder", "combien de temps"]],
        "fait": "La loi 09-08 impose de ne conserver les données personnelles que le temps nécessaire "
                "à la finalité (art. 3). Il n'existe pas de durée chiffrée dans la loi pour les CV : "
                "la pratique recommandée est de 2 ans maximum après le dernier contact avec le "
                "candidat non retenu, en l'en informant, puis suppression ou anonymisation.",
        "verifie_le": "2026-10",
    },
    {
        "id": "fuite_donnees",
        "mots_cles": [["fuite", "violation", "piratage", "cyberattaque"], ["donnee", "donnees", "data"]],
        "fait": "Au Maroc, la loi 09-08 oblige le responsable du traitement à protéger les données "
                "(art. 23) mais ne fixe pas de délai de notification chiffré : il faut contenir "
                "l'incident, documenter la violation et informer la CNDP et les personnes concernées "
                "sans délai. Si le RGPD s'applique (clients dans l'UE), la notification à l'autorité "
                "de contrôle doit intervenir dans les 72 heures (RGPD, art. 33).",
        "verifie_le": "2026-10",
    },
]


def normaliser(texte: str) -> str:
    texte = unicodedata.normalize("NFD", texte.lower())
    return "".join(c for c in texte if unicodedata.category(c) != "Mn").replace("’", "'")


def trouver_faits(question: str, maximum: int = 2) -> list[str]:
    q = normaliser(question)
    trouves = []
    for f in FAITS:
        if all(any(normaliser(m) in q for m in groupe) for groupe in f["mots_cles"]):
            trouves.append(f["fait"])
    return trouves[:maximum]
