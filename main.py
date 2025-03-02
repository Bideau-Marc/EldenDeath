import tkinter as tk
from PIL import ImageGrab, ImageEnhance, Image
import pytesseract
import time
import threading
import os
import easyocr
import re
from fuzzywuzzy import fuzz


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Elden Ring Death Counter")

        # Variables pour savoir si le programme doit capturer ou non
        self.is_running = False

        # Initialisation du compteur de morts
        self.death_count = self.load_death_count()

        # Créer l'interface
        self.status_label = tk.Label(
            root, text="Statut du joueur", font=("Helvetica", 16)
        )
        self.status_label.pack(pady=10)

        self.death_counter_label = tk.Label(
            root, text=f"Morts: {self.death_count}", font=("Helvetica", 16)
        )
        self.death_counter_label.pack(pady=10)

        # Bouton Start
        self.start_button = tk.Button(root, text="Start", command=self.start_capture)
        self.start_button.pack(pady=10)

        # Bouton Stop
        self.stop_button = tk.Button(root, text="Stop", command=self.stop_capture)
        self.stop_button.pack(pady=10)

    def start_capture(self):
        self.is_running = True
        self.start_button.config(state="disabled")  # Désactive le bouton Start
        self.stop_button.config(state="normal")  # Active le bouton Stop

        # Lancer la capture dans un thread séparé pour ne pas bloquer l'interface
        threading.Thread(target=self.capture_loop).start()

    def similar_str(self, input_str: str, target_str: str, threshold=80):
        """
        Compare le texte détecté par l'OCR avec la chaîne cible (ici 'VOUS AVEZ PÉRI').
        Renvoie True si la similarité est supérieure au seuil spécifié (par défaut 80%).
        """
        # Supprime tous les espaces multiples (si tu veux que les espaces soient supprimés)0
        input_str = re.sub(
            r"(?<=\S) (?=\S)", "", input_str
        )  # Supprime les espaces simples, mais garde les doubles
        # Supprime les espaces multiples (si tu veux que les espaces soient réduits à un seul espace)
        input_str = re.sub(
            r"\s+", " ", input_str
        )  # Remplace tous les espaces consécutifs par un seul espace
        similarity = fuzz.ratio(
            input_str.lower(), target_str.lower()
        )  # Comparer la similarité
        print(similarity)
        print(input_str + " != " + target_str)
        return similarity >= threshold  # Renvoie True si la similarité est suffisante

    def stop_capture(self):
        self.is_running = False
        self.start_button.config(state="normal")  # Réactive le bouton Start
        self.stop_button.config(state="disabled")  # Désactive le bouton Stop

    def capture_loop(self):
        while self.is_running:

            # Prendre un screenshot d'une portion de l'écran (ajuste le bbox selon tes besoins)
            screenshot = ImageGrab.grab(bbox=(500, 400, 1500, 700))  # Zone spécifique
            screenshot.save("screenshot.png")  # Sauvegarder l'image pour vérification
            image = Image.open("screenshot.png")
            # Appliquer un ajustement du contraste
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(
                2
            )  # Augmente le contraste de 2x (à ajuster selon tes tests)
            image.save("screenshot.png")
            # Crée un lecteur OCR pour le français
            reader = easyocr.Reader(["fr"])

            # Lire le texte dans l'image
            result = reader.readtext("screenshot.png")
            print(len(result))
            if len(result) > 0:
                print(len(result))
                if len(result[0]) >= 1:
                    txtConcat = " ".join([r for r in result[0][1]])

                    if self.similar_str(txtConcat, "VOUS AVEZ PÉRI"):
                        self.increment_death_count()
                        self.status_label.config(text="Le joueur est mort", fg="red")
            else:
                self.status_label.config(text="Le joueur est vivant", fg="green")
                print("Texte non reconnu ou trop différent.")
                print("text concat : " + txtConcat)

            time.sleep(2)  # Attendre 2 secondes avant de refaire une capture

    def load_death_count(self):
        """Lire le fichier de compteur de morts ou initialiser à 0 si le fichier n'existe pas."""
        if os.path.exists("deaths.txt"):
            with open("deaths.txt", "r") as f:
                return int(f.read().strip())
        else:
            return 0

    def increment_death_count(self):
        """Incrémenter le compteur de morts et mettre à jour le fichier."""
        self.death_count += 1
        self.death_counter_label.config(text=f"Morts: {self.death_count}")

        # Sauvegarder la nouvelle valeur dans le fichier
        with open("deaths.txt", "w") as f:
            f.write(str(self.death_count))


# Créer la fenêtre Tkinter
root = tk.Tk()
app = App(root)
root.mainloop()
