import os
import re
import sys
from collections import defaultdict
import logging

import pdfplumber

LOGGING_DIR = "logs"


class DataCleaner:
    def __init__(self, pdf_paths):
        """
        Initialise le nettoyeur de texte avec les chemins des fichiers PDF.

        :param pdf_paths: Liste des chemins des fichiers PDF à nettoyer
        """
        self.pdf_paths = pdf_paths

        # Configuration du logger
        os.makedirs(LOGGING_DIR, exist_ok=True)  # Create the directory if it doesn't exist

        # Get the root logger
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)  # Set the logging level

        if not logger.handlers:
            # Create a formatter
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

            # Create a file handler
            file_handler = logging.FileHandler(f"{LOGGING_DIR}/data_cleaning.log")
            file_handler.setFormatter(formatter)

            # Create a console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)

            # Add handlers to the logger
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
    def clean_text(self):
        """
        Nettoie le texte extrait des PDF en appliquant plusieurs étapes de prétraitement.

        :return: Texte nettoyé et concaténé de tous les PDF
        """
        full_cleaned_text = ""
        for path in self.pdf_paths:
            logging.info("Traitement du fichier PDF : %s", path)
            raw_text = self.__extract_text_without_tables(path)
            cleaned_text = self.__remove_headers_and_footers(raw_text, "Forward-Looking Statements", "Signature")
            cleaned_text = self.__normalize_whitespace(cleaned_text)
            cleaned_text = self.__clean_broken_lines(cleaned_text)
            cleaned_text = self.__remove_redundant_sentences(cleaned_text, redundancy_threshold=0.05)
            full_cleaned_text += cleaned_text
            logging.info("Fichier PDF traité avec succès : %s", path)
        return full_cleaned_text

    def __extract_text_without_tables(self, pdf_path):
        """
        Extrait le texte d'un PDF en ignorant les tables.

        :param pdf_path: Chemin du fichier PDF
        :return: Texte extrait sans les tables
        """
        cleaned_text = ""
        logging.info("Extraction du texte sans les tables pour le fichier : %s", pdf_path)

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                # Identifier les tables sur la page
                tables = page.find_tables()
                table_bounds = [table.bbox for table in tables]

                # Extraire le texte en excluant les régions des tables
                non_table_text = page.filter(lambda obj: not self.__is_within_table(obj, table_bounds)).extract_text()

                if non_table_text:
                    cleaned_text += non_table_text + "\n"

        logging.info("Texte extrait avec succès pour le fichier : %s", pdf_path)
        return cleaned_text

    def __is_within_table(self, obj, table_bounds):
        """
        Vérifie si un objet (par exemple, une boîte de texte) se trouve dans les limites d'une table.

        :param obj: Objet à vérifier
        :param table_bounds: Liste des limites des tables
        :return: True si l'objet est dans une table, sinon False
        """
        x0, y0, x1, y1 = obj.get("x0", 0), obj.get("top", 0), obj.get("x1", 0), obj.get("bottom", 0)
        for bounds in table_bounds:
            bx0, by0, bx1, by1 = bounds
            if bx0 <= x0 <= bx1 and by0 <= y0 <= by1:
                return True
        return False

    def __remove_headers_and_footers(self, text, start_marker, end_marker):
        """
        Supprime les en-têtes et pieds de page répétés dans le texte.

        :param text: Texte brut
        :param start_marker: Marqueur de début (tout le texte avant ce marqueur est supprimé)
        :param end_marker: Marqueur de fin (tout le texte après ce marqueur est supprimé)
        :return: Texte sans en-têtes et pieds de page
        """
        logging.info("Suppression des en-têtes et pieds de page")

        # Find the start and end positions
        start_pos = text.lower().find(start_marker.lower())
        end_pos = text.lower().rfind(end_marker.lower())

        # Extract the relevant portion of the text
        if start_pos != -1 and end_pos != -1:
            cleaned_text = text[start_pos:end_pos + len(end_marker)]
        else:
            cleaned_text = text  # If markers are not found, return the original text
        return cleaned_text.strip()

    def __normalize_whitespace(self, text):
        """
        Normalise les espaces blancs en remplaçant les espaces multiples et les sauts de ligne par un seul espace.

        :param text: Texte à normaliser
        :return: Texte normalisé
        """
        logging.info("Normalisation des espaces blancs")
        return re.sub(r"\s+", " ", text)

    def __clean_broken_lines(self, text):
        """
        Répare les lignes cassées en fusionnant les lignes qui ne se terminent pas par une ponctuation.

        :param text: Texte avec des lignes cassées
        :return: Texte avec des lignes réparées
        """
        logging.info("Réparation des lignes cassées")
        return re.sub(r"(?<!\.)\n", " ", text)

    def __remove_redundant_sentences(self, text, redundancy_threshold=0.05):
        """
        Supprime les phrases qui se répètent excessivement dans le texte et enregistre les phrases supprimées dans un log.

        :param text: Texte à traiter
        :param redundancy_threshold: Taux de redondance (entre 0 et 1) pour supprimer une phrase
        :return: Texte sans les phrases redondantes
        """
        logging.info("Suppression des phrases redondantes")
        sentences = re.split(r'(?<=[.!?])\s+', text)  # Découpage en phrases

        sentence_counts = defaultdict(int)
        for sentence in sentences:
            sentence_counts[sentence] += 1

        total_sentences = len(sentences)
        redundant_sentences = set()
        for sentence, count in sentence_counts.items():
            redundancy_rate = count / total_sentences
            if redundancy_rate > redundancy_threshold:
                redundant_sentences.add(sentence)
                logging.info("Phrase supprimée : '%s' (taux de redondance : %.2f)", sentence, redundancy_rate)

        filtered_sentences = [sentence for sentence in sentences if sentence not in redundant_sentences]
        cleaned_text = " ".join(filtered_sentences)
        return cleaned_text
