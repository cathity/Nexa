import tkinter as tk
from tkinter import font as tkfont, messagebox, scrolledtext, filedialog  #######
import json
import os
import shutil
import re
import uuid

try:
    from PIL import Image, ImageTk, ImageGrab

    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False
    print("Brak biblioteki Pillow. Obrazy nie będą działać. Zainstaluj: pip install Pillow")

#  KONFIGURACJA OCR
try:
    import pytesseract

    HAS_OCR = True

    # Python musi wiedzieć, gdzie jest plik tesseract.exe
    # Sprawdzamy typowe ścieżki instalacji na Windows
    possible_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\Users\\" + os.getlogin() + r"\AppData\Local\Tesseract-OCR\tesseract.exe"
        r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    ]


    found_tesseract = False
    for path in possible_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            found_tesseract = True
            break
    if not found_tesseract:
        print("UWAGA: Nie znaleziono tesseract.exe w typowych folderach. OCR może nie działać.")

except ImportError:
    HAS_OCR = False
    print("Brak biblioteki pytesseract. Zainstaluj: pip install pytesseract")

NOTES_FILE = "notes.json"
IMAGES_DIR = "images"


class NotepadApplication(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller
        self.current_user_id = None
        self.all_notes = []
        self.current_note_index = None
        self.displayed_notes_indices = []

        # ZMIENNE DO OBRAZÓW
        self.images_cache = {}
        self.pil_images = {}
        self.in_preview_mode = False

        # Stwórz folder na obrazy
        if not os.path.exists(IMAGES_DIR):
            os.makedirs(IMAGES_DIR)
            # struktura interfejsu
        self.paned_window = tk.PanedWindow(self, orient="horizontal", sashrelief="raised")
        self.paned_window.pack(fill="both", expand=True)

        # Ramka LEWA (Lista Notatek i Wyszukiwanie)
        self.list_frame = tk.Frame(self.paned_window, relief="solid", bd=1)
        self.list_frame.pack(fill="both", expand=False)

        self.list_label = tk.Label(self.list_frame, text="Moje Notatki", font=("Helvetica", 14, "bold"))
        self.list_label.pack(pady=(10, 5))

        #  Panel Wyszukiwania
        self.search_frame = tk.Frame(self.list_frame)
        self.search_frame.pack(fill="x", padx=5, pady=(0, 5))

        self.search_var = tk.StringVar()
        # filtrowanie przy każdej zmianie tekstu
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

        #  Ramka PRAWA (Edytor)
        self.editor_frame = tk.Frame(self.paned_window)
        self.editor_frame.pack(fill="both", expand=True)

        #  Pasek tytułu
        top_bar = tk.Frame(self.editor_frame, bg="white")
        top_bar.pack(fill="x", padx=10, pady=5)

        self.title_label = tk.Label(top_bar, text="Tytuł:", font=("Helvetica", 14, "bold"))
        self.title_label.pack(side="left")

        # pole tekstowe tytułu
        self.title_entry = tk.Entry(self.editor_frame, font=("Helvetica", 14), relief="solid", bd=1)
        self.title_entry.pack(fill="x", padx=10, pady=(0, 10), ipady=4)

        self.notepad_text = scrolledtext.ScrolledText(self.editor_frame, wrap="word",
                                                      undo=True, font=("Helvetica", 12),
                                                      relief="solid", bd=1)
        self.notepad_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # SKRÓTY KLAWISZOWE
        self.notepad_text.bind("<Control-v>", self.handle_paste)

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

        settings_menu.add_command(label="Wstaw obraz (z pliku)", command=self.insert_image)
        #  NOWA OPCJA OCR
        settings_menu.add_command(label="Zczytaj tekst z obrazu (OCR)", command=self.ocr_from_image)
        settings_menu.add_separator()

        # Prawidłowa pozycja dla Kalendarza
        settings_menu.add_command(label="Otwórz Kalendarz",
                                  command=lambda: self.controller.show_frame("CalendarApplication",
                                                                             {"id": self.current_user_id}))
        settings_menu.add_separator()

        # Tylko JEDNA opcja zmiany motywu
        if self.controller.current_theme == "light":
            theme_label_text = "Zmień na motyw ciemny"
        else:
            theme_label_text = "Zmień na motyw jasny"

        settings_menu.add_command(label=theme_label_text,
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
                # Indeks 8 to zmiana motywu (przesunął się, bo doszła opcja OCR)
                self.settings_menu.entryconfig(8, label=theme_label_text)
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

        #  Aktualizacja kolorów wyszukiwarki
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

    # W notepad_frame.py ZMIEŃ te funkcje:

    def load_notes_from_file(self):
        if not self.current_user_id:
            self.all_notes = []
            return

        from supabase_client import get_supabase
        supabase = get_supabase()

        if not supabase:
            self.all_notes = []
            return

        try:
            # Upewnij się że user_id jest stringiem
            user_id_str = str(self.current_user_id)

            response = supabase.table("notes") \
                .select("*") \
                .eq("user_id", user_id_str) \
                .execute()

            self.all_notes = response.data or []

            print(f"DEBUG: Załadowano {len(self.all_notes)} notatek dla user_id: {user_id_str}")

        except Exception as e:
            print(f"Błąd ładowania notatek: {e}")
            self.all_notes = []

    def save_notes_to_file(self):
        if not self.current_user_id:
            messagebox.showerror("Błąd", "Nie jesteś zalogowany!")
            return False

        from supabase_client import get_supabase
        supabase = get_supabase()

        if not supabase:
            messagebox.showerror("Błąd", "Brak połączenia z bazą danych!")
            return False

        title = self.title_entry.get()
        content = self.serialize_content_with_images()

        if not title:
            messagebox.showwarning("Brak tytułu", "Notatka musi mieć tytuł!")
            return False

        # Upewnij się że user_id jest stringiem
        user_id_str = str(self.current_user_id)

        note_data = {
            "user_id": user_id_str,
            "title": title,
            "content": content
        }

        try:
            if self.current_note_index is not None and self.current_note_index < len(self.all_notes):
                # Aktualizacja istniejącej notatki
                note = self.all_notes[self.current_note_index]
                if "id" in note:
                    response = supabase.table("notes") \
                        .update(note_data) \
                        .eq("id", note["id"]) \
                        .execute()

                    print(f"DEBUG: Zaktualizowano notatkę ID: {note['id']}")
                else:
                    # Jeśli nie ma ID, dodaj jako nową
                    response = supabase.table("notes").insert(note_data).execute()
                    if response.data:
                        note_data["id"] = response.data[0]["id"]
                        self.all_notes[self.current_note_index] = note_data

                        print(f"DEBUG: Dodano nową notatkę z ID: {note_data['id']}")
            else:

                response = supabase.table("notes").insert(note_data).execute()
                if response.data:
                    note_data["id"] = response.data[0]["id"]
                    self.all_notes.append(note_data)
                    self.current_note_index = len(self.all_notes) - 1

                    print(f"DEBUG: Utworzono nową notatkę ID: {note_data['id']}")

            self.search_var.set("")
            self.populate_notes_list()
            messagebox.showinfo("Sukces", f"Notatka '{title}' zapisana!")
            return True

        except Exception as e:
            print(f"Pełny błąd zapisu: {e}")  # Debug
            messagebox.showerror("Błąd", f"Nie udało się zapisać: {str(e)}")
            return False


    def filter_notes(self, *args):
        search_term = self.search_var.get().lower()
        self.populate_notes_list(filter_text=search_term)

    def populate_notes_list(self, filter_text=""):
        self.notes_listbox.delete(0, tk.END)
        self.displayed_notes_indices = []

        for index, note in enumerate(self.all_notes):
            title = note.get("title", "Brak tytułu")
            if filter_text in title.lower():
                self.notes_listbox.insert(tk.END, title)
                self.displayed_notes_indices.append(index)

    def on_note_select(self, event=None):
        selected_indices = self.notes_listbox.curselection()
        if not selected_indices:
            return

        listbox_index = selected_indices[0]
        real_index = self.displayed_notes_indices[listbox_index]

        self.current_note_index = real_index
        note = self.all_notes[real_index]

        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, note.get("title", ""))

        # Wczytywanie obrazów
        content = note.get("content", "")
        self.render_content_with_images(content)

    def file_new(self):
        if not self.current_user_id:
            messagebox.showerror("Błąd", "Musisz być zalogowany, aby tworzyć notatki!")
            return

        self.title_entry.delete(0, tk.END)
        self.notepad_text.delete(1.0, tk.END)
        self.current_note_index = None
        self.notes_listbox.selection_clear(0, tk.END)
        self.search_var.set("")
        messagebox.showinfo("Nowa notatka", "Wpisz tytuł i treść, a następnie naciśnij 'Zapisz notatkę'.")

    def file_save(self):
        if not self.current_user_id:
            messagebox.showerror("Błąd", "Musisz być zalogowany, aby zapisywać notatki!")
            return

        title = self.title_entry.get()
        content = self.serialize_content_with_images()  # Zapis z obrazami

        if not title:
            messagebox.showwarning("Brak tytułu", "Notatka musi mieć tytuł, aby ją zapisać.")
            return

        note_data = {
            "title": title,
            "content": content,
            "user_id": self.current_user_id
        }

        if self.current_note_index is not None:
            self.all_notes[self.current_note_index] = note_data
        else:
            self.all_notes.append(note_data)
            self.current_note_index = len(self.all_notes) - 1

        if self.save_notes_to_file():

            self.search_var.set("")
            self.populate_notes_list()
            try:
                display_index = self.displayed_notes_indices.index(self.current_note_index)
                self.notes_listbox.selection_set(display_index)
                self.notes_listbox.see(display_index)
            except ValueError:
                pass
            messagebox.showinfo("Zapisano", f"Notatka '{title}' została zapisana.")

    # OBSŁUGA OBRAZKÓW (Skalowanie i Wklejanie)

    def render_content_with_images(self, content):
        self.notepad_text.delete("1.0", tk.END)
        self.images_cache.clear()
        self.pil_images.clear()

        parts = re.split(r"(\[\[IMG:.*?\]\])", content)

        for part in parts:
            if part.startswith("[[IMG:") and part.endswith("]]"):
                inner = part[6:-2]
                if "|" in inner:
                    filename, dims = inner.split("|")
                    try:
                        w, h = map(int, dims.split("x"))
                        self.insert_image_direct(filename, (w, h))
                    except:
                        self.insert_image_direct(filename)
                else:
                    self.insert_image_direct(inner)
            else:
                self.notepad_text.insert(tk.END, part)

    def insert_image_direct(self, filename, size=None):
        path = os.path.join(IMAGES_DIR, filename)
        if os.path.exists(path):
            try:
                if filename not in self.pil_images:
                    self.pil_images[filename] = Image.open(path)

                pil_img = self.pil_images[filename]

                if size:
                    pil_img_resized = pil_img.resize(size, Image.Resampling.LANCZOS)
                else:
                    if pil_img.width > 400:
                        ratio = 400 / pil_img.width
                        new_h = int(pil_img.height * ratio)
                        pil_img_resized = pil_img.resize((400, new_h), Image.Resampling.LANCZOS)
                    else:
                        pil_img_resized = pil_img

                tk_img = ImageTk.PhotoImage(pil_img_resized)
                self.images_cache[filename] = tk_img

                img_tag = f"IMG_{filename}_{uuid.uuid4().hex[:6]}"
                self.notepad_text.image_create(tk.END, image=tk_img, name=img_tag)

                # Dodaj tagi do skalowania
                self.notepad_text.tag_add(img_tag, "end-2c", "end-1c")
                self.notepad_text.tag_bind(img_tag, "<Enter>", lambda e: self.notepad_text.config(cursor="sizing"))
                self.notepad_text.tag_bind(img_tag, "<Leave>", lambda e: self.notepad_text.config(cursor=""))
                self.notepad_text.tag_bind(img_tag, "<Button-1>",
                                           lambda e, n=img_tag, f=filename: self.start_resize(e, n, f))
                self.notepad_text.tag_bind(img_tag, "<B1-Motion>", self.perform_resize)

                self.notepad_text.insert(tk.END, "\n")
            except Exception as e:
                print(f"Img error: {e}")
                self.notepad_text.insert(tk.END, f"[[IMG:{filename}]]")
        else:
            self.notepad_text.insert(tk.END, f"[[IMG:{filename}]]")

    def start_resize(self, event, tag_name, filename):
        self.resize_data = {
            "tag": tag_name,
            "filename": filename,
            "start_x": event.x
        }

    def perform_resize(self, event):
        if not hasattr(self, 'resize_data'): return
        data = self.resize_data
        filename = data["filename"]

        if filename not in self.pil_images: return
        orig_pil = self.pil_images[filename]

        dx = event.x - data["start_x"]

        current_tk_img = self.images_cache.get(filename)
        if not current_tk_img: return

        new_w = max(50, current_tk_img.width() + (dx // 5))
        aspect = orig_pil.height / orig_pil.width
        new_h = int(new_w * aspect)

        resized_pil = orig_pil.resize((new_w, new_h), Image.Resampling.NEAREST)
        new_tk = ImageTk.PhotoImage(resized_pil)

        self.images_cache[filename] = new_tk
        img_name_in_text = data["tag"]
        self.notepad_text.image_configure(img_name_in_text, image=new_tk)

    def serialize_content_with_images(self):
        content = ""
        try:
            for key, value, index in self.notepad_text.dump("1.0", "end-1c", text=True, image=True):
                if key == "text":
                    content += value
                elif key == "image":
                    parts = value.split('_')
                    if len(parts) >= 3:
                        real_filename = "_".join(parts[1:-1])
                        if real_filename in self.images_cache:
                            tk_img = self.images_cache[real_filename]
                            w, h = tk_img.width(), tk_img.height()
                            content += f"[[IMG:{real_filename}|{w}x{h}]]"
                        else:
                            content += f"[[IMG:{real_filename}]]"
                    else:
                        content += f"[[IMG:unknown.png]]"
        except Exception as e:
            print(f"Serialize error: {e}")
        return content

    def handle_paste(self, e):
        if not HAS_PILLOW: return
        try:
            img = ImageGrab.grabclipboard()
            if isinstance(img, Image.Image):
                name = f"img_{uuid.uuid4().hex[:6]}.png"
                img.save(os.path.join(IMAGES_DIR, name))
                self.insert_image_direct(name)
                return "break"
        except:
            pass

    def insert_image(self):
        '''Pozwala wybrać obraz z pliku'''
        if not HAS_PILLOW:
            messagebox.showerror("Błąd", "Brak biblioteki Pillow.")
            return

        file_path = filedialog.askopenfilename(
            filetypes=[("Obrazy", "*.png;*.jpg;*.jpeg;*.gif"), ("Wszystkie pliki", "*.*")]
        )

        if file_path:
            filename = os.path.basename(file_path)
            target_path = os.path.join(IMAGES_DIR, filename)

            if not os.path.exists(target_path):
                try:
                    shutil.copy(file_path, target_path)
                except Exception as e:
                    messagebox.showerror("Błąd", f"Nie udało się skopiować obrazu: {e}")
                    return

            self.insert_image_direct(filename)

    #  OCR Z OBRAZU
    def ocr_from_image(self):
        '''Zczytuje tekst z wybranego pliku graficznego (OCR)'''
        if not HAS_OCR:
            messagebox.showerror("Błąd OCR",
                                 "Nie znaleziono biblioteki pytesseract lub silnika Tesseract.\n\nUpewnij się, że zainstalowałeś program Tesseract-OCR.")  #######
            return

            # Wybór pliku
        file_path = filedialog.askopenfilename(
            title="Wybierz obraz do zczytania tekstu",
            filetypes=[("Obrazy", "*.png;*.jpg;*.jpeg;*.bmp"), ("Wszystkie pliki", "*.*")]
        )

        if file_path:
            try:
                # Zmieniamy kursor na "czekanie"
                self.config(cursor="wait")
                self.update()

                img = Image.open(file_path)

                # Próba zczytania (najpierw polski, potem domyślny)
                try:
                    text = pytesseract.image_to_string(img, lang='pol')
                except pytesseract.TesseractError:
                    text = pytesseract.image_to_string(img)

                    # Wstawiamy wynik
                if text.strip():
                    self.notepad_text.insert(tk.INSERT,
                                             f"\n--- [OCR] Tekst z obrazu: ---\n{text}\n---------------------------\n")
                    messagebox.showinfo("Sukces", "Tekst został zczytany!")
                else:
                    messagebox.showwarning("Info", "Nie udało się znaleźć tekstu na tym obrazku.")

            except Exception as e:
                messagebox.showerror("Błąd", f"Wystąpił błąd podczas OCR: {e}")
            finally:
                self.config(cursor="")
