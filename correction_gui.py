import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import string
import re
from spellchecker import SpellChecker
from pathlib import Path

class SpellCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Correcteur Orthographique")
        self.root.geometry("1900x1000")
        
        # Initialisation du correcteur
        self.spell = SpellChecker(language='fr')
        self.mots_ignores = set()
        self.corrections_perso = {}  # Format: {mot_correct: set(variantes)}
        self.load_ignored_words()
        self.load_custom_corrections()
        
        # Variable pour la barre de progression
        self.progress_var = tk.DoubleVar()
        
        self.setup_gui()
        
        # Rafraîchir l'affichage du dictionnaire
        self.refresh_dict()
        
    def setup_gui(self):
        # Configuration de la grille principale
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Barre d'outils
        self.create_toolbar()
        
        # Zone principale
        self.create_main_area()
        
        # Barre de progression
        self.progress_bar = ttk.Progressbar(self.root, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        
        # Label pour le statut
        self.status_label = ttk.Label(self.root, text="")
        self.status_label.grid(row=3, column=0, sticky="w", padx=5, pady=2)
        
        # Configurer les tags pour le surlignage
        self.text_area.tag_configure("error", foreground="red", underline=True)
        self.text_area.tag_configure("selected", background="yellow")
        
    def create_toolbar(self):
        toolbar = ttk.Frame(self.root)
        toolbar.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        ttk.Button(toolbar, text="Ouvrir", command=self.open_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Sauvegarder", command=self.save_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Corriger", command=self.check_spelling).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Effacer surlignages", command=self.clear_highlights).pack(side=tk.LEFT, padx=2)

    def create_main_area(self):
        # Création du PanedWindow pour diviser l'écran
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Zone de texte
        self.text_area = scrolledtext.ScrolledText(paned, wrap=tk.WORD, font=('Arial', 12))
        paned.add(self.text_area, weight=3)
        
        # Frame droite pour les corrections et le dictionnaire
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=1)
        
        # Configuration de la grille pour right_frame
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_rowconfigure(3, weight=1)
        
        # Panel de correction (en haut à droite)
        correction_frame = ttk.LabelFrame(right_frame, text="Corrections")
        correction_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Liste des erreurs
        self.error_listbox = tk.Listbox(correction_frame, font=('Arial', 11))
        self.error_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.error_listbox.bind('<<ListboxSelect>>', self.on_select_error)
        
        # Frame pour les suggestions
        suggestions_frame = ttk.Frame(correction_frame)
        suggestions_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(suggestions_frame, text="Suggestions:").pack(anchor='w')
        self.suggestions_listbox = tk.Listbox(suggestions_frame, height=5, font=('Arial', 11))
        self.suggestions_listbox.pack(fill=tk.X, expand=True)
        
        # Boutons de correction
        buttons_frame = ttk.Frame(correction_frame)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(buttons_frame, text="Corriger", command=self.apply_correction).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="Ignorer", command=self.ignore_word).pack(side=tk.LEFT, padx=2)
        
        # Panel du dictionnaire personnel (en bas à droite)
        self.dict_frame = ttk.LabelFrame(right_frame, text=self.get_dict_title())
        self.dict_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Créer un Treeview pour afficher le dictionnaire
        self.dict_tree = ttk.Treeview(self.dict_frame, columns=("Correction", "Variantes"), show="headings")
        self.dict_tree.heading("Correction", text="Correction", command=lambda: self.treeview_sort_column("Correction", False))
        self.dict_tree.heading("Variantes", text="Variantes", command=lambda: self.treeview_sort_column("Variantes", False))
        # Ajuster la largeur des colonnes
        self.dict_tree.column("Correction", width=100)
        self.dict_tree.column("Variantes", width=200)
        self.dict_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Ajouter une barre de défilement
        dict_scrollbar = ttk.Scrollbar(self.dict_frame, orient="vertical", command=self.dict_tree.yview)
        dict_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.dict_tree.configure(yscrollcommand=dict_scrollbar.set)
        
        # Boutons pour gérer le dictionnaire
        dict_buttons_frame = ttk.Frame(self.dict_frame)
        dict_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(dict_buttons_frame, text="Ajouter", command=self.add_to_dict).pack(side=tk.LEFT, padx=2)
        ttk.Button(dict_buttons_frame, text="Supprimer", command=self.remove_from_dict).pack(side=tk.LEFT, padx=2)
        ttk.Button(dict_buttons_frame, text="Rafraîchir", command=self.refresh_dict).pack(side=tk.LEFT, padx=2)

    def treeview_sort_column(self, col, reverse):
        """Fonction pour trier le Treeview en cliquant sur les en-têtes de colonnes"""
        l = [(self.dict_tree.set(k, col), k) for k in self.dict_tree.get_children('')]
        l.sort(reverse=reverse)

        # Réorganiser les éléments dans l'ordre trié
        for index, (val, k) in enumerate(l):
            self.dict_tree.move(k, '', index)

        # Inverser le tri la prochaine fois
        self.dict_tree.heading(col, command=lambda: self.treeview_sort_column(col, not reverse))

    def refresh_dict(self):
        # Effacer l'arbre
        for item in self.dict_tree.get_children():
            self.dict_tree.delete(item)
        
        # Remplir avec les données actuelles, triées par correction
        items = []
        for correction, variantes in self.corrections_perso.items():
            variantes_str = ", ".join(sorted(variantes))
            items.append((correction, variantes_str))
        
        # Trier les items par la correction
        for correction, variantes_str in sorted(items, key=lambda x: x[0].lower()):
            self.dict_tree.insert('', 'end', values=(correction, variantes_str))
            
        # Trier par la colonne Correction par défaut
        self.treeview_sort_column("Correction", False)

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")]
        )
        if file_path:
            try:
                self.progress_var.set(0)
                self.status_label.config(text="Chargement du fichier...")
                self.root.update()
                
                with open(file_path, 'r', encoding='utf-8') as file:
                    self.text_area.delete(1.0, tk.END)
                    content = file.read()
                    self.text_area.insert(1.0, content)
                    
                self.progress_var.set(50)
                self.status_label.config(text="Vérification orthographique en cours...")
                self.root.update()
                
                # Lancer la vérification orthographique automatiquement
                self.check_spelling()
                
                self.progress_var.set(100)
                self.status_label.config(text="Terminé")
                self.root.update()
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'ouverture du fichier : {str(e)}")
                self.status_label.config(text="Erreur lors du chargement")
                self.progress_var.set(0)
                
    def save_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(self.text_area.get(1.0, tk.END))
                messagebox.showinfo("Succès", "Fichier sauvegardé avec succès!")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde : {str(e)}")
    
    def load_ignored_words(self):
        try:
            with open('dictionnaire_ignore.txt', 'r', encoding='utf-8') as f:
                self.mots_ignores = set(line.strip() for line in f)
        except FileNotFoundError:
            self.mots_ignores = set()
            
    def save_ignored_words(self):
        with open('dictionnaire_ignore.txt', 'w', encoding='utf-8') as f:
            for mot in sorted(self.mots_ignores):
                f.write(f"{mot}\n")
                
    def clear_highlights(self):
        # Effacer tous les surlignages
        self.text_area.tag_remove("error", "1.0", tk.END)
        self.text_area.tag_remove("selected", "1.0", tk.END)
        
    def highlight_word(self, word):
        # Trouver et surligner toutes les occurrences du mot
        start_pos = "1.0"
        while True:
            start_pos = self.text_area.search(word, start_pos, tk.END)
            if not start_pos:
                break
            end_pos = f"{start_pos}+{len(word)}c"
            self.text_area.tag_add("error", start_pos, end_pos)
            start_pos = end_pos

    def load_custom_corrections(self):
        """Charge le dictionnaire de corrections personnalisées"""
        try:
            self.corrections_perso = {}  # Réinitialiser le dictionnaire
            with open('mots-corrections.txt', 'r', encoding='utf-8') as f:
                for ligne in f:
                    if ':' in ligne:
                        mot_correct, variantes = ligne.strip().split(':')
                        mot_correct = mot_correct.strip()
                        if mot_correct not in self.corrections_perso:
                            self.corrections_perso[mot_correct] = set()
                        # Ajouter les variantes au set
                        if variantes:
                            for variante in variantes.split(','):
                                self.corrections_perso[mot_correct].add(variante.strip())
            print(f"Dictionnaire personnalisé chargé : {len(self.corrections_perso)} mots corrects")
            if hasattr(self, 'dict_frame'):
                self.update_dict_title()
        except FileNotFoundError:
            print("Fichier mots-corrections.txt non trouvé")
            self.corrections_perso = {}

    def check_spelling(self):
        print("Début de la vérification orthographique")
        # Effacer les anciennes erreurs
        self.error_listbox.delete(0, tk.END)
        self.clear_highlights()
        
        # Récupérer le texte
        text = self.text_area.get("1.0", tk.END).strip()
        print(f"Texte récupéré, longueur : {len(text)} caractères")
        
        if not text:
            messagebox.showwarning("Attention", "Aucun texte à vérifier")
            self.status_label.config(text="Aucun texte à vérifier")
            self.progress_var.set(0)
            return
        
        # Diviser en mots et vérifier l'orthographe
        words = re.findall(r'\b[a-zA-ZÀ-ÿ]+\b', text)
        total_words = len(words)
        print(f"Nombre de mots trouvés : {total_words}")
        misspelled = set()  # Utiliser un set pour les mots uniques
        corrections_made = 0
        
        # Position actuelle dans le texte
        current_pos = "1.0"
        
        for i, word in enumerate(words):
            # Mettre à jour la progression
            progress = (i / total_words) * 50 + 50  # De 50% à 100%
            self.progress_var.set(progress)
            self.status_label.config(text=f"Vérification : {i+1}/{total_words} mots")
            self.root.update()
            
            # Nettoyer le mot
            clean_word = word.strip(string.punctuation).lower()
            
            # Ignorer les mots courts (1 ou 2 lettres) et les nombres
            if len(clean_word) > 2 and not clean_word.isdigit():
                # Vérifier si le mot est dans la liste des mots ignorés
                if clean_word not in self.mots_ignores:
                    correction_needed = False
                    correction = None
                    
                    # Vérifier d'abord dans le dictionnaire personnalisé
                    if clean_word in self.corrections_perso:
                        correction = self.corrections_perso[clean_word]
                        correction_needed = True
                    # Sinon utiliser le correcteur orthographique
                    elif self.spell.correction(clean_word) != clean_word:
                        misspelled.add(word)  # Ajouter au set au lieu de la liste
                        print(f"Mot mal orthographié trouvé : {word}")
                        self.highlight_word(word)
                    
                    # Si une correction est disponible dans le dictionnaire personnel
                    if correction_needed and correction:
                        # Trouver la position du mot dans le texte
                        while True:
                            # Chercher le mot à partir de la position actuelle
                            pos = self.text_area.search(word, current_pos, tk.END)
                            if not pos:
                                break
                                
                            # Vérifier que c'est bien un mot entier
                            word_end = f"{pos}+{len(word)}c"
                            
                            # Obtenir les caractères avant et après le mot
                            before = ""
                            after = ""
                            if pos != "1.0":
                                before = self.text_area.get(f"{pos}-1c", pos)
                            after = self.text_area.get(word_end, f"{word_end}+1c")
                            
                            # Vérifier si c'est un mot entier (entouré d'espaces ou de ponctuation)
                            if (not before.isalpha() and not after.isalpha()):
                                # Remplacer le mot
                                self.text_area.delete(pos, word_end)
                                self.text_area.insert(pos, correction)
                                corrections_made += 1
                            
                            # Mettre à jour la position courante
                            current_pos = word_end
        
        # Afficher les erreurs et les corrections
        if misspelled:
            # Trier les mots pour une meilleure lisibilité
            for word in sorted(misspelled):
                self.error_listbox.insert(tk.END, word)
            print(f"Nombre total d'erreurs trouvées : {len(misspelled)}")
            self.status_label.config(text=f"Terminé : {len(misspelled)} erreurs uniques trouvées, {corrections_made} corrections automatiques")
        else:
            print("Aucune erreur trouvée")
            if corrections_made > 0:
                self.status_label.config(text=f"Terminé : {corrections_made} corrections automatiques effectuées")
            else:
                self.status_label.config(text="Terminé : Aucune erreur trouvée")
        
        self.progress_var.set(100)
        self.root.update()

    def on_select_error(self, event):
        # Effacer les anciennes suggestions et la sélection précédente
        self.suggestions_listbox.delete(0, tk.END)
        self.text_area.tag_remove("selected", "1.0", tk.END)
        
        # Obtenir le mot sélectionné
        selection = self.error_listbox.curselection()
        if not selection:
            return
        
        word = self.error_listbox.get(selection[0])
        clean_word = word.strip(string.punctuation).lower()
        
        # Trouver et mettre en évidence toutes les occurrences du mot dans le texte
        start_pos = "1.0"
        while True:
            start_pos = self.text_area.search(word, start_pos, tk.END)
            if not start_pos:
                break
                
            # Vérifier que c'est un mot entier
            word_end = f"{start_pos}+{len(word)}c"
            
            # Obtenir les caractères avant et après le mot
            before = ""
            after = ""
            if start_pos != "1.0":
                before = self.text_area.get(f"{start_pos}-1c", start_pos)
            after = self.text_area.get(word_end, f"{word_end}+1c")
            
            # Vérifier si c'est un mot entier (entouré d'espaces ou de ponctuation)
            if not before.isalpha() and not after.isalpha():
                self.text_area.tag_add("selected", start_pos, word_end)
                # Faire défiler jusqu'au premier mot trouvé
                self.text_area.see(start_pos)
            
            start_pos = word_end
        
        # Ajouter les suggestions
        if clean_word in self.corrections_perso:
            self.suggestions_listbox.insert(tk.END, self.corrections_perso[clean_word])
        else:
            try:
                suggestions = self.spell.candidates(clean_word)
                if suggestions:
                    for suggestion in suggestions:
                        self.suggestions_listbox.insert(tk.END, suggestion)
                else:
                    self.suggestions_listbox.insert(tk.END, "Aucune suggestion disponible")
            except Exception as e:
                print(f"Erreur lors de la recherche de suggestions pour '{clean_word}': {str(e)}")
                self.suggestions_listbox.insert(tk.END, "Erreur lors de la recherche de suggestions")

    def apply_correction(self):
        # Obtenir le mot incorrect sélectionné
        error_selection = self.error_listbox.curselection()
        suggestion_selection = self.suggestions_listbox.curselection()
        
        if not error_selection or not suggestion_selection:
            return
            
        incorrect_word = self.error_listbox.get(error_selection[0])
        correction = self.suggestions_listbox.get(suggestion_selection[0])
        
        # Remplacer dans le texte et mettre à jour les surlignages
        text = self.text_area.get(1.0, tk.END)
        new_text = text.replace(incorrect_word, correction)
        
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, new_text)
        
        # Supprimer les surlignages du mot corrigé
        self.clear_highlights()
        
        # Mettre à jour la liste des erreurs
        self.error_listbox.delete(error_selection[0])
        
        # Relancer la vérification pour mettre à jour les surlignages
        self.check_spelling()

    def ignore_word(self):
        selection = self.error_listbox.curselection()
        if not selection:
            return
            
        word = self.error_listbox.get(selection[0]).strip(string.punctuation)
        self.mots_ignores.add(word)
        self.save_ignored_words()
        
        # Supprimer le mot de la liste des erreurs
        self.error_listbox.delete(selection[0])

    def add_to_dict(self):
        # Obtenir la sélection actuelle
        error_sel = self.error_listbox.curselection()
        sugg_sel = self.suggestions_listbox.curselection()
        
        if error_sel and sugg_sel:
            variante = self.error_listbox.get(error_sel[0])
            correction = self.suggestions_listbox.get(sugg_sel[0])
            
            # Ajouter ou mettre à jour le dictionnaire
            if correction not in self.corrections_perso:
                self.corrections_perso[correction] = set()
            self.corrections_perso[correction].add(variante.lower())
            
            # Sauvegarder dans le fichier
            self.save_custom_corrections()
            
            # Rafraîchir l'affichage
            self.refresh_dict()
            self.update_dict_title()
            messagebox.showinfo("Succès", f"Variante '{variante}' ajoutée pour la correction '{correction}'")

    def remove_from_dict(self):
        selection = self.dict_tree.selection()
        if selection:
            item = selection[0]
            correction = self.dict_tree.item(item)['values'][0]
            
            # Supprimer l'entrée du dictionnaire
            if correction in self.corrections_perso:
                del self.corrections_perso[correction]
                
                # Sauvegarder dans le fichier
                self.save_custom_corrections()
                
                # Rafraîchir l'affichage
                self.refresh_dict()
                self.update_dict_title()
                messagebox.showinfo("Succès", f"'{correction}' et ses variantes supprimés du dictionnaire")

    def save_custom_corrections(self):
        try:
            with open('mots-corrections.txt', 'w', encoding='utf-8') as f:
                for correction, variantes in sorted(self.corrections_perso.items()):
                    variantes_str = ",".join(sorted(variantes))
                    f.write(f"{correction}:{variantes_str}\n")
            print("Dictionnaire personnel sauvegardé")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du dictionnaire : {str(e)}")
            messagebox.showerror("Erreur", "Erreur lors de la sauvegarde du dictionnaire")

    def get_dict_title(self):
        """Retourne le titre du cadre du dictionnaire avec le nombre de mots"""
        nb_mots = len(self.corrections_perso)
        return f"Dictionnaire Personnel ({nb_mots} mots)"

    def update_dict_title(self):
        """Met à jour le titre du cadre du dictionnaire"""
        self.dict_frame.configure(text=self.get_dict_title())

def main():
    root = tk.Tk()
    app = SpellCheckerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
