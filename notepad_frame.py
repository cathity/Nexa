import tkinter as tk
from tkinter import font as tkfont, messagebox, scrolledtext
import json
import os

NOTES_FILE = "notes.json"


class NotepadApplication(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller
        self.current_user_id = None
        self.all_notes = []
        self.current_note_index = None
        self.displayed_notes_indices = []

        # struktura interfejsu
        self.paned_window = tk.PanedWindow(self, orient="horizontal", sashrelief="raised")
        self.paned_window.pack(fill="both", expand=True)

        # --- Ramka LEWA (Lista Notatek i Wyszukiwanie) ---
        self.list_frame = tk.Frame(self.paned_window, relief="solid", bd=1)
        self.list_frame.pack(fill="both", expand=False)

        self.list_label = tk.Label(self.list_frame, text="Moje Notatki", font=("Helvetica", 14, "bold"))
        self.list_label.pack(pady=(10, 5))

        #  Panel Wyszukiwania
        self.search_frame = tk.Frame(self.list_frame)
        self.search_frame.pack(fill="x", padx=5, pady=(0, 5))

        self.search_var = tk.StringVar()
        #filtrowanie przy każdej zmianie tekstu
        self.search_var.trace_add("write", self.filter_notes)

        search_label = tk.Label(self.search_frame, text="Szukaj:", font=("Helvetica", 10))
        search_label.pack(side="left")

        self.search_entry = tk.Entry(self.search_frame, textvariable=self.search_var, font=("Helvetica", 10))
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))


        self.notes_listbox = tk.Listbox(self.list_frame, font=("Helvetica", 12),
                                        relief="flat", highlightthickness=0,
                                        exportselection=False)
        self.notes_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.notes_listbox.bind("<<ListboxSelect>>", self.on_note_select)

        self.paned_window.add(self.list_frame)

        # --- Ramka PRAWA (Edytor) ---
        self.editor_frame = tk.Frame(self.paned_window)
        self.editor_frame.pack(fill="both", expand=True)

        self.title_label = tk.Label(self.editor_frame, text="Tytuł:", font=("Helvetica", 14, "bold"))
        self.title_label.pack(pady=(10, 5), anchor="nw", padx=10)

        self.title_entry = tk.Entry(self.editor_frame, font=("Helvetica", 14), relief="solid", bd=1)
        self.title_entry.pack(fill="x", padx=10, pady=(0, 10), ipady=4)

        self.notepad_text = scrolledtext.ScrolledText(self.editor_frame, wrap="word",
                                                      undo=True, font=("Helvetica", 12),
                                                      relief="solid", bd=1)
        self.notepad_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.paned_window.add(self.editor_frame, width=600)


    def set_current_user(self, user_id):
        """Ustaw ID zalogowanego użytkownika i załaduj jego notatki"""
        self.current_user_id = user_id
        self.load_notes_from_file()
        self.populate_notes_list()

    def create_notepad_menu(self):
        '''Tworzy menu notatnika w głównym oknie'''
        main_window = self.controller

        main_window.menubar = tk.Menu(main_window)
        main_window.config(menu=main_window.menubar)

        settings_menu = tk.Menu(main_window.menubar, tearoff=0)
        main_window.menubar.add_cascade(label="Ustawienia", menu=settings_menu)

        self.settings_menu = settings_menu

        settings_menu.add_command(label="Nowa notatka", command=self.file_new)
        settings_menu.add_command(label="Zapisz notatkę", command=self.file_save)
        settings_menu.add_separator()

        settings_menu.add_command(label="Zmień motyw",
                                  command=self.controller.toggle_theme)

        settings_menu.add_separator()
        settings_menu.add_command(label="Wyloguj", command=self.logout)
        settings_menu.add_separator()
        settings_menu.add_command(label="Wyjdź", command=self.controller.quit_app)

        self.update_theme(self.controller.colors)

    def logout(self):
        """Wyloguj użytkownika i wyczyść dane"""
        self.current_user_id = None
        self.all_notes = []
        self.current_note_index = None
        self.title_entry.delete(0, tk.END)
        self.notepad_text.delete(1.0, tk.END)
        self.notes_listbox.delete(0, tk.END)
        self.controller.show_frame("StartPage")

    def update_theme(self, colors):
        '''Aktualizuje wszystkie kolory w tej ramce'''

        if self.controller.current_theme == "light":
            theme_label_text = "Zmień na motyw ciemny"
        else:
            theme_label_text = "Zmień na motyw jasny"

        if hasattr(self, 'settings_menu'):
            try:
                self.settings_menu.entryconfig(3, label=theme_label_text)
            except Exception:
                pass

        if hasattr(self.controller, 'menubar'):
            self.controller.menubar.config(bg=colors["bg_primary"], fg=colors["fg_primary"])
            if hasattr(self, 'settings_menu'):
                self.settings_menu.config(bg=colors["bg_secondary"], fg=colors["fg_primary"])

        self.config(bg=colors["bg_secondary"])
        self.paned_window.config(bg=colors["bg_secondary"])

        self.list_frame.config(bg=colors["bg_primary"])
        self.list_label.config(bg=colors["bg_primary"], fg=colors["fg_primary"])

        # --- Aktualizacja kolorów wyszukiwarki ---
        self.search_frame.config(bg=colors["bg_primary"])
        for child in self.search_frame.winfo_children():
            if isinstance(child, tk.Label):
                child.config(bg=colors["bg_primary"], fg=colors["fg_primary"])
            elif isinstance(child, tk.Entry):
                child.config(bg=colors["entry_bg"], fg=colors["entry_fg"], insertbackground=colors["fg_primary"])

        self.notes_listbox.config(bg=colors["list_bg"], fg=colors["list_fg"],
                                  selectbackground=colors["list_highlight"],
                                  selectforeground=colors["list_fg"])

        self.editor_frame.config(bg=colors["bg_secondary"])
        self.title_label.config(bg=colors["bg_secondary"], fg=colors["fg_primary"])
        self.title_entry.config(bg=colors["entry_bg"], fg=colors["entry_fg"],
                                insertbackground=colors["fg_primary"])
        self.notepad_text.config(bg=colors["entry_bg"], fg=colors["entry_fg"],
                                 insertbackground=colors["fg_primary"])

    # --- FUNKCJE OBSŁUGI NOTATEK ---
    def load_notes_from_file(self):
        """Teraz ładujemy tylko notatki danego użytkownika"""
        if not self.current_user_id:
            self.all_notes = []
            return

        if os.path.exists(NOTES_FILE):
            try:
                with open(NOTES_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # filtracja notatek po user_id
                    self.all_notes = [
                        note for note in data.get("notes", [])
                        if note.get("user_id") == self.current_user_id
                    ]
            except json.JSONDecodeError:
                self.all_notes = []
        else:
            self.all_notes = []

    def save_notes_to_file(self):
        """Zapisujemy wszystkie notatki, ale dodajemy user_id"""
        if not self.current_user_id:
            messagebox.showerror("Błąd", "Nie jesteś zalogowany!")
            return False

        # Wczytywanie notatek wszystkich użytkowników
        all_users_notes = []
        if os.path.exists(NOTES_FILE):
            try:
                with open(NOTES_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    all_users_notes = data.get("notes", [])
            except json.JSONDecodeError:
                all_users_notes = []

        # usuwanie starych notatek  użytkownika
        all_users_notes = [
            note for note in all_users_notes
            if note.get("user_id") != self.current_user_id
        ]


        for note in self.all_notes:
            note["user_id"] = self.current_user_id
            all_users_notes.append(note)

        try:
            with open(NOTES_FILE, "w", encoding="utf-8") as f:
                json.dump({"notes": all_users_notes}, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            messagebox.showerror("Błąd zapisu", f"Nie udało się zapisać: {e}")
            return False

    # --- Funkcja filtrująca ---
    def filter_notes(self, *args):
        search_term = self.search_var.get().lower()
        self.populate_notes_list(filter_text=search_term)

    def populate_notes_list(self, filter_text=""):
        self.notes_listbox.delete(0, tk.END)
        self.displayed_notes_indices = []  # Reset mapowania indeksów

        for index, note in enumerate(self.all_notes):
            title = note.get("title", "Brak tytułu")
            # Sprawdź, czy tytuł zawiera szukaną frazę
            if filter_text in title.lower():
                self.notes_listbox.insert(tk.END, title)
                self.displayed_notes_indices.append(index)

    def on_note_select(self, event=None):
        selected_indices = self.notes_listbox.curselection()
        if not selected_indices:
            return

        # Pobieramy indeks z listy (która może być przefiltrowana)
        listbox_index = selected_indices[0]

        # Mapujemy go na prawdziwy indeks w bazie danych
        real_index = self.displayed_notes_indices[listbox_index]

        self.current_note_index = real_index
        note = self.all_notes[real_index]

        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, note.get("title", ""))
        self.notepad_text.delete(1.0, tk.END)
        self.notepad_text.insert(1.0, note.get("content", ""))

    def file_new(self):
        if not self.current_user_id:
            messagebox.showerror("Błąd", "Musisz być zalogowany, aby tworzyć notatki!")
            return

        self.title_entry.delete(0, tk.END)
        self.notepad_text.delete(1.0, tk.END)
        self.current_note_index = None
        self.notes_listbox.selection_clear(0, tk.END)

        # Czyścimy wyszukiwanie przy nowej notatce
        self.search_var.set("")

        messagebox.showinfo("Nowa notatka", "Wpisz tytuł i treść, a następnie naciśnij 'Zapisz notatkę'.")

    def file_save(self):
        if not self.current_user_id:
            messagebox.showerror("Błąd", "Musisz być zalogowany, aby zapisywać notatki!")
            return

        title = self.title_entry.get()
        content = self.notepad_text.get(1.0, tk.END).strip()

        if not title:
            messagebox.showwarning("Brak tytułu", "Notatka musi mieć tytuł, aby ją zapisać.")
            return

        note_data = {
            "title": title,
            "content": content,
            "user_id": self.current_user_id  # 👈 WAŻNE: dodajemy user_id
        }

        if self.current_note_index is not None:
            self.all_notes[self.current_note_index] = note_data
        else:
            self.all_notes.append(note_data)
            self.current_note_index = len(self.all_notes) - 1

        if self.save_notes_to_file():
            # Czyścimy wyszukiwanie po zapisie, żeby nowa notatka była widoczna
            self.search_var.set("")
            self.populate_notes_list()

            # Zaznaczamy zapisaną notatkę
            try:
                display_index = self.displayed_notes_indices.index(self.current_note_index)
                self.notes_listbox.selection_set(display_index)
                self.notes_listbox.see(display_index)
            except ValueError:
                pass

            messagebox.showinfo("Zapisano", f"Notatka '{title}' została zapisana.")