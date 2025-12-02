
import tkinter as tk
from tkinter import messagebox
from tkcalendar import Calendar
from database import get_connection
import datetime


class CalendarApplication(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller
        self.current_user_id = None
        self.selected_date = None

        # Układ: Lewa strona (Kalendarz), Prawa strona (Lista wydarzeń dnia)
        self.paned_window = tk.PanedWindow(self, orient="horizontal", sashrelief="raised")
        self.paned_window.pack(fill="both", expand=True)

        # --- LEWA STRONA: KALENDARZ ---
        self.left_frame = tk.Frame(self.paned_window, padx=10, pady=10)
        self.paned_window.add(self.left_frame)

        # Tworzymy kalendarz
        self.cal = Calendar(self.left_frame, selectmode='day', date_pattern='yyyy-mm-dd')
        self.cal.pack(fill="both", expand=True)
        self.cal.bind("<<CalendarSelected>>", self.on_date_select)

        # To sprawi, że dni z tagiem 'event' będą miały zielone tło i biały tekst
        self.cal.tag_config('has_event', background='#2ecc71', foreground='white')

        # Przycisk dodawania wydarzenia
        self.add_btn = tk.Button(self.left_frame, text="Dodaj wydarzenie", command=self.add_event_popup,
                                 bg="#3498db", fg="white", font=("Helvetica", 10, "bold"))
        self.add_btn.pack(pady=10, fill="x")

        # --- PRAWA STRONA: LISTA WYDARZEŃ ---
        self.right_frame = tk.Frame(self.paned_window, padx=10, pady=10)
        self.paned_window.add(self.right_frame)

        self.info_label = tk.Label(self.right_frame, text="Wydarzenia:", font=("Helvetica", 14, "bold"))
        self.info_label.pack(anchor="w")

        self.events_listbox = tk.Listbox(self.right_frame, font=("Helvetica", 11), relief="flat", bg="#f0f0f0")
        self.events_listbox.pack(fill="both", expand=True, pady=5)

        self.delete_btn = tk.Button(self.right_frame, text="Usuń zaznaczone", command=self.delete_event,
                                    bg="#e74c3c", fg="white")
        self.delete_btn.pack(fill="x")

    def set_current_user(self, user_id):
        self.current_user_id = user_id

        # 1. Zaznaczamy dzisiejszą datę
        today = datetime.date.today().strftime("%Y-%m-%d")
        self.cal.selection_set(today)

        # 2. Rysujemy "kropki/kolory" na dniach, które mają wydarzenia
        self.mark_days_with_events()

        # 3. Ładujemy listę dla dzisiejszego dnia
        self.on_date_select(None)

    def mark_days_with_events(self):
        """Pobiera wszystkie daty wydarzeń użytkownika i zaznacza je na kalendarzu"""
        # Najpierw czyścimy stare znaczniki
        self.cal.calevent_remove('all')

        if not self.current_user_id: return

        conn = get_connection()
        cur = conn.cursor()
        # Pobieramy tylko daty
        cur.execute("SELECT event_date FROM events WHERE user_id=?", (self.current_user_id,))
        rows = cur.fetchall()
        conn.close()

        for row in rows:
            date_str = row[0]
            # Musimy zamienić napis '2023-11-26' na obiekt daty, żeby kalendarz zrozumiał
            try:
                date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                # Dodajemy znacznik (event) do kalendarza
                self.cal.calevent_create(date_obj, 'Wydarzenie', 'has_event')
            except ValueError:
                pass  # Ignorujemy błędne daty

    def on_date_select(self, event):
        self.selected_date = self.cal.get_date()
        self.info_label.config(text=f"Wydarzenia na: {self.selected_date}")
        self.load_events_for_date(self.selected_date)

    def load_events_for_date(self, date_str):
        self.events_listbox.delete(0, tk.END)
        self.events_listbox.event_ids = []  # Czyścimy listę ID

        if not self.current_user_id: return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, title, description FROM events WHERE user_id=? AND event_date=?",
                    (self.current_user_id, date_str))
        rows = cur.fetchall()
        conn.close()

        for row in rows:
            display_text = f"• {row[1]}"
            if row[2]: display_text += f" ({row[2]})"
            self.events_listbox.insert(tk.END, display_text)
            self.events_listbox.event_ids.append(row[0])

    def add_event_popup(self):
        if not self.current_user_id: return

        top = tk.Toplevel(self)
        top.title("Nowe wydarzenie")
        top.geometry("300x200")

        tk.Label(top, text=f"Data: {self.selected_date}").pack(pady=5)

        tk.Label(top, text="Tytuł:").pack(pady=2)
        e_title = tk.Entry(top)
        e_title.pack(padx=10, fill="x")

        tk.Label(top, text="Opis (opcjonalnie):").pack(pady=2)
        e_desc = tk.Entry(top)
        e_desc.pack(padx=10, fill="x")

        def save():
            title = e_title.get()
            desc = e_desc.get()
            if not title:
                messagebox.showwarning("Błąd", "Podaj tytuł!")
                return

            conn = get_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO events (user_id, event_date, title, description) VALUES (?, ?, ?, ?)",
                        (self.current_user_id, self.selected_date, title, desc))
            conn.commit()
            conn.close()

            top.destroy()

            self.mark_days_with_events()  # To pomaluje dzień na zielono!
            self.load_events_for_date(self.selected_date)  # To odświeży listę po prawej

        tk.Button(top, text="Zapisz", command=save, bg="#2ecc71", fg="white").pack(pady=15)

    def delete_event(self):
        sel = self.events_listbox.curselection()
        if not sel: return

        index = sel[0]
        # Sprawdzamy czy mamy listę ID (zabezpieczenie)
        if not hasattr(self.events_listbox, 'event_ids') or index >= len(self.events_listbox.event_ids):
            return

        event_id = self.events_listbox.event_ids[index]

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM events WHERE id=?", (event_id,))
        conn.commit()
        conn.close()

        self.mark_days_with_events()  # Jeśli usunięto ostatnie wydarzenie, kolor zniknie
        self.load_events_for_date(self.selected_date)

    def create_calendar_menu(self):
        main_window = self.controller

        main_window.menubar = tk.Menu(main_window)
        main_window.config(menu=main_window.menubar)

        nav_menu = tk.Menu(main_window.menubar, tearoff=0)
        main_window.menubar.add_cascade(label="Nawigacja", menu=nav_menu)

        nav_menu.add_command(label="Wróć do Notatnika",
                             command=lambda: self.controller.show_frame("NotepadApplication",
                                                                        {"id": self.current_user_id}))

        settings_menu = tk.Menu(main_window.menubar, tearoff=0)
        main_window.menubar.add_cascade(label="Opcje", menu=settings_menu)

        if self.controller.current_theme == "light":
            theme_label = "Zmień na motyw ciemny"
        else:
            theme_label = "Zmień na motyw jasny"

        settings_menu.add_command(label=theme_label, command=self.controller.toggle_theme)
        settings_menu.add_separator()
        settings_menu.add_command(label="Wyloguj", command=self.logout)

        self.update_theme(self.controller.colors)

    def logout(self):
        self.current_user_id = None
        self.controller.show_frame("StartPage")

    def update_theme(self, colors):
        self.config(bg=colors["bg_secondary"])
        self.paned_window.config(bg=colors["bg_secondary"])
        self.left_frame.config(bg=colors["bg_primary"])
        self.right_frame.config(bg=colors["bg_primary"])
        self.info_label.config(bg=colors["bg_primary"], fg=colors["fg_primary"])
        self.events_listbox.config(bg=colors["list_bg"], fg=colors["list_fg"])
