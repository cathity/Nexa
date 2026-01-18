import tkinter as tk
from tkinter import font as tkfont, messagebox, ttk, scrolledtext
import os
import re
from PIL import Image, ImageTk

# Import funkcji z kontrolerów
from friends_controller import send_friend_request, get_user_friends, get_incoming_requests, accept_friend_request, reject_friend_request
from sharing_controller import get_shared_with_me, get_shared_by_me, get_my_notes_to_share, share_note, revoke_access

IMAGES_DIR = "images"  # Folder, w którym zapisywane są zdjęcia

class FriendDetailsWindow(tk.Toplevel):
    """Okno szczegółów znajomego - zarządzanie udostępnionymi notatkami"""
    def __init__(self, parent, current_user_id, friend_data):
        super().__init__(parent)
        self.title(f"Znajomy: {friend_data['username']}")
        self.geometry("600x500")
        
        self.current_user_id = current_user_id
        self.friend_id = friend_data['id']
        self.friend_name = friend_data['username']
        
        # Cache na obrazki, aby Python ich nie usunął z pamięci
        self.images_cache = {} 

        # Stylizacja zakładek
        style = ttk.Style()
        style.configure("TNotebook", tabposition='n') 
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # === ZAKŁADKA 1: Udostępnione DLA MNIE (Odebrane) ===
        self.tab_received = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.tab_received, text="Odebrane od znajomego")
        self.setup_received_tab()

        # === ZAKŁADKA 2: Udostępnione PRZEZE MNIE (Wysłane) ===
        self.tab_shared = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.tab_shared, text="Udostępnione przeze mnie")
        self.setup_shared_tab()

    def setup_received_tab(self):
        lbl = tk.Label(self.tab_received, text=f"Notatki, które {self.friend_name} udostępnił Tobie:", 
                       font=("Helvetica", 10, "bold"), bg="white")
        lbl.pack(pady=10)

        self.list_received = tk.Listbox(self.tab_received, font=("Helvetica", 11))
        self.list_received.pack(fill="both", expand=True, padx=10, pady=5)
        # Podwójne kliknięcie otwiera notatkę
        self.list_received.bind('<Double-Button-1>', self.view_received_note)

        tk.Label(self.tab_received, text="(Kliknij dwukrotnie, aby otworzyć notatkę)", 
                 font=("Arial", 8), bg="white", fg="gray").pack(pady=5)

        self.refresh_received()

    def setup_shared_tab(self):
        top_frame = tk.Frame(self.tab_shared, bg="white")
        top_frame.pack(fill="x", padx=10, pady=10)

        lbl = tk.Label(top_frame, text=f"Notatki, które Ty udostępniłeś dla {self.friend_name}:", 
                       font=("Helvetica", 10, "bold"), bg="white")
        lbl.pack(side="left")

        btn_share_new = tk.Button(top_frame, text="+ Udostępnij nową", bg="#3498db", fg="white",
                                  command=self.open_share_dialog)
        btn_share_new.pack(side="right")

        self.list_shared = tk.Listbox(self.tab_shared, font=("Helvetica", 11))
        self.list_shared.pack(fill="both", expand=True, padx=10, pady=5)

        btn_revoke = tk.Button(self.tab_shared, text="Zabierz dostęp (Usuń)", bg="#e74c3c", fg="white",
                               command=self.revoke_selected_note)
        btn_revoke.pack(fill="x", padx=10, pady=10)

        self.refresh_shared()

    def refresh_received(self):
        self.list_received.delete(0, tk.END)
        self.received_data = get_shared_with_me(self.current_user_id, self.friend_id)
        for note in self.received_data:
            self.list_received.insert(tk.END, f"📄 {note['title']}")

    def refresh_shared(self):
        self.list_shared.delete(0, tk.END)
        self.shared_data = get_shared_by_me(self.current_user_id, self.friend_id)
        for note in self.shared_data:
            self.list_shared.insert(tk.END, f"📤 {note['title']}")

    # --- LOGIKA WYŚWIETLANIA I OBRAZKÓW ---

    def view_received_note(self, event):
        """Otwiera okno z treścią notatki, renderując tekst i obrazy"""
        sel = self.list_received.curselection()
        if not sel: return
        
        index = sel[0]
        note = self.received_data[index]

        viewer = tk.Toplevel(self)
        viewer.title(f"Podgląd: {note['title']}")
        viewer.geometry("600x500")

        tk.Label(viewer, text=note['title'], font=("Helvetica", 14, "bold")).pack(pady=10)
        
        text_area = scrolledtext.ScrolledText(viewer, font=("Helvetica", 12))
        text_area.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Użycie funkcji renderującej
        self.render_content(text_area, note['content'])
        
        text_area.config(state="disabled") # Blokada edycji (tylko odczyt)

    def render_content(self, text_widget, content):
        """Parsuje tekst i zamienia tagi [[IMG:...]] na widoczne obrazki"""
        # Dzielimy tekst po tagach obrazków
        parts = re.split(r"(\[\[IMG:.*?\]\])", content)
        
        for part in parts:
            if part.startswith("[[IMG:") and part.endswith("]]"):
                # Mamy obrazek
                inner = part[6:-2]
                filename = inner
                size = None
                
                # Obsługa rozmiaru zapisanego w tagu (np. nazwa.png|200x100)
                if "|" in inner:
                    try:
                        f_part, s_part = inner.split("|")
                        filename = f_part
                        w, h = map(int, s_part.split("x"))
                        size = (w, h)
                    except:
                        filename = inner

                path = os.path.join(IMAGES_DIR, filename)
                
                if os.path.exists(path):
                    try:
                        pil_img = Image.open(path)
                        
                        # Skalowanie
                        if size:
                            pil_img = pil_img.resize(size, Image.Resampling.LANCZOS)
                        elif pil_img.width > 500: # Ograniczenie szerokości
                            ratio = 500 / pil_img.width
                            new_h = int(pil_img.height * ratio)
                            pil_img = pil_img.resize((500, new_h), Image.Resampling.LANCZOS)
                            
                        tk_img = ImageTk.PhotoImage(pil_img)
                        
                        # Zapisanie w cache (ważne!)
                        img_id = f"{filename}_{len(self.images_cache)}"
                        self.images_cache[img_id] = tk_img
                        
                        text_widget.image_create(tk.END, image=tk_img)
                        text_widget.insert(tk.END, "\n")
                    except Exception as e:
                        print(f"Błąd obrazka: {e}")
                        text_widget.insert(tk.END, f"[Błąd obrazka: {filename}]")
                else:
                    text_widget.insert(tk.END, f"[Brak pliku: {filename}]")
            else:
                # Zwykły tekst
                text_widget.insert(tk.END, part)

    # --- LOGIKA UDOSTĘPNIANIA ---

    def revoke_selected_note(self):
        sel = self.list_shared.curselection()
        if not sel: 
            messagebox.showinfo("Info", "Zaznacz notatkę do usunięcia dostępu.")
            return

        index = sel[0]
        share_id = self.shared_data[index]['share_id']

        if messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz zabrać dostęp do tej notatki?"):
            success, msg = revoke_access(share_id)
            if success:
                self.refresh_shared()
            else:
                messagebox.showerror("Błąd", msg)

    def open_share_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Wybierz notatkę")
        dialog.geometry("300x400")

        tk.Label(dialog, text="Wybierz notatkę do udostępnienia:", font=("Helvetica", 10)).pack(pady=10)

        lb = tk.Listbox(dialog, selectmode="single")
        lb.pack(fill="both", expand=True, padx=10, pady=5)

        my_notes = get_my_notes_to_share(self.current_user_id)
        for n in my_notes:
            lb.insert(tk.END, n['title'])

        def confirm():
            sel = lb.curselection()
            if not sel: return
            
            note_to_share = my_notes[sel[0]]
            success, msg = share_note(note_to_share['id'], self.friend_id)
            
            if success:
                messagebox.showinfo("Sukces", msg)
                self.refresh_shared()
                dialog.destroy()
            else:
                messagebox.showerror("Błąd", msg)

        tk.Button(dialog, text="Udostępnij", bg="#27ae60", fg="white", command=confirm).pack(pady=10)


