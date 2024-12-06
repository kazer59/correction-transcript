import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import string
from spell_checker import SpellCheckerManager
from dictionary_manager import DictionaryManager
import re
from unidecode import unidecode

class SpellCheckerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Correcteur Orthographique")
        self.root.geometry("1900x1000")
        
        # Initialisation des gestionnaires
        self.spell_manager = SpellCheckerManager()
        self.dict_manager = DictionaryManager()
        
        # Chargement des corrections personnalisées
        self.dict_manager.corrections_perso = self.dict_manager.load_custom_corrections()
        
        # Variable pour la barre de progression
        self.progress_var = tk.DoubleVar()
        
        # Variable pour stocker le mot erroné sélectionné
        self.selected_error_word = None
        self.selected_error_index = None
        
        self.setup_gui()
        self.refresh_dict()
        
    def setup_gui(self):
        """Configure l'interface graphique principale"""
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        self.create_toolbar()
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
        
        # Bind pour le double-clic sur le dictionnaire personnel
        self.dict_tree.bind('<Double-1>', self.on_dict_word_double_click)
        
    def create_toolbar(self):
        """Crée la barre d'outils"""
        toolbar = ttk.Frame(self.root)
        toolbar.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        ttk.Button(toolbar, text="Ouvrir", command=self.open_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Sauvegarder", command=self.save_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Corriger", command=self.check_spelling).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Effacer surlignages", command=self.clear_highlights).pack(side=tk.LEFT, padx=2)

    def create_main_area(self):
        """Crée la zone principale de l'interface"""
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Zone de texte
        self.text_area = scrolledtext.ScrolledText(paned, wrap=tk.WORD, width=120, font=('Consolas', 14), bg='black', fg='white', insertbackground='white')
        paned.add(self.text_area, weight=19)
        
        # Frame droite
        self.create_right_frame(paned)
        
    def create_right_frame(self, parent):
        """Crée le panneau droit de l'interface"""
        right_frame = ttk.Frame(parent)
        parent.add(right_frame, weight=1)
        
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_rowconfigure(3, weight=1)
        
        self.create_correction_frame(right_frame)
        self.create_dictionary_frame(right_frame)
        
    def create_correction_frame(self, parent):
        """Crée le panneau de correction"""
        self.correction_frame = ttk.LabelFrame(parent, text="Corrections (0 erreur)")
        self.correction_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Liste des erreurs
        self.error_listbox = tk.Listbox(self.correction_frame, font=('Arial', 11))
        self.error_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.error_listbox.bind('<<ListboxSelect>>', self.on_select_error)
        
        # Frame pour les suggestions
        suggestions_frame = ttk.Frame(self.correction_frame)
        suggestions_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(suggestions_frame, text="Suggestions:").pack(anchor='w')
        self.suggestions_listbox = tk.Listbox(suggestions_frame, height=5, font=('Arial', 11))
        self.suggestions_listbox.pack(fill=tk.X, expand=True)
        self.suggestions_listbox.bind('<<ListboxSelect>>', self.on_suggestion_select)
        
        # Boutons de correction
        buttons_frame = ttk.Frame(self.correction_frame)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(buttons_frame, text="Corriger", command=self.apply_correction).pack(side=tk.LEFT, padx=2)
        # ttk.Button(buttons_frame, text="Ignorer", command=self.ignore_word).pack(side=tk.LEFT, padx=2)
        
    def create_dictionary_frame(self, parent):
        """Crée le panneau du dictionnaire personnel"""
        self.dict_frame = ttk.LabelFrame(parent, text=self.get_dict_title())
        self.dict_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        self.create_dictionary_tree()
        self.create_dictionary_buttons()
        
    def create_dictionary_tree(self):
        """Crée l'arbre du dictionnaire"""
        self.dict_tree = ttk.Treeview(self.dict_frame, columns=("Correction", "Variantes"), show="headings")
        self.dict_tree.heading("Correction", text="Correction", command=lambda: self.treeview_sort_column("Correction", False))
        self.dict_tree.heading("Variantes", text="Variantes", command=lambda: self.treeview_sort_column("Variantes", False))
        
        self.dict_tree.column("Correction", width=150, minwidth=150)
        self.dict_tree.column("Variantes", width=400, minwidth=400, stretch=True)
        
        # Variables pour le redimensionnement des lignes
        self.current_row_height = 30
        self.is_resizing = False
        self.resize_start_y = 0
        self.resize_start_height = 0
        
        # Configurer le style pour la hauteur initiale des lignes
        style = ttk.Style()
        style.configure("Treeview", rowheight=self.current_row_height)
        
        # Lier les événements de la souris pour le redimensionnement et la sélection
        self.dict_tree.bind('<Button-1>', self.start_resize)
        self.dict_tree.bind('<B1-Motion>', self.do_resize)
        self.dict_tree.bind('<ButtonRelease-1>', self.end_resize)
        self.dict_tree.bind('<<TreeviewSelect>>', self.on_dict_select)
        
        self.dict_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Barre de défilement
        dict_scrollbar = ttk.Scrollbar(self.dict_frame, orient="vertical", command=self.dict_tree.yview)
        dict_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.dict_tree.configure(yscrollcommand=dict_scrollbar.set)

    def create_dictionary_buttons(self):
        """Crée les boutons du dictionnaire"""
        dict_buttons_frame = ttk.Frame(self.dict_frame)
        dict_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(dict_buttons_frame, text="Ajouter", command=self.add_to_dict).pack(side=tk.LEFT, padx=2)
        ttk.Button(dict_buttons_frame, text="Supprimer", command=self.remove_from_dict).pack(side=tk.LEFT, padx=2)
        ttk.Button(dict_buttons_frame, text="Rafraîchir", command=self.refresh_dict).pack(side=tk.LEFT, padx=2)
        
        # Ajouter les nouveaux boutons sous le dictionnaire
        add_word_btn = ttk.Button(dict_buttons_frame, text="Ajouter un mot", command=self.show_add_word_dialog)
        add_word_btn.pack(side=tk.LEFT, padx=2)
        edit_word_btn = ttk.Button(dict_buttons_frame, text="Modifier le mot", command=self.show_edit_word_dialog)
        edit_word_btn.pack(side=tk.LEFT, padx=2)
        
    # Méthodes de gestion des fichiers
    def open_file(self):
        """Ouvre un fichier"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    # Ajoute deux retours à la ligne après chaque point
                    content = content.replace(". ", ".\n\n")
                    content = content.replace(".\n", ".\n\n")  # Pour gérer les points déjà suivis d'un retour
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(1.0, content)
                self.check_spelling()
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'ouverture du fichier : {str(e)}")
                
    def save_file(self):
        """Sauvegarde le fichier"""
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
                
    # Méthodes de correction orthographique
    def check_spelling(self):
        """Vérifie l'orthographe du texte"""
        self.error_listbox.delete(0, tk.END)
        self.clear_highlights()
        
        text = self.text_area.get("1.0", tk.END).strip()
        if not text:
            self.status_label.config(text="Aucun texte à vérifier")
            self.progress_var.set(0)
            self.correction_frame.configure(text="Corrections (0 erreur)")
            return
            
        # Maintenant word_matches est un itérateur de MatchObject
        word_matches = self.spell_manager.extract_words(text)
        # Convertir en liste pour pouvoir compter
        word_matches = list(word_matches)
        total_words = len(word_matches)
        misspelled = set()
        corrections_made = 0
        
        # Position actuelle dans le texte
        current_pos = "1.0"
        
        for i, match in enumerate(word_matches):
            progress = (i / total_words) * 100
            self.progress_var.set(progress)
            self.status_label.config(text=f"Vérification : {i+1}/{total_words} mots")
            self.root.update()
            
            # Extraire le mot et sa ponctuation
            word = match.group(1)  # Le mot lui-même
            punctuation = match.group(2)  # La ponctuation qui suit
            
            # Vérifier d'abord dans le dictionnaire personnel
            correction_found = False
            for correct_word, variants in self.dict_manager.corrections_perso.items():
                # Vérifier le mot tel quel et en minuscules
                if word in variants or word.lower() in variants:
                    # Chercher et remplacer le mot dans le texte
                    while True:
                        pos = self.text_area.search(word + punctuation, current_pos, tk.END)
                        if not pos:
                            break
                        
                        word_end = f"{pos}+{len(word + punctuation)}c"
                        # Vérifier que c'est un mot entier
                        before = "" if pos == "1.0" else self.text_area.get(f"{pos}-1c", pos)
                        
                        if not before.isalpha():
                            # Conserver la casse d'origine si le mot commence par une majuscule
                            if word[0].isupper():
                                replacement = correct_word.capitalize()
                            else:
                                replacement = correct_word.lower()
                            self.text_area.delete(pos, word_end)
                            self.text_area.insert(pos, replacement + punctuation)
                            corrections_made += 1
                        current_pos = word_end
                    correction_found = True
                    break
            
            if not correction_found and not self.spell_manager.check_word(word):
                misspelled.add(word)
                # Surligner uniquement le mot, pas la ponctuation
                start_pos = "1.0"
                while True:
                    pos = self.text_area.search(word + punctuation, start_pos, tk.END)
                    if not pos:
                        break
                    # Surligner seulement le mot, pas la ponctuation
                    word_end = f"{pos}+{len(word)}c"
                    self.text_area.tag_add("error", pos, word_end)
                    start_pos = f"{pos}+{len(word + punctuation)}c"
                
        # Afficher les statistiques
        status_text = []
        if corrections_made > 0:
            status_text.append(f"{corrections_made} corrections automatiques")
        if misspelled:
            status_text.append(f"{len(misspelled)} erreurs trouvées")
            for word in sorted(misspelled):
                self.error_listbox.insert(tk.END, word)
            # Mettre à jour le titre du cadre de correction
            self.correction_frame.configure(text=f"Corrections ({len(misspelled)} erreurs)")
        else:
            self.correction_frame.configure(text="Corrections (0 erreur)")
        
        if status_text:
            self.status_label.config(text="Terminé : " + ", ".join(status_text))
        else:
            self.status_label.config(text="Terminé : Aucune erreur trouvée")
            
        self.progress_var.set(100)

    def clear_highlights(self):
        """Efface tous les surlignages"""
        self.text_area.tag_remove("error", "1.0", tk.END)
        self.text_area.tag_remove("selected", "1.0", tk.END)
        
    def highlight_word(self, word):
        """Surligne toutes les occurrences d'un mot"""
        start_pos = "1.0"
        while True:
            start_pos = self.text_area.search(word, start_pos, tk.END)
            if not start_pos:
                break
            # Ne surligner que le mot, pas la ponctuation qui suit
            base_word = re.match(r'[a-zA-ZÀ-ÿ]+', word).group(0)
            end_pos = f"{start_pos}+{len(base_word)}c"
            self.text_area.tag_add("error", start_pos, end_pos)
            start_pos = end_pos
            
    def on_select_error(self, event):
        """Gère la sélection d'une erreur"""
        selection = self.error_listbox.curselection()
        if not selection:
            return
            
        # Stocke le mot et l'index sélectionnés
        self.selected_error_index = selection[0]
        self.selected_error_word = self.error_listbox.get(self.selected_error_index)
        
        # Affiche les suggestions pour ce mot
        word = self.error_listbox.get(selection[0])
        self.suggestions_listbox.delete(0, tk.END)
        suggestions = self.spell_manager.get_suggestions(word)
        for suggestion in suggestions:
            self.suggestions_listbox.insert(tk.END, suggestion)
            
        # Surligne le mot dans le texte
        self.highlight_selected_word(word)

    def on_suggestion_select(self, event):
        """Gère la sélection d'une suggestion"""
        print("Suggestion sélectionnée")
        
        # Vérifie si une suggestion est sélectionnée
        suggestion_selection = self.suggestions_listbox.curselection()
        if not suggestion_selection:
            print("Pas de suggestion sélectionnée")
            return
            
        # Vérifie si un mot erroné a été sélectionné précédemment
        if self.selected_error_word is None:
            print("Aucun mot erroné n'a été sélectionné")
            return
            
        # Récupère la suggestion sélectionnée
        suggestion = self.suggestions_listbox.get(suggestion_selection[0])
        
        print(f"Mot à corriger: '{self.selected_error_word}'")
        print(f"Suggestion: '{suggestion}'")
        
        # Trouve la position du mot dans le texte
        start_pos = "1.0"
        found = False
        while True:
            pos = self.text_area.search(self.selected_error_word, start_pos, tk.END)
            if not pos:
                print(f"Mot '{self.selected_error_word}' non trouvé dans le texte")
                break
                
            print(f"Mot trouvé à la position: {pos}")
            # Calcule la position de fin du mot
            end_pos = f"{pos}+{len(self.selected_error_word)}c"
            
            # Vérifie si ce mot est surligné
            tags = self.text_area.tag_names(pos)
            print(f"Tags à cette position: {tags}")
            
            if "error" in tags:
                print("Tag 'error' trouvé, remplacement du mot...")
                # Remplace le mot
                self.text_area.delete(pos, end_pos)
                self.text_area.insert(pos, suggestion)
                # Retire le tag d'erreur
                self.text_area.tag_remove("error", pos, f"{pos}+{len(suggestion)}c")
                found = True
                break
                
            start_pos = end_pos
            
        if found:
            print("Mot remplacé avec succès")
            # Supprime le mot de la liste des erreurs
            self.error_listbox.delete(self.selected_error_index)
            
            # Met à jour le titre du cadre des corrections
            remaining_errors = self.error_listbox.size()
            self.correction_frame.configure(text=f"Corrections ({remaining_errors} erreur{'s' if remaining_errors > 1 else ''})")
            
            # Efface la liste des suggestions et réinitialise la sélection
            self.suggestions_listbox.delete(0, tk.END)
            self.selected_error_word = None
            self.selected_error_index = None
        else:
            print("Échec du remplacement du mot")
            
    def apply_correction(self):
        """Applique la correction sélectionnée"""
        error_selection = self.error_listbox.curselection()
        suggestion_selection = self.suggestions_listbox.curselection()
        
        if not error_selection or not suggestion_selection:
            return
            
        incorrect_word = self.error_listbox.get(error_selection[0])
        correction = self.suggestions_listbox.get(suggestion_selection[0])
        
        # Mettre à jour le texte
        text = self.text_area.get(1.0, tk.END)
        new_text = text.replace(incorrect_word, correction)
        
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, new_text)
        
        # Supprimer le mot de la liste des erreurs
        self.error_listbox.delete(error_selection[0])
        
        # Mettre à jour le titre avec le nouveau nombre d'erreurs
        remaining_errors = self.error_listbox.size()
        self.correction_frame.configure(text=f"Corrections ({remaining_errors} erreurs)")
        
        # Relancer la vérification orthographique
        self.check_spelling()

    def highlight_selected_word(self, word):
        """Met en évidence le mot sélectionné"""
        start_pos = "1.0"
        while True:
            start_pos = self.text_area.search(word, start_pos, tk.END)
            if not start_pos:
                break
            # Surligner seulement le mot, pas la ponctuation
            word_end = f"{start_pos}+{len(word)}c"
            self.text_area.tag_add("selected", start_pos, word_end)
            self.text_area.see(start_pos)
            start_pos = f"{start_pos}+{len(word)}c"
            
    # Méthodes de gestion du dictionnaire
    def add_to_dict(self):
        """Ajoute une correction au dictionnaire"""
        error_sel = self.error_listbox.curselection()
        sugg_sel = self.suggestions_listbox.curselection()
        
        if error_sel and sugg_sel:
            variante = self.error_listbox.get(error_sel[0])
            correction = self.suggestions_listbox.get(sugg_sel[0])
            
            self.dict_manager.add_correction(correction, variante)
            self.dict_manager.save_custom_corrections(self.dict_manager.corrections_perso)
            
            self.refresh_dict()
            self.update_dict_title()
            messagebox.showinfo("Succès", f"Variante '{variante}' ajoutée pour la correction '{correction}'")
            
    def remove_from_dict(self):
        """Supprime une correction et toutes ses variantes du dictionnaire"""
        selection = self.dict_tree.selection()
        if selection:
            item = selection[0]
            correction = self.dict_tree.item(item)['values'][0]
            variantes = self.dict_tree.item(item)['values'][1]
            
            # Demander confirmation avant la suppression
            if messagebox.askyesno("Confirmation", f"Voulez-vous vraiment supprimer '{correction}' et toutes ses variantes du dictionnaire ?"):
                self.dict_manager.remove_correction(correction)
                self.dict_manager.save_custom_corrections(self.dict_manager.corrections_perso)
                
                self.refresh_dict()
                self.update_dict_title()
                messagebox.showinfo("Succès", f"'{correction}' et ses variantes ont été supprimés du dictionnaire")
            
    def refresh_dict(self):
        """Rafraîchit l'affichage du dictionnaire"""
        for item in self.dict_tree.get_children():
            self.dict_tree.delete(item)
        
        # Créer une liste triée des corrections (insensible à la casse)
        corrections_triees = sorted(self.dict_manager.corrections_perso.items(), 
                                  key=lambda x: unidecode(x[0]).lower())
        
        for correction, variantes in corrections_triees:
            # Trier les variantes
            variantes_triees = sorted(variantes)
            
            # Formater les variantes sur plusieurs lignes
            variantes_formatees = []
            ligne_courante = []
            longueur_courante = 0
            
            for variante in variantes_triees:
                # Ajouter la longueur de la variante plus la virgule et l'espace
                longueur_variante = len(variante) + 2
                
                # Si l'ajout de cette variante dépasse ~80 caractères, commencer une nouvelle ligne
                if longueur_courante + longueur_variante > 80 and ligne_courante:
                    variantes_formatees.append(", ".join(ligne_courante))
                    ligne_courante = []
                    longueur_courante = 0
                
                ligne_courante.append(variante)
                longueur_courante += longueur_variante
            
            # Ajouter la dernière ligne si elle n'est pas vide
            if ligne_courante:
                variantes_formatees.append(", ".join(ligne_courante))
            
            # Joindre toutes les lignes avec un retour à la ligne
            variantes_str = "\n".join(variantes_formatees)
            
            self.dict_tree.insert('', 'end', values=(correction, variantes_str))
            
    def get_dict_title(self):
        """Retourne le titre du cadre du dictionnaire"""
        nb_mots = self.dict_manager.get_correction_count()
        return f"Dictionnaire Personnel ({nb_mots} mots)"
        
    def update_dict_title(self):
        """Met à jour le titre du cadre du dictionnaire"""
        self.dict_frame.configure(text=self.get_dict_title())
        
    def treeview_sort_column(self, col, reverse):
        """Trie une colonne du Treeview"""
        l = [(unidecode(self.dict_tree.set(k, col)).lower(), k) for k in self.dict_tree.get_children('')]
        l.sort(reverse=reverse)
        
        for index, (_, k) in enumerate(l):
            self.dict_tree.move(k, '', index)
            
        self.dict_tree.heading(col, command=lambda: self.treeview_sort_column(col, not reverse))

    def start_resize(self, event):
        """Commence le redimensionnement des lignes"""
        item = self.dict_tree.identify_row(event.y)
        region = self.dict_tree.identify_region(event.x, event.y)
        
        # Si on clique près du bas d'une ligne
        if item and region == "cell" and event.y > self.dict_tree.bbox(item)[1] + self.current_row_height - 5:
            self.is_resizing = True
            self.resize_start_y = event.y
            self.resize_start_height = self.current_row_height
        else:
            self.is_resizing = False

    def do_resize(self, event):
        """Effectue le redimensionnement des lignes"""
        if self.is_resizing:
            delta_y = event.y - self.resize_start_y
            new_height = max(30, self.resize_start_height + delta_y)  # Minimum 30 pixels
            style = ttk.Style()
            style.configure("Treeview", rowheight=int(new_height))
            self.current_row_height = new_height

    def end_resize(self, event):
        """Termine le redimensionnement des lignes"""
        self.is_resizing = False

    def on_dict_select(self, event):
        """Gère la sélection d'un mot dans le dictionnaire personnel"""
        # Vérifier si nous sommes en train de redimensionner
        if self.is_resizing:
            return
            
        selection = self.dict_tree.selection()
        if not selection:
            print("Aucune sélection dans le dictionnaire")
            return
            
        # Obtenir le mot sélectionné dans le dictionnaire
        item = selection[0]
        values = self.dict_tree.item(item)['values']
        if not values:
            print("Pas de valeurs pour l'item sélectionné")
            return
            
        correction = values[0]
        print(f"Mot sélectionné dans le dictionnaire : {correction}")
        
        # Vérifier s'il y a un mot erroné sélectionné
        error_sel = self.error_listbox.curselection()
        if not error_sel:
            print("Aucun mot erroné sélectionné")
            return
            
        # Obtenir le mot erroné
        incorrect_word = self.error_listbox.get(error_sel[0])
        print(f"Mot erroné sélectionné : {incorrect_word}")
        
        # Demander confirmation à l'utilisateur
        message = f"Voulez-vous :\n\n" \
                 f"1. Corriger '{incorrect_word}' en '{correction}'\n" \
                 f"2. Ajouter '{incorrect_word}' comme variante de '{correction}' dans le dictionnaire ?"
        
        if not messagebox.askyesno("Confirmation", message):
            return
            
        # Effacer les suggestions actuelles
        self.suggestions_listbox.delete(0, tk.END)
        
        # Ajouter le mot du dictionnaire comme suggestion
        self.suggestions_listbox.insert(0, correction)
        self.suggestions_listbox.selection_set(0)
        print(f"Ajout de la suggestion : {correction}")
        
        # Ajouter le mot erroné comme variante
        self.dict_manager.add_correction(correction, incorrect_word)
        self.dict_manager.save_custom_corrections(self.dict_manager.corrections_perso)
        print(f"Ajout de la variante {incorrect_word} pour {correction}")
        
        # Appliquer la correction dans le texte
        text = self.text_area.get(1.0, tk.END)
        new_text = text.replace(incorrect_word, correction)
        
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, new_text)
        print("Correction appliquée dans le texte")
        
        # Supprimer le mot de la liste des erreurs
        self.error_listbox.delete(error_sel[0])
        
        # Mettre à jour le titre avec le nouveau nombre d'erreurs
        remaining_errors = self.error_listbox.size()
        self.correction_frame.configure(text=f"Corrections ({remaining_errors} erreurs)")
        
        # Rafraîchir l'affichage du dictionnaire
        self.refresh_dict()
        print("Dictionnaire rafraîchi")
        
        # Forcer la mise à jour de l'interface
        self.root.update()

    def on_dict_word_double_click(self, event):
        """Gère le double-clic sur un mot dans le dictionnaire personnel"""
        # Obtenir l'item sélectionné
        item = self.dict_tree.selection()
        if not item:
            return
            
        # Récupérer le mot correct (première colonne)
        mot_correct = self.dict_tree.item(item[0])['values'][0]
        if not mot_correct:
            return
            
        # Demander confirmation avant d'insérer le mot
        reponse = messagebox.askyesno(
            "Confirmation",
            f"Voulez-vous insérer le mot '{mot_correct}' à la position actuelle du curseur ?",
            icon='question'
        )
        
        if reponse:
            # Insérer le mot à la position actuelle du curseur dans le text_area
            try:
                current_pos = self.text_area.index("insert")
                self.text_area.insert(current_pos, mot_correct)
                self.text_area.see(current_pos)  # S'assurer que le mot inséré est visible
                self.check_spelling()  # Relancer la vérification orthographique
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible d'insérer le mot : {str(e)}")

    def show_add_word_dialog(self):
        """Affiche une boîte de dialogue pour ajouter un mot au dictionnaire"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Ajouter un mot au dictionnaire")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Frame pour le mot correct
        correct_frame = ttk.Frame(dialog)
        correct_frame.pack(fill="x", padx=5, pady=5)
        ttk.Label(correct_frame, text="Mot correct:").pack(side="left")
        correct_entry = ttk.Entry(correct_frame)
        correct_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # Frame pour la variante
        variant_frame = ttk.Frame(dialog)
        variant_frame.pack(fill="x", padx=5, pady=5)
        ttk.Label(variant_frame, text="Variante:").pack(side="left")
        variant_entry = ttk.Entry(variant_frame)
        variant_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        def add_word():
            correct = correct_entry.get().strip()
            variant = variant_entry.get().strip()
            
            if not correct or not variant:
                messagebox.showerror("Erreur", "Veuillez remplir tous les champs")
                return
                
            # Demander confirmation
            if messagebox.askyesno("Confirmation", 
                                 f"Voulez-vous ajouter le mot '{correct}' avec la variante '{variant}' au dictionnaire ?"):
                try:
                    # Ajouter au dictionnaire
                    self.dict_manager.add_correction(correct, variant)
                    # Sauvegarder les modifications
                    self.dict_manager.save_custom_corrections(self.dict_manager.corrections_perso)
                    # Recharger le dictionnaire
                    self.dict_manager.corrections_perso = self.dict_manager.load_custom_corrections()
                    # Mettre à jour l'affichage
                    self.refresh_dict()
                    # Fermer la boîte de dialogue
                    dialog.destroy()
                    # Afficher un message de succès
                    messagebox.showinfo("Succès", "Le mot a été ajouté au dictionnaire")
                except Exception as e:
                    messagebox.showerror("Erreur", f"Impossible d'ajouter le mot : {str(e)}")
        
        # Boutons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill="x", padx=5, pady=10)
        ttk.Button(button_frame, text="Annuler", command=dialog.destroy).pack(side="right", padx=5)
        ttk.Button(button_frame, text="Ajouter", command=add_word).pack(side="right")

    def show_edit_word_dialog(self):
        """Affiche une boîte de dialogue pour modifier un mot du dictionnaire"""
        # Vérifier si un mot est sélectionné
        selection = self.dict_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un mot à modifier dans le dictionnaire")
            return
            
        # Récupérer le mot et ses variantes
        item = selection[0]
        mot_correct = self.dict_tree.item(item)['values'][0]
        variantes = self.dict_manager.corrections_perso.get(mot_correct, set())
        
        # Créer la boîte de dialogue
        dialog = tk.Toplevel(self.root)
        dialog.title("Modifier un mot du dictionnaire")
        dialog.geometry("500x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Frame pour le mot correct
        correct_frame = ttk.Frame(dialog)
        correct_frame.pack(fill="x", padx=5, pady=5)
        ttk.Label(correct_frame, text="Mot correct:").pack(side="left")
        correct_entry = ttk.Entry(correct_frame)
        correct_entry.insert(0, mot_correct)
        correct_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # Frame pour les variantes
        variants_frame = ttk.Frame(dialog)
        variants_frame.pack(fill="both", expand=True, padx=5, pady=5)
        ttk.Label(variants_frame, text="Variantes (une par ligne):").pack(side="top", anchor="w")
        
        # Zone de texte pour les variantes
        variants_text = tk.Text(variants_frame, height=8)
        variants_text.pack(fill="both", expand=True)
        variants_text.insert("1.0", "\n".join(sorted(variantes)))
        
        def save_changes():
            new_correct = correct_entry.get().strip()
            if not new_correct:
                messagebox.showerror("Erreur", "Le mot correct ne peut pas être vide")
                return
                
            # Récupérer les variantes (une par ligne)
            new_variants = set(v.strip() for v in variants_text.get("1.0", "end-1c").split("\n") if v.strip())
            
            # Demander confirmation
            if messagebox.askyesno("Confirmation", 
                                 f"Voulez-vous modifier le mot '{mot_correct}' en '{new_correct}' avec les nouvelles variantes ?"):
                try:
                    # Supprimer l'ancienne entrée
                    if mot_correct in self.dict_manager.corrections_perso:
                        del self.dict_manager.corrections_perso[mot_correct]
                    
                    # Ajouter la nouvelle entrée avec ses variantes
                    self.dict_manager.corrections_perso[new_correct] = new_variants
                    
                    # Sauvegarder les modifications
                    self.dict_manager.save_custom_corrections(self.dict_manager.corrections_perso)
                    
                    # Recharger le dictionnaire
                    self.dict_manager.corrections_perso = self.dict_manager.load_custom_corrections()
                    
                    # Mettre à jour l'affichage
                    self.refresh_dict()
                    
                    # Fermer la boîte de dialogue
                    dialog.destroy()
                    
                    # Afficher un message de succès
                    messagebox.showinfo("Succès", "Le mot a été modifié dans le dictionnaire")
                except Exception as e:
                    messagebox.showerror("Erreur", f"Impossible de modifier le mot : {str(e)}")
        
        # Boutons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill="x", padx=5, pady=10)
        ttk.Button(button_frame, text="Annuler", command=dialog.destroy).pack(side="right", padx=5)
        ttk.Button(button_frame, text="Enregistrer", command=save_changes).pack(side="right")
