#!/usr/bin/env python3
"""
STATIC PAGE CONTENT
===================

This file contains static page titles and descriptions that rarely change.
You don't need to edit this file - it's just to keep config.py clean and simple.
"""

# Static page titles for each language (these rarely change)
PAGE_TITLES = {
    "de-DE": {
        "ueber-uns": "Über uns",
        "kontakt": "Kontakt", 
        "datenschutz": "Datenschutz",
        "nutzungsbedingungen": "Nutzungsbedingungen",
        "cookies": "Cookie-Richtlinie",
        "dmca": "DMCA",
        "eltern-information": "Eltern-Information"
    },
    "en-US": {
        "about-us": "About Us",
        "contact": "Contact",
        "privacy-policy": "Privacy Policy", 
        "terms-of-service": "Terms of Service",
        "cookies-policy": "Cookie Policy",
        "dmca": "DMCA",
        "parents-information": "Parents Information"
    },
    "fr-FR": {
        "a-propos": "À propos de nous",
        "contact": "Contact",
        "confidentialite": "Politique de confidentialité",
        "conditions-utilisation": "Conditions d'utilisation", 
        "politique-cookies": "Politique des cookies",
        "dmca": "DMCA",
        "information-parents": "Information aux parents"
    },
    "nl-NL": {
        "over-ons": "Over ons",
        "contact": "Contact",
        "privacybeleid": "Privacybeleid",
        "gebruiksvoorwaarden": "Gebruiksvoorwaarden",
        "cookie-beleid": "Cookiebeleid", 
        "dmca": "DMCA",
        "ouder-informatie": "Ouder informatie"
    }
}

# Static page descriptions for each language (these rarely change)
PAGE_DESCRIPTIONS = {
    "de-DE": {
        "ueber-uns": "Erfahre mehr über unser Team und unsere Mission, die besten kostenlosen Online-Spiele anzubieten.",
        "kontakt": "Kontaktiere uns bei Fragen, Feedback oder Support zu unseren kostenlosen Online-Spielen.",
        "datenschutz": "Unsere Datenschutzrichtlinie erklärt, wie wir deine persönlichen Daten sammeln, verwenden und schützen.",
        "nutzungsbedingungen": "Lies unsere Nutzungsbedingungen für die Verwendung unserer Website und Spiele.",
        "cookies": "Erfahre mehr über unsere Verwendung von Cookies und wie du sie verwalten kannst.",
        "dmca": "Informationen zu unserem DMCA-Verfahren für Urheberrechtsbeschwerden.",
        "eltern-information": "Wichtige Informationen für Eltern über Online-Sicherheit und Spielrichtlinien."
    },
    "en-US": {
        "about-us": "Learn more about our team and mission to provide the best free online games.",
        "contact": "Contact us for questions, feedback, or support regarding our free online games.",
        "privacy-policy": "Our privacy policy explains how we collect, use, and protect your personal information.",
        "terms-of-service": "Read our terms of service for using our website and games.",
        "cookies-policy": "Learn about our use of cookies and how you can manage them.",
        "dmca": "Information about our DMCA process for copyright complaints.",
        "parents-information": "Important information for parents about online safety and gaming guidelines."
    },
    "fr-FR": {
        "a-propos": "Apprenez-en plus sur notre équipe et notre mission de fournir les meilleurs jeux en ligne gratuits.",
        "contact": "Contactez-nous pour des questions, commentaires ou support concernant nos jeux en ligne gratuits.",
        "confidentialite": "Notre politique de confidentialité explique comment nous collectons, utilisons et protégeons vos informations personnelles.",
        "conditions-utilisation": "Lisez nos conditions d'utilisation pour l'usage de notre site web et nos jeux.",
        "politique-cookies": "Apprenez-en plus sur notre utilisation des cookies et comment vous pouvez les gérer.",
        "dmca": "Informations sur notre processus DMCA pour les plaintes de droits d'auteur.",
        "information-parents": "Informations importantes pour les parents sur la sécurité en ligne et les directives de jeu."
    },
    "nl-NL": {
        "over-ons": "Leer meer over ons team en onze missie om de beste gratis online games te bieden.",
        "contact": "Neem contact met ons op voor vragen, feedback of ondersteuning betreffende onze gratis online games.",
        "privacybeleid": "Ons privacybeleid legt uit hoe we je persoonlijke informatie verzamelen, gebruiken en beschermen.",
        "gebruiksvoorwaarden": "Lees onze gebruiksvoorwaarden voor het gebruik van onze website en games.",
        "cookie-beleid": "Leer meer over ons gebruik van cookies en hoe je ze kunt beheren.",
        "dmca": "Informatie over ons DMCA-proces voor auteursrechtklachten.",
        "ouder-informatie": "Belangrijke informatie voor ouders over online veiligheid en game richtlijnen."
    }
}

def get_page_title(page_key, language_code):
    """Get page title for specified language"""
    return PAGE_TITLES.get(language_code, {}).get(page_key, page_key.title())

def get_page_description(page_key, language_code):
    """Get page description for specified language"""
    return PAGE_DESCRIPTIONS.get(language_code, {}).get(page_key, "")