class FriendsPage(tk.Frame):
    """Główna strona Przyjaciół - lista i zaproszenia"""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.current_user_id = None
        self.friends_data_cache = [] 
        
        # --- UI Layout ---
        self.main_container = tk.Frame(self)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # === Lewa strona: MOI ZNAJOMI ===
        self.left_frame = tk.Frame(self.main_container)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.lbl_friends = tk.Label(self.left_frame, text="Twoi znajomi:", font=("Helvetica", 14, "bold"))
        self.lbl_friends.pack(anchor="w", pady=(0, 10))
        
        tk.Label(self.left_frame, text="(Kliknij dwukrotnie, aby zobaczyć notatki)", font=("Arial", 9)).pack(anchor="w")

        self.friends_listbox = tk.Listbox(self.left_frame, font=("Helvetica", 12), relief="flat", bd=1, bg="#ecf0f1")
        self.friends_listbox.pack(fill="both", expand=True)
        # BINDING: Dwukrotne kliknięcie otwiera szczegóły
        self.friends_listbox.bind('<Double-Button-1>', self.on_friend_double_click)

        # === Prawa strona: ZAPROSZENIA i DODAWANIE ===
        self.right_frame = tk.Frame(self.main_container)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # -- Sekcja 1: Oczekujące zaproszenia --
        self.lbl_requests = tk.Label(self.right_frame, text="Oczekujące zaproszenia:", font=("Helvetica", 12, "bold"))
        self.lbl_requests.pack(anchor="w", pady=(0, 5))

        self.requests_listbox = tk.Listbox(self.right_frame, font=("Helvetica", 11), relief="flat", bd=1, height=6)
        self.requests_listbox.pack(fill="x", pady=(0, 5))
        
        self.req_btn_frame = tk.Frame(self.right_frame)
        self.req_btn_frame.pack(fill="x", pady=(0, 20))

        self.btn_accept = tk.Button(self.req_btn_frame, text="Akceptuj", command=self.perform_accept,
                                    bg="#27ae60", fg="white", font=("Helvetica", 9))
        self.btn_accept.pack(side="left", fill="x", expand=True, padx=(0, 2))

        self.btn_reject = tk.Button(self.req_btn_frame, text="Odrzuć", command=self.perform_reject,
                                    bg="#e74c3c", fg="white", font=("Helvetica", 9))
        self.btn_reject.pack(side="left", fill="x", expand=True, padx=(2, 0))

        # -- Sekcja 2: Wyślij zaproszenie --
        tk.Frame(self.right_frame, height=2, bg="#bdc3c7").pack(fill="x", pady=10)

        self.lbl_add = tk.Label(self.right_frame, text="Wyślij zaproszenie:", font=("Helvetica", 14, "bold"))
        self.lbl_add.pack(anchor="w", pady=(0, 10))

        self.lbl_info = tk.Label(self.right_frame, text="Wpisz nazwę użytkownika (Login):", font=("Helvetica", 10))
        self.lbl_info.pack(anchor="w")

        self.username_entry = tk.Entry(self.right_frame, font=("Helvetica", 12), relief="solid", bd=1)
        self.username_entry.pack(fill="x", pady=5, ipady=4)

        self.btn_add = tk.Button(self.right_frame, text="Wyślij zaproszenie", command=self.perform_send_request,
                                 bg="#3498db", fg="white", font=("Helvetica", 10, "bold"), relief="flat")
        self.btn_add.pack(fill="x", pady=10)

        # -- Powrót --
        self.btn_back = tk.Button(self, text="Wróć do notatnika", 
                                  command=lambda: controller.show_frame("NotepadApplication", {"id": self.current_user_id}),
                                  bg="#95a5a6", fg="white")
        self.btn_back.pack(fill="x", side="bottom", pady=10, padx=20)

        self.pending_requests_data = []

    def set_current_user(self, user_id):
        self.current_user_id = user_id
        self.refresh_all()

    def refresh_all(self):
        self.refresh_friends_list()
        self.refresh_requests_list()

    def refresh_friends_list(self):
        self.friends_listbox.delete(0, tk.END)
        self.friends_data_cache = get_user_friends(self.current_user_id)
        
        if not self.friends_data_cache:
            self.friends_listbox.insert(tk.END, "(Brak znajomych)")
            return

        for friend in self.friends_data_cache:
            display_text = f"👤 {friend['username']}"
            self.friends_listbox.insert(tk.END, display_text)

    def on_friend_double_click(self, event):
        """Otwiera okno szczegółów znajomego"""
        sel = self.friends_listbox.curselection()
        if not sel: return
        
        index = sel[0]
        # Sprawdzamy czy lista nie jest pusta
        if not self.friends_data_cache or index >= len(self.friends_data_cache):
            return

        friend_data = self.friends_data_cache[index]
        
        # Otwieramy nowe okno
        FriendDetailsWindow(self, self.current_user_id, friend_data)

    def refresh_requests_list(self):
        self.requests_listbox.delete(0, tk.END)
        self.pending_requests_data = get_incoming_requests(self.current_user_id)
        
        if not self.pending_requests_data:
            self.requests_listbox.insert(tk.END, "(Brak nowych zaproszeń)")
            self.btn_accept.config(state="disabled")
            self.btn_reject.config(state="disabled")
            return
        
        self.btn_accept.config(state="normal")
        self.btn_reject.config(state="normal")

        for req in self.pending_requests_data:
            self.requests_listbox.insert(tk.END, f"📩 Od: {req['username']}")

    def perform_send_request(self):
        target_username = self.username_entry.get()
        if not target_username:
            messagebox.showwarning("Błąd", "Podaj nazwę użytkownika.")
            return

        success, msg = send_friend_request(self.current_user_id, target_username)
        if success:
            messagebox.showinfo("Sukces", msg)
            self.username_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Błąd", msg)

    def get_selected_request_id(self):
        sel = self.requests_listbox.curselection()
        if not sel:
            messagebox.showinfo("Info", "Wybierz zaproszenie z listy.")
            return None
        
        index = sel[0]
        if index >= len(self.pending_requests_data):
            return None
            
        return self.pending_requests_data[index]['request_id']

    def perform_accept(self):
        req_id = self.get_selected_request_id()
        if req_id:
            success, msg = accept_friend_request(req_id)
            if success:
                messagebox.showinfo("Sukces", msg)
                self.refresh_all()
            else:
                messagebox.showerror("Błąd", msg)

    def perform_reject(self):
        req_id = self.get_selected_request_id()
        if req_id:
            success, msg = reject_friend_request(req_id)
            if success:
                messagebox.showinfo("Info", msg)
                self.refresh_requests_list()
            else:
                messagebox.showerror("Błąd", msg)

    def update_theme(self, colors):
        self.config(bg=colors["bg_primary"])
        self.main_container.config(bg=colors["bg_primary"])
        self.left_frame.config(bg=colors["bg_primary"])
        self.right_frame.config(bg=colors["bg_primary"])
        self.req_btn_frame.config(bg=colors["bg_primary"])
        
        self.lbl_friends.config(bg=colors["bg_primary"], fg=colors["fg_primary"])
        self.lbl_add.config(bg=colors["bg_primary"], fg=colors["fg_primary"])
        self.lbl_info.config(bg=colors["bg_primary"], fg=colors["fg_primary"])
        self.lbl_requests.config(bg=colors["bg_primary"], fg=colors["fg_primary"])
        
        self.friends_listbox.config(bg=colors["list_bg"], fg=colors["list_fg"])
        self.requests_listbox.config(bg=colors["list_bg"], fg=colors["list_fg"])
        self.username_entry.config(bg=colors["entry_bg"], fg=colors["entry_fg"], insertbackground=colors["fg_primary"])
