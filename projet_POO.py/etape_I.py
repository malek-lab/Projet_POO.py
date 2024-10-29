import os
from bases import base_livre, base_bibli
from ebooklib import epub
import fitz  # PyMuPDF pour les fichiers PDF

#1
class LivrePDF(base_livre):
    def __init__(self, ressource):
        self.ressource = ressource

    def type(self):
        return "PDF"

    def titre(self):
        doc = fitz.open(self.ressource)
        return doc.metadata.get('title', 'Titre inconnu')

    def auteur(self):
        doc = fitz.open(self.ressource)
        return doc.metadata.get('author', 'Auteur inconnu')

    # Ajout de méthodes pour langue, sujet, et date avec des valeurs par défaut
    def langue(self):
        return "Langue inconnue"

    def sujet(self):
        return "Sujet inconnu"

    def date(self):
        return "Date inconnue"


class LivreEPUB(base_livre):
    def __init__(self, ressource):
        self.ressource = ressource

    def type(self):
        return "EPUB"

    def titre(self):
        book = epub.read_epub(self.ressource)
        return book.get_metadata('DC', 'title')[0][0] if book.get_metadata('DC', 'title') else "Titre inconnu"

    def auteur(self):
        book = epub.read_epub(self.ressource)
        return book.get_metadata('DC', 'creator')[0][0] if book.get_metadata('DC', 'creator') else "Auteur inconnu"

    def langue(self):
        book = epub.read_epub(self.ressource)
        return book.get_metadata('DC', 'language')[0][0] if book.get_metadata('DC', 'language') else "Langue inconnue"

    def sujet(self):
        return "Sujet inconnu"

    def date(self):
        return "Date inconnue"
    
#2
class simple_bibli(base_bibli):
    def __init__(self, path):
        self.path = path
        self.livres = []

    def ajouter(self, livre):
        self.livres.append(livre)

    def rapport_livres(self, format, fichier):
        with open(fichier, 'w') as f:
            f.write("Rapport des livres dans la bibliothèque:\n\n")
            for livre in self.livres:
                f.write(f"Titre : {livre.titre()}\n")
                f.write(f"Auteur : {livre.auteur()}\n")
                f.write(f"Type : {livre.type()}\n")
                f.write(f"Nom de fichier : {os.path.basename(livre.ressource)}\n\n")

    def rapport_auteurs(self, format, fichier):
        auteurs = {}
        for livre in self.livres:
            if livre.auteur() not in auteurs:
                auteurs[livre.auteur()] = []
            auteurs[livre.auteur()].append((livre.titre(), livre.type(), os.path.basename(livre.ressource)))

        with open(fichier, 'w') as f:
            f.write("Rapport des auteurs et leurs livres:\n\n")
            for auteur, livres in auteurs.items():
                f.write(f"Auteur : {auteur}\n")
                for titre, type_, nom_fichier in livres:
                    f.write(f" - Titre : {titre}, Type : {type_}, Fichier : {nom_fichier}\n")
                f.write("\n")

#3
import requests
from bs4 import BeautifulSoup

class bibli(simple_bibli):
    def alimenter(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Recherche des liens vers des fichiers PDF et EPUB
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.endswith('.pdf'):
                pdf_path = os.path.join(self.path, os.path.basename(href))
                self._telecharger_fichier(url, href, pdf_path)
                self.ajouter(LivrePDF(pdf_path))
            elif href.endswith('.epub'):
                epub_path = os.path.join(self.path, os.path.basename(href))
                self._telecharger_fichier(url, href, epub_path)
                self.ajouter(LivreEPUB(epub_path))

    def _telecharger_fichier(self, base_url, href, chemin_local):
        if not href.startswith(('http://', 'https://')):
            href = base_url + href  # URL relative
        response = requests.get(href)
        with open(chemin_local, 'wb') as f:
            f.write(response.content)


#tester : 

ma_bibli = bibli(path="path/to/local/library")
"""
ma_bibli.alimenter("https://math.univ-angers.fr/~jaclin/biblio/livres/")"""

# Générer des rapports
ma_bibli.rapport_livres(format="txt", fichier="rapport_livres.txt")
ma_bibli.rapport_auteurs(format="txt", fichier="rapport_auteurs.txt")
